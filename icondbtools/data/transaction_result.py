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

import json
from enum import IntEnum, auto
from typing import List, Dict, Union, Any

from iconservice.base.address import Address
from ..data.event_log import EventLog
from ..utils import pack
from ..utils.convert_type import hex_to_bytes, bytes_to_hex, str_to_int


class TransactionResult(pack.Serializable):
    class Index(IntEnum):
        TX_HASH = 0
        STATUS = auto()
        TX_INDEX = auto()
        TO = auto()
        SCORE_ADDRESS = auto()
        BLOCK_HEIGHT = auto()
        BLOCK_HASH = auto()
        STEP_PRICE = auto()
        STEP_USED = auto()
        EVENT_LOGS = auto()

    class Status(IntEnum):
        FAILURE = 0
        SUCCESS = 1

    def __init__(
        self,
        tx_hash: bytes = None,
        status: Union[Status, int] = Status.FAILURE,
        tx_index: int = -1,
        to: "Address" = None,
        score_address: "Address" = None,
        block_height: int = -1,
        block_hash: bytes = None,
        step_price: int = 0,
        step_used: int = -1,
        event_logs: List["EventLog"] = None,
    ):
        self._tx_hash: bytes = tx_hash
        self._status = (
            status if isinstance(status, self.Status) else self.Status(status)
        )
        self._tx_index: int = tx_index
        self._to: "Address" = to
        self._score_address = score_address
        self._block_height: int = block_height
        self._block_hash: bytes = block_hash
        self._step_price = step_price
        self._step_used = step_used
        self._event_logs: List["EventLog"] = [] if event_logs is None else event_logs

        self._fee = step_price * step_used

    def __str__(self) -> str:
        items = (
            ("status", self._status),
            ("to", self._to),
            ("score_address", self._score_address),
            ("block_height", self._block_height),
            ("block_hash", self._block_hash),
            ("tx_index", self._tx_index),
            ("tx_hash", self._tx_hash),
            ("step_used", self._step_used),
            ("step_price", self._step_price),
            ("fee", self._fee),
            # ("event_logs", self._event_logs)
        )

        def _func():
            for key, value in items:
                if isinstance(value, bytes):
                    value = bytes_to_hex(value)

                yield f"{key}={value}"

        return " ".join(_func())

    @property
    def tx_hash(self) -> bytes:
        return self._tx_hash

    @property
    def tx_index(self) -> int:
        return self._tx_index

    @property
    def status(self) -> Status:
        return self._status

    @property
    def to(self) -> "Address":
        return self._to

    @property
    def block_height(self) -> int:
        return self._block_height

    @property
    def block_hash(self) -> bytes:
        return self._block_hash

    @property
    def step_price(self) -> int:
        return self._step_price

    @property
    def step_used(self) -> int:
        return self._step_used

    @property
    def fee(self) -> int:
        return self._fee

    @property
    def event_logs(self) -> List["EventLog"]:
        return self._event_logs

    @classmethod
    def from_json(cls, data: bytes) -> "TransactionResult":
        data_in_dict = json.loads(data)

        # The result of a transaction is nested with "result" key in the transaction data in loopchain db.
        return cls.from_dict(data_in_dict["result"])

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, List]]) -> "TransactionResult":
        status = cls.Status(str_to_int(data["status"]))
        to: "Address" = Address.from_string(data["to"])
        score_address: "Address" = Address.from_string(
            data["scoreAddress"]
        ) if "scoreAddress" in data else None
        tx_hash: bytes = hex_to_bytes(data["txHash"])
        tx_index: int = str_to_int(data["txIndex"])
        block_height: int = str_to_int(data["blockHeight"])
        block_hash: bytes = hex_to_bytes(data["blockHash"])
        step_price: int = str_to_int(data["stepPrice"])
        step_used: int = str_to_int(data["stepUsed"])
        event_logs: List["EventLog"] = cls._parse_event_logs(data["eventLogs"])

        return TransactionResult(
            status=status,
            to=to,
            score_address=score_address,
            tx_hash=tx_hash,
            tx_index=tx_index,
            block_height=block_height,
            block_hash=block_hash,
            step_price=step_price,
            step_used=step_used,
            event_logs=event_logs,
        )

    @classmethod
    def _parse_event_logs(cls, event_logs: List[Dict[str, str]]) -> List["EventLog"]:
        ret = []
        for log in event_logs:
            ret.append(EventLog.from_dict(log))

        return ret

    def to_list(self) -> List[Any]:
        if len(self._event_logs) > 0:
            event_logs = [event_log.to_list() for event_log in self._event_logs]
        else:
            event_logs = None

        return [
            self._tx_hash,
            self._status.value,
            self._tx_index,
            self._to,
            self._score_address,
            self._block_height,
            self._block_hash,
            self._step_price,
            self._step_used,
            event_logs,
        ]

    @classmethod
    def from_list(cls, obj: List[Any]) -> "TransactionResult":
        return cls(*obj)

    @classmethod
    def get_ext_type(cls) -> int:
        return pack.ExtType.TX_RESULT.value

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = pack.decode(data)
        assert isinstance(obj, list)
        return cls.from_list(obj)

    def to_bytes(self) -> bytes:
        return pack.encode(self.to_list())
