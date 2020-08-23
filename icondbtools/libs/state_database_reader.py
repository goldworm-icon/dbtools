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

import plyvel

from iconservice.base.block import Block
from iconservice.base.address import Address
from iconservice.icx.icx_account import Account
from iconservice.icx.stake_part import StakePart


class StateHash(object):
    def __init__(self,
                 hash_data: bytes=None,
                 rows: int=0,
                 total_key_size: int=0,
                 total_value_size: int=0):
        self.hash_data = hash_data
        self.rows = rows
        self.total_key_size = total_key_size
        self.total_value_size = total_value_size

    def __str__(self):
        return f'hash: {self.hash_data.hex()}\n' \
            f'rows: {self.rows}\n' \
            f'total_key_size: {self.total_key_size}\n' \
            f'total_value_size: {self.total_value_size}'


class StateDatabaseReader(object):
    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db is not None:
            self._db.close()
            self._db = None

    def get_account(self, address: 'Address') -> 'Account':
        """Read the account from statedb

        :param address:
        :return:
        """
        value: bytes = self._db.get(address.to_bytes())
        if value is None:
            return None

        account = Account.from_bytes(value)
        account.address = address

        return account

    def get_by_key(self, key):
        value: bytes = self._db.get(key)

        if value is None:
            return None

        return value

    def get_last_block(self) -> 'Block':
        """Read the last commited block from statedb

        :return: last block
        """
        value: bytes = self._db.get(b'last_block')
        if value is None:
            return None

        return Block.from_bytes(value)

    def create_state_hash(self, prefix: bytes=None) -> 'StateHash':
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

    def iterate_stake_part(self, cmp: callable) -> list:
        return self.iterate_db(StakePart.PREFIX, cmp)

    def iterate_db(self, prefix: bytes, cmp: callable) -> list:
        result = []

        if prefix is None:
            db = self._db
        else:
            db = self._db.prefixed_db(prefix)

        for key, value in db:
            address = Address.from_bytes_including_prefix(key)
            stake_part = StakePart.from_bytes(value)
            stake_part.set_complete(True)
            if cmp(stake_part):
                result.append((address, stake_part))

        return result

