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
from typing import Iterable, Tuple

from ..data.transaction import Transaction
from ..data.transaction_result import TransactionResult
from ..libs.block_database_raw_reader import BlockDatabaseRawReader
from ..libs.loopchain_block import LoopchainBlock
from ..utils.convert_type import hex_to_bytes


class TransactionFilter(metaclass=ABCMeta):
    @abstractmethod
    def run(self, tx: "Transaction", tx_result: "TransactionResult") -> bool:
        pass


class TransactionCollector(object):
    """Collect the transactions which satisfy a specific condition from loopchain DB

    """

    def __init__(self):
        self._reader = BlockDatabaseRawReader()

        self._start_block_height = -1
        self._end_block_height = -1

    def __str__(self) -> str:
        return (
            f"start_block_height={self._start_block_height}"
            f"end_block_height={self._end_block_height}"
        )

    @property
    def start_block_height(self) -> int:
        return self._start_block_height

    @property
    def end_block_height(self) -> int:
        return self._end_block_height

    def open(self, db_path: str):
        self.close()
        self._clear()
        self._reader.open(db_path)

    def run(
        self,
        start_block_height: int,
        end_block_height: int,
        tx_filter: "TransactionFilter" = None,
    ) -> Iterable[Tuple["Transaction", "TransactionResult"]]:
        """

        :param start_block_height:
        :param end_block_height: -1 means the last block
        :param tx_filter:
        :return:
        """
        if start_block_height > end_block_height:
            raise ValueError(
                f"start_block_height({start_block_height}) > end_block_height({end_block_height})"
            )

        self._start_block_height = start_block_height

        block_height = start_block_height
        print(f"BH-{block_height}")

        while True:
            if -1 < end_block_height < block_height:
                break

            block_data: bytes = self._reader.get_block_by_height(block_height)
            if block_data is None:
                break

            if block_height % 1000 == 0:
                print(f"BH-{block_height}")

            block = LoopchainBlock.from_bytes(block_data)

            for tx_data in block.transactions:
                # Skip base transactions
                if "from" not in tx_data:
                    continue

                tx = Transaction.from_dict(tx_data)
                tx_result = self._get_transaction_result(tx.tx_hash)

                ret = tx_filter.run(tx, tx_result) if tx_filter else True
                if ret:
                    yield tx, tx_result

            block_height += 1

        self._end_block_height = block_height - 1

    def run_with_file(self, path: str):
        with open(path, mode="r") as f:
            for line in f:
                line: str = line.strip(" \t\n")
                if line.startswith("#"):
                    continue

                tx_hash = hex_to_bytes(line)
                data: bytes = self._reader.get_transaction_by_hash(tx_hash)
                if data is None:
                    break

                tx = Transaction.from_bytes(data)
                tx_result = TransactionResult.from_bytes(data)
                yield tx, tx_result

    def _get_transaction_result(self, tx_hash: bytes) -> "TransactionResult":
        data: bytes = self._reader.get_transaction_result_by_hash(tx_hash)
        assert isinstance(data, bytes)

        return TransactionResult.from_bytes(data)

    def close(self):
        self._reader.close()

    def _clear(self):
        self._start_block_height = -1
        self._end_block_height = -1
