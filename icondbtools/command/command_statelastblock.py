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

from datetime import datetime
from typing import TYPE_CHECKING

from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader

if TYPE_CHECKING:
    from iconservice.base.block import Block


class CommandStateLastBlock(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "statelastblock"
        desc = "Print the information of last block commited to statedb"

        # create the parser for statelastblock
        parser_state_last_block = sub_parser.add_parser(
            name, parents=[common_parser], help=desc
        )
        parser_state_last_block.set_defaults(func=self.run)

    def run(self, args):
        """Read the last block from statedb

        :param args:
        :return:
        """
        db_path: str = args.db
        reader = StateDatabaseReader()

        try:
            reader.open(db_path)

            block: "Block" = reader.get_last_block()

            print(
                f"height: {block.height}\n"
                f"timestamp: {block.timestamp} "
                f"({datetime.fromtimestamp(block.timestamp / 10 ** 6)})\n"
                f"prev_hash: 0x{block.prev_hash.hex()}\n"
                f"block_hash: 0x{block.hash.hex()}"
            )
        finally:
            reader.close()
