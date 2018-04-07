import sys

from setuptools import setup

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

setup(
    name='markdowndotnet',
    version='0.1.0a1',
    author='Galarzaa90',
    author_email="allan.galarza@gmail.com",
    description='A Python markdown generator for C# libraries documentation.',
    long_description=readme,
    url='https://github.com/Galarzaa90/markdowndotnet',
    py_modules=['markdowndotnet'],
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        markdowndotnet=markdowndotnet:cli
    ''',
    include_package_data=True,
)