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

from abc import ABCMeta, abstractmethod
from typing import List

from ..data.transaction import Transaction
from ..libs.block_database_raw_reader import BlockDatabaseRawReader
from ..libs.loopchain_block import LoopchainBlock


class TransactionFilter(metaclass=ABCMeta):
    @abstractmethod
    def run(self, tx: 'Transaction') -> bool:
        pass


class TransactionCollector(object):
    """Collect the transactions which satisfy a specific condition from loopchain DB

    """

    def __init__(self):
        self._reader = BlockDatabaseRawReader()

        self._start_block_height = -1
        self._end_block_height = -1
        self._transactions: List['Transaction'] = []

    @property
    def transactions(self) -> List['Transaction']:
        return self._transactions

    def __str__(self) -> str:
        return f"start_block_height: {self._start_block_height}\n" \
            f"end_block_height: {self._end_block_height}\n" \
            f"transactions: {len(self._transactions)}"

    def open(self, db_path: str):
        self.close()
        self._clear()
        self._reader.open(db_path)

    def run(self,
            start_block_height: int, end_block_height: int, tx_filter: 'TransactionFilter' = None):
        if start_block_height > end_block_height:
            raise ValueError(f"start_block_height({start_block_height}) > end_block_height({end_block_height})")

        self._transactions.clear()

        for block_height in range(start_block_height, end_block_height + 1):
            block_data: bytes = self._reader.get_block_by_height(block_height)
            if block_data is None:
                break

            block = LoopchainBlock.from_bytes(block_data)

            for tx_data in block.transactions:
                transaction = Transaction.from_bytes(tx_data)

                ret = tx_filter.run(transaction) if tx_filter else True
                if ret:
                    self._transactions.append(transaction)

        size = len(self._transactions)
        if size > 0:
            self._start_block_height = start_block_height
            self._end_block_height = self._start_block_height + len(self._transactions) - 1

    def close(self):
        self._reader.close()

    def _clear(self):
        self._start_block_height = -1
        self._end_block_height = -1
        self._transactions.clear()
