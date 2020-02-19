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

import unittest

from iconservice.base.address import Address
from icondbtools.utils.convert_type import convert_hex_str_to_bytes, bytes_to_str
from icondbtools.data.transaction import Transaction


class TestTransaction(unittest.TestCase):
    def test_from_dict(self):
        from_ = Address.from_string("hx3aa778e1f00c77d3490e9e625f1f83ed26f90133")
        to = Address.from_string("cx0000000000000000000000000000000000000000")
        version = 0x3
        nid = 0x1
        step_limit = 0x1a2c0
        timestamp = 0x59ddd22448390
        data_type = "call"
        signature = "Ot+ouYw5Fdb4XkfODSv+8X3q7Kn8Fse4D51nLmzY62cPgR/5HZ26JTMCxO6D44pbbCumy8vS6e70XdB+ddL/mwA="
        tx_hash = convert_hex_str_to_bytes("0x5241633c13fefaa423148a43b703c5f5a2478d592a91ef0483845729c635c89c")
        tx_index = 0x1
        block_height = 0xde2cf7
        block_hash = convert_hex_str_to_bytes("0xad934d67b8bd658dd2261a60afb3d7909cc329defd1ddb21c23d2947cceeb80c")

        tx_data = {
            "version": hex(version),
            "nid": hex(nid),
            "from": str(from_),
            "to": str(to),
            "stepLimit": hex(step_limit),
            "timestamp": hex(timestamp),
            "dataType": data_type,
            "data": {
                "method": "claimIScore",
                "params": {}
            },
            "signature": signature,
            "txHash": bytes_to_str(tx_hash),
            "txIndex": hex(tx_index),
            "blockHeight": hex(block_height),
            "blockHash": bytes_to_str(block_hash)
        }

        tx = Transaction.from_dict(tx_data)
        assert tx.version == version
        assert tx.nid == nid
        assert tx.from_ == from_
        assert tx.to == to
        assert tx.value == 0
        assert tx.timestamp == timestamp
        assert tx._step_limit == step_limit
        assert tx.tx_index == tx_index
        assert tx.tx_hash == tx_hash
        assert tx.block_height == block_height
        assert tx.block_hash == block_hash
        assert tx.nonce is None
        assert tx.data_type == data_type


if __name__ == '__main__':
    unittest.main()
