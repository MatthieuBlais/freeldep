#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

PROJECT = "freeldep"
VERSION = "0.1"


try:
    long_description = open("README.md", "rt").read()
except IOError:
    long_description = ""

setup(
    name=PROJECT,
    version=VERSION,
    description="Serverless Infrastructure as code deployment",
    long_description=long_description,
    author="Matthieu Blais",
    author_email="matthieu.blais1@gmail.com",
    url="https://github.com/MatthieuBlais/freeldep",
    download_url="https://github.com/MatthieuBlais/freeldep.git",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Environment :: Console",
    ],
    platforms=["Any"],
    scripts=[],
    provides=[],
    install_requires=[
        "Click==7.1.2",
        "jinja2==2.11.2",
        "pyaml==20.4.0",
        "cfnlint==0.0.9",
        "pytest==6.1.2",
        "coverage==5.3",
        "moto==1.3.16",
    ],
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points="""
        [console_scripts]
        freeldep=cli.main:cli
    """,
    zip_safe=False,
)
