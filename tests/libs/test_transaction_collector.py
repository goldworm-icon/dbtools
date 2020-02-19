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
from typing import TYPE_CHECKING

from icondbtools.libs.transaction_collector import TransactionCollector, TransactionFilter
from iconservice.base.address import Address, AddressPrefix

if TYPE_CHECKING:
    from icondbtools.data.transaction import Transaction


class TransactionFilterByAddress(TransactionFilter):
    def __init__(self, address: 'Address'):
        super().__init__()
        self._address = address

    def run(self, tx: 'Transaction') -> bool:
        return tx.from_ == self._address or tx.to == self._address


class TestTransactionCollector(unittest.TestCase):
    def setUp(self) -> None:
        self.tx_collector = TransactionCollector()

    def test_run(self):
        db_path = ""
        address = Address.from_prefix_and_int(AddressPrefix.EOA, 0)
        tx_collector = self.tx_collector
        tx_filter = TransactionFilterByAddress(address)

        tx_collector.open(db_path)
        tx_collector.run(start_block_height=0, end_block_height=10, tx_filter=tx_filter)
        tx_collector.close()

        assert isinstance(tx_collector.transactions, list)


if __name__ == '__main__':
    unittest.main()
