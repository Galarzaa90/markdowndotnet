import json
import os
import re
import xml.etree.ElementTree as ET

import clr
from typing import Dict, List

import yaml
from System.Reflection import Assembly
from System.IO import FileInfo
from System import Type

dll_path = FileInfo("ExampleSolution/ExampleProject/bin/Debug/ExampleProject.dll")
tree = ET.parse("ExampleSolution/ExampleProject/bin/Debug/ExampleProject.xml")
root = tree.getroot()

types_documentation = {}
properties_documentation = {}
methods_documentation = {}

class_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<name>\w.+)")
field_property_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<class>\w.+)\.(?P<name>[\w#].+)")
method_pattern = re.compile(r"(?P<namespace>\w.+)\.(?P<class>\w.+)\.(?P<name>[\w#]+.\(.*\))")
parameters_pattern = re.compile(r"(\(.*\))")

hierarchy = {}


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


def get_type(type_str) -> Type:
    local_type = dll.GetType(type_str)
    if local_type is None:
        return Type.GetType(type_str)
    return local_type


def build_table(headers : List[str], rows : List[List[str]]) -> str:
    output = f"\n| {' | '.join(headers)} |\n"
    output += f"| {' | '.join(['---']*len(headers))} |\n"
    for row in rows:
        output += f"| {' | '.join(row)} |\n\n"
    return output


# Explore the XML file to get a structured hierarchy for the project
for member_item in root.find('members'):
    member_type, full_name = member_item.attrib['name'].split(":")
    documentation = {}
    for child in member_item:
        pattern = r"<(?:\w+:)?%(tag)s(?:[^>]*)>(.*)</(?:\w+:)?%(tag)s" % {"tag": child.tag}
        content = re.findall(pattern, ET.tostring(child).decode('utf-8'), re.DOTALL)[0].strip()
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

try:
    os.mkdir("output")
except FileExistsError:
    pass

# Generate a json file, for debugging purposes
with open('output/hierarchy.json', 'w') as outfile:
    json.dump(hierarchy, outfile, indent=4)

dll = Assembly.LoadFile(dll_path.FullName)

# Iterate through all namespaces
# Each namespace is a folder, each class is a file
# Also builds a YAML index
index = []
for namespace, members in hierarchy.items():
    index_files = []
    for member, content in members.items():
        with open(f"output/{namespace}.{member}.md", "w") as file:
            index_files.append({member: f"{namespace}.{member}.md"})
            _type = dll.GetType(f"{namespace}.{member}")
            file.write(f"# Class {member}\n")
            file.write(f"{content.get('summary','')}")
            _temp = {}
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
                        declaration = f"\n**Declaration**\n" \
                                      f"```csharp\n" \
                                      f"public {field_type} {name}\n" \
                                      f"```\n"
                        _content += declaration
                        _content += "**Field Value**\n"
                        table = build_table(["Type", "Description"], [[str(field_type), documentation.get("value", "")]])
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
                        getter = "" if prop.GetMethod is None else "get; "
                        setter = "" if prop.SetMethod is None else "set; "
                        declaration = f"\n**Declaration**\n" \
                                      f"```csharp\n" \
                                      f"public {property_type} {name} {{{getter}{setter}}}\n" \
                                      f"```\n"
                        _content += declaration
                        _content += "**Property Value**\n"
                        table = build_table(["Type", "Description"], [[str(property_type), documentation.get("value","")]])
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
                        param_types = [get_type(x) for x in params]
                        method = _type.GetMethod(method_name, param_types)
                    paramsInfo = method.GetParameters()
                    paramString = " ,".join([f"{x.ParameterType} {x.Name}" for x in paramsInfo])
                    complete_name = f"{method_name}({paramString})"
                    if "methods" not in _temp:
                        _temp["methods"] = []
                    _content = f'### {name}\n'
                    if "summary" in documentation:
                        _content += f"{documentation['summary']}\n"
                    if method is not None:
                        _content += f"\n```csharp\n" \
                                    f"public {method.ReturnType} {complete_name}\n" \
                                    f"```\n"
                    if len(paramsInfo) > 0 and "param" in documentation:
                        _content += "**Parameters**\n"
                        headers = ["Type", "Name", "Description"]
                        rows = []
                        for param in paramsInfo:
                            description = documentation["param"][param.Name]
                            rows.append([str(param.ParameterType), param.Name, description])
                        _content += build_table(headers, rows)
                    if method is not None:
                        _content += "Returns\n"
                        table = build_table(["Type", "Description"], [[str(method.ReturnType), documentation.get("returns","")]])
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

with open('output/index.yml', 'w') as yamlfile:
    yaml.dump(index, yamlfile, default_flow_style=False)


