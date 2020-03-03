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

from typing import TYPE_CHECKING

import pytest

from icondbtools.libs.transaction_collector import TransactionCollector, TransactionFilter
from iconservice.base.address import Address, AddressPrefix

if TYPE_CHECKING:
    from icondbtools.data.transaction import Transaction
    from icondbtools.data.transaction_result import TransactionResult


class TransactionFilterByAddress(TransactionFilter):
    def __init__(self, address: 'Address'):
        super().__init__()
        self._address = address

    def run(self, tx: 'Transaction', tx_result: 'TransactionResult') -> bool:
        return tx.from_ == self._address or tx.to == self._address


@pytest.mark.skip
class TestTransactionCollector(object):
    @pytest.fixture
    def tx_collector(self):
        db_path = "/Users/goldworm/work/icon/db-data/mainnet/db/"

        tx_collector = TransactionCollector()
        tx_collector.open(db_path)
        yield tx_collector
        tx_collector.close()

    def test_run(self, tx_collector):
        address = Address.from_prefix_and_int(AddressPrefix.EOA, 0)
        tx_filter = TransactionFilterByAddress(address)

        tx_collector.run(start_block_height=0, end_block_height=10, tx_filter=tx_filter)

        assert isinstance(tx_collector.transactions, list)

    def test_run_with_file(self, tx_collector):
        path = "/Users/goldworm/transactions.txt"
        tx_collector.run_with_file(path)
