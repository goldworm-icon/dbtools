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

import argparse
import sys

from .icon_service_validator import IconServiceValidator
from .block_reader import BlockReader

def print_last_block(args):
    db_path: str = args.db

    block_reader = BlockReader()
    block_reader.open(db_path)
    block: dict = block_reader.get_last_block()
    block_reader.close()

    print(block)


def print_block(args):
    db_path: str = args.db
    height: int = args.height

    block_reader = BlockReader()
    block_reader.open(db_path)
    block: dict = block_reader.get_block_hash_by_block_height(height)
    block_reader.close()

    print(block)


def sync(args):
    db_path: str = args.db
    start: int = args.start
    count: int = args.count
    builtin_score_owner = 'hx677133298ed5319607a321a38169031a8867085c'

    print(f'loopchain_db_path: {db_path}\n'
          f'start: {start}\n'
          f'count: {count}')

    validator = IconServiceValidator()
    validator.open(builtin_score_owner=builtin_score_owner)
    validator.run(db_path, start_height=start, count=count)
    validator.close()


def main():
    parser = argparse.ArgumentParser(prog='icondbtools', description='icon db tools')

    subparsers = parser.add_subparsers(title='subcommands')

    # create the parser for the 'sync' command
    parser_sync = subparsers.add_parser('sync')
    parser_sync.add_argument('--db', type=str, required=True)
    parser_sync.add_argument('-s', '--start', type=int, default=0, help='start height to sync')
    parser_sync.add_argument('-c', '--count', type=int, default=999999999, help='The number of blocks to sync')
    # parser_sync.add_argument('--stop_on_error', action='store_true')
    parser_sync.set_defaults(func=sync)

    # create the parser for lastblock
    parser_last_block = subparsers.add_parser('lastblock')
    parser_last_block.add_argument('--db', type=str, required=True)
    parser_last_block.set_defaults(func=print_last_block)

    # create the parser for block
    parser_block = subparsers.add_parser('block')
    parser_block.add_argument('--db', type=str, required=True)
    parser_block.add_argument('--height', type=int, default=0, help='start height to sync', required=True)
    parser_block.set_defaults(func=print_block)

    args = parser.parse_args()
    print(args)
    args.func(args)


if __name__ == '__main__':
    main()
