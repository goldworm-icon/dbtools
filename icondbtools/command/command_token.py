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

from iconservice.base.address import Address
from iconservice.utils import int_to_bytes

from icondbtools.command.command import Command
from icondbtools.libs.score_database_manager import ScoreDatabaseManager


class CommandToken(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "token"
        desc = (
            "Read a token balance from IRC2 Standard Token SCORE and "
            "Write a new balance to StateDB for IRC2 Standard Token SCORE"
        )

        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument(
            "--score",
            type=str,
            required=True,
            help="score address ex) cx63af7f2e073985a9e9965765e809f66da3b0f238",
        )
        parser.add_argument(
            "--user",
            type=str,
            required=True,
            help="user address ex) hxd7cf2f6bcbbfa542a08e9cd0e48bf848018a2ec7",
        )
        parser.add_argument(
            "--balance",
            type=int,
            default=-1,
            required=False,
            help="token balance to write. ex) 100",
        )
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        score_address: "Address" = Address.from_string(args.score)
        address: "Address" = Address.from_string(args.user)
        balance: int = args.balance
        # Name of DictDB in Standard Token
        name: str = "balances"

        manager = ScoreDatabaseManager()
        manager.open(db_path, score_address)

        if balance < 0:
            value: bytes = manager.read_from_dict_db(name, address)
            balance: int = int.from_bytes(value, "big")
            print(f"token balance: {balance}")
        else:
            value: bytes = int_to_bytes(balance)
            manager.write_to_dict_db(name, address, value)

        manager.close()
