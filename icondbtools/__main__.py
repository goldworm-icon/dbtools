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
from pprint import pprint

from icondbtools.command.command_account import CommandAccount
from icondbtools.command.command_balance import CommandBalance
from icondbtools.command.command_block import CommandBlock
from icondbtools.command.command_clear import CommandClear
from icondbtools.command.command_copy import CommandCopy
from icondbtools.command.command_dbinfo import CommandDbinfo
from icondbtools.command.command_iiss_data import CommandIISSData
from icondbtools.command.command_iiss_tx_data import CommandIISSTXData
from icondbtools.command.command_invalidtx import CommandInvalidTx
from icondbtools.command.command_lastblock import CommandLastBlock
from icondbtools.command.command_statehash import CommandStateHash
from icondbtools.command.command_statelastblock import CommandStateLastBlock
from icondbtools.command.command_sync import CommandSync
from icondbtools.command.command_term import CommandTerm
from icondbtools.command.command_token import CommandToken
from icondbtools.command.command_tps import CommandTps
from icondbtools.command.command_txresult import CommandTxResult
from icondbtools.libs.timer import Timer
from icondbtools.utils import get_dbtools_version


def main():
    commands = [
        CommandSync,
        CommandLastBlock,
        CommandBlock,
        CommandClear,
        CommandTxResult,
        CommandStateHash,
        CommandStateLastBlock,
        CommandAccount,
        CommandTps,
        CommandToken,
        CommandInvalidTx,
        CommandDbinfo,
        CommandIISSData,
        CommandIISSTXData,
        CommandCopy,
        CommandTerm,
        CommandBalance
    ]

    version = get_dbtools_version()
    parser = argparse.ArgumentParser(prog='icondbtools', description=f'icon db tools v{version}')

    sub_parser = parser.add_subparsers(title='subcommands')
    common_parser = create_common_parser()

    for command in commands:
        command(sub_parser, common_parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args()
    pprint(args)

    timer = Timer()
    timer.start()
    ret: int = args.func(args)
    timer.stop()
    print(f'elapsedTime: {timer.duration()} seconds')

    return ret


def create_common_parser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--db",
        type=str,
        required=True,
    )

    return parent_parser


if __name__ == '__main__':
    exit_code: int = main()
    sys.exit(exit_code)
