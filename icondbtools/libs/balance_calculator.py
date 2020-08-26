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

from enum import IntEnum, auto
from typing import List, Iterable, Tuple, Dict, Optional

from iconservice.base.address import AddressPrefix, Address
from ..data.transaction import Transaction
from ..data.transaction_result import TransactionResult
from ..utils.convert_type import bytes_to_hex, str_to_int

ICON_SERVICE_ADDRESS = Address.from_prefix_and_int(AddressPrefix.CONTRACT, 0)


class StakeInfo(object):
    def __init__(self):
        self.stake = 0
        self.unstake = 0
        self.block_height = 0
        self.block_hash: Optional[bytes] = None
        self.tx_hash: Optional[bytes] = None

    def __str__(self) -> str:
        return (
            f"stake={self.stake} "
            f"unstake={self.unstake} "
            f"block_height={self.block_height} "
            f"block_hash={bytes_to_hex(self.block_hash)} "
            f"tx_hash={bytes_to_hex(self.tx_hash)}"
        )


class TransactionType(IntEnum):
    ICX_SEND = auto()
    ICX_RECV = auto()
    REGISTER_PREP = auto()
    SET_PREP = auto()
    UNREGISTER_PREP = auto()
    SET_STAKE = auto()
    SET_DELEGATION = auto()
    CLAIM_ISCORE = auto()
    CALL = auto()


class BalanceCalculator(object):
    """Calculate the balance of a given address with transactions and transaction results

    """

    def __init__(self, address: "Address"):
        self._address = address
        self._txs: List["Transaction"] = []
        self._tx_results: List["TransactionResult"] = []
        self._stake_info: Optional[StakeInfo] = None

        self._method_to_tx_type = {
            "registerPRep": TransactionType.REGISTER_PREP,
            "setPRep": TransactionType.SET_PREP,
            "unregisterPRep": TransactionType.UNREGISTER_PREP,
            "setStake": TransactionType.SET_STAKE,
            "setDelegation": TransactionType.SET_DELEGATION,
            "claimIScore": TransactionType.CLAIM_ISCORE,
        }

    @property
    def address(self) -> "Address":
        return self._address

    @property
    def txs(self) -> List["Transaction"]:
        return self._txs

    @property
    def tx_results(self) -> List["TransactionResult"]:
        return self._tx_results

    def run(
        self,
        it: Iterable[Tuple["Transaction", "TransactionResult"]],
        init_balance: int = 0,
        init_stake: int = 0,
        init_unstake: int = 0,
    ) -> Tuple[int, StakeInfo]:
        self._txs.clear()
        self._tx_results.clear()
        self._stake_info = StakeInfo()

        balance = init_balance
        self._stake_info.stake = init_stake
        self._stake_info.unstake = init_unstake

        self._print_title()

        i = 0
        for tx, tx_result in it:
            if self._address not in (tx.from_, tx.to):
                continue

            delta = self._calculate_balance_delta(tx, tx_result)
            balance += delta

            self._txs.append(tx)
            self._tx_results.append(tx_result)

            tx_type = self._get_tx_type(tx)
            self._print_detail(i, tx_type, balance, delta, tx, tx_result)
            i += 1

        return balance, self._stake_info

    def _calculate_balance_delta(
        self, tx: "Transaction", tx_result: "TransactionResult"
    ) -> int:
        is_tx_owner = tx.from_ == self._address
        balance_delta = 0

        if tx_result.status == TransactionResult.Status.SUCCESS:
            balance_delta += self._calc_balance_delta_with_value(tx, tx_result)
            balance_delta += self._calc_balance_delta_in_call(tx, tx_result)

        if is_tx_owner:
            balance_delta -= tx_result.fee

        return balance_delta

    def _calc_balance_delta_with_value(self, tx, tx_result) -> int:
        assert tx_result.status == TransactionResult.Status.SUCCESS

        delta = 0

        if tx.from_ == self._address:
            delta -= tx.value
        if tx.to == self._address:
            delta += tx.value

        return delta

    def _calc_balance_delta_in_call(
        self, tx: "Transaction", tx_result: "TransactionResult"
    ) -> int:
        assert tx_result.status == TransactionResult.Status.SUCCESS

        delta = 0

        if tx.data_type == "call":
            call_data: "Transaction.CallData" = tx.data
            method: str = call_data.method

            if method == "setStake":
                delta = self._calc_balance_delta_in_set_stake(
                    call_data.params, tx_result
                )
            elif method == "claimIScore":
                delta = self._calc_balance_delta_in_claim_iscore(tx_result)

        return delta

    @staticmethod
    def _calc_balance_delta_in_claim_iscore(tx_result) -> int:
        assert tx_result.status == TransactionResult.Status.SUCCESS

        delta = 0

        for event_log in tx_result.event_logs:
            if (
                event_log.score_address == ICON_SERVICE_ADDRESS
                and event_log.signature == "IScoreClaimed(int,int)"
            ):
                delta += event_log.data[1]

        return delta

    def _calc_balance_delta_in_set_stake(
        self, params: Dict[str, str], tx_result: "TransactionResult"
    ) -> int:
        assert tx_result.status == TransactionResult.Status.SUCCESS

        old_stake = self._stake_info.stake
        new_stake = str_to_int(params["value"])


        if old_stake > new_stake:
            unstake = old_stake - new_stake
        else:
            unstake = 0

        self._stake_info.stake = new_stake
        self._stake_info.unstake = unstake
        self._stake_info.block_height = tx_result.block_height
        self._stake_info.block_hash = tx_result.block_hash
        self._stake_info.tx_hash = tx_result.tx_hash

        return 0

    def _get_tx_type(self, tx: "Transaction") -> TransactionType:
        if tx.to == self._address:
            return TransactionType.ICX_RECV

        tx_type = TransactionType.ICX_SEND

        if tx.data_type == "call":
            call_data: "Transaction.CallData" = tx.data
            method: str = call_data.method
            tx_type = self._method_to_tx_type.get(method, TransactionType.CALL)

        return tx_type

    @classmethod
    def _print_title(cls):
        print(
            f"index | status | tx_type | BH | tx_hash | balance | delta | value | fee\n"
            f"-----------------------------------------------------------------------"
        )

    @classmethod
    def _print_detail(
        cls,
        i: int,
        tx_type: TransactionType,
        balance: int,
        delta: int,
        tx: "Transaction",
        tx_result: "TransactionResult",
    ):
        print(
            f"{i:04d} "
            f"{tx_result.status.name} "
            f"{tx_type.name:14s} "
            f"{tx_result.block_height:010d} "
            f"{bytes_to_hex(tx.tx_hash)} "
            f"{balance} "
            f"{delta} "
            f"{tx.value} "
            f"{tx_result.fee} "
        )
