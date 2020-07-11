# -*- coding: utf-8 -*-
# Copyright 2018 ICON Foundation Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = os.environ.get("VERSION")
if version is None:
    with open(os.path.join(".", "VERSION")) as version_file:
        version = version_file.read().strip()

with open("requirements.txt") as requirements:
    requires = list(requirements)

setuptools.setup(
    name="icondbtools",
    version=version,
    author="ICON Foundation",
    author_email="goldworm@icon.foundation",
    description="icondbtools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goldworm-icon/dbtools",
    packages=setuptools.find_packages(exclude=["tests*"]),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    test_suite="tests",
    install_requires=requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    entry_points={"console_scripts": ["icondbtools=icondbtools.__main__:main"]},
)
