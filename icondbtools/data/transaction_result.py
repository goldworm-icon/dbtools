# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
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

from iconservice.base.address import Address
from ..utils.convert_type import convert_hex_str_to_int, convert_hex_str_to_bytes


class TransactionResult(object):
    def __init__(self, tx_hash: bytes, status: int, to: 'Address', block_height: int, block_hash: bytes):
        self._tx_hash: bytes = tx_hash
        self._status = status
        self._to: 'Address' = to
        self._block_height: int = block_height
        self._block_hash: bytes = block_hash

    @property
    def tx_hash(self) -> bytes:
        return self._tx_hash

    @property
    def status(self) -> int:
        return self._status

    @property
    def to(self) -> 'Address':
        return self._to

    @property
    def block_height(self) -> int:
        return self._block_height

    @property
    def block_hash(self) -> bytes:
        return self._block_hash

    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionResult':
        tx_hash: bytes = convert_hex_str_to_bytes(data["txHash"])
        status: int = convert_hex_str_to_int(data["status"])
        to: 'Address' = Address.from_string(data["to"])
        block_height: int = convert_hex_str_to_int(data["blockHeight"])
        block_hash: bytes = convert_hex_str_to_bytes(data["blockHash"])

        return TransactionResult(
            tx_hash=tx_hash, status=status, to=to,
            block_height=block_height, block_hash=block_hash)
