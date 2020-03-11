# -*- coding: utf-8 -*-
# Copyright 2020 ICON Foundation
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
import time
from typing import Callable

import pytest

from iconservice.base.address import Address, AddressPrefix


@pytest.fixture(scope="function")
def tx_hash() -> bytes:
    """Returns 32 length random tx_hash in bytes

    :return: tx_hash in bytes
    """
    print("tx_hash()")
    return os.urandom(32)


@pytest.fixture(scope="function")
def block_hash() -> bytes:
    """Returns 32 length random block_hash in bytes

    :return: block_hash in bytes
    """
    print("block_hash()")
    return os.urandom(32)


@pytest.fixture
def address() -> 'Address':
    return Address(AddressPrefix.EOA, os.urandom(20))


@pytest.fixture(scope="session")
def create_address() -> Callable[[], 'Address']:
    def func():
        return Address(AddressPrefix.EOA, os.urandom(20))

    return func


@pytest.fixture
def step_price() -> int:
    return 10 ** 10


@pytest.fixture
def timestamp() -> int:
    return int(time.time() * 1_000_000)
