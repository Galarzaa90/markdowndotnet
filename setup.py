import sys

from setuptools import setup

if sys.version_info < (3, 4):
    sys.exit('Sorry, Python < 3.4 is not supported')

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.rst') as f:
    readme = f.read()

setup(
    name='markdowndotnet',
    version='0.1.0a2',
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
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: C#',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)