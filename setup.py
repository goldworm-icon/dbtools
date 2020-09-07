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

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "icondbtools", "__about__.py"), "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt") as requirements:
    requires = list(requirements)

extras_require = {"test": ["hypothesis", "coverage", "pytest",]}

tests_require = extras_require["test"]

setuptools.setup(
    name=about["name"],
    version=about["version"],
    author=about["author"],
    author_email=about["author_email"],
    description=about["description"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["url"],
    packages=setuptools.find_packages(exclude=["tests*"]),
    extras_require=extras_require,
    setup_requires=["pytest-runner"],
    tests_require=tests_require,
    test_suite="tests",
    install_requires=requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    entry_points={"console_scripts": ["icondbtools=icondbtools.__main__:main"]},
)
