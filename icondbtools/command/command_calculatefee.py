# -*- coding: utf-8 -*-
# Copyright 2020 ICON Foundation Inc.
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

from icondbtools.command.command import Command
from icondbtools.libs.block_database_reader import BlockDatabaseReader

IGNORE_DATA_TYPES = ("base", )
TX_KEY = "transactions"
OLD_TX_KEY = "confirmed_transaction_list"


class CommandCalculateFee(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "calcfee"
        desc = "calculate fee while given period"

        # create the parser for calcFee
        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument(
            "--start", dest="start", help="start block height", required=True, type=int, default=-1)
        parser.add_argument(
            "--end", dest="end", help="end block height", required=True, type=int, default=-1)
        parser.add_argument(
            "--print-detail", dest="detail_flag", help="print detail flag", action="store_true"
        )
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        start: int = args.start
        end: int = args.end
        detail_flag: bool = args.detail_flag
        total_fee: int = 0

        block_reader = BlockDatabaseReader()
        block_reader.open(db_path)

        if start < 0:
            last_block = block_reader.get_last_block()
            start = last_block.height["height"]
        if end < start:
            raise ValueError(f'end({end} < start({start})')

        for height in range(start, end+1):
            block = block_reader.get_block_by_block_height(height)
            txs = block.get(TX_KEY)
            txs = txs if txs is not None else block.get(OLD_TX_KEY)
            for tx in txs:
                if tx.get("dataType") in IGNORE_DATA_TYPES:
                    continue
                tx_hash = tx.get("txHash")
                tx_hash = tx_hash if tx_hash is not None else tx.get("tx_hash")
                tx_result = block_reader.get_transaction_result_by_hash(tx_hash)["result"]
                step_used: str = tx_result.get("stepUsed", 0)
                step_price: str = tx_result.get("stepPrice", 0)
                step_used: int = int(step_used, 0)
                step_price: int = int(step_price, 0)
                total_fee += step_used * step_price
                if detail_flag:
                    print(f"TxHash : {tx_hash} | \t"
                          f"BH : {height} \t"
                          f"stepUsed : {step_used} | \t"
                          f"stepPrice: {step_price} | \t"
                          f"accumulatedFee : {total_fee}")
        print(f"total fee in {start} - {end} is {total_fee}")
