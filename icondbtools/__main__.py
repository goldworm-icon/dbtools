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
import shutil
import sys
from datetime import datetime

from iconservice.base.address import Address
from iconservice.utils import int_to_bytes
from .block_database_reader import BlockDatabaseReader
from .icon_service_syncer import IconServiceSyncer
from .invalid_transaction_checker import InvalidTransactionChecker
from .state_database_reader import StateDatabaseReader, StateHash
from .tps_calculator import TPSCalculator
from .score_database_manager import ScoreDatabaseManager
from .timer import Timer


def print_last_block(args):
    db_path: str = args.db

    block_reader = BlockDatabaseReader()
    block_reader.open(db_path)
    block: dict = block_reader.get_last_block()
    block_reader.close()

    print(block)


def print_block(args):
    db_path: str = args.db
    height: int = args.height
    block_hash: str = args.hash

    block_reader = BlockDatabaseReader()
    block_reader.open(db_path)

    if block_hash is not None:
        block: dict = block_reader.get_block_by_block_hash(block_hash)
    else:
        block: dict = block_reader.get_block_by_block_height(height)
    block_reader.close()

    print(block)


def print_transaction_result(args):
    db_path: str = args.db
    tx_hash: str = args.tx_hash

    block_reader = BlockDatabaseReader()
    block_reader.open(db_path)
    tx_result: dict = block_reader.get_transaction_result_by_hash(tx_hash)
    block_reader.close()

    print(tx_result)


def sync(args):
    db_path: str = args.db
    start: int = args.start
    end: int = args.end
    count: int = args.count
    stop_on_error: bool = args.stop_on_error
    no_commit: bool = args.no_commit
    write_precommit_data: bool = args.write_precommit_data
    builtin_score_owner: str = args.builtin_score_owner
    fee: bool = not args.no_fee
    audit: bool = not args.no_audit
    deployer_whitelist: bool = args.deployer_whitelist
    score_package_validator: bool = args.score_package_validator
    channel: str = args.channel

    # If --start option is not present, set start point to the last block height from statedb
    if start < 0:
        try:
            state_db_path = '.statedb/icon_dex'
            reader = StateDatabaseReader()
            reader.open(state_db_path)
            block: 'Block' = reader.get_last_block()
            start = block.height + 1
        except:
            start = 0
        finally:
            reader.close()

    if end > -1:
        if end < start:
            raise ValueError(f'end({end} < start({start})')
        count: int = end - start + 1

    print(f'loopchain_db_path: {db_path}\n'
          f'start: {args.start}, {start}\n'
          f'end: {end}\n'
          f'count: {count}\n'
          f'fee: {fee}\n'
          f'audit: {audit}\n'
          f'deployerWhitelist: {deployer_whitelist}\n'
          f'scorePackageValidator: {score_package_validator}\n')

    syncer = IconServiceSyncer()
    syncer.open(
        fee=fee,
        audit=audit,
        deployer_whitelist=deployer_whitelist,
        score_package_validator=score_package_validator,
        builtin_score_owner=builtin_score_owner)
    ret: int = syncer.run(
        db_path, channel, start_height=start, count=count,
        stop_on_error=stop_on_error, no_commit=no_commit,
        write_precommit_data=write_precommit_data)
    syncer.close()

    return ret


def clear(args):
    """Clear .score and .statedb

    :param args:
    :return:
    """
    paths = ['.score', '.statedb']
    for path in paths:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass


def run_command_state_hash(args):
    """Create hash from state db

    :param args:
    :return:
    """
    db_path: str = args.db
    prefix: str = args.prefix

    reader = StateDatabaseReader()
    reader.open(db_path)

    # convert hexa string to bytes
    if prefix is not None:
        if prefix.startswith('0x'):
            prefix = prefix[2:]

        prefix: bytes = bytes.fromhex(prefix)

    state_hash: 'StateHash' = reader.create_state_hash(prefix)
    reader.close()

    print(state_hash)


