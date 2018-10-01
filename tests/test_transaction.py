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
from icondbtools.transaction import Transaction


class TestTransaction(unittest.TestCase):
    def test_from_dict(self):
        version = 3
        nid = 1
        from_ = Address.from_string('hxeb56a51667eb0491bd1308426865193a9684908a')
        to = Address.from_string('hx5c328b010e4ef0f81670ef48eb1b903aac1443e2')
        value = int('0x8ac7230489e80000', 16)
        step_limit = int('0x186a0', 16)
        nonce = int('0x1', 16)
        timestamp = int('0x57648a309f940', 16)
        signature = 'KglKpRzx1kRCmfOEnU7ltIa2PFaJDhHElowNFxDeXgNP7ksttPCT3fnSR4PpoPpkVVh3wprQVZr+KCPK6r7uRwA='
        tx_hash = bytes.fromhex('30cdeb912b4acdac5c2cdd885983648c366ec0d99ce99a841bb4620f34f9b5c9')

        tx_dict = {
            'from': str(from_),
            'to': str(to),
            'value': hex(value),
            'version': hex(version),
            'nid': hex(nid),
            'stepLimit': hex(step_limit),
            'nonce': hex(nonce),
            'timestamp': hex(timestamp),
            'signature': signature,
            'txHash': tx_hash.hex()
        }

        tx = Transaction.from_dict(tx_dict)

        self.assertEqual(version, tx.version)
        self.assertEqual(nid, tx.nid)
        self.assertEqual(from_, tx.from_)
        self.assertEqual(to, tx.to)
        self.assertEqual(value, tx.value)
        self.assertEqual(step_limit, tx.step_limit)
        self.assertEqual(nonce, tx.nonce)
        self.assertEqual(timestamp, tx.timestamp)
        self.assertEqual(signature, tx.signature)
        self.assertEqual(tx_hash, tx.tx_hash)
