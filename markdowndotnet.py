import collections
import json
import logging
import os
import re
from xml.etree import ElementTree

import click
# noinspection PyUnresolvedReferences,PyPackageRequirements
import clr
import requests
import yaml

from System.Reflection import Assembly, MemberInfo
from System.IO import FileInfo
from System import Type

class_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<name>\w.+)")
field_property_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<class>\w.+)\.(?P<name>[\w#].*)")
method_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<class>\w.+)\.(?P<name>[\w#]+.\(.*\))")
parameters_pattern = re.compile(r"(\(.*\))")

see_pattern = re.compile(r'<see\s+cref="(\w):([^"]+)"\s+/>')
c_pattern = re.compile(r'<c>([^<]+)</c>')

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter('%(levelname)-7s: %(message)s'))
log.addHandler(consoleHandler)

output_dir = ""


def get_params(func):
    """
    Gets a list of parameter types (as strings)

    :param func: The method's full name, with parenthesis
    :return: containing the type of each parameter in order.
    :rtype: list[str]
    """
    m = parameters_pattern.search(func)
    if not m:
        # If there are no parenthesis in name, method has no parameters
        return []
    else:
        return m.group(1).replace("(", "").replace(")", "").split(",")


def get_type(local_assembly, type_name):
    """Gets the type's class via reflection

    The type is looked for in the local assembly first,
    if not found, it will be looked in the system assembly.

    :param Assembly local_assembly:  Assembly object to look for.
    :param str type_name: The full name of the type.
    :return: A C# Type object.
    :rtype: Type
    """
    local_type = local_assembly.GetType(type_name)
    if local_type is None:
        return Type.GetType(type_name)
    return local_type


def get_link(local_assembly, *, type_name=None, cs_type=None, current_file=None):
    """Gets a link in markdown format for the type

    If type_name is supplied, cs_type will be obtained from it.
    If the type is in the local assembly, a relative link to type's markdown file will be generated
    Otherwise, a link to docs.microsoft will be returned

    :param Assembly local_assembly: The local C# Assembly object.
    :param str type_name: The full name of the type.
    :param Type cs_type: The C# Type object.
    :param str current_file: The path of the file where the type is being referenced from.
    :return: A markdown syntax link to the type's documentation.
    :rtype: str
    :raises ValueError: if both type_name and cs_type are None.
    """
    if not type_name and not cs_type:
        raise ValueError("Both type_name and cs_type can't be None")
    if type_name is not None:
        cs_type = get_type(local_assembly, type_name)
    if cs_type is None:
        log.warning("Couldn't find type: {}", type_name)
        return type_name
    suffix = ""
    if cs_type.IsArray:
        cs_type = cs_type.GetElementType()
        suffix = "[]"
    # Type belongs to the assembly, so link will be relative
    if cs_type.Assembly.FullName == local_assembly.FullName:
        current_path = os.path.dirname(current_file) + "/"
        target_file = os.path.join(output_dir, str(cs_type).replace('.', '/') + ".md")
        relative_path = os.path.relpath(target_file, current_path)
        return "[{0}]({1}){2}".format(cs_type.Name, relative_path, suffix)
    else:
        r = requests.get('https://xref.docs.microsoft.com/query', params={"uid": cs_type.FullName})
        data = json.loads(r.text)
        if len(data) < 0:
            log.warning("Couldn't find documentation reference for {0}.".format(cs_type.FullName))
            return cs_type.FullName
        return "[{0}]({1}){2}".format(data[0]['name'], data[0]['href'], suffix)


def build_table(headers, rows):
    """Builds a markdown syntax table

    :param list[str] headers: The table's header
    :param list[list[str]] rows: A list of rows to put in the table, where each row is a list of columns.
    :return: The table in markdown syntax
    :rtype: str
    """
    output = "\n| {0} |\n".format(' | '.join(headers))
    output += "| {0} |\n".format(' | '.join(['---']*len(headers)))
    for row in rows:
        output += "| {0} |\n".format(' | '.join(row))
    return output+'\n'


def get_type_name(cs_type):
    """Gets a C# type's short name (without namespace)

    The types are first looked up in an aliases dictionary.
    If an alias is found, the alias is returned, otherwise, the name is returned.

    :param Type cs_type: The C# type
    :return: The name or alias of the Type
    :rtype: str
    """
    aliases = {
        "System.String": "string",
        "System.SByte": "sbyte",
        "System.Byte": "byte",
        "System.Int16": "short",
        "System.UInt16": "ushort",
        "System.Int32": "int",
        "System.UInt32": "uint",
        "System.Int64": "long",
        "System.UInt64": "ulong",
        "System.Char": "char",
        "System.Single": "float",
        "System.Double": "double",
        "System.Boolean": "bool",
        "System.Decimal": "decimal",
        "System.Void": "void"
    }
    return aliases.get(cs_type.FullName, cs_type.Name)


def parse_content(assembly, content, current_file):
    """ Parses the content of a XML tag, converting inner XML tags into markdown format.

    'see' tags are converted into links
    'c' tags are converted into inline code

    :param assembly: The string's assembly's context
    :param content: The contents of the xml tag
    :param current_file: The current file location
    :return: The string with markdown format
    """
    def parse_see_tag(m):
        member_type = m.group(1)
        full_name = m.group(2)
        if member_type == "T":
            return get_link(assembly, type_name=full_name, current_file=current_file)
        else:
            return "`{0}`".format(m.group(2))

    content = see_pattern.sub(lambda match: parse_see_tag(match), content)
    content = c_pattern.sub("`\g<1>`", content)
    return content


def parse_constructor(member_type: Type, name, documentation, file_path):
    """Generates markdown content for an object's constructor

    :param Type member_type: The C# type of the member containing the constructor
    :param str name: The name of the field
    :param dict[str, Any] documentation: A dictionary containing the XML documentation.
    :param str file_path: The file path of the markdown file containing the member.
    :return: A string containing the constructor's formatted documentation
    :rtype: str
    """
    assembly = member_type.Assembly
    # Get a list of the parameter types
    params = get_params(name)
    # Get the actual C# types of parameters
    param_types = [get_type(assembly, x) for x in params]
    constructor = member_type.GetConstructor(param_types)
    if constructor is None:
        log.warning("Constructor '{0}' not found in assembly.", name.replace('.', '#'))
        return ""

    parameters = constructor.GetParameters()
    # Get a string list containing the parameter's type and name.
    params_declaration = ", ".join(["{0} {1}".format(get_type_name(x.ParameterType), x.Name) for x in parameters])
    # Show a level 3 header with the method's name
    content = '### {0}({1})\n'.format(member_type.Name, ",".join([str(x.ParameterType) for x in parameters]))
    # Show the constructor's summary if available
    if "summary" in documentation:
        content += "{}  \n".format(parse_content(assembly, documentation['summary'], file_path))
    # Show the constructor's declaration
    declaration = "**Declaration**\n" \
                  "```csharp\n" \
                  "public {}({});\n" \
                  "```\n".format(member_type.Name, params_declaration)
    content += declaration
    # Show the constructor's remarks if available
    if "remarks" in documentation:
        content += "**Remarks**  \n"
        content += "{}  \n".format(parse_content(assembly, documentation['remarks'], file_path))
    # If the constructor has parameters, show a table with their type, name and description
    if len(parameters) > 0 and "param" in documentation:
        content += "**Parameters**\n"
        param_documentation = documentation.get('param', collections.OrderedDict())
        headers = ["Type", "Name", "Description"]
        rows = []
        for param in parameters:
            description = parse_content(assembly, param_documentation.get(param.Name, ""), file_path)
            param_link = get_link(assembly, cs_type=param.ParameterType, current_file=file_path)
            rows.append([param_link, param.Name, description])
        content += build_table(headers, rows)
    return content


def parse_field(member_type, name, documentation, file_path):
    """Generates markdown content for an object's field

    :param Type member_type: The C# type of the member containing the field
    :param str name: The name of the field
    :param Dict documentation: A dictionary containing the XML documentation.
    :param file_path: The file path of the markdown file containing the member.
    :return: A string containing the field's formatted documentation
    """
    assembly = member_type.Assembly
    field = member_type.GetField(name)
    if field is None:
        log.warning("Field '{}' not found in assembly.".format(name))
        return ""

    field_type = field.FieldType
    type_link = get_link(assembly, cs_type=field_type, current_file=file_path)
    # Show a level 3 header with the field's name
    content = '### {}\n'.format(name)
    # Show the field's summary if available
    if "summary" in documentation:
        content += "{}  \n".format(parse_content(assembly, documentation['summary'], file_path))
    # Show the field's declaration
    declaration = "**Declaration**\n" \
                  "```csharp\n" \
                  "public {0} {1};\n" \
                  "```\n".format(get_type_name(field_type), name)
    content += declaration
    # Show the field's remarks if available
    if "remarks" in documentation:
        content += "**Remarks**  \n"
        content += "{}  \n".format(parse_content(assembly, documentation['remarks'], file_path))
    # Show a table containing the field's type and value
    content += "**Field Value**\n"
    field_value = parse_content(assembly, documentation.get("value", ""), file_path)
    table = build_table(["Type", "Description"], [[type_link, field_value]])
    content += table
    return content


def parse_property(member_type, name, documentation, file_path):
    """Generates markdown content for an object's property

    :param Type member_type: The C# type of the member containing the field
    :param str name: The name of the field
    :param Dict documentation: A dictionary containing the XML documentation.
    :param file_path: The file path of the markdown file containing the member.
    :return: A string containing the property's formatted documentation
    """
    assembly = member_type.Assembly
    cs_property = member_type.GetProperty(name)
    if cs_property is None:
        log.warning("Property '{}' not found in assembly.".format(name))
        return ""

    property_type = cs_property.PropertyType
    type_link = get_link(assembly, cs_type=property_type, current_file=file_path)
    getter = "" if cs_property.GetGetMethod(False) is None else "get; "
    setter = "" if cs_property.GetSetMethod(False) is None else "set; "
    # Show a level 3 header with the property's name
    content = "### {}\n".format(name)
    # Show the field's summary if available
    if "summary" in documentation:
        content += "{}  \n".format(parse_content(assembly, documentation['summary'], file_path))
    # Show the property's declaration
    declaration = "**Declaration**\n" \
                  "```csharp\n" \
                  "public {0} {1} {{{2}{3}}}\n" \
                  "```\n".format(get_type_name(property_type), name, getter, setter)
    content += declaration
    # Show the property's remarks if available
    if "remarks" in documentation:
        content += "**Remarks**  \n"
        content += "{}  \n".format(parse_content(assembly, documentation['remarks'], file_path))
    # Show a table containing the property's type and value
    content += "**Property Value**\n"
    property_value = parse_content(assembly, documentation.get("value", ""), file_path)
    table = build_table(["Type", "Description"], [[type_link, property_value]])
    content += table
    return content


def parse_delegate(delegate, documentation, file_path):
    """Generates markdown content for an object's method

    :param Type delegate: The C# type of the member containing the method
    :param Dict documentation: A dictionary containing the XML documentation.
    :param file_path: The file path of the markdown file containing the member.
    :return: A string containing the delegate's formatted documentation
    """
    assembly = delegate.Assembly
    name = delegate.Name
    method = delegate.GetMethod('Invoke')
    # If method doesn't have parameters, we add empty parenthesis to the name
    if delegate is None or method is None:
        log.warning("Delegate '{}' not found in assembly.").format(name)
        return ""

    return_type = method.ReturnType
    parameters = method.GetParameters()
    # Get a string list containing the parameter's type and name.
    params_declaration = " ,".join(["{} {}".format(get_type_name(x.ParameterType), x.Name) for x in parameters])
    # Show the method's declaration
    content = "**\nDeclaration**\n" \
              "```csharp\n" \
              "public delegate {} {}({})\n" \
              "```\n".format(get_type_name(return_type), name, params_declaration)
    # Show the method's remarks if available
    if "remarks" in documentation:
        content += "**Remarks**  \n"
        content += "{}  \n".format(parse_content(assembly, documentation['remarks'], file_path))
    # If method has parameters, show a table with their type, name and description
    if len(parameters) > 0 and "param" in documentation:
        content += "**Parameters**\n"
        param_documentation = documentation.get('param', collections.OrderedDict())
        headers = ["Type", "Name", "Description"]
        rows = []
        for param in parameters:
            description = parse_content(assembly, param_documentation.get(param.Name, ""), file_path)
            param_link = get_link(assembly, cs_type=param.ParameterType, current_file=file_path)
            rows.append([param_link, param.Name, description])
        content += build_table(headers, rows)
    # Show table with the returned value, type and description, unless the type is Void.
    if return_type.Name != "Void":
        content += "**Returns**\n"
        description = parse_content(assembly, documentation.get("returns", ""), file_path)
        type_link = get_link(assembly, cs_type=method.ReturnType, current_file=file_path)
        table = build_table(["Type", "Description"], [[type_link, description]])
        content += table
    return content


def parse_method(member_type, name, documentation, file_path):
    """Generates markdown content for an object's method

    :param Type member_type: The C# type of the member containing the method
    :param str name: The name of the field
    :param Dict documentation: A dictionary containing the XML documentation.
    :param file_path: The file path of the markdown file containing the member.
    :return: A string containing the method's formatted documentation
    """
    assembly = member_type.Assembly
    # Remove any parenthesis from the name if found
    method_name = name.split("(")[0]
    # Get a list of the parameter types
    params = get_params(name)
    # Get the actual C# types of parameters
    param_types = [get_type(assembly, x) for x in params]
    method = member_type.GetMethod(method_name, param_types)
    # If method doesn't have parameters, we add empty parenthesis to the name
    if len(params) == 0:
        name += "()"
    if method is None:
        log.warning("Method '{}' not found in assembly.".format(name))
        return ""

    return_type = method.ReturnType
    parameters = method.GetParameters()
    modifiers_checks = {
        'private': method.IsPrivate,
        'public': method.IsPublic,
        'static': method.IsStatic,
        'abstract': method.IsAbstract,
        'virtual': method.IsVirtual,
        'sealed': method.IsFinal,
    }
    method_modifiers = " ".join([k for k, v in modifiers_checks.items() if v])
    # Get a string list containing the parameter's type and name.
    params_declaration = " ,".join(["{} {}".format(get_type_name(x.ParameterType), x.Name) for x in parameters])
    # Show a level 3 header with the method's name
    content = "### {}\n".format(name)
    # Show the method's summary if available
    if "summary" in documentation:
        content += "{}  \n".format(parse_content(assembly, documentation['summary'], file_path))
    # Show the method's declaration
    content += "**Declaration**\n" \
               "```csharp\n" \
               "{0} {1} {2}({3})\n" \
               "```\n".format(method_modifiers, get_type_name(return_type), method_name, params_declaration)
    # Show the method's remarks if available
    if "remarks" in documentation:
        content += "**Remarks**  \n"
        content += "{}  \n".format(parse_content(assembly, documentation['remarks'], file_path))
    # If method has parameters, show a table with their type, name and description
    if len(parameters) > 0 and "param" in documentation:
        content += "**Parameters**\n"
        param_documentation = documentation.get('param', collections.OrderedDict())
        headers = ["Type", "Name", "Description"]
        rows = []
        for param in parameters:
            description = parse_content(assembly, param_documentation.get(param.Name, ""), file_path)
            param_link = get_link(assembly, cs_type=param.ParameterType, current_file=file_path)
            rows.append([param_link, param.Name, description])
        content += build_table(headers, rows)
    # Show table with the returned value, type and description, unless the type is Void.
    if return_type.Name != "Void":
        content += "**Returns**\n"
        description = parse_content(assembly, documentation.get("returns", ""), file_path)
        type_link = get_link(assembly, cs_type=method.ReturnType, current_file=file_path)
        table = build_table(["Type", "Description"], [[type_link, description]])
        content += table
    return content


def parse_event(member_type, name, documentation, file_path):
    """Generates markdown content for an object's method

    :param Type member_type: The C# type of the member containing the event
    :param str name: The name of the event
    :param Dict documentation: A dictionary containing the XML documentation.
    :param file_path: The file path of the markdown file containing the member.
    :return: A string containing the event's formatted documentation
    """
    assembly = member_type.Assembly
    event = member_type.GetEvent(name)
    # If method doesn't have parameters, we add empty parenthesis to the name
    if event is None:
        log.warning("Event '{}' not found in assembly.".format(name))
        return ""

    handler_type = event.EventHandlerType
    # Show a level 3 header with the method's name
    content = '### {}\n'.format(name)
    # Show the method's summary if available
    if "summary" in documentation:
        content += "{}  \n".format(parse_content(assembly, documentation['summary'], file_path))
    # Show the method's declaration
    content += "**Declaration**\n" \
               "```csharp\n" \
               "public event {} {}\n" \
               "```\n".format(get_type_name(handler_type), event.Name)
    # Show the method's remarks if available
    if "remarks" in documentation:
        content += "**Remarks**  \n"
        content += "{}  \n".format(parse_content(assembly, documentation['remarks'], file_path))
    # Show table with the handler type and description, unless the type is Void.
    if handler_type.Name != "Void":
        content += "**Event Handler**  \n"
        content += get_link(assembly, cs_type=handler_type, current_file=file_path)
    return content


def parse_documentation(path):
    log.info("Parsing documentation")
    tree = ElementTree.parse(path)
    hierarchy = collections.OrderedDict()
    root = tree.getroot()
    # Explore the XML file to get a structured hierarchy for the project
    for member_item in root.find('members'):
        member_type, full_name = member_item.attrib['name'].split(":")
        documentation = collections.OrderedDict()
        for child in member_item:
            pattern = r"<(?:\w+:)?%(tag)s(?:[^>]*)>(.*)</(?:\w+:)?%(tag)s" % {"tag": child.tag}
            try:
                content = re.findall(pattern, ElementTree.tostring(child).decode('utf-8'), re.DOTALL)[0].strip()
            except IndexError:
                content = ""
            if child.tag == "param":
                if child.tag not in documentation:
                    documentation[child.tag] = collections.OrderedDict()
                documentation[child.tag][child.get("name")] = content
            else:
                documentation[child.tag] = content
        if member_type == "T":
            m = class_pattern.search(full_name)
            if m:
                namespace = m.group("namespace")
                name = m.group("name")
                in_class = None
                log.debug("Type found: %s", name)
            else:
                continue
        else:
            m = method_pattern.search(full_name)
            if not m:
                m = field_property_pattern.search(full_name)
                if not m:
                    continue
            namespace = m.group("namespace")
            in_class = m.group("class")
            name = m.group("name")
            log.debug("Member found: %s", name)
            if "#ctor" in name:
                name = name.replace("#ctor", '.ctor')
                member_type = 'C'

        if namespace not in hierarchy:
            hierarchy[namespace] = collections.OrderedDict()
        if member_type == "T":
            if name not in hierarchy[namespace]:
                hierarchy[namespace][name] = {"children": collections.OrderedDict(), "documentation": documentation, 'type': member_type}
        else:
            hierarchy[namespace][in_class]["children"][name] = {"documentation": documentation, 'type': member_type}

    os.makedirs(output_dir, exist_ok=True)

    hierarchy = dict(sorted(hierarchy.items()))

    # Generate a json file, for debugging purposes
    with open(os.path.join(output_dir, "hierarchy.json"), 'w') as outfile:
        json.dump(hierarchy, outfile, indent=4)
        log.debug("Generated hierarchy file on: %s", outfile.name)

    return hierarchy


def build_documentation(dll_path, hierarchy):
    log.info("Building documentation")
    dll_file = FileInfo(dll_path)
    assembly = Assembly.LoadFile(dll_file.FullName)
    # Iterate through all namespaces
    # Each namespace is a folder, each class is a file
    # Also builds a YAML index
    index = []
    for namespace, members in hierarchy.items():
        index_files = []
        for member, content in members.items():
            filename = "{}.md".format((namespace+'/'+member).replace('.','/'))
            file_path = os.path.join(output_dir, filename)
            # Ensure intermediary directories exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                log.debug("Building %s", file.name)
                index_files.append({member: filename})
                member_type = assembly.GetType("{}.{}".format(namespace, member))
                object_type = "Class"
                if member_type is None:
                    member_type = assembly.GetType("{}+{}".format(namespace, member))
                    object_type = "Delegate"
                if member_type.IsEnum:
                    object_type = "Enum"
                # Check if member inherits other members:
                base_type = member_type.BaseType
                if base_type is not None:
                    file.write("**Inherits**  \n{}\n".format(get_link(assembly, cs_type=base_type, current_file=file_path)))
                file.write("# {} {}\n".format(object_type, member))
                file.write("{}\n".format(parse_content(assembly, content.get('documentation',collections.OrderedDict()).get('summary'), current_file=file_path)))
                _temp = collections.OrderedDict()
                # Enums are represented differently
                if object_type == "Enum":
                    rows = []
                    for field, subcontent in content["children"].items():
                        documentation = subcontent["documentation"]
                        rows.append([field, documentation.get("summary", "")])
                    enum_table = build_table(["Field", "Description"], rows)
                    file.write(enum_table)
                    continue
                if object_type == "Delegate":
                    file.write(parse_delegate(member_type, content.get('documentation', collections.OrderedDict()), file_path))
                    continue
                for name, subcontent in content['children'].items():
                    if "documentation" not in subcontent:
                        continue
                    documentation = subcontent["documentation"]
                    if subcontent["type"] == "C":
                        if "constructors" not in _temp:
                            _temp['constructors'] = []
                        _temp["constructors"].append(parse_constructor(member_type, name, documentation, file_path))

                    if subcontent["type"] == "F":
                        if "fields" not in _temp:
                            _temp["fields"] = []
                        _temp["fields"].append(parse_field(member_type, name, documentation, file_path))

                    if subcontent["type"] == "P":
                        if "properties" not in _temp:
                            _temp["properties"] = []
                        _temp["properties"].append(parse_property(member_type, name, documentation, file_path))

                    if subcontent["type"] == "M":
                        if "methods" not in _temp:
                            _temp["methods"] = []
                        _temp["methods"].append(parse_method(member_type, name, documentation, file_path))

                    if subcontent["type"] == "E":
                        if "events" not in _temp:
                            _temp["events"] = []
                        _temp["events"].append(parse_event(member_type, name, documentation, file_path))

                if "constructors" in _temp:
                    file.write("## Constructors\n----\n")
                    file.write("\n".join(_temp["constructors"]))

                if "fields" in _temp:
                    file.write("## Fields\n----\n")
                    file.write("\n".join(_temp["fields"]))

                if "properties" in _temp:
                    file.write("## Properties\n----\n")
                    file.write("\n".join(_temp["properties"]))

                if "methods" in _temp:
                    file.write("## Methods\n----\n")
                    file.write("\n".join(_temp["methods"]))

                if "events" in _temp:
                    file.write("## Events\n----\n")
                    file.write("\n".join(_temp["events"]))
        index.append({namespace: index_files})

    with open(os.path.join(output_dir, "index.yml"), 'w') as yamlfile:
        yaml.dump(index, yamlfile, default_flow_style=False)
        log.info("Generated index file: %s", yamlfile.name)


@click.command()
@click.argument('dll_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('xml_path', type=click.Path(exists=True, dir_okay=False))
@click.option('-v', '--verbose', is_flag=True, help="Enables verbose output")
@click.option('-q', '--quiet', is_flag=True, help="Hides warnings")
@click.option('-o', '--output', type=click.Path(exists=False, file_okay=False), default="output/", help="Folder where files will be generated in")
def cli(dll_path, xml_path, verbose, quiet, output):
    global output_dir
    output_dir = output
    if verbose:
        log.setLevel(logging.DEBUG)
    if quiet:
        log.setLevel(logging.ERROR)
    hierarchy = parse_documentation(xml_path)
    build_documentation(dll_path, hierarchy)


if __name__ == '__main__':
    cli()