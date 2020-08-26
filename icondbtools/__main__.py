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

from icondbtools.command.command_total_balance import CommandTotalBalance

from .__about__ import version, name
from .command.command_account import CommandAccount
from .command.command_balance import CommandBalance
from .command.command_block import CommandBlock
from .command.command_cdb import CommandCDB
from .command.command_clear import CommandClear
from .command.command_copy import CommandCopy
from .command.command_dbinfo import CommandDbinfo
from .command.command_fastsync import CommandFastSync
from .command.command_iiss_data import CommandIISSData
from .command.command_iiss_tx_data import CommandIISSTXData
from .command.command_invalidtx import CommandInvalidTx
from .command.command_lastblock import CommandLastBlock
from .command.command_migrate import CommandMigrate
from .command.command_statehash import CommandStateHash
from .command.command_statelastblock import CommandStateLastBlock
from .command.command_sync import CommandSync
from .command.command_term import CommandTerm
from .command.command_token import CommandToken
from .command.command_tps import CommandTps
from .command.command_txresult import CommandTxResult
from .command.command_transactions import CommandTransactions
from .utils.timer import Timer


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
        CommandBalance,
        CommandTransactions,
        CommandTotalBalance,

        # Commands for compact db
        CommandCDB,
        CommandMigrate,
        CommandFastSync,
    ]

    parser = argparse.ArgumentParser(prog=name, description=f"{name}-{version}")

    sub_parser = parser.add_subparsers(title="subcommands")
    common_parser = create_common_parser()

    for command in commands:
        command(sub_parser, common_parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args()
    # pprint(args)

    timer = Timer()
    timer.start()
    ret: int = args.func(args)
    timer.stop()
    print(f"elapsedTime: {timer.duration()} seconds")

    return ret


def create_common_parser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--db", type=str, required=True,
    )

    return parent_parser


if __name__ == "__main__":
    exit_code: int = main()
    sys.exit(exit_code)
