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

import hashlib
from typing import Union, Optional

import plyvel

from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.icx.coin_part import CoinPart
from iconservice.icx.delegation_part import DelegationPart
from iconservice.icx.icx_account import Account
from iconservice.icx.stake_part import StakePart


class StateHash(object):
    def __init__(
        self,
        hash_data: bytes = None,
        rows: int = 0,
        total_key_size: int = 0,
        total_value_size: int = 0,
    ):
        self.hash_data = hash_data
        self.rows = rows
        self.total_key_size = total_key_size
        self.total_value_size = total_value_size

    def __str__(self):
        return (
            f"hash: {self.hash_data.hex()}\n"
            f"rows: {self.rows}\n"
            f"total_key_size: {self.total_key_size}\n"
            f"total_value_size: {self.total_value_size}"
        )


class StateDatabaseReader(object):
    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db is not None:
            self._db.close()
            self._db = None

    def get_account(self, address: "Address", current_block_height: int, revision: int) -> Optional["Account"]:
        """Read the account from statedb

        :param address:
        :param current_block_height:
        :param revision:
        :return:
        """
        value: bytes = self._db.get(address.to_bytes())
        if value is None:
            return None

        coin_part = self._get_part(CoinPart, address)
        stake_part = self._get_part(StakePart, address)

        return Account(
            address,
            current_block_height,
            revision,
            coin_part=coin_part,
            stake_part=stake_part
        )

    @property
    def iterator(self):
        return self._db.iterator()

    def get_coin_part(self, address: 'Address') -> CoinPart:
        return self._get_part(CoinPart, address)

    def get_stake_part(self, address: 'Address') -> StakePart:
        return self._get_part(StakePart, address)

    def get_delegation_part(self, address: 'Address') -> DelegationPart:
        return self._get_part(DelegationPart, address)

    def _get_part(self,
                  part_class: Union[type(CoinPart), type(StakePart), type(DelegationPart)],
                  address: 'Address') -> Union['CoinPart', 'StakePart', 'DelegationPart']:
        key: bytes = part_class.make_key(address)
        value: bytes = self._db.get(key)

        part = part_class.from_bytes(value) if value else part_class()
        part.set_complete(True)
        return part

    def get_by_key(self, key):
        value: bytes = self._db.get(key)

        if value is None:
            return None

        return value

    def get_last_block(self) -> "Block":
        """Read the last commited block from statedb

        :return: last block
        """
        value: bytes = self._db.get(b"last_block")
        if value is None:
            return None

        return Block.from_bytes(value)

    def get_total_supply(self) -> int:
        value: bytes = self._db.get(b'total_supply')
        return int.from_bytes(value, 'big') if value else 0

    def create_state_hash(self, prefix: bytes = None) -> "StateHash":
        """Read key and value from state db and create sha3 hash value from them

        :return: StateHash object
        """

        if prefix is None:
            db = self._db
        else:
            db = self._db.prefixed_db(prefix)

        state_hash, rows, total_key_size, total_value_size = self._create_state_hash(db)
        return StateHash(state_hash, rows, total_key_size, total_value_size)

    @staticmethod
    def _create_state_hash(db) -> tuple:
        """Read key and value from state db and create sha3 hash value from them

        :return: StateHash object
        """

        rows = 0
        total_key_size = 0
        total_value_size = 0

        sha3_256 = hashlib.sha3_256()

        for key, value in db:
            sha3_256.update(key)
            sha3_256.update(value)

            rows += 1
            total_key_size += len(key)
            total_value_size += len(value)

        state_hash: bytes = sha3_256.digest()
        return state_hash, rows, total_key_size, total_value_size
