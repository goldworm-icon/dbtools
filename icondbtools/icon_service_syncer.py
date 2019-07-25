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

import logging
import shutil
import os
from typing import TYPE_CHECKING, Optional

from iconcommons.icon_config import IconConfig
from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.icon_config import default_icon_config
from iconservice.icon_service_engine import IconServiceEngine
from . import utils
from .block_database_reader import BlockDatabaseReader
from .loopchain_block import LoopchainBlock

if TYPE_CHECKING:
    from iconservice.precommit_data_manager import PrecommitData, PrecommitDataManager
    from iconservice.database.batch import BlockBatch


class IconServiceSyncer(object):
    def __init__(self):
        self._block_reader = BlockDatabaseReader()
        self._engine = IconServiceEngine()

    def open(self,
             fee: bool = True,
             audit: bool = True,
             deployer_whitelist: bool = False,
             score_package_validator: bool = False,
             builtin_score_owner: str = ''):
        conf = IconConfig('', default_icon_config)
        conf.update_conf({
            'builtinScoreOwner': builtin_score_owner,
            'service': {
                'fee': fee,
                'audit': audit,
                'scorePackageValidator': score_package_validator,
                'deployerWhiteList': deployer_whitelist
            }
        })

        self._engine.open(conf)

    def run(self,
            db_path: str,
            channel: str,
            start_height: int = 0,
            count: int = 99999999,
            stop_on_error: bool = True,
            no_commit: bool = False,
            backup_period: int = 0,
            write_precommit_data: bool = False) -> int:
        """Begin to synchronize IconServiceEngine with blocks from loopchain db

        :param db_path: loopchain db path
        :param channel: channel name used as a key to get commit_state in loopchain db
        :param start_height: start height to sync
        :param count: The number of blocks to sync
        :param stop_on_error: If error happens, stop syncing
        :param no_commit: Do not commit
        :param backup_state_period: state backup period in block
        :param write_precommit_data:
        :return: 0(success), otherwise(error)
        """
        ret: int = 0
        self._block_reader.open(db_path)

        print('block_height | commit_state | state_root_hash | tx_count')

        prev_block: Optional['Block'] = None

        for height in range(start_height, start_height + count):
            block_dict: dict = self._block_reader.get_block_by_block_height(height)
            if block_dict is None:
                print(f'last block: {height - 1}')
                break

            loopchain_block = LoopchainBlock.from_dict(block_dict)
            block: 'Block' = utils.create_block(loopchain_block)
            tx_requests: list = utils.create_transaction_requests(loopchain_block)

            if prev_block is not None:
                # print(f'prev_block({prev_block.hash.hex()}) == block({block.prev_hash.hex()})')
                if prev_block.hash != block.prev_hash:
                    raise Exception()

            tx_results, state_root_hash = self._engine.invoke(block, tx_requests)
            commit_state: bytes = self._block_reader.get_commit_state(block_dict, channel, b'')

            # "commit_state" is the field name of state_root_hash in loopchain block
            print(f'{height} | {commit_state.hex()[:6]} | {state_root_hash.hex()[:6]} | {len(tx_requests)}')

            if write_precommit_data:
                self._print_precommit_data(block)

            try:
                if stop_on_error:
                    if commit_state:
                        if commit_state != state_root_hash:
                            raise Exception()

                    if height > 0 and not self._check_invoke_result(tx_results):
                        raise Exception()
            except Exception as e:
                logging.exception(e)

                print(block_dict)
                self._print_precommit_data(block)
                ret: int = 1
                break

            if not no_commit:
                self._engine.commit(block.height, block.hash, None)

            self._backup_state_db(block, backup_period)
            prev_block = block

        self._block_reader.close()

        return ret

    def _check_invoke_result(self, tx_results: list):
        """Compare the transaction results from IconServiceEngine
        with the results stored in loopchain db

        If transaction result is not compatible to protocol v3, pass it

        :param tx_results: the transaction results that IconServiceEngine.invoke() returns
        :return: True(same) False(different)
        """

        for tx_result in tx_results:
            tx_info_in_db: dict =\
                self._block_reader.get_transaction_result_by_hash(
                    tx_result.tx_hash.hex())
            tx_result_in_db = tx_info_in_db['result']

            # tx_v2 dose not have transaction result_v3
            if 'status' not in tx_result_in_db:
                continue

            # information extracted from db
            status: int = int(tx_result_in_db['status'], 16)
            tx_hash: bytes = bytes.fromhex(tx_result_in_db['txHash'])
            step_used: int = int(tx_result_in_db['stepUsed'], 16)
            step_price: int = int(tx_result_in_db['stepPrice'], 16)
            event_logs: list = tx_result_in_db['eventLogs']
            step: int = step_used * step_price

            if tx_hash != tx_result.tx_hash:
                print(f'tx_hash: {tx_hash.hex()} != {tx_result.tx_hash.hex()}')
                return False
            if status != tx_result.status:
                print(f'status: {status} != {tx_result.status}')
                return False
            if step_used != tx_result.step_used:
                print(f'step_used: {step_used} != {tx_result.step_used}')
                return False

            tx_result_step: int = tx_result.step_used * tx_result.step_price
            if step != tx_result_step:
                print(f'step: {step} != {tx_result_step}')
                return False
            if step_price != tx_result.step_price:
                print(f'step_price: {step_price} != {tx_result.step_price}')
                return False

            if not self._check_event_logs(event_logs, tx_result.event_logs):
                return False

        return True

    @staticmethod
    def _check_event_logs(event_logs_in_db: list,
                          event_logs_in_tx_result: list):
        for event_log, _tx_result_event_log in zip(event_logs_in_db, event_logs_in_tx_result):
            tx_result_event_log: dict = _tx_result_event_log.to_dict()

            # convert Address to str
            if 'score_address' in tx_result_event_log:
                score_address: 'Address' = tx_result_event_log['score_address']
                del tx_result_event_log['score_address']
                tx_result_event_log['scoreAddress'] = str(score_address)

            # convert Address objects to str objects in 'indexes'
            indexed: list = tx_result_event_log['indexed']
            for i in range(len(indexed)):
                value = indexed[i]
                indexed[i] = utils.object_to_str(value)

            data: list = tx_result_event_log['data']
            for i in range(len(data)):
                value = data[i]
                data[i] = utils.object_to_str(value)

            if event_log != tx_result_event_log:
                print(f'{event_log} != {tx_result_event_log}')
                return False

        return True

    def _print_precommit_data(self, block: 'Block'):
        """Print the latest updated states stored in IconServiceEngine

        :return:
        """
        precommit_data_manager: PrecommitDataManager =\
            getattr(self._engine, '_precommit_data_manager')

        precommit_data: PrecommitData = precommit_data_manager.get(block.hash)
        block_batch: BlockBatch = precommit_data.block_batch
        state_root_hash: bytes = block_batch.digest()

        filename = f'{block.height}-precommit-data.txt'
        with open(filename, 'wt') as f:
            for i, key in enumerate(block_batch):
                value: bytes = block_batch[key]

                if value:
                    line = f'{i}: {key.hex()} - {value.hex()}'
                else:
                    line = f'{i}: {key.hex()} - None'

                print(line)
                f.write(f'{line}\n')

            f.write(f'state_root_hash: {state_root_hash.hex()}\n')

    @staticmethod
    def _backup_state_db(block: 'Block', backup_period: int):
        if backup_period <= 0:
            return
        if block.height == 0:
            return

        if block.height % backup_period == 0:
            print(f"----------- Backup statedb: {block.height} ------------")
            dirname: str = f"block-{block.height}"

            for basename in (".score", ".statedb"):
                try:
                    shutil.copytree(basename, f"{dirname}/{basename}/")
                except FileExistsError:
                    pass

    def close(self):
        self._engine.close()


def main():
    loopchain_db_path = '../data/icon_dex'
    channel: str = 'icon_dex'

    executor = IconServiceSyncer()
    executor.open(builtin_score_owner='hx677133298ed5319607a321a38169031a8867085c')
    executor.run(loopchain_db_path, channel, 0, 1)
    executor.close()


if __name__ == '__main__':
    main()
