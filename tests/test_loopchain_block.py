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

import unittest

from iconservice.base.address import Address

from icondbtools.libs.loopchain_block import LoopchainBlock


class TestLoopchainBlock(unittest.TestCase):

    def test_block_v0_1a_from_dict(self):
        version = '0.1a'
        prev_block_hash = bytes.fromhex(
            'f578312788010043e7a0b959e0c0dbca87c4e7a90331ac59a91fb2fdb62c8640')
        merkle_tree_root_hash = bytes.fromhex(
            '30cdeb912b4acdac5c2cdd885983648c366ec0d99ce99a841bb4620f34f9b5c9')
        timestamp = 1537429228235545
        block_hash = bytes.fromhex(
            '15bbaed5a869738b4c40614a4134f666057de1dd492234d7aa3e06f05a5e85ca')
        height = 59669
        peer_id = Address.from_string('hx667e748e93a5a4e1d61c92c482577888e8c35c9d')
        commit_state = bytes.fromhex('4b57f72f29ebdf5d5543e12ea63e684ab6636c53ca24600f0208e410f0311447')
        confirmed_transaction_list = [{
            'from': 'hxeb56a51667eb0491bd1308426865193a9684908a',
            'to': 'hx5c328b010e4ef0f81670ef48eb1b903aac1443e2',
            'value': '0x8ac7230489e80000',
            'version': '0x3',
            'nid': '0x1',
            'stepLimit': '0x186a0',
            'timestamp': '0x57648a309f940',
            'signature': 'KglKpRzx1kRCmfOEnU7ltIa2PFaJDhHElowNFxDeXgNP7ksttPCT3fnSR4PpoPpkVVh3wprQVZr+KCPK6r7uRwA=',
            'txHash': '30cdeb912b4acdac5c2cdd885983648c366ec0d99ce99a841bb4620f34f9b5c9'
        }]

        block_dict = {
            'version': version,
            'prev_block_hash': prev_block_hash.hex(),
            'merkle_tree_root_hash': merkle_tree_root_hash.hex(),
            'time_stamp': timestamp,
            'confirmed_transaction_list': confirmed_transaction_list,
            'block_hash': block_hash.hex(),
            'height': height,
            'peer_id': str(peer_id),
            'signature': 'M97tADsivw0qtzD0qJUDjIc/ki6Zf5HatoAnOTgpi2dNmP5WvJccAVpD86mjxxNOtdnFnO009iwnvw6yU0RBNAA=',
            'commit_state': {'icon_dex': commit_state.hex()}
        }

        loopchain_block = LoopchainBlock.from_dict(block_dict)
        self.assertEqual(prev_block_hash, loopchain_block.prev_block_hash)
        self.assertEqual(timestamp, loopchain_block.timestamp)
        self.assertEqual(block_hash, loopchain_block.block_hash)
        self.assertEqual(height, loopchain_block.height)

    def test_from_dict_with_block_v3(self):
        pass
