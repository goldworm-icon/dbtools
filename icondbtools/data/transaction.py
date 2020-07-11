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
import json
from typing import Optional, Dict, Union

from iconservice.base.address import Address
from ..utils.convert_type import str_to_int, bytes_to_hex, hex_to_bytes


class Transaction(object):
    """Transaction information loaded from loopchain DB
    """

    class CallData(object):
        def __init__(self, method: str, params: Union[None, Dict[str, str]]):
            self._method = method
            self._params = {} if params is None else params

        @property
        def method(self) -> str:
            return self._method

        @property
        def params(self) -> Dict[str, str]:
            return self._params

    def __init__(
        self,
        from_: Optional["Address"],
        to: Optional["Address"],
        version: int = 3,
        nid: int = 1,
        step_limit: int = 0,
        timestamp: int = 0,
        signature: bytes = None,
        tx_hash: bytes = None,
        value: int = 0,
        data_type: Optional[str] = None,
        data: Union[None, "CallData"] = None,
        nonce: Optional[int] = None,
    ) -> None:
        """Transaction class for icon score context
        """
        self._version = version
        self._nid = nid
        self._tx_hash = tx_hash
        self._from = from_
        self._to = to
        self._step_limit = step_limit
        self._value = value
        self._timestamp = timestamp
        self._signature = signature
        self._nonce = nonce
        self._data_type = data_type
        self._data = data

    def __str__(self) -> str:
        items = (
            ("tx_hash", self._tx_hash),
            ("from", self._from),
            ("to", self._to),
            ("value", self._value),
            ("step_limit", self._step_limit),
            ("timestamp", self._timestamp),
            ("signature", self._signature),
            ("nonce", self._nonce),
            ("version", self._version),
            ("nid", self._nid),
        )

        def _func():
            for key, value in items:
                if isinstance(value, bytes):
                    value = bytes_to_hex(value)

                yield f"{key}={value}"

        return " ".join(_func())

    @property
    def version(self) -> int:
        return self._version

    @property
    def nid(self) -> int:
        return self._nid

    @property
    def from_(self) -> "Address":
        """
        The account who created the transaction.
        """
        return self._from

    @property
    def to(self) -> "Address":
        """
        The account of tx to.
        """
        return self._to

    @property
    def tx_hash(self) -> bytes:
        """
        Transaction hash
        """
        return self._tx_hash

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
    def step_limit(self) -> int:
        return self._step_limit

    @property
    def value(self) -> int:
        return self._value

    @property
    def data_type(self) -> Optional[str]:
        return self._data_type

    @property
    def data(self) -> Union[None, "CallData"]:
        return self._data

    @property
    def signature(self) -> bytes:
        return self._signature

    @classmethod
    def from_bytes(cls, data: bytes) -> "Transaction":
        """

        :param data: data loaded from loopchain DB
        :return:
        """
        data_in_dict = json.loads(data)
        data_in_dict["transaction"]["txHash"] = data_in_dict["result"]["txHash"]

        return cls.from_dict(data_in_dict["transaction"])

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Transaction":
        version = str_to_int(data.get("version", "0x2"))
        nid = str_to_int(data.get("nid", "0x1"))
        from_ = Address.from_string(data["from"])
        to = Address.from_string(data["to"])
        value = str_to_int(data.get("value", "0x0"))
        tx_hash = cls._get_tx_hash(data)
        timestamp = str_to_int(data["timestamp"])
        signature: bytes = base64.b64decode(data["signature"])
        data_type = data.get("dataType")
        step_limit = str_to_int(data["stepLimit"]) if "stepLimit" in data else 0

        if "nonce" in data:
            nonce = str_to_int(data["nonce"])
        else:
            nonce = None

        tx_data = cls._get_data(data_type, data.get("data"))

        return Transaction(
            version=version,
            nid=nid,
            from_=from_,
            to=to,
            value=value,
            tx_hash=tx_hash,
            signature=signature,
            step_limit=step_limit,
            timestamp=timestamp,
            data_type=data_type,
            data=tx_data,
            nonce=nonce,
        )

    @classmethod
    def _get_tx_hash(cls, data: Dict[str, str]) -> bytes:
        for key in ("txHash", "tx_hash"):
            value: str = data.get(key)
            if value:
                break

        return hex_to_bytes(value)

    @classmethod
    def _get_data(
        cls, data_type: Optional[str], data: Union[None, str, Dict]
    ) -> Union[None, "CallData"]:
        if data_type == "call":
            return Transaction.CallData(
                method=data["method"], params=data.get("params")
            )
