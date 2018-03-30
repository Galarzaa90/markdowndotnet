import json
import logging
import os
import re
from xml.etree import ElementTree
from typing import Dict, List

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


def get_type(type_str, assembly) -> Type:
    local_type = assembly.GetType(type_str)
    if local_type is None:
        return Type.GetType(type_str)
    return local_type


def get_link(local_assembly, *, type_name: str=None, cs_type=None, current_file=None):
    if not type_name and not cs_type:
        raise ValueError("Both type_name and cs_type can't be None")
    if type_name is not None:
        cs_type = get_type(type_name, local_assembly)
    if cs_type is None:
        log.warning(f"Couldn't find type: {type_name}")
        return type_name
    # Type belongs to the assembly, so link will be relative
    if cs_type.Assembly.FullName == local_assembly.FullName:
        current_path = os.path.dirname(current_file) + "/"
        target_file = os.path.join(output_dir, str(cs_type).replace('.', '/') + ".md")
        relative_path = os.path.relpath(target_file, current_path)
        return f"[{cs_type.Name}]({relative_path})"
    else:
        r = requests.get('https://xref.docs.microsoft.com/query', params={"uid": cs_type.FullName})
        data = json.loads(r.text)
        if len(data) < 0:
            log.warning(f"Couldn't find documentation reference for {cs_type.FullName}.")
            return cs_type.FullName
        return f"[{data[0]['name']}]({data[0]['href']})"


def build_table(headers : List[str], rows : List[List[str]]) -> str:
    output = f"\n| {' | '.join(headers)} |\n"
    output += f"| {' | '.join(['---']*len(headers))} |\n"
    for row in rows:
        output += f"| {' | '.join(row)} |\n"
    return output+'\n'


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
            filepath = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as file:
                log.debug(f"Building {file.name}")
                index_files.append({member: filename})
                _type = assembly.GetType(f"{namespace}.{member}")
                object_type = "Class"
                if _type.IsEnum:
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
                        _content = f'### {name}\n'
                        field = _type.GetField(name)
                        if "summary" in documentation:
                            _content += f"{documentation['summary']}\n"
                        if field is not None:
                            field_type = field.FieldType
                            type_link = get_link(assembly, cs_type=field_type, current_file=filepath)
                            declaration = f"\n**Declaration**\n" \
                                          f"```csharp\n" \
                                          f"public {field_type.Name} {name}\n" \
                                          f"```\n"
                            _content += declaration
                            _content += "**Field Value**\n"
                            table = build_table(["Type", "Description"], [[type_link, documentation.get("value", "")]])
                            _content += table
                        _temp["fields"].append(_content)

                    if subcontent["type"] == "P":
                        if "properties" not in _temp:
                            _temp["properties"] = []
                        _content = f"### {name}\n"
                        prop = _type.GetProperty(name)
                        if "summary" in documentation:
                            _content += f"{documentation['summary']}\n"
                        if prop is not None:
                            property_type = prop.PropertyType
                            type_link = get_link(assembly, cs_type=property_type, current_file=filepath)
                            getter = "" if prop.GetMethod is None else "get; "
                            setter = "" if prop.SetMethod is None else "set; "
                            declaration = f"\n**Declaration**\n" \
                                          f"```csharp\n" \
                                          f"public {property_type.Name} {name} {{{getter}{setter}}}\n" \
                                          f"```\n"
                            _content += declaration
                            _content += "**Property Value**\n"
                            table = build_table(["Type", "Description"], [[type_link, documentation.get("value","")]])
                            _content += table

                        _temp["properties"].append(_content)

                    if subcontent["type"] == "M":
                        params = get_params(name)
                        method_name = name.split("(")[0]
                        method = None
                        if len(params) == 0:
                            method = _type.GetMethod(method_name)
                            name += "()"
                        else:
                            param_types = [get_type(x, assembly) for x in params]
                            method = _type.GetMethod(method_name, param_types)
                        parameters = method.GetParameters()
                        param_string = " ,".join([f"{x.ParameterType} {x.Name}" for x in parameters])
                        complete_name = f"{method_name}({param_string})"
                        if "methods" not in _temp:
                            _temp["methods"] = []
                        _content = f'### {name}\n'
                        if "summary" in documentation:
                            _content += f"{documentation['summary']}\n"
                        if method is not None:
                            _content += f"\n```csharp\n" \
                                        f"public {method.ReturnType.Name} {complete_name}\n" \
                                        f"```\n"
                        if len(parameters) > 0 and "param" in documentation:
                            _content += "**Parameters**\n"
                            headers = ["Type", "Name", "Description"]
                            rows = []
                            for param in parameters:
                                description = documentation["param"][param.Name]
                                param_link = get_link(assembly, cs_type=param.ParameterType, current_file=filepath)
                                rows.append([param_link, param.Name, description])
                            _content += build_table(headers, rows)
                        if method is not None:
                            _content += "Returns\n"
                            type_link = get_link(assembly, cs_type=method.ReturnType, current_file=filepath)
                            table = build_table(["Type", "Description"], [[type_link, documentation.get("returns", "")]])
                            _content += table

                        _temp["methods"].append(_content)

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