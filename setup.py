import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='aiana',
    lisense='GPL 3',
    version='0.9',
    author='Leonard Raumann',
    author_email='leo.raumann@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/IEK-5/aiana.git',
    packages=setuptools.find_packages()
)
