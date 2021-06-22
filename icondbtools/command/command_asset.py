# -*- coding: utf-8 -*-
# Copyright 2021 ICON Foundation Inc.
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
from typing import TYPE_CHECKING

from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader
from iconservice.base.address import Address

if TYPE_CHECKING:
    from iconservice.icx.icx_account import Account


class CommandAsset(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "asset"
        desc = "Print expired unstake + balance of the account indicated by an address"

        # create the parser for account
        parser_account = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_account.add_argument(
            "--path",
            type=str,
            required=True,
            help="json file path include addresses",
        )
        parser_account.add_argument(
            "--out",
            type=str,
            required=True,
            help="json file path to write result",
        )
        parser_account.set_defaults(func=self.run)

    def run(self, args):
        """Print the account info of a given address

        :param args:
        :return:
        """
        db_path: str = args.db
        path: str = args.path
        with open(path, 'r') as f:
            addresses = json.load(f)
        reader = StateDatabaseReader()

        try:
            reader.open(db_path)
            block = reader.get_last_block()
            print(f"BH: {block.height}")
            contents = {}
            for address in addresses:
                account: "Account" = reader.get_account(
                    Address.from_string(address), reader.get_last_block().height, 10)
                if account is None:
                    print(f"Account not found: {address}")
                else:
                    expired_usntakes = sum((u[0] for u in account.unstakes_info if block.height > u[1]))
                    s = expired_usntakes + account.balance
                    print(f"{address}'s balance in ICON2:", s)
                    contents[address] = s
            with open(args.out, 'w') as f:
                json.dump(contents, f, indent=4)
        finally:
            reader.close()
