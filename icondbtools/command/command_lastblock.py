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

from pprint import pprint

from icondbtools.command.command import Command
from icondbtools.libs.block_database_reader import BlockDatabaseReader


class CommandLastBlock(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'lastblock'
        desc = 'Print the last block in block db'

        # create the parser for lastblock
        parser_last_block = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_last_block.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db

        block_reader = BlockDatabaseReader()
        block_reader.open(db_path)
        block: dict = block_reader.get_last_block()
        block_reader.close()

        pprint(block)

