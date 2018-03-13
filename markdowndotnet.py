import clr
import xml.etree.ElementTree as ET

from System.Reflection import Assembly
from System.IO import FileInfo

path = FileInfo("ExampleSolution/ExampleProject/bin/Debug/ExampleProject.dll")
tree = ET.parse("ExampleSolution/ExampleProject/bin/Debug/ExampleProject.xml")
dll = Assembly.LoadFile(path.FullName)
print(dll)

types = dll.GetTypes()

with open("output.md", "w") as output:
    for type in types:
        output.write(f"# class {type.Name}\n")
        print(type.Name)
        methods = type.GetMethods()
        if len(methods) > 0:
            output.write("## Methods\n")
        for method in methods:
            output.write(f"### {method}\n")
            print("\t", method)
