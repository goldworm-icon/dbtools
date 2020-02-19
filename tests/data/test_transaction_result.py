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

from icondbtools.data.transaction_result import TransactionResult
from icondbtools.utils.convert_type import convert_hex_str_to_bytes, bytes_to_str


class TestTransactionResult(unittest.TestCase):
    def test_from_dict_with_icx_transfer_tx(self):
        tx_hash: bytes = convert_hex_str_to_bytes("0xb35299d299951c16e417be40c3c0f68ed941dadccfe50f3b8501600695504855")
        block_height = 0xe65585
        block_hash = convert_hex_str_to_bytes("0x42d887e9a51aad7d69f22bbcc4fa7b74d7549beb202cd1577bcf0ded62e57785")
        tx_index = 0x2
        to = Address.from_string("hxf3db3ffed154bb34af67429e8038e5f4aca84390")
        step_used = 0x186a0
        step_price = 0x2540be400
        status = 0x1

        tx_result_data = {
            "txHash": bytes_to_str(tx_hash),
            "blockHeight": hex(block_height),
            "blockHash": bytes_to_str(block_hash),
            "txIndex": hex(tx_index),
            "to": str(to),
            "stepUsed": hex(step_used),
            "stepPrice": hex(step_price),
            "cumulativeStepUsed": "0x912d0",
            "eventLogs": [],
            "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "status": hex(status)
        }

        tx_result = TransactionResult.from_dict(tx_result_data)
        assert tx_result.tx_hash == tx_hash
        assert tx_result.block_height == block_height
        assert tx_result.block_hash == block_hash
        assert tx_result.tx_index == tx_index
        assert tx_result.to == to
        assert tx_result.step_used == step_used
        assert tx_result.step_price == step_price
        assert tx_result.fee == step_price * step_used
        assert len(tx_result.event_logs) == 0
        assert tx_result.status == status

    def test_from_dict_with_claim_iscore_tx(self):
        tx_hash: bytes = convert_hex_str_to_bytes("0x5241633c13fefaa423148a43b703c5f5a2478d592a91ef0483845729c635c89c")
        block_height = 0xde2cf7
        block_hash = convert_hex_str_to_bytes("0xad934d67b8bd658dd2261a60afb3d7909cc329defd1ddb21c23d2947cceeb80c")
        tx_index = 0x1
        to = Address.from_string("cx0000000000000000000000000000000000000000")
        step_used = 0x1a2c0
        step_price = 0x2540be400
        status = 0x1

        # eventLog
        score_address = Address.from_string("cx0000000000000000000000000000000000000000")
        signature = "IScoreClaimed(int,int)"
        iscore = 0x147f175d36cd5737754e38
        icx = 0x53f415f8af514478a93

        tx_result_data = {
            "txHash": bytes_to_str(tx_hash),
            "blockHeight": hex(block_height),
            "blockHash": bytes_to_str(block_hash),
            "txIndex": hex(tx_index),
            "to": str(to),
            "stepUsed": hex(step_used),
            "stepPrice": hex(step_price),
            "cumulativeStepUsed": "0x1a2c0",
            "eventLogs": [
                {
                    "scoreAddress": str(score_address),
                    "indexed": [signature],
                    "data": [hex(iscore), hex(icx)]
                }
            ],
            "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "status": hex(status)
        }

        tx_result = TransactionResult.from_dict(tx_result_data)
        assert tx_result.tx_hash == tx_hash
        assert tx_result.block_height == block_height
        assert tx_result.block_hash == block_hash
        assert tx_result.tx_index == tx_index
        assert tx_result.to == to
        assert tx_result.step_used == step_used
        assert tx_result.step_price == step_price
        assert tx_result.fee == step_price * step_used
        assert tx_result.status == status

        assert len(tx_result.event_logs) == 1
        event_log = tx_result.event_logs[0]
        assert event_log.score_address == score_address
        assert event_log.signature == signature
        assert event_log.indexed[0] == signature
        assert len(event_log.indexed) == 1
        assert len(event_log.data) == 2
        assert event_log.data[0] == iscore
        assert event_log.data[1] == icx


if __name__ == '__main__':
    unittest.main()
