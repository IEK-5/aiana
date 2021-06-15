import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='agri-pv',
    version='0.1',
    author='Leonard Raumann',
    author_email='leo.raumann@gmail.com',
    description='agri pv',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='git@jugit.fz-juelich.de:pearl-project/agri-pv.git',
    packages=setuptools.find_packages()
)
