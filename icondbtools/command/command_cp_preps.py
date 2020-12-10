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
from ..migrate.block_migrator import BlockMigrator


class CommandCopyPReps(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "cp_preps"
        desc = "copy preps data from src_db to dest_db"

        # create the parser for the 'sync' command
        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument(
            "--new-db", type=str, default="", help="new DB path for blocks to be copied"
        )
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        new_db_path: str = args.new_db

        block_migrator = BlockMigrator()
        block_migrator.open(db_path, new_db_path)
        block_migrator.cp_preps()
        block_migrator.close()
