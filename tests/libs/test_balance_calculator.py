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

import os
import unittest
from typing import Iterable, Tuple

from iconservice.base.address import AddressPrefix, Address
from iconservice.utils import icx_to_loop

from icondbtools.data.event_log import EventLog
from icondbtools.data.transaction import Transaction
from icondbtools.data.transaction_result import TransactionResult
from icondbtools.libs.balance_calculator import BalanceCalculator, ICON_SERVICE_ADDRESS


class TestBalanceCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.addresses = []

        for i in range(10):
            address = Address.from_prefix_and_int(AddressPrefix.EOA, i)
            self.addresses.append(address)

    def test_run_icx_transfer(self):
        body: bytes = os.urandom(20)
        address = Address(AddressPrefix.EOA, body)
        tx_hash: bytes = os.urandom(32)
        value = icx_to_loop(5)
        step_limit = 2_000_000
        step_used = step_limit
        step_price = 10 ** 8
        init_balance = icx_to_loop(100)

        tx = Transaction(version=3,
                         nid=1,
                         tx_hash=tx_hash,
                         from_=address,
                         to=self.addresses[0],
                         value=value,
                         step_limit=step_limit)

        tx_result = TransactionResult(tx_hash=tx_hash,
                                      status=1,
                                      tx_index=0,
                                      step_price=step_price,
                                      step_used=step_used)

        def func() -> Iterable[Tuple['Transaction', 'TransactionResult']]:
            yield tx, tx_result

        calculator = BalanceCalculator(address)
        balance: int = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance - value - step_price * step_used
        assert balance == expected_balance

    def test_run_icx_received(self):
        body: bytes = os.urandom(20)
        address = Address(AddressPrefix.EOA, body)
        tx_hash: bytes = os.urandom(32)
        value = icx_to_loop(5)
        step_limit = 2_000_000
        step_used = step_limit
        step_price = 10 ** 8
        init_balance = icx_to_loop(100)

        tx = Transaction(version=3,
                         nid=1,
                         tx_hash=tx_hash,
                         from_=self.addresses[0],
                         to=address,
                         value=value,
                         step_limit=step_limit)

        tx_result = TransactionResult(tx_hash=tx_hash,
                                      status=1,
                                      tx_index=0,
                                      step_price=step_price,
                                      step_used=step_used)

        def func() -> Iterable[Tuple['Transaction', 'TransactionResult']]:
            yield tx, tx_result

        calculator = BalanceCalculator(address)
        balance: int = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance + value
        assert balance == expected_balance

    def test_run_iscore_claimed(self):
        body: bytes = os.urandom(20)
        address = Address(AddressPrefix.EOA, body)
        score_address = ICON_SERVICE_ADDRESS
        tx_hash: bytes = os.urandom(32)
        value = icx_to_loop(0)
        step_limit = 2_000_000
        step_used = step_limit
        step_price = 10 ** 8
        init_balance = icx_to_loop(100)

        tx = Transaction(version=3,
                         nid=1,
                         tx_hash=tx_hash,
                         from_=address,
                         to=score_address,
                         value=value,
                         step_limit=step_limit)

        claimed_icx = icx_to_loop(6)
        claimed_iscore = claimed_icx * 1000
        event_log = EventLog(score_address, indexed=["IScoreClaimed"], data=[claimed_iscore, claimed_icx])

        tx_result = TransactionResult(tx_hash=tx_hash,
                                      status=1,
                                      tx_index=0,
                                      step_price=step_price,
                                      step_used=step_used,
                                      event_logs=[event_log])

        def func() -> Iterable[Tuple['Transaction', 'TransactionResult']]:
            yield tx, tx_result

        calculator = BalanceCalculator(address)
        balance: int = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance - step_price * step_used + claimed_icx
        assert balance == expected_balance
