
markdowndotnet
==============

Python command line tool to generate markdown documents from C# Library files and their XML documentation.


.. image:: https://img.shields.io/badge/python-3.6-yellow.svg
   :target: https://img.shields.io/badge/python-3.6-yellow.svg
   :alt: Python version
 
.. image:: https://travis-ci.org/Galarzaa90/markdowndotnet.svg?branch=master
   :target: https://travis-ci.org/Galarzaa90/markdowndotnet
   :alt: Build Status
  
.. image:: https://img.shields.io/pypi/v/markdowndotnet.svg
   :target: https://pypi.python.org/pypi/markdowndotnet/
   :alt: PyPI


Requirements
------------


* Python 3.6 or higher
* `pythonnet <https://github.com/pythonnet/pythonnet>`_
* `PyYAML <https://github.com/yaml/pyyaml>`_
* `click <https://github.com/pallets/click>`_

The generated files markdown files are meant to be used with `mkdocs <https://github.com/mkdocs/mkdocs>`_ 
(with the `material theme <https://github.com/squidfunk/mkdocs-material>`_\ ), but may be compatible with other site generators.

How to use
----------

The script requires setting the ``DocumentationFile`` setting in the project's configuration, e.g.

.. code-block:: xml

   <DocumentationFile>bin\Debug\ExampleProject.xml</DocumentationFile>

Once this has been set, an XML file will be built along with the library's dll file.

Now, when running the script, the path to the dll and the xml file must be specified:

.. code-block:: shell

   python markdowndotnet.py ExampleProject.dll ExampleProject.xml

By default, the files will be generated in a folder named ``output/`` in the working directory.

This contains markdown files generated for each object found in the assembly, ordered in directories by namespace. Aditionally, a file named ``index.yml`` is created, which can be appened to a ``mkdocs.yml`` file to use with `mkdocs <https://github.com/mkdocs/mkdocs>`_.

Features
--------


* Generates markdown documents from a compiled binary (dll) and it's documentation file.
* Displays all public fields, properties and methods, along with their parameters and return types.
* Generate internal links between members
* External links to system classes
* Partial support for summary, params and returns tags.

Planned features
----------------


* Support for all XML tags
