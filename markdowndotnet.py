import clr
import re
import xml.etree.ElementTree as ET

from System.Reflection import Assembly
from System.IO import FileInfo

path = FileInfo("ExampleSolution/ExampleProject/bin/Debug/ExampleProject.dll")
tree = ET.parse("ExampleSolution/ExampleProject/bin/Debug/ExampleProject.xml")
root = tree.getroot()

types_documentation = {}
properties_documentation = {}
methods_documentation = {}

for member_item in root.find('members'):
    member_type, member_name = member_item.attrib['name'].split(":")
    member = {}
    for child in member_item:
        pattern = r"<(?:\w+:)?%(tag)s(?:[^>]*)>(.*)</(?:\w+:)?%(tag)s" % {"tag": child.tag}
        member[child.tag] = re.findall(pattern, ET.tostring(child).decode('utf-8'), re.DOTALL)[0].strip()
    if member_type == "T":
        types_documentation[member_name] = member
    if member_type == "P":
        properties_documentation[member_name] = member
    if member_type == "M":
        methods_documentation[member_name] = member


dll = Assembly.LoadFile(path.FullName)
types = dll.GetTypes()

with open("output.md", "w") as output:
    for type in types:
        output.write(f"# class {type.Name}\n")
        output.write(f"{types_documentation.get(type.FullName,{}).get('summary','')}\n")
        print(type.Name)
        methods = type.GetMethods()
        if len(methods) > 0:
            output.write("## Methods\n")
        for method in methods:
            output.write(f"### {method}\n")
            output.write(f"{methods_documentation.get(type.FullName+'.'+method.Name,{}).get('summary','')}\n")
            print("\t", method)
