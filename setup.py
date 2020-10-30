#!/usr/bin/env python
from setuptools import setup, find_packages


def license():
    with open('LICENSE') as f:
        return f.read()


def readme():
    with open('README.md') as f:
        return f.read()

test_deps = [
    "pytest==3.9.2",
    "pytest-mock==1.10.0",
    "pytest-html>=1.19.0,<2",
    "testfixtures==6.3.0",
    "coverage==4.5.1"
]
extras = {
    'test': test_deps,
}
# do not modify version number it will be injected by build script
setup(
    name="target-mako",
    version="0.1.0",
    description="Singer.io target for extracting data",
    long_description=readme(),
    ong_description_content_type="text/markdown",
    author="elebail",
    url="http://singer.io",
    license=license(),
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target_mako"],
    install_requires=[
        "singer-python==5.9.0",
        "jsonschema==2.6.0",
        "Mako==1.1.3",
    ],
    tests_require=test_deps,
    extras_require=extras,
    entry_points="""
    [console_scripts]
    target-mako=target_mako:main
    """,
    packages=find_packages(),
    package_data={
        "sample-config": ["sample_config.json"]
    },
    include_package_data=True,
    zip_safe=False
)
