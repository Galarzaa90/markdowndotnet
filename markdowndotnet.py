import json
import os
import re
import xml.etree.ElementTree as ET

import clr
import yaml
from System.Reflection import Assembly
from System.IO import FileInfo

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

# Explore the XML file to get a structured hierarchy for the project
for member_item in root.find('members'):
    member_type, full_name = member_item.attrib['name'].split(":")
    documentation = {}
    for child in member_item:
        pattern = r"<(?:\w+:)?%(tag)s(?:[^>]*)>(.*)</(?:\w+:)?%(tag)s" % {"tag": child.tag}
        documentation[child.tag] = re.findall(pattern, ET.tostring(child).decode('utf-8'), re.DOTALL)[0].strip()
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
            file.write(f"# class {member}\n")
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
                    if "summary" in documentation:
                        _content += f"{documentation['summary']}\n"
                    _temp["fields"].append(_content)

                if subcontent["type"] == "P":
                    if "properties" not in _temp:
                        _temp["properties"] = []
                    _content = f"### {name}\n"
                    if "summary" in documentation:
                        _content += f"{documentation['summary']}\n"
                    _temp["properties"].append(_content)

                if subcontent["type"] == "M":
                    if "methods" not in _temp:
                        _temp["methods"] = []
                    _content = f'### {name}\n'
                    if "summary" in documentation:
                        _content += f"{documentation['summary']}\n"
                    _temp["methods"].append(_content)
            if "constructors" in _temp:
                file.write("## Constructors\n")
                file.write("\n".join(_temp["constructors"]))

            if "fields" in _temp:
                file.write("## Fields\n")
                file.write("\n".join(_temp["fields"]))

            if "properties" in _temp:
                file.write("## Properties\n")
                file.write("\n".join(_temp["properties"]))

            if "methods" in _temp:
                file.write("## Methods\n")
                file.write("\n".join(_temp["methods"]))
    index.append({namespace: index_files})
print(index)
with open('output/index.yml', 'w') as yamlfile:
    yaml.dump(index, yamlfile, default_flow_style=False)


