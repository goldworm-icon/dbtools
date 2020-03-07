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
from typing import Optional

import plyvel

from icondbtools.command.command import Command
from icondbtools.libs import NID_KEY, TRANSACTION_COUNT_KEY, LAST_BLOCK_KEY, PREPS_KEY_PREFIX, ZERO_HASH, UTF8
from icondbtools.libs.block_database_raw_reader import BlockDatabaseRawReader, TransactionParser


class CommandCopy(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'copy'
        desc = 'Copy Loopchain blocks from start height and end height to target DB path'

        parser_copy = sub_parser.add_parser(name, parents=[common_parser], help=desc)

        parser_copy.add_argument('-s', '--start', type=int, default=-1, help='start block height to be copied')
        parser_copy.add_argument('--end', type=int, default=-1, help='end block height to be copied, inclusive')
        parser_copy.add_argument('--count', type=int, default=-1, help='block count to be copied')
        parser_copy.add_argument('--new-db', type=str, default="", help='new DB path for blocks to be copied')
        parser_copy.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        start: int = args.start
        end: int = args.end
        count: int = args.count
        new_db_path: str = args.new_db

        if end > -1:
            if end < start:
                raise ValueError(f'end({end} < start({start})')
            count = max(count, end - start + 1)
        elif count == -1:
            count = 999999999

        block_reader = BlockDatabaseRawReader()
        block_reader.open(db_path)
        new_db = plyvel.DB(new_db_path, create_if_missing=True)
        block: Optional[bytes] = None

        with new_db.write_batch() as wb:
            for height in range(start, start + count):
                block_height_key: bytes = block_reader.get_block_height_key(height)
                block: bytes = block_reader.get_block_by_height(height)

                if block is None:
                    break

                # Get transaction data from the DB using transactions in block
                transactions: list = block_reader.get_transactions_from_block(block)
                for transaction in transactions:
                    tx_hash_key: Optional[bytes] = TransactionParser.get_tx_hash_key_from_transaction(transaction)
                    if tx_hash_key is not None:
                        full_transaction: bytes = block_reader.get_transaction_by_key(tx_hash_key)
                        wb.put(tx_hash_key, full_transaction)

                block_hash_key: bytes = block_reader.get_block_hash_key_by_height(height)
                wb.put(block_hash_key, block)
                wb.put(block_height_key, block_hash_key)
                block_dict: dict = json.loads(block)
                reps_hash: str = block_dict.get("repsHash", "0x")[2:]
                reps_data = block_reader.get_reps(bytes.fromhex(reps_hash))
                reps_data = reps_data.decode(UTF8)
                wb.put(PREPS_KEY_PREFIX + reps_hash.encode(UTF8), json.dumps(reps_data).encode(UTF8))
                next_reps_hash = block_dict.get("nextRepsHash")
                if next_reps_hash != ZERO_HASH:
                    next_reps_hash = bytes.fromhex(next_reps_hash[2:])
                    reps_data = block_reader.get_reps(next_reps_hash)
                    wb.put(PREPS_KEY_PREFIX + next_reps_hash, reps_data)
            if block is not None:
                wb.put(NID_KEY, block_reader.get_nid())
                wb.put(TRANSACTION_COUNT_KEY, block_reader.get_transaction_count())
                block: dict = json.loads(block)
                last_block_hash: str = block.get('block_hash') if 'block_hash' in block \
                    else block.get("hash")[2:]
                wb.put(LAST_BLOCK_KEY, last_block_hash.encode(UTF8))
        block_reader.close()
