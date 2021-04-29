#!/usr/bin/env python
from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


test_deps = [
    "pytest==6.2.2",
    "pytest-cov==2.11.1",
    "pytest-mock==1.10.0",
    "testfixtures==6.3.0",
    "coverage==5.5"
]
extras = {
    'test': test_deps,
}
# do not modify version number it will be injected by build script
setup(
    name="target-mako",
    version="1.2.1",
    description="Singer.io target for extracting data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="elebail",
    url="https://github.com/ericlebail/target-mako",
    classifiers=["Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent"],
    py_modules=["target_mako"],
    install_requires=[
        "singer-python==5.12.1",
        "jsonschema==2.6.0",
        "Mako==1.1.4",
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
