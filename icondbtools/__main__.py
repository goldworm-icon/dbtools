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


def run_last_block(args):
    if args.help:
        print(f'{sys.argv[0]} {args.command}')


def validate_icon_service(loopchain_db_path: str):
    loopchain_db_path = './data/testnet_db'
    builtin_score_owner = 'hx677133298ed5319607a321a38169031a8867085c'

    executor = IconServiceValidator()
    executor.open(builtin_score_owner=builtin_score_owner)
    executor.run(loopchain_db_path, 0, 2)
    executor.close()


def main():
    """
    command_handlers = {
        'lastblock': run_last_block
    }

    parser = argparse.ArgumentParser(
        prog='icondbtools',
        description='icon db tools')
    parser.add_argument(
        'command',
        help='blockbyheight blockbyhash lastblock stateroothash',
        required=True)

    args = parser.parse_args()

    command_handler = command_handlers[args.command]
    if command_handler:
        command_handler(args)
    """
    validate_icon_service()


if __name__ == '__main__':
    main()
