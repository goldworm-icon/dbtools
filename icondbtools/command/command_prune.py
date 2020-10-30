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

from icondbtools.command.command import Command
from icondbtools.libs.prune_database import PruneDatabase


class CommandPrune(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "prune"
        desc = "Prune Block DB for AWS snapshot upload"

        # create the parser for block
        parser_block = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_block.add_argument(
            "-d",
            dest="debug_prt",
            help="Debug dest database for string",
            action='store_true',
        )
        parser_block.add_argument(
            "-b",
            dest="remain_blocks",
            type=int,
            help="Prune LastBlock - remain_blocks",
            default=86400
        )
        parser_block.add_argument(
            "--dest",
            type=str,
            help="Dest new database path",
            required=True,
        )

        parser_block.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        dest_path: str = args.dest
        remain_blocks: int = args.remain_blocks
        debug_prt: bool = args.debug_prt

        prune_db = PruneDatabase(
            db_path=db_path,
            dest_path=dest_path,
            remain_blocks=remain_blocks
        )
        prune_db.ready_make()
        prune_db.make_v1()
        prune_db.clear()

        if debug_prt:
            prune_db.debug_prt(dest_path)
