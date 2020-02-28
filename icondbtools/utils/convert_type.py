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

from typing import Optional
from iconservice.base.address import Address


def str_to_int(value: str) -> int:
    if isinstance(value, int):
        return value

    base = 16 if is_hex(value) else 10
    return int(value, base)


def object_to_str(value) -> str:
    if isinstance(value, Address):
        return str(value)
    elif isinstance(value, int):
        return hex(value)
    elif isinstance(value, bytes):
        return bytes_to_hex(value)
    elif isinstance(value, bool):
        return "0x1" if value else "0x0"

    return value


def str_to_object(object_type: str, value: str) -> object:
    if object_type == "Address":
        return Address.from_string(value)
    if object_type == "int":
        return str_to_int(value)
    if object_type == "bytes":
        return convert_hex_str_to_bytes(value)
    if object_type == "bool":
        return bool(str_to_int(value))
    if object_type == "str":
        return value

    raise TypeError(f"Unknown type: {object_type}")


def bytes_to_hex(value: bytes, prefix: str = "0x") -> str:
    return f'{prefix}{value.hex()}'


def hex_to_bytes(value: Optional[str]) -> Optional[bytes]:
    if value is None:
        return None

    return bytes.fromhex(remove_0x_prefix(value))


def remove_0x_prefix(value: str) -> str:
    if is_hex(value):
        return value[2:]
    return value


def is_hex(value: str) -> bool:
    return value.startswith('0x') or value.startswith('-0x')


def convert_hex_str_to_bytes(value: str):
    """Converts hex string prefixed with '0x' into bytes."""
    return bytes.fromhex(remove_0x_prefix(value))


def is_str(value):
    str_types = (str,)
    return isinstance(value, str_types)