def run_command_state_last_block(args):
    """Read the last block from statedb

    :param args:
    :return:
    """
    db_path: str = args.db

    try:
        reader = StateDatabaseReader()
        reader.open(db_path)

        block: 'Block' = reader.get_last_block()

        print(f'height: {block.height}\n'
              f'timestamp: {block.timestamp} '
              f'({datetime.fromtimestamp(block.timestamp / 10 ** 6)})\n'
              f'prev_hash: 0x{block.prev_hash.hex()}\n'
              f'block_hash: 0x{block.hash.hex()}')
    finally:
        reader.close()


def run_command_account(args):
    """Print the account info of a given address

    :param args:
    :return:
    """
    db_path: str = args.db
    address: 'Address' = Address.from_string(args.address)

    try:
        reader = StateDatabaseReader()
        reader.open(db_path)

        account: 'Account' = reader.get_account(address)
        if account is None:
            print(f'Account not found: {address}')
        else:
            print(f'address: {account.address}\n'
                  f'amount: {account.icx / 10 ** 18} in icx\n'
                  f'is_c_rep: {account.c_rep}\n'
                  f'is_locked: {account.locked}')
    finally:
        reader.close()


def setup_invalid_transaction(subparsers):
    parser = subparsers.add_parser('invalidtx')
    parser.add_argument('--db', type=str, required=True)
    parser.add_argument('--start', type=int, default=1, required=False)
    parser.add_argument('--end', type=int, default=-1, required=False)
    parser.set_defaults(func=run_command_invalid_transaction)


def run_command_invalid_transaction(args):
    """Check whether invalid transaction are present or not
    for example transactions that are processed without any fees

    :param args:
    :return:
    """
    db_path: str = args.db
    start: int = args.start
    end: int = args.end

    checker = InvalidTransactionChecker()
    try:
        checker.open(db_path)
        checker.run(start, end)
    finally:
        checker.close()


def setup_tps_calculation(subparsers):
    parser = subparsers.add_parser('tps')
    parser.add_argument('--db', type=str, required=True)
    parser.add_argument('--start', type=int, default=0, required=False)
    parser.add_argument('--end', type=int, default=-1, required=False)
    parser.set_defaults(func=run_command_tps_calculation)


def run_command_tps_calculation(args):
    """Calculate tps for confirmed transactions in blockchain
    TPS = # of confirmed txs between start block and end block / (end block timestamp - start block timestamp)

    :param args:
    :return:
    """
    db_path: str = args.db
    start: int = args.start
    end: int = args.end

    calculator = TPSCalculator()
    try:
        calculator.open(db_path)
        calculator.run(start, end)
    finally:
        calculator.close()


def setup_token(subparsers):
    parser = subparsers.add_parser('token')
    parser.add_argument('--db', type=str, required=True)
    parser.add_argument(
        '--score', type=str, required=True, help='score address ex) cx63af7f2e073985a9e9965765e809f66da3b0f238')
    parser.add_argument(
        '--user', type=str, required=True, help='user address ex) hxd7cf2f6bcbbfa542a08e9cd0e48bf848018a2ec7')
    parser.add_argument('--balance', type=int, default=-1, required=False, help='token balance to write. ex) 100')
    parser.set_defaults(func=run_command_token)


def run_command_token(args):
    db_path: str = args.db
    score_address: 'Address' = Address.from_string(args.score)
    address: 'Address' = Address.from_string(args.user)
    balance: int = args.balance
    # Name of DictDB in Standard Token
    name: str = 'balances'

    manager = ScoreDatabaseManager()
    manager.open(db_path, score_address)

    if balance < 0:
        value: bytes = manager.read_from_dict_db(name, address)
        balance: int = int.from_bytes(value, 'big')
        print(f'token balance: {balance}')
    else:
        value: bytes = int_to_bytes(balance)
        manager.write_to_dict_db(name, address, value)

    manager.close()


