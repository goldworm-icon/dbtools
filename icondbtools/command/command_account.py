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

from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader
from iconservice.base.address import Address

if TYPE_CHECKING:
    from iconservice.icx.icx_account import Account


class CommandAccount(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'account'
        desc = 'Print the information of the account indicated by an address'

        # create the parser for account
        parser_account = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_account.add_argument(
            '--address', type=str, required=True,
            help='EOA or SCORE address. ex) hx21a0f22e65ad8cd76c282b8b7fb35ba0368aa9bd')
        parser_account.set_defaults(func=self.run)

    def run(self, args):
        """Print the account info of a given address

        :param args:
        :return:
        """
        db_path: str = args.db
        address: 'Address' = Address.from_string(args.address)
        reader = StateDatabaseReader()

        try:
            reader.open(db_path)

            account: 'Account' = reader.get_account(address)
            if account is None:
                print(f"Account not found: {address}")
            else:
                print(f"address: {account.address}\n"
                      f"amount: {account.balance / 10 ** 18} in icx\n"
                      f"stake: {account.stake}\n")
        finally:
            reader.close()
