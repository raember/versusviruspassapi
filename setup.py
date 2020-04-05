import setuptools
import versusviruspassapi

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='VersusVirusPass',
    version=versusviruspassapi.__version__,
    author='raember',
    description='Backend API for hackathon challenge',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="viruspass versusvirus hackathon corona covid19",
    license="MIT",
    url='https://github.com/raember/versusviruspass',
    packages=setuptools.find_packages(),
)
