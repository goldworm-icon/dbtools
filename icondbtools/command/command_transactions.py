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

from typing import TYPE_CHECKING

from iconservice.base.address import Address

from ..command.command import Command
from ..libs.transaction_collector import TransactionCollector, TransactionFilter

if TYPE_CHECKING:
    from ..data.transaction import Transaction
    from ..data.transaction_result import TransactionResult


class MyFilter(TransactionFilter):
    def __init__(self, from_: Address, to: Address):
        self._from = from_
        self._to = to

    def run(self, tx: "Transaction", tx_result: "TransactionResult") -> bool:
        return tx.from_ == self._from or tx.to == self._to


class CommandTransactions(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "txs"
        desc = "Collect the transactions which satisfy a specific condition"

        # create the parser for txresult
        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument("--from", dest="from_", required=True)
        parser.add_argument("--to", dest="to", required=True)
        parser.add_argument("--start", type=int, dest="start", help="start BH", required=True)
        parser.add_argument("--end", type=int, dest="end", help="end BH", required=True)
        parser.add_argument("--output", type=str, help="output file path", required=True)
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        from_ = Address.from_string(args.from_)
        to = Address.from_string(args.to)
        start: int = args.start
        end: int = args.end
        path: str = args.output

        tx_filter = MyFilter(from_, to)

        transaction_collector = TransactionCollector()
        transaction_collector.open(db_path)

        it = transaction_collector.run(start, end, tx_filter)

        size = 0
        with open(path, "wt") as f:
            for tx, tx_result in it:
                f.write(f"0x{tx.tx_hash.hex()}\n")
                size += 1

        transaction_collector.close()
        print(f"tx_count: {size}")
