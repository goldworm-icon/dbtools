# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
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

import json
from typing import Optional, Tuple

import plyvel

from icondbtools.command.command import Command
from icondbtools.libs import (
    NID_KEY,
    TRANSACTION_COUNT_KEY,
    LAST_BLOCK_KEY,
    PREPS_KEY_PREFIX,
    ZERO_HASH,
    UTF8,
)
from icondbtools.libs.block_database_raw_reader import (
    BlockDatabaseRawReader,
    TransactionParser,
)
from icondbtools.migrate.block_migrator import make_preps_key
from icondbtools.migrate.preps import PReps


class CommandCopy(Command):

    MAX_COPY_BLOCK_COUNT = 999_999_999

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "copy"
        desc = (
            "Copy Loopchain blocks from start height and end height to target DB path"
        )

        parser_copy = sub_parser.add_parser(name, parents=[common_parser], help=desc)

        parser_copy.add_argument(
            "-s",
            "--start",
            type=int,
            default=-1,
            help="start block height to be copied",
        )
        parser_copy.add_argument(
            "--end",
            type=int,
            default=-1,
            help="end block height to be copied, inclusive",
        )
        parser_copy.add_argument(
            "--count", type=int, default=-1, help="block count to be copied"
        )
        parser_copy.add_argument(
            "--new-db", type=str, default="", help="new DB path for blocks to be copied"
        )
        parser_copy.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        start: int = args.start
        end: int = args.end
        count: int = args.count
        new_db_path: str = args.new_db

        start, end = self._get_copy_block_range(start, end, count)

        block_reader = BlockDatabaseRawReader()
        block_reader.open(db_path)
        new_db = plyvel.DB(new_db_path, create_if_missing=True)

        last_block: Optional[bytes] = None
        height = start
        wb_size = 1000

        while height < end:
            with new_db.write_batch() as wb:
                # Write batch_data to leveldb every 10000 blocks
                for _ in range(wb_size):
                    block: bytes = block_reader.get_block_by_height(height)
                    if block is None:
                        height = end
                        break

                    # Copy a block data from source db to target db
                    self._copy_block(wb, block_reader, block, height)

                    height += 1
                    last_block = block

            # Display copy progress status
            print(".", end="", flush=True)

        if last_block:
            with new_db.write_batch() as wb:
                self._copy_stats(wb, block_reader, last_block)

        block_reader.close()

    @classmethod
    def _copy_block(cls, wb, block_reader, block: bytes, height: int):
        cls._write_transactions(wb, block_reader, block)
        cls._write_block(wb, block_reader, block, height)
        cls._write_reps_data(wb, block_reader, block)

    @classmethod
    def _write_transactions(cls, wb, block_reader, block):
        # Get transaction data from the DB using transactions in block
        transactions: list = block_reader.get_transactions_from_block(block)
        for transaction in transactions:
            tx_hash_key: Optional[
                bytes
            ] = TransactionParser.get_tx_hash_key_from_transaction(transaction)
            if tx_hash_key is not None:
                full_transaction: bytes = block_reader.get_transaction_by_key(
                    tx_hash_key
                )
                wb.put(tx_hash_key, full_transaction)

    @classmethod
    def _write_block(cls, wb, block_reader, block: bytes, height: int):
        block_height_key: bytes = block_reader.get_block_height_key(height)
        block_hash_key: bytes = block_reader.get_block_hash_key_by_height(height)
        wb.put(block_hash_key, block)
        wb.put(block_height_key, block_hash_key)

    @classmethod
    def _write_reps_data(cls, wb, block_reader, block: bytes):
        reps_data: dict = block_reader.get_reps_data()
        for key, value in reps_data.items():
            wb.put(key, value)

    @classmethod
    def _copy_stats(cls, wb, block_reader, last_block: bytes):
        # Copy nid
        nid_data: bytes = block_reader.get_nid()
        if nid_data:
            wb.put(NID_KEY, nid_data)

        # Copy transaction count
        transaction_count_data: bytes = block_reader.get_transaction_count()
        if transaction_count_data:
            wb.put(TRANSACTION_COUNT_KEY, transaction_count_data)

        # Copy last_block_hash
        block: dict = json.loads(last_block)
        last_block_hash: str = block.get(
            "block_hash"
        ) if "block_hash" in block else block.get("hash")[2:]
        wb.put(LAST_BLOCK_KEY, last_block_hash.encode(UTF8))

    @classmethod
    def _get_copy_block_range(cls, start: int, end: int, count: int) -> Tuple[int, int]:
        """
        :return: start block and end block height, exclusive
        """
        if end > -1:
            if end < start:
                raise ValueError(f"end({end} < start({start})")
            count = max(count, end - start + 1)
        elif count == -1:
            count = cls.MAX_COPY_BLOCK_COUNT

        return start, start + count
