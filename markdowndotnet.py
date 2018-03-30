import json
import logging
import os
import re
from xml.etree import ElementTree
from typing import Dict, List, Any

import click
# noinspection PyUnresolvedReferences,PyPackageRequirements
import clr
import requests
import yaml

from System.Reflection import Assembly
from System.IO import FileInfo
from System import Type

class_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<name>\w.+)")
field_property_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<class>\w.+)\.(?P<name>[\w#].+)")
method_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<class>\w.+)\.(?P<name>[\w#]+.\(.*\))")
parameters_pattern = re.compile(r"(\(.*\))")

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter('%(levelname)-7s: %(message)s'))
log.addHandler(consoleHandler)

output_dir = ""


def get_params(func) -> List[str]:
    """
    Gets a list of parameter types (as strings)
    :param func: The method's full name, with parenthesis
    :return: List containing the type of each parameter in order.
    """
    m = parameters_pattern.search(func)
    if not m:
        # If there are no parenthesis in name, method has no parameters
        return []
    else:
        return m.group(1).replace("(", "").replace(")", "").split(",")


def get_type(local_assembly: Assembly, type_name: str) -> Type:
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


def get_link(local_assembly: Assembly, *, type_name: str=None, cs_type: Type=None, current_file: str=None) -> str:
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
        log.warning(f"Couldn't find type: {type_name}")
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
        return f"[{cs_type.Name}]({relative_path}){suffix}"
    else:
        r = requests.get('https://xref.docs.microsoft.com/query', params={"uid": cs_type.FullName})
        data = json.loads(r.text)
        if len(data) < 0:
            log.warning(f"Couldn't find documentation reference for {cs_type.FullName}.")
            return cs_type.FullName
        return f"[{data[0]['name']}]({data[0]['href']}){suffix}"


def build_table(headers: List[str], rows : List[List[str]]) -> str:
    """Builds a markdown syntax table

    :param List[str] headers: The table's header
    :param List[List[str]] rows: A list of rows to put in the table, where each row is a list of columns.
    :return: The table in markdown syntax
    :rtype: str
    """
    output = f"\n| {' | '.join(headers)} |\n"
    output += f"| {' | '.join(['---']*len(headers))} |\n"
    for row in rows:
        output += f"| {' | '.join(row)} |\n"
    return output+'\n'


def parse_field(member_type: Type, name: str, documentation: Dict[str, Any], file_path: str):
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
        log.warning(f"Field '{name}' not found in assembly.")
        return ""

    field_type = field.FieldType
    type_link = get_link(assembly, cs_type=field_type, current_file=file_path)
    # Show a level 3 header with the field's name
    content = f'### {name}\n'
    # Show the field's summary if available
    if "summary" in documentation:
        content += f"{documentation['summary']}  \n"
    # Show the field's declaration
    declaration = f"**Declaration**\n" \
                  f"```csharp\n" \
                  f"public {field_type.Name} {name};\n" \
                  f"```\n"
    content += declaration
    # Show a table containing the field's type and value
    content += "**Field Value**\n"
    table = build_table(["Type", "Description"], [[type_link, documentation.get("value", "")]])
    content += table
    return content


def parse_property(member_type: Type, name: str, documentation: Dict[str, Any], file_path: str):
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
        log.warning(f"Property '{name}' not found in assembly.")
        return ""

    property_type = cs_property.PropertyType
    type_link = get_link(assembly, cs_type=property_type, current_file=file_path)
    getter = "" if cs_property.GetMethod is None else "get; "
    setter = "" if cs_property.SetMethod is None else "set; "
    # Show a level 3 header with the property's name
    content = f"### {name}\n"
    # Show the field's summary if available
    if "summary" in documentation:
        content += f"{documentation['summary']}  \n"
    # Show the property's declaration
    declaration = f"**Declaration**\n" \
                  f"```csharp\n" \
                  f"public {property_type.Name} {name} {{{getter}{setter}}}\n" \
                  f"```\n"
    content += declaration
    # Show a table containing the property's type and value
    content += "**Property Value**\n"
    table = build_table(["Type", "Description"], [[type_link, documentation.get("value", "")]])
    content += table
    return content


def parse_method(member_type: Type, name: str, documentation: Dict[str, Any], file_path: str):
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
        log.warning(f"Method '{name}' not found in assembly.")
        return ""

    return_type = method.ReturnType
    parameters = method.GetParameters()
    # Get a string list containing the parameter's type and name.
    params_declaration = " ,".join([f"{x.ParameterType.Name} {x.Name}" for x in parameters])
    # Show a level 3 header with the method's name
    content = f'### {name}\n'
    # Show the method's summary if available
    if "summary" in documentation:
        content += f"{documentation['summary']}  \n"
    # Show the method's declaration
    content += f"**Declaration**\n" \
               f"```csharp\n" \
               f"public {return_type.Name} {method_name}({params_declaration})\n" \
               f"```\n"
    # If method has parameters, show a table with their type, name and description
    if len(parameters) > 0 and "param" in documentation:
        content += "**Parameters**\n"
        param_documentation = documentation.get('param', {})
        headers = ["Type", "Name", "Description"]
        rows = []
        for param in parameters:
            description = param_documentation.get(param.Name, "")
            param_link = get_link(assembly, cs_type=param.ParameterType, current_file=file_path)
            rows.append([param_link, param.Name, description])
        content += build_table(headers, rows)
    # Show table with the returned value, type and description, unless the type is Void.
    if return_type.Name != "Void":
        content += "**Returns**\n"
        type_link = get_link(assembly, cs_type=method.ReturnType, current_file=file_path)
        table = build_table(["Type", "Description"], [[type_link, documentation.get("returns", "")]])
        content += table
    return content


def parse_documentation(path):
    log.info("Parsing documentation")
    tree = ElementTree.parse(path)
    hierarchy = {}
    root = tree.getroot()
    # Explore the XML file to get a structured hierarchy for the project
    for member_item in root.find('members'):
        member_type, full_name = member_item.attrib['name'].split(":")
        documentation = {}
        for child in member_item:
            pattern = r"<(?:\w+:)?%(tag)s(?:[^>]*)>(.*)</(?:\w+:)?%(tag)s" % {"tag": child.tag}
            content = re.findall(pattern, ElementTree.tostring(child).decode('utf-8'), re.DOTALL)[0].strip()
            if child.tag == "param":
                if child.tag not in documentation:
                    documentation[child.tag] = {}
                documentation[child.tag][child.get("name")] = content
            else:
                documentation[child.tag] = content
        if member_type == "T":
            m = class_pattern.search(full_name)
            if m:
                namespace = m.group("namespace")
                name = m.group("name")
                in_class = None
                log.debug(f"Type found: {name}")
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
            log.debug(f"Member found: {name}")
            if "#ctor" in name:
                name = name.replace("#ctor", '.ctor')
                member_type = 'C'

        if namespace not in hierarchy:
            hierarchy[namespace] = {}
        if member_type == "T":
            if name not in hierarchy[namespace]:
                hierarchy[namespace][name] = {"children": {}, "documentation": documentation, 'type': member_type}
        else:
            hierarchy[namespace][in_class]["children"][name] = {"documentation": documentation, 'type': member_type}

    os.makedirs(output_dir, exist_ok=True)

    # Generate a json file, for debugging purposes
    with open(os.path.join(output_dir, "hierarchy.json"), 'w') as outfile:
        json.dump(hierarchy, outfile, indent=4)
        log.debug(f"Generated hierarchy file on: {outfile.name}")

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
            filename = f"{(namespace+'/'+member).replace('.','/')}.md"
            file_path = os.path.join(output_dir, filename)
            # Ensure intermediary directories exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                log.debug(f"Building {file.name}")
                index_files.append({member: filename})
                member_type = assembly.GetType(f"{namespace}.{member}")
                object_type = "Class"
                if member_type.IsEnum:
                    object_type = "Enum"
                file.write(f"# {object_type} {member}\n")
                file.write(f"{content.get('documentation',{}).get('summary')}\n")
                _temp = {}
                # Enums are represented differently
                if object_type == "Enum":
                    rows = []
                    for field, subcontent in content["children"].items():
                        documentation = subcontent["documentation"]
                        rows.append([field, documentation.get("summary", "")])
                    enum_table = build_table(["Field", "Description"], rows)
                    file.write(enum_table)
                    continue
                for name, subcontent in content['children'].items():
                    if "documentation" not in subcontent:
                        continue
                    documentation = subcontent["documentation"]
                    if subcontent["type"] == "C":
                        if "constructors" not in _temp:
                            _temp['constructors'] = []
                        _content = f"### {member}()\n"
                        if "summary" in documentation:
                            _content += f"{documentation['summary']}\n"
                        _temp["constructors"].append(_content)

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
        index.append({namespace: index_files})

    with open(os.path.join(output_dir, "index.yml"), 'w') as yamlfile:
        yaml.dump(index, yamlfile, default_flow_style=False)
        log.info(f"Generated index file: {yamlfile.name}")


@click.command()
@click.argument('dll_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('xml_path', type=click.Path(exists=True, dir_okay=False))
@click.option('-v', '--verbose', is_flag=True, help="Enables verbose output")
@click.option('-q', '--quiet', is_flag=True, help="Hides warnings")
@click.option('-o', '--output', type=click.Path(exists=False, file_okay=False), default="output/", help="Folder where files will be generated in")
def run(dll_path, xml_path, verbose, quiet, output):
    global output_dir
    output_dir = output
    if verbose:
        log.setLevel(logging.DEBUG)
    if quiet:
        log.setLevel(logging.ERROR)
    hierarchy = parse_documentation(xml_path)
    build_documentation(dll_path, hierarchy)


if __name__ == '__main__':
    run()