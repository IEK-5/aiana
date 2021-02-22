import setuptools
import os
import stat


with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='open-elevation',
    version='0.1',
    author='Evgenii Sovetkin',
    author_email='e.sovetkin@gmail.com',
    description='Extended open-elevation server',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='git@github.com:esovetkin/open-elevation',
    packages=setuptools.find_packages()
)
