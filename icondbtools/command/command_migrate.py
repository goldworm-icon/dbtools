# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
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

from typing import Tuple

from icondbtools.command.command import Command
from ..migrate.BlockMigrator import BlockMigrator


class CommandMigrate(Command):

    MAX_COPY_BLOCK_COUNT = 999_999_999

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "migrate"
        desc = (
            "Convert loopchain blocks between start and end BH to binary blocks, "
            "writing them to target db"
        )

        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)

        parser.add_argument(
            "-s",
            "--start",
            type=int,
            default=-1,
            help="start block height to be copied",
        )
        parser.add_argument(
            "--end",
            type=int,
            default=-1,
            help="end block height to be copied, inclusive",
        )
        parser.add_argument(
            "--count", type=int, default=-1, help="block count to be copied"
        )
        parser.add_argument(
            "--new-db", type=str, default="", help="new DB path for blocks to be copied"
        )
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        start: int = args.start
        end: int = args.end
        count: int = args.count
        new_db_path: str = args.new_db

        start, end = self._get_copy_block_range(start, end, count)

        block_migrator = BlockMigrator()
        block_migrator.open(db_path, new_db_path)
        block_migrator.run(start, end)
        block_migrator.close()

    @classmethod
    def _get_copy_block_range(cls, start: int, end: int, count: int) -> Tuple[int, int]:
        """
        :return: start block and end block height, exclusive
        """
        if end > -1:
            if end < start:
                raise ValueError(f"end({end} < start({start})")
            count = max(count, end - start + 1)
        elif count == -1:
            count = cls.MAX_COPY_BLOCK_COUNT

        return start, start + count
