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

import asyncio
import inspect
import logging
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Optional, List, Tuple, Dict

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.database.batch import TransactionBatchValue
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import Revision
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.iconscore.icon_score_context import IconScoreContextType, IconScoreContext

from icondbtools.utils.convert_type import object_to_str
from icondbtools.utils.transaction import create_transaction_requests
from icondbtools.word_detector import WordDetector
from .block_database_reader import BlockDatabaseReader
from .loopchain_block import LoopchainBlock
from .vote import Vote
from ..data.node_container import NodeContainer

if TYPE_CHECKING:
    from iconservice.database.batch import BlockBatch
    from iconservice.precommit_data_manager import PrecommitData, PrecommitDataManager


def _create_iconservice_block(loopchain_block: 'LoopchainBlock') -> 'Block':
    return Block(
        block_height=loopchain_block.height,
        block_hash=loopchain_block.block_hash,
        timestamp=loopchain_block.timestamp,
        prev_hash=loopchain_block.prev_block_hash)


def _create_block_validators(block_dict: dict, leader: Optional['Address']) -> Optional[List['Address']]:
    if "prevVotes" not in block_dict:
        return None

    validators: List['Address'] = []

    for item in block_dict["prevVotes"]:
        if not isinstance(item, dict):
            continue

        vote = Vote.from_dict(item)
        if leader != vote.rep:
            validators.append(vote.rep)

    return validators


def _create_prev_block_votes(block_dict: dict,
                             leader: Optional['Address'],
                             main_preps: Optional['NodeContainer']) -> Optional[List[Tuple['Address', int]]]:
    if "prevVotes" not in block_dict:
        return None

    if main_preps is None:
        return None

    ret: List[Tuple['Address', int]] = []
    prev_votes = {}

    # Parse prevVotes
    for item in block_dict["prevVotes"]:
        if not isinstance(item, dict):
            continue

        vote = Vote.from_dict(item)
        prev_votes[vote.rep] = vote

    for main_prep in main_preps:
        address: 'Address' = main_prep.address

        if address == leader:
            # Skip it if address is a leader address
            continue

        vote_result = 1 if address in prev_votes else 0
        ret.append((address, vote_result))

    return ret


