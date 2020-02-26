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

from typing import List, Dict

from iconservice.base.address import Address

from ..data.event_log import EventLog
from ..utils.convert_type import convert_hex_str_to_int, convert_hex_str_to_bytes, str_to_int


class TransactionResult(object):
    def __init__(self,
                 tx_hash: bytes = None,
                 status: int = 0,
                 tx_index: int = -1,
                 to: 'Address' = None,
                 block_height: int = -1,
                 block_hash: bytes = None,
                 step_price: int = 0,
                 step_used: int = -1,
                 event_logs: List['EventLog'] = None):
        self._tx_hash: bytes = tx_hash
        self._tx_index: int = tx_index
        self._status = status
        self._to: 'Address' = to
        self._block_height: int = block_height
        self._block_hash: bytes = block_hash
        self._step_price = step_price
        self._step_used = step_used
        self._fee = step_price * step_used
        self._event_logs: List['EventLog'] = [] if event_logs is None else event_logs

    @property
    def tx_hash(self) -> bytes:
        return self._tx_hash

    @property
    def tx_index(self) -> int:
        return self._tx_index

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
    def event_logs(self) -> List['EventLog']:
        return self._event_logs

    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionResult':
        tx_hash: bytes = convert_hex_str_to_bytes(data["txHash"])
        tx_index: int = str_to_int(data["txIndex"])
        status: int = convert_hex_str_to_int(data["status"])
        to: 'Address' = Address.from_string(data["to"])
        block_height: int = convert_hex_str_to_int(data["blockHeight"])
        block_hash: bytes = convert_hex_str_to_bytes(data["blockHash"])
        step_price: int = convert_hex_str_to_int(data["stepPrice"])
        step_used: int = convert_hex_str_to_int(data["stepUsed"])
        event_logs: List['EventLog'] = cls._parse_event_logs(data["eventLogs"])

        return TransactionResult(
            tx_hash=tx_hash, status=status, tx_index=tx_index,
            to=to, block_height=block_height, block_hash=block_hash,
            step_price=step_price, step_used=step_used, event_logs=event_logs)

    @classmethod
    def _parse_event_logs(cls, event_logs: List[Dict[str, str]]) -> List['EventLog']:
        ret = []
        for log in event_logs:
            ret.append(EventLog.from_dict(log))

        return ret
