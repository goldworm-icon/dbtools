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

from typing import TYPE_CHECKING

from icondbtools.command.command import Command
from icondbtools.libs.icon_service_syncer import IconServiceSyncer
from icondbtools.libs.state_database_reader import StateDatabaseReader

if TYPE_CHECKING:
    from iconservice.base.block import Block


class CommandSync(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "sync"
        desc = 'Syncronize ICON Service statedb with confirmed_transaction_list of block db'
        mainnet_builtin_score_owner = 'hx677133298ed5319607a321a38169031a8867085c'

        # create the parser for the 'sync' command
        parser_sync = sub_parser.add_parser(name, parents=[common_parser], help=desc)
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
        parser_sync.add_argument('--backup-period', type=int, default=0, help="Backup statedb every this period blocks")
        parser_sync.add_argument('--is-config', type=str, default="", help="iconservice_config.json filepath")
        parser_sync.add_argument('--print-block-height', type=int, default=1, help="Print every this block height")
        parser_sync.set_defaults(func=self.run)

    def run(self, args):
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
        backup_period: int = args.backup_period
        iconservice_config_path: str = args.is_config
        print_block_height: int = args.print_block_height

        reader = StateDatabaseReader()

        # If --start option is not present, set start point to the last block height from statedb
        if start < 0:
            try:
                state_db_path = '.statedb/icon_dex'
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

        if print_block_height < 1:
            raise ValueError(f'print block height should be more than 0')

        syncer = IconServiceSyncer()
        try:
            syncer.open(
                config_path=iconservice_config_path,
                fee=fee,
                audit=audit,
                deployer_whitelist=deployer_whitelist,
                score_package_validator=score_package_validator,
                builtin_score_owner=builtin_score_owner)
            return syncer.run(
                db_path, channel, start_height=start, count=count,
                stop_on_error=stop_on_error, no_commit=no_commit,
                write_precommit_data=write_precommit_data,
                backup_period=backup_period,
                print_block_height=print_block_height)
        finally:
            syncer.close()
