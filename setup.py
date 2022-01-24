import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="Geo localisation use case",
    version="0.0.1",
    author="Badr Arrabatchou",
    author_email="arr.badr@gmail.com",
    description=(
        "An demonstration of how to create, document, and publish "
        "to the cheese shop a5 pypi.org."
    ),
    license="BSD",
    keywords="example documentation tutorial",
    url="http://packages.python.org/an_example_pypi_project",
    packages=["an_example_pypi_project", "tests"],
    long_description=read("README"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
