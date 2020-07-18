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

from .command import Command
from ..fastsync.block_reader import BlockDatabaseReader
from ..migrate.block import Block
from ..utils.convert_type import hex_to_bytes


class CommandCDB(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "cdb"
        desc = "Print details of compact db"

        # create the parser for block
        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument(
            "--block-height",
            type=int,
            required=False,
            help="Print block indicated by a given height",
        )
        parser.add_argument(
            "--block-hash",
            type=hex_to_bytes,
            required=False,
            help="Print block indicated by a given hash",
        )
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db

        block_reader = BlockDatabaseReader()
        try:
            block_reader.open(db_path)

            self.print_block_range(block_reader)

            if hasattr(args, "block_height") and isinstance(args.block_height, int):
                self._print_block_by_height(block_reader, args.block_height)
            elif hasattr(args, "block_hash") and isinstance(args.block_hash, bytes):
                self._print_block_by_hash(block_reader, args.block_hash)

        finally:
            block_reader.close()

    @classmethod
    def print_block_range(cls, block_reader: BlockDatabaseReader):
        start_height: int = block_reader.get_start_block_height()
        end_height: int = block_reader.get_end_block_height()
        print(f"block range: {start_height} ~ {end_height}")

    @classmethod
    def _print_block_by_height(
        cls, block_reader: BlockDatabaseReader, block_height: int
    ):
        block = block_reader.get_block_by_height(block_height)
        cls._print_block(block)

    @classmethod
    def _print_block_by_hash(cls, block_reader: BlockDatabaseReader, block_hash: bytes):
        block = block_reader.get_block_by_hash(block_hash)
        cls._print_block(block)

    @classmethod
    def _print_block(cls, block: Block):
        print(block)
