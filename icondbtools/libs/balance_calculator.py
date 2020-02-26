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

from typing import List, Iterable, Tuple

from iconservice.base.address import AddressPrefix, Address
from ..data.transaction import Transaction
from ..data.transaction_result import TransactionResult

ICON_SERVICE_ADDRESS = Address.from_prefix_and_int(AddressPrefix.CONTRACT, 0)


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

    def run(self, it: Iterable[Tuple['Transaction', 'TransactionResult']], init_balance: int = 0) -> int:
        self._txs.clear()
        self._tx_results.clear()

        balance = init_balance

        for tx, tx_result in it:
            assert tx.tx_hash == tx_result.tx_hash

            if self._address not in (tx.from_, tx.to):
                continue

            balance += self._calculate_balance_delta(tx, tx_result)
            self._txs.append(tx)
            self._tx_results.append(tx_result)

        return balance

    def _calculate_balance_delta(self, tx: 'Transaction', tx_result: 'TransactionResult') -> int:
        is_tx_owner = tx.from_ == self._address
        balance_delta = 0

        if tx_result.status == 1:
            balance_delta += self._calc_balance_delta_with_value(tx, tx_result)
            balance_delta += self._calc_balance_delta_in_iscore_claimed_event_log(tx_result)

        if is_tx_owner:
            balance_delta -= tx_result.fee

        return balance_delta

    def _calc_balance_delta_with_value(self, tx, tx_result) -> int:
        assert tx_result.status == 1

        delta = 0

        if tx.from_ == self._address:
            delta -= tx.value
        if tx.to == self._address:
            delta += tx.value

        return delta

    @staticmethod
    def _calc_balance_delta_in_iscore_claimed_event_log(tx_result) -> int:
        assert tx_result.status == 1

        delta = 0

        for event_log in tx_result.event_logs:
            if event_log.score_address == ICON_SERVICE_ADDRESS and event_log.signature == "IScoreClaimed":
                delta += event_log.data[1]

        return delta
