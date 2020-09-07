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

import pkg_resources

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(DIR_PATH, "..", ".."))


def get_dbtools_version() -> str:
    """Get version of preptools.
    The location of the file that holds the version information is different when packaging and when executing.
    :return: version of tbears.
    """
    try:
        version = pkg_resources.get_distribution("icondbtools").version
    except pkg_resources.DistributionNotFound:
        version_path = os.path.join(PROJECT_ROOT_PATH, "VERSION")
        with open(version_path, mode="r") as version_file:
            version = version_file.read()
    except:
        version = "unknown"
    return version


def estimate_remaining_time_s(
        total_blocks: int, blocks_done: int, elapsed_time_s: float) -> float:
    blocks_to_do = total_blocks - blocks_done
    return blocks_to_do * elapsed_time_s / blocks_done
