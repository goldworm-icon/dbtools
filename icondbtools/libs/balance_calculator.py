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

from typing import List, Dict
from ..data.transaction import Transaction
from ..data.transaction_result import TransactionResult


class BalanceCalculator(object):
    """Calculate the balance of a given address with transactions and transaction results

    """

    def __init__(self, address: 'Address'):
        self._address = address
        self._txs: List['Transaction'] = []
        self._tx_results: List['TransactionResult'] = []

    @property
    def address(self) -> 'Address':
        return self._address

    @property
    def txs(self) -> List['Transaction']:
        return self._txs

    @property
    def tx_results(self) -> List['TransactionResult']:
        return self._tx_results

    def update(self, tx: 'Transaction', tx_result: 'TransactionResult'):
        self._txs.append(tx)
        self._tx_results.append(tx_result)

    def run(self, init_balance: int = 0) -> int:
        balance = init_balance

        for tx, tx_result in zip(self._txs, self._tx_results):
            if tx_result.status:
                pass
            else:
                balance -= tx_result.fee

        return balance
