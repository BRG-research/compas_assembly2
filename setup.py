#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8: noqa
import io
import os

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools

from setuptools.command.develop import develop
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))


def read(*names, **kwargs):
    return io.open(
        os.path.join(here, *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


long_description = read("README.md")
requirements = read("requirements.txt").split("\n")
optional_requirements = {}


setup(
    name="compas_assembly2",
    version="0.1.0",
    description="tree and graph assembly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BRG-research/compas_assembly2",
    author="petras vestartas",
    author_email="petrasvestartas@gmail.com",
    license="GPL-3 License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords=[],
    project_urls={},
    packages=["compas_assembly2"],
    package_dir={"": "src"},
    # package_data={},
    # data_files=[],
    # include_package_data=True,
    ext_modules=[],
    setup_requires=["pybind11>=2.5.0"],
    install_requires=requirements,
    python_requires=">=3.6",
    extras_require=optional_requirements,
    zip_safe=False,
)
