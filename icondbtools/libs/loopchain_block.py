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

import json
from typing import Optional

from iconservice.base.address import Address
from ..utils.convert_type import convert_hex_str_to_int, convert_hex_str_to_bytes


class LoopchainBlock(object):

    def __init__(self,
                 version: str = None,
                 height: int = -1,
                 timestamp: int = -1,
                 block_hash: bytes = None,
                 prev_block_hash: bytes = None,
                 leader: 'Address' = None,
                 state_hash: bytes = None,
                 transactions: list = None):
        self.version = version
        self.height = height
        self.block_hash = block_hash
        self.prev_block_hash = prev_block_hash
        self.timestamp: int = timestamp
        self.leader = leader
        self.state_hash: bytes = state_hash
        self.transactions = transactions

    def __bool__(self):
        return True

    @classmethod
    def from_bytes(cls, data: bytes) -> 'LoopchainBlock':
        block_dict: dict = json.loads(data)
        return cls.from_dict(block_dict)

    @classmethod
    def from_dict(cls, block: dict) -> 'LoopchainBlock':
        version: str = block["version"]
        handlers = {
            "0.1a": cls.from_dict_v1,
        }

        handler = handlers.get(version, cls._from_dict_recent_v)
        return handler(block)

    @classmethod
    def from_dict_v1(cls, block: dict) -> 'LoopchainBlock':
        version = block['version']
        height: int = block["height"]
        block_hash: bytes = convert_hex_str_to_bytes(block["block_hash"])
        prev_block_hash: bytes = convert_hex_str_to_bytes(block["prev_block_hash"])

        key: str = "timestamp" if "timestamp" in block else "time_stamp"
        timestamp: int = block[key]

        state_hash: bytes = cls._get_commit_state(block)
        leader: 'Address' = cls._get_peer_id(block)

        transactions: list = block['confirmed_transaction_list']

        return LoopchainBlock(version=version,
                              height=height,
                              block_hash=block_hash,
                              timestamp=timestamp,
                              prev_block_hash=prev_block_hash,
                              state_hash=state_hash,
                              leader=leader,
                              transactions=transactions)

    @classmethod
    def _get_commit_state(cls, block: dict) -> bytes:
        try:
            return convert_hex_str_to_bytes(block["commit_state"]["icon_dex"])
        except BaseException:
            return b""

    @classmethod
    def _get_peer_id(cls, block: dict) -> Optional['Address']:
        peer_id = block['peer_id']
        if peer_id:
            return Address.from_string(peer_id)

        return None

    @classmethod
    def _from_dict_recent_v(cls, block: dict) -> 'LoopchainBlock':
        # In case of version >= 0.3
        version: str = block["version"]

        height: int = convert_hex_str_to_int(block["height"])
        block_hash: bytes = convert_hex_str_to_bytes(block["hash"])
        prev_block_hash: bytes = convert_hex_str_to_bytes(block["prevHash"])
        leader = Address.from_string(block["leader"])
        timestamp: int = convert_hex_str_to_int(block["timestamp"])
        state_hash: bytes = convert_hex_str_to_bytes(block["stateHash"])
        transactions: list = block["transactions"]

        return LoopchainBlock(version=version,
                              height=height,
                              block_hash=block_hash,
                              timestamp=timestamp,
                              prev_block_hash=prev_block_hash,
                              state_hash=state_hash,
                              leader=leader,
                              transactions=transactions)
