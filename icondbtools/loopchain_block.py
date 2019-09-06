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

from iconservice.base.block import Block

from . import utils


class LoopchainBlock(Block):

    def __init__(self,
                 height: int = -1,
                 hash: bytes = None,
                 timestamp: int = -1,
                 prev_hash: bytes = None,
                 cumulative_fee: int = 0,
                 transactions: list = None):
        super().__init__(height, hash, timestamp, prev_hash, cumulative_fee)
        self.transactions = transactions

    @staticmethod
    def from_dict(block: dict) -> 'LoopchainBlock':
        version = block['version']

        keynames = {
            'hash': {"0.3": "hash", "0.1a": "block_hash"},
            'timestamp': {"0.3": "timestamp", "0.1a": "time_stamp"},
            'prev_hash': {"0.3": "prevHash", "0.1a": "prev_block_hash"},
            'transactions': {"0.3": "transactions", "0.1a": "confirmed_transaction_list"}
        }

        height = utils.convert_hex_str_to_int(block['height'])
        hash = utils.convert_hex_str_to_bytes(block[keynames['hash'][version]])
        timestamp = block[keynames['timestamp'][version]]
        if version == "0.3":
            timestamp = int(timestamp, 16)
        prev_hash = utils.convert_hex_str_to_bytes(block[keynames['prev_hash'][version]])
        transactions = block[keynames['transactions'][version]]

        return LoopchainBlock(height, hash, timestamp, prev_hash, transactions=transactions)