def main():
    mainnet_builtin_score_owner = 'hx677133298ed5319607a321a38169031a8867085c'

    parser = argparse.ArgumentParser(prog='icondbtools', description='icon db tools')

    subparsers = parser.add_subparsers(title='subcommands')

    # create the parser for the 'sync' command
    parser_sync = subparsers.add_parser('sync')
    parser_sync.add_argument('--db', type=str, required=True)
    parser_sync.add_argument('-s', '--start', type=int, default=-1, help='start height to sync')
    parser_sync.add_argument('--end', type=int, default=-1, help='end height to sync, inclusive')
    parser_sync.add_argument(
        '-c', '--count', type=int, default=999999999, help='The number of blocks to sync')
    parser_sync.add_argument(
        '-o', '--owner',
        dest='builtin_score_owner',
        default=mainnet_builtin_score_owner,
        help='BuiltinScoreOwner')
    parser_sync.add_argument(
        '--stop-on-error',
        action='store_true',
        help='stop running when commit_state is different from state_root_hash')
    parser_sync.add_argument(
        '--no-commit', action='store_true', help='Do not commit')
    parser_sync.add_argument(
        '--write-precommit-data', action='store_true', help='Write precommit data to file')
    parser_sync.add_argument('--no-fee', action='store_true', help='Disable fee')
    parser_sync.add_argument('--no-audit', action='store_true', help='Diable audit')
    parser_sync.add_argument('--deployer-whitelist', action='store_true', help='Enable deployer whitelist')
    parser_sync.add_argument('--score-package-validator', action='store_true', help='Enable score package validator')
    parser_sync.add_argument(
        '--channel', type=str,
        default='icon_dex', help='channel name used as a key of commit_state in block data')
    parser_sync.set_defaults(func=sync)

    # create the parser for lastblock
    parser_last_block = subparsers.add_parser('lastblock')
    parser_last_block.add_argument('--db', type=str, required=True)
    parser_last_block.set_defaults(func=print_last_block)

    # create the parser for block
    parser_block = subparsers.add_parser('block')
    parser_block.add_argument('--db', type=str, required=True)
    parser_block.add_argument('--height', type=int, default=0, help='start height to sync', required=False)
    parser_block.add_argument('--hash', type=str,
        help='block hash without "0x" (ex: e9cad58aae99c1cae85c2545ad33ddb34e8dc4b5e5dd9f363a30cb55e809018e)',
        required=False)
    parser_block.set_defaults(func=print_block)

    # create the parser for txresult
    parser_block = subparsers.add_parser('txresult')
    parser_block.add_argument('--db', type=str, required=True)
    parser_block.add_argument(
        '--hash', dest='tx_hash', help='tx hash without "0x" prefix', required=True)
    parser_block.set_defaults(func=print_transaction_result)

    # create the parser for clear
    parser_clear = subparsers.add_parser('clear', help='clear .score and .statedb')
    parser_clear.set_defaults(func=clear)

    # create the parser for statehash
    parser_state_hash = subparsers.add_parser('statehash')
    parser_state_hash.add_argument('--db', type=str, required=True)
    parser_state_hash.add_argument('--prefix', type=str, default=None,
        help='Generate a state hash using data of which keys start with a given prefix')
    parser_state_hash.set_defaults(func=run_command_state_hash)

    # create the parser for statelastblock
    parser_state_last_block = subparsers.add_parser('statelastblock')
    parser_state_last_block.add_argument('--db', type=str, required=True)
    parser_state_last_block.set_defaults(func=run_command_state_last_block)

    # create the parser for account
    parser_account = subparsers.add_parser('account')
    parser_account.add_argument('--db', type=str, required=True)
    parser_account.add_argument(
        '--address', type=str, required=True,
        help='EOA or SCORE address. ex) hx21a0f22e65ad8cd76c282b8b7fb35ba0368aa9bd')
    parser_account.set_defaults(func=run_command_account)

    # create the parser for invalid tx checker
    setup_invalid_transaction(subparsers)

    setup_tps_calculation(subparsers)

    setup_token(subparsers)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args()
    print(args)

    timer = Timer()
    timer.start()
    ret = args.func(args)
    timer.stop()
    print(f'elapsedTime: {timer.duration()} seconds')

    return ret


if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
