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

import csv
import json
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
        parser.add_argument("--input", type=str, help="input file path", required=True)
        parser.add_argument("--output", type=str, help="output file path", required=True)
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        from_ = Address.from_string(args.from_)
        to = Address.from_string(args.to)
        start: int = args.start
        end: int = args.end
        input_path: str = args.input
        output_path: str = args.output

        tx_filter = MyFilter(from_, to)

        transaction_collector = TransactionCollector()
        transaction_collector.open(db_path)

        tx_it = transaction_collector.run(start, end, tx_filter)

        src = open(input_path, 'r', encoding='utf-8')
        dst = open(output_path, 'w', encoding='utf-8')
        rdr = csv.reader(src)
        wr = csv.writer(dst)

        for i, line in enumerate(rdr):
            if line[2] == "icx_sendTransaction":
                payload = json.loads(line[-1])
                timestamp = int(payload["params"]["timestamp"], 16)
                # add URL
                url = self._get_tracker_url(tx_it, timestamp)
                line.append(url)
            else:
                if i == 0:
                    line.append("Tracker URL")
                else:
                    line.append("N/A")
            wr.writerow(line)

        transaction_collector.close()
        src.close()
        dst.close()

    @staticmethod
    def _get_tracker_url(tx_it, timestamp: int) -> str:
        for tx, tx_result in tx_it:
            if tx.timestamp == timestamp:
                return f"https://tracker.icon.foundation/transaction/0x{tx.tx_hash.hex()}"

        return "N/A"

