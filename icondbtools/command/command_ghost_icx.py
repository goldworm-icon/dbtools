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

from .command import Command
from ..ghost_icx.ghost_icx_inspector import GhostICXInspector

if TYPE_CHECKING:
    pass


class CommandGhostICX(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "ghosticx"
        desc = (
            "Print the information about invisible ghost icx for given addresses, "
            "inspecting state-db"
        )

        # create the parser for account
        parser_account = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_account.add_argument(
            "--addresses",
            type=str,
            required=True,
            help="filepath containing addresses to inspect"
        )
        parser_account.set_defaults(func=self.run)

    def run(self, args):
        """Print the account info of a given address

        :param args:
        :return:
        """
        db_path: str = args.db
        path: str = args.addresses

        inspector = GhostICXInspector()
        inspector.open(db_path)
        inspector.run(path)
        inspector.close()
