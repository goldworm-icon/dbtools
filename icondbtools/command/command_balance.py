# -*- coding: utf-8 -*-
# Copyright 2020 ICON Foundation Inc.
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

from typing import TYPE_CHECKING, List

from icondbtools.command.command import Command
from iconservice.base.address import Address
from ..libs.balance_calculator import BalanceCalculator, StakeInfo
from ..libs.transaction_collector import TransactionCollector
from ..utils.convert_type import bytes_to_hex

if TYPE_CHECKING:
    from ..data.transaction import Transaction
    from ..data.transaction_result import TransactionResult


class CommandBalance(Command):
    """Calculate balance delta amount with transactions and results ranging in block from start-BH to end-BH

    """

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'balance'
        desc = 'Inspect the transactions and results associated with the balance of a given address'

        # create the parser for balance
        parser_balance = sub_parser.add_parser(name, parents=[common_parser], help=desc)

        parser_balance.add_argument(
            'address', type=str, help='EOA or SCORE address ex) hx21a0f22e65ad8cd76c282b8b7fb35ba0368aa9bd')

        parser_balance.add_argument('-s', '--start', type=int, required=True, default=0, help='start block height')
        parser_balance.add_argument('-e', '--end', type=int, default=-1, help='end block height, inclusive')
        parser_balance.add_argument('--count', type=int, default=-1, help='How many blocks to inspect')
        parser_balance.add_argument('--init-balance', type=int, default=0, help='Initial balance in loop')
        parser_balance.add_argument('--file', type=str, default='', help='file including transaction hashes')
        parser_balance.add_argument(
            '--details', action='store_true', default=False, help='Show the result in more detail')

        parser_balance.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        address = Address.from_string(args.address)
        init_balance: int = args.init_balance
        start: int = args.start
        path: str = args.file

        if args.end > 0:
            end = args.end
        elif args.count > 0:
            end = start + args.count - 1
        else:
            end = -1

        transaction_collector = TransactionCollector()
        transaction_collector.open(db_path)

        if path:
            it = transaction_collector.run_with_file(path)
        else:
            it = transaction_collector.run(start, end)

        balance_calculator = BalanceCalculator(address)
        balance, stake_info = balance_calculator.run(it, init_balance=init_balance)

        transaction_collector.close()

        self._print(args.details,
                    address,
                    balance,
                    stake_info,
                    transaction_collector.start_block_height,
                    transaction_collector.end_block_height,
                    balance_calculator.txs,
                    balance_calculator.tx_results)

    @classmethod
    def _print(cls,
               details: bool,
               address: 'Address',
               balance: int,
               stake_info: 'StakeInfo',
               start_height: int,
               end_height: int,
               txs: List['Transaction'],
               tx_results: List['TransactionResult']):
        assert len(txs) == len(tx_results)

        print(
            f'Result ------------------------------------------------\n'
            f'address: {address}\n'
            f'start: {start_height}\n'
            f'end: {end_height}\n'
            f'balance including stake: {balance}\n'
            f'balance excluding stake: {balance - stake_info.stake}\n'
            f'stake_info: {stake_info}\n'
            f'transactions: {len(txs)}\n')

        if details:
            cls._print_details(txs, tx_results)

    @classmethod
    def _print_details(cls, txs: List['Transaction'], tx_results: List['TransactionResult']):
        for i, (tx, tx_result) in enumerate(zip(txs, tx_results)):
            print(
                f'{i}: '
                f'tx_hash={bytes_to_hex(tx.tx_hash)} '
                f'from={tx.from_} '
                f'to={tx.to} '
                f'value={tx.value} '
                f'data_type={tx.data_type} '
                f'block_height={tx_result.block_height} '
                f'status={tx_result.status}')
