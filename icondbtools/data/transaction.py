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

import base64
from typing import Optional, Dict

from iconservice.base.address import Address

from ..utils.convert_type import convert_hex_str_to_int, convert_hex_str_to_bytes


class Transaction(object):
    """Transaction class containing transaction information from
    """

    def __init__(self,
                 version: int,
                 nid: int,
                 from_: Optional['Address'],
                 to: Optional['Address'],
                 step_limit: int,
                 timestamp: int,
                 signature: bytes,
                 block_height: int,
                 block_hash: bytes,
                 tx_hash: bytes,
                 tx_index: int,
                 value: int = 0,
                 data_type: Optional[str] = None,
                 nonce: Optional[int] = None) -> None:
        """Transaction class for icon score context
        """
        self._version = version
        self._nid = nid
        self._tx_hash = tx_hash
        self._tx_index = tx_index
        self._from = from_
        self._to = to
        self._step_limit = step_limit
        self._value = value
        self._timestamp = timestamp
        self._signature = signature
        self._block_height = block_height
        self._block_hash = block_hash
        self._data_type = data_type
        self._nonce = nonce

    @property
    def version(self) -> int:
        return self._version

    @property
    def nid(self) -> int:
        return self._nid

    @property
    def from_(self) -> 'Address':
        """
        The account who created the transaction.
        """
        return self._from

    @property
    def to(self) -> 'Address':
        """
        The account of tx to.
        """
        return self._to

    @property
    def tx_index(self) -> int:
        """
        Transaction index in a block
        """
        return self._tx_index

    @property
    def tx_hash(self) -> bytes:
        """
        Transaction hash
        """
        return self._tx_hash

    @property
    def block_height(self) -> int:
        return self._block_height

    @property
    def block_hash(self) -> bytes:
        return self._block_hash

    @property
    def timestamp(self) -> int:
        """
        Timestamp of a transaction request in microseconds
        This is NOT a block timestamp
        """
        return self._timestamp

    @property
    def nonce(self) -> Optional[int]:
        """
        (optional)
        nonce of a transaction request.
        random value
        """
        return self._nonce

    @property
    def value(self) -> int:
        return self._value

    @property
    def data_type(self) -> Optional[str]:
        return self._data_type

    @property
    def signature(self) -> bytes:
        return self._signature

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Transaction':
        version = convert_hex_str_to_int(data["version"])
        nid = convert_hex_str_to_int(data["nid"])
        from_ = Address.from_string(data["from"])
        to = Address.from_string(data["to"])
        value = convert_hex_str_to_int(data.get("value", "0x0"))
        tx_index = convert_hex_str_to_int(data["txIndex"])
        tx_hash = convert_hex_str_to_bytes(data["txHash"])
        block_height = convert_hex_str_to_int(data["blockHeight"])
        block_hash = convert_hex_str_to_bytes(data["blockHash"])
        step_limit = convert_hex_str_to_int(data["stepLimit"])
        timestamp = convert_hex_str_to_int(data["timestamp"])
        signature: bytes = base64.b64decode(data["signature"])
        data_type = data.get("dataType")

        if "nonce" in data:
            nonce = convert_hex_str_to_int(data["nonce"])
        else:
            nonce = None

        return Transaction(
            version=version, nid=nid, nonce=nonce,
            from_=from_, to=to, value=value,
            tx_index=tx_index, tx_hash=tx_hash, signature=signature,
            block_height=block_height, block_hash=block_hash,
            step_limit=step_limit, timestamp=timestamp, data_type=data_type)
