# -*- coding: utf-8 -*-
# Copyright 2018 theloop Inc.
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

from .block_database_reader import BlockDatabaseReader


class InvalidTransactionChecker(object):
    """Check whether the transactions which are processed without charged fee are present or not

    """
    def __init__(self):
        self._block_reader = BlockDatabaseReader()

    def open(self, db_path: str):
        self._block_reader.open(db_path)

    def run(self, start: int, end: int):
        tx_count: int = 0

        if end < 0:
            last_block: dict = self._block_reader.get_last_block()
            end: int = last_block['height']

        for height in range(start, end + 1):
            block: dict = self._block_reader.get_block_by_block_height(height)

            tx_list: list = block['confirmed_transaction_list']
            for tx in tx_list:
                tx_hash: str = tx.get('txHash')
                if tx_hash is None:
                    tx_hash: str = tx['tx_hash']

                self._check_invalid_tx_result(height, tx_hash)
                tx_count += 1

        print(f'The number of transactions: {tx_count}')

    def _check_invalid_tx_result(self, height: int, tx_hash: str):
        tx_result: dict = self._block_reader.get_transaction_result_by_hash(tx_hash)['result']

        # information extracted from db
        status: int = int(tx_result['status'], 16)
        step_used: int = int(tx_result['stepUsed'], 16)
        step_price: int = int(tx_result['stepPrice'], 16)
        step = step_used * step_price

        if status == 1 and step == 0:
            print(f'{height}: txHash({tx_hash}) stepUsed({step_used}) stepPrice({step_price})')

    def close(self):
        self._block_reader.close()
