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
from typing import Iterable, Tuple

from icondbtools.data.event_log import EventLog
from icondbtools.data.transaction import Transaction
from icondbtools.data.transaction_result import TransactionResult
from icondbtools.libs.balance_calculator import BalanceCalculator, ICON_SERVICE_ADDRESS
from iconservice.utils import icx_to_loop


class TestBalanceCalculator(object):
    def test_run_on_icx_transfer(self, create_address, tx_hash, step_price):
        from_ = create_address()
        to = create_address()
        tx_hash: bytes = os.urandom(32)
        value = icx_to_loop(5)
        step_limit = 2_000_000
        step_used = step_limit
        init_balance = icx_to_loop(100)

        tx = Transaction(
            version=3,
            nid=1,
            tx_hash=tx_hash,
            from_=from_,
            to=to,
            value=value,
            step_limit=step_limit,
        )

        tx_result = TransactionResult(
            tx_hash=tx_hash,
            status=1,
            tx_index=0,
            step_price=step_price,
            step_used=step_used,
        )

        def func() -> Iterable[Tuple["Transaction", "TransactionResult"]]:
            yield tx, tx_result

        calculator = BalanceCalculator(from_)
        balance, _ = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance - value - step_price * step_used
        assert balance == expected_balance

    def test_run_on_icx_received(self, create_address, tx_hash, step_price):
        from_ = create_address()
        to = create_address()
        value = icx_to_loop(5)
        step_limit = 2_000_000
        step_used = step_limit
        init_balance = icx_to_loop(100)

        tx = Transaction(
            version=3,
            nid=1,
            tx_hash=tx_hash,
            from_=from_,
            to=to,
            value=value,
            step_limit=step_limit,
        )

        tx_result = TransactionResult(
            tx_hash=tx_hash,
            status=1,
            tx_index=0,
            step_price=step_price,
            step_used=step_used,
        )

        def func() -> Iterable[Tuple["Transaction", "TransactionResult"]]:
            yield tx, tx_result

        calculator = BalanceCalculator(to)
        balance, _ = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance + value
        assert balance == expected_balance

    def test_run_on_claim_iscore(self, address, tx_hash, step_price):
        score_address = ICON_SERVICE_ADDRESS
        value = icx_to_loop(0)
        step_limit = 2_000_000
        step_used = step_limit
        init_balance = icx_to_loop(100)
        data_type = "call"
        data = Transaction.CallData("claimIScore", None)

        tx = Transaction(
            version=3,
            nid=1,
            tx_hash=tx_hash,
            from_=address,
            to=score_address,
            value=value,
            step_limit=step_limit,
            data_type=data_type,
            data=data,
        )

        claimed_icx = icx_to_loop(6)
        claimed_iscore = claimed_icx * 1000
        event_log = EventLog(
            score_address,
            indexed=["IScoreClaimed(int,int)"],
            data=[claimed_iscore, claimed_icx],
        )

        tx_result = TransactionResult(
            tx_hash=tx_hash,
            status=1,
            tx_index=0,
            step_price=step_price,
            step_used=step_used,
            event_logs=[event_log],
        )

        def func() -> Iterable[Tuple["Transaction", "TransactionResult"]]:
            yield tx, tx_result

        calculator = BalanceCalculator(address)
        balance, _ = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance - step_price * step_used + claimed_icx
        assert balance == expected_balance

    def test_run_on_set_stake(self, address, tx_hash, step_price):
        score_address = ICON_SERVICE_ADDRESS
        value = icx_to_loop(0)
        step_limit = 2_000_000
        step_used = step_limit
        init_balance = icx_to_loop(200)
        data_type = "call"
        stake = icx_to_loop(100)
        data = Transaction.CallData(method="setStake", params={"value": hex(stake)})

        tx = Transaction(
            version=3,
            nid=1,
            tx_hash=tx_hash,
            from_=address,
            to=score_address,
            value=value,
            step_limit=step_limit,
            data_type=data_type,
            data=data,
        )

        tx_result = TransactionResult(
            tx_hash=tx_hash,
            status=TransactionResult.Status.SUCCESS,
            tx_index=0,
            step_price=step_price,
            step_used=step_used,
        )

        def func() -> Iterable[Tuple["Transaction", "TransactionResult"]]:
            yield tx, tx_result

        calculator = BalanceCalculator(address)
        balance, stake_info = calculator.run(func(), init_balance=init_balance)

        expected_balance = init_balance - step_price * step_used
        assert balance == expected_balance
        assert stake_info.stake == stake
        assert stake_info.unstake == 0
        assert stake_info.tx_hash == tx_hash