class IconServiceSyncer(object):
    _TAG = "SYNC"

    def __init__(self):
        self._block_reader = BlockDatabaseReader()
        self._engine = IconServiceEngine()

    def open(self,
             config_path: str,
             fee: bool = True,
             audit: bool = True,
             deployer_whitelist: bool = False,
             score_package_validator: bool = False,
             builtin_score_owner: str = ''):
        conf = IconConfig("", default_icon_config)

        if config_path != "":
            conf.load(config_path)

        conf.update_conf({
            "builtinScoreOwner": builtin_score_owner,
            "service": {
                "fee": fee,
                "audit": audit,
                "scorePackageValidator": score_package_validator,
                "deployerWhiteList": deployer_whitelist
            }
        })

        Logger.load_config(conf)
        self._engine.open(conf)

    def run(self, *args, **kwargs) -> int:
        Logger.debug(tag=self._TAG, msg=f"run() start: {args} {kwargs}")

        loop = asyncio.get_event_loop()
        future = asyncio.Future()

        try:
            asyncio.ensure_future(self._wait_for_complete(future, *args, **kwargs))
            loop.run_until_complete(future)
        finally:
            self._engine.close()
            loop.close()

        ret = future.result()
        Logger.debug(tag=self._TAG, msg=f"run() end: {ret}")

        return ret

    async def _wait_for_complete(self, result_future: asyncio.Future, *args, **kwargs):
        Logger.debug(tag=self._TAG, msg="_wait_for_complete() start")

        executor = ThreadPoolExecutor(max_workers=1)
        f = executor.submit(self._run, *args, **kwargs)
        future = asyncio.wrap_future(f)

        await future

        Logger.debug(tag=self._TAG, msg="_wait_for_complete() end1")
        result_future.set_result(future.result())

        Logger.debug(tag=self._TAG, msg="_wait_for_complete() end2")

    def _run(self,
             db_path: str,
             channel: str,
             start_height: int = 0,
             count: int = 99999999,
             stop_on_error: bool = True,
             no_commit: bool = False,
             backup_period: int = 0,
             write_precommit_data: bool = False,
             print_block_height: int = 1) -> int:
        """Begin to synchronize IconServiceEngine with blocks from loopchain db

        :param db_path: loopchain db path
        :param channel: channel name used as a key to get commit_state in loopchain db
        :param start_height: start height to sync
        :param count: The number of blocks to sync
        :param stop_on_error: If error happens, stop syncing
        :param no_commit: Do not commit
        :param backup_period: state backup period in block
        :param write_precommit_data:
        :param print_block_height: print every this block height
        :return: 0(success), otherwise(error)
        """
        Logger.debug(tag=self._TAG, msg="_run() start")

        word_detector = WordDetector(filename='iconservice.log',
                                     block_word=r'CALCULATE\(',
                                     release_word=r'CALCULATE_DONE\(')
        ret: int = 0
        self._block_reader.open(db_path)

        print('block_height | commit_state | state_root_hash | tx_count')

        prev_block: Optional['Block'] = None
        prev_loopchain_block: Optional['LoopchainBlock'] = None
        if start_height > 0:
            block_dict = self._block_reader.get_block_by_block_height(start_height - 1)
            prev_loopchain_block = LoopchainBlock.from_dict(block_dict)

        main_preps: Optional['NodeContainer'] = None
        next_main_preps: Optional['NodeContainer'] = None

        for height in range(start_height, start_height + count):
            block_dict: dict = self._block_reader.get_block_by_block_height(height)

            if block_dict is None:
                print(f'last block: {height - 1}')
                break

            loopchain_block: 'LoopchainBlock' = LoopchainBlock.from_dict(block_dict)
            block: 'Block' = _create_iconservice_block(loopchain_block)

            tx_requests: list = create_transaction_requests(loopchain_block)
            prev_block_generator: Optional['Address'] = \
                prev_loopchain_block.leader if prev_loopchain_block else None
            prev_block_validators: Optional[List['Address']] = \
                _create_block_validators(block_dict, prev_block_generator)
            prev_block_votes: Optional[List[Tuple['Address', int]]] = \
                _create_prev_block_votes(block_dict, prev_block_generator, main_preps)

            Logger.info(tag=self._TAG, msg=f"prev_block_generator={prev_block_generator}")
            Logger.info(tag=self._TAG, msg=f"prev_block_validators={prev_block_validators}")
            Logger.info(tag=self._TAG, msg=f"prev_block_votes={prev_block_votes}")

            if prev_block is not None and prev_block.hash != block.prev_hash:
                raise Exception()

            invoke_result = self._engine.invoke(block, tx_requests,
                                                prev_block_generator, prev_block_validators, prev_block_votes)
            tx_results, state_root_hash = invoke_result[0], invoke_result[1]
            main_preps_as_dict: Optional[Dict] = invoke_result[3]

            commit_state: bytes = self._block_reader.get_commit_state(block_dict, channel, b'')

            # "commit_state" is the field name of state_root_hash in loopchain block
            if (height - start_height) % print_block_height == 0:
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

                self._print_precommit_data(block)
                ret: int = 1
                break

            is_calculation_block = self._check_calculation_block(block)

            if is_calculation_block:
                word_detector.start()
                time.sleep(0.5)

            if not no_commit:
                while word_detector.get_hold():
                    time.sleep(0.5)

                if 'block' in inspect.signature(self._engine.commit).parameters:
                    self._engine.commit(block)
                else:
                    self._engine.commit(block.height, block.hash, block.hash)

            while word_detector.get_hold():
                time.sleep(0.5)

            # Prepare the next iteration
            self._backup_state_db(block, backup_period)
            prev_block = block
            prev_loopchain_block = loopchain_block

            if next_main_preps:
                main_preps = next_main_preps
                next_main_preps = None

            if main_preps_as_dict is not None:
                next_main_preps = NodeContainer.from_dict(main_preps_as_dict)

        self._block_reader.close()

        Logger.debug(tag=self._TAG, msg=f"_run() end: {ret}")
        return ret

    def _check_invoke_result(self, tx_results: list):
        """Compare the transaction results from IconServiceEngine
        with the results stored in loopchain db

        If transaction result is not compatible to protocol v3, pass it

        :param tx_results: the transaction results that IconServiceEngine.invoke() returns
        :return: True(same) False(different)
        """

        for tx_result in tx_results:
            tx_info_in_db: dict = \
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

        if event_logs_in_db is None:
            event_logs_in_db = []

        if event_logs_in_tx_result is None:
            event_logs_in_tx_result = []

        if len(event_logs_in_db) != len(event_logs_in_tx_result):
            return False

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
                indexed[i] = object_to_str(value)

            data: list = tx_result_event_log['data']
            for i in range(len(data)):
                value = data[i]
                data[i] = object_to_str(value)

            if event_log != tx_result_event_log:
                print(f'{event_log} != {tx_result_event_log}')
                return False

        return True

    def _print_precommit_data(self, block: 'Block'):
        """Print the latest updated states stored in IconServiceEngine

        :return:
        """
        precommit_data_manager: PrecommitDataManager = \
            getattr(self._engine, '_precommit_data_manager')

        precommit_data: PrecommitData = precommit_data_manager.get(block.hash)
        block_batch: BlockBatch = precommit_data.block_batch
        state_root_hash: bytes = block_batch.digest()

        filename = f'{block.height}-precommit-data.txt'
        with open(filename, 'wt') as f:
            for i, key in enumerate(block_batch):
                value: 'TransactionBatchValue' = block_batch[key]

                if value:
                    hex_value = value.value.hex()
                    include_state_root_hash = value.include_state_root_hash

                    line = f'{i}: {key.hex()} - {hex_value}, {include_state_root_hash}'
                else:
                    line = f'{i}: {key.hex()} - None'

                print(line)
                f.write(f'{line}\n')

            f.write(f'state_root_hash: {state_root_hash.hex()}\n')

    def _check_calculation_block(self, block: 'Block') -> bool:
        """check calculation block"""

        precommit_data_manager: PrecommitDataManager = getattr(self._engine, '_precommit_data_manager')
        precommit_data: PrecommitData = precommit_data_manager.get(block.hash)
        if precommit_data.revision < Revision.IISS.value:
            return False

        context = IconScoreContext(IconScoreContextType.DIRECT)
        context.block = block

        if hasattr(context.engine.iiss, 'get_start_block_of_calc'):
            start_block = context.engine.iiss.get_start_block_of_calc(context)
            return start_block == block.height or start_block == block.height - 1
        else:
            return context.engine.iiss._is_iiss_calc(precommit_data.precommit_flag)

    @staticmethod
    def _backup_state_db(block: 'Block', backup_period: int):
        if backup_period <= 0:
            return
        if block.height == 0:
            return

        if block.height % backup_period == 0:
            print(f"----------- Backup statedb: {block.height} ------------")
            dirname: str = f"block-{'%09d' % block.height}"
            for basename in (".score", ".statedb"):
                try:
                    shutil.copytree(basename, f"{dirname}/{basename}/")
                except FileExistsError:
                    pass

    def close(self):
        pass
