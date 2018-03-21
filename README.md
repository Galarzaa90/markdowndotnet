*This project is currently in early development and is still not usable*
# markdowndotnet
Python command line tool to generate markdown documents from C# Library files and their XML documentation.

## Requirements
* Python 3.6 or higher
* [pythonnet](https://github.com/pythonnet/pythonnet)
* [PyYAML](https://github.com/yaml/pyyaml)
* [click](https://github.com/pallets/click)


The generated files markdown files are meant to be used with [mkdocs](https://github.com/mkdocs/mkdocs) 
(with the [material theme](https://github.com/squidfunk/mkdocs-material)), but may be compatible with other site generators.

## Features
* Generates markdown documents from a compiled binary (dll) and it's documentation file.
* Displays all public fields, properties and methods, along with their parameters and return types.

## Planned features
* Generate internal links between members
* External links to system classes