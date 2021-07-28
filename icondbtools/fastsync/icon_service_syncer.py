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
import logging
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import TYPE_CHECKING, Optional, List, Tuple, Dict, Any

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.database.batch import TransactionBatchValue
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import Revision
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.iconscore.icon_score_context import (
    IconScoreContextType,
    IconScoreContext,
)
from iconservice.iiss.reward_calc.storage import Storage

from icondbtools.utils.convert_type import object_to_str
from icondbtools.word_detector import WordDetector
from ..data.node_container import NodeContainer
from ..fastsync.block_reader import BlockDatabaseReader as BinBlockDatabaseReader
from ..fastsync.utils import (
    create_transaction_requests,
    create_iconservice_block,
    create_block_validators,
    create_prev_block_votes,
)
from ..migrate.block import Block as BinBlock
from ..utils import estimate_remaining_time_s
from ..utils.timer import Timer
from ..utils.utils import remove_dir

if TYPE_CHECKING:
    from iconservice.database.batch import BlockBatch
    from iconservice.precommit_data_manager import PrecommitData, PrecommitDataManager


class IconServiceSyncer(object):
    _TAG = "SYNC"

    def __init__(self):
        self._block_reader = BinBlockDatabaseReader()
        self._engine = IconServiceEngine()
        self._timer = Timer()

    def open(
        self,
        config_path: str,
        fee: bool = True,
        audit: bool = True,
        deployer_whitelist: bool = False,
        score_package_validator: bool = False,
        builtin_score_owner: str = "",
    ):
        conf = IconConfig("", default_icon_config)

        if config_path != "":
            conf.load(config_path)

        conf.update_conf(
            {
                "builtinScoreOwner": builtin_score_owner,
                "service": {
                    "fee": fee,
                    "audit": audit,
                    "scorePackageValidator": score_package_validator,
                    "deployerWhiteList": deployer_whitelist,
                },
            }
        )

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
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.close()

        ret = future.result()
        Logger.debug(tag=self._TAG, msg=f"run() end: {ret}")

        return ret

    async def _wait_for_complete(self, result_future: asyncio.Future, *args, **kwargs):
        Logger.debug(tag=self._TAG, msg="_wait_for_complete() start")

        # Wait for rc to be ready
        future = self._engine.get_ready_future()
        await future

        with ThreadPoolExecutor(max_workers=1) as executor:
            # Call IconServiceEngine.hello()
            f = executor.submit(self._hello)
            future = asyncio.wrap_future(f)
            await future

            # Start to sync blocks
            f = executor.submit(self._run, *args, **kwargs)
            f = asyncio.wrap_future(f)
            for fut in asyncio.as_completed([f]):
                try:
                    ret = await fut
                except Exception as exc:
                    self._engine.close()
                    # Wait to stop ipc_server for 1s
                    await asyncio.sleep(1)
                    result_future.set_exception(exc)
                else:
                    self._engine.close()
                    # Wait to stop ipc_server for 1s
                    await asyncio.sleep(1)
                    Logger.debug(tag=self._TAG, msg="_wait_for_complete() end1")
                    result_future.set_result(ret)
                    Logger.debug(tag=self._TAG, msg="_wait_for_complete() end2")

    def _hello(self):
        self._engine.hello()

    def _run(
        self,
        db_path: str,
        channel: str,
        start_height: int = 0,
        count: int = 99_999_999,
        stop_on_error: bool = True,
        no_commit: bool = False,
        backup_period: int = 0,
        write_precommit_data: bool = False,
        print_block_height: int = 1,
        iiss_db_backup_path: Optional[str] = None,
    ) -> int:
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

        word_detector = WordDetector(
            filename="iconservice.log",
            block_word=r"CALCULATE\(",
            release_word=r"CALCULATE_DONE\(",
        )
        ret: int = 0
        self._block_reader.open(db_path)

        print("block_height | commit_state | state_root_hash | tx_count")

        prev_bin_block: Optional["BinBlock"] = None
        prev_block: Optional["Block"] = None
        main_preps: Optional['NodeContainer'] = None
        next_main_preps: Optional["NodeContainer"] = None

        if start_height > 0:
            prev_bin_block: Optional[BinBlock] = self._block_reader.get_block_by_height(start_height - 1)
            # init main_preps
            preps: list = self._block_reader.load_main_preps(reps_hash=prev_bin_block.reps_hash)
            main_preps: Optional['NodeContainer'] = NodeContainer.from_list(preps=preps)

            # when sync from the first block of term, have to initialize next_main_preps here
            # in that case, invoke_result[3] will be None on first block and can not update next_main_preps
            cur_bin_block: Optional[BinBlock] = self._block_reader.get_block_by_height(start_height)
            block: "Block" = create_iconservice_block(cur_bin_block)
            if self._check_calculation_block(block):
                preps: list = self._block_reader.load_main_preps(reps_hash=cur_bin_block.reps_hash)
                next_main_preps: Optional['NodeContainer'] = NodeContainer.from_list(preps=preps)

        end_height = start_height + count - 1

        self._timer.start()

        for height in range(start_height, end_height + 1):
            bin_block = self._block_reader.get_block_by_height(height)
            if bin_block is None:
                print(f"last block: {height - 1}")
                break

            block: "Block" = create_iconservice_block(bin_block)

            tx_requests: List[Dict[str, Any]] = create_transaction_requests(
                bin_block.transactions
            )
            prev_block_generator: Optional[
                "Address"
            ] = prev_bin_block.leader if prev_bin_block else None
            prev_block_validators: Optional[List["Address"]] = create_block_validators(
                bin_block.prev_votes, prev_block_generator
            )
            prev_block_votes: Optional[
                List[Tuple["Address", int]]
            ] = create_prev_block_votes(
                bin_block.prev_votes, prev_block_generator, main_preps
            )

            Logger.info(
                tag=self._TAG, msg=f"prev_block_generator={prev_block_generator}"
            )
            Logger.info(
                tag=self._TAG, msg=f"prev_block_validators={prev_block_validators}"
            )
            Logger.info(tag=self._TAG, msg=f"prev_block_votes={prev_block_votes}")

            if prev_block is not None and prev_block.hash != block.prev_hash:
                raise Exception(f"Invalid prev_block_hash: height={height}")

            invoke_result = self._engine.invoke(
                block,
                tx_requests,
                prev_block_generator,
                prev_block_validators,
                prev_block_votes,
            )
            tx_results, state_root_hash = invoke_result[0], invoke_result[1]
            main_preps_as_dict: Optional[Dict] = invoke_result[3]

            commit_state: bytes = bin_block.state_hash

            # "commit_state" is the field name of state_root_hash in loopchain block
            if (height - start_height) % print_block_height == 0:
                self._print_status(
                    height, start_height, count,
                    commit_state, state_root_hash, len(tx_requests)
                )

            if write_precommit_data:
                self._print_precommit_data(block)

            try:
                if stop_on_error:
                    if commit_state:
                        if commit_state != state_root_hash:
                            raise Exception("state_root_hash mismatch")

                    if height > 0 and not self._check_invoke_result(tx_results):
                        raise Exception("tx_result mismatch")
            except Exception as e:
                logging.exception(e)

                self._print_precommit_data(block)
                ret: int = 1
                break

            is_calculation_block = self._check_calculation_block(block)

            if is_calculation_block:
                word_detector.start()
                time.sleep(0.5)
                if iiss_db_backup_path is not None:
                    self._backup_iiss_db(iiss_db_backup_path, block.height)

            # If no_commit is set to True, the config only affects to the last block to commit
            if not no_commit or height < end_height:
                while word_detector.get_hold():
                    time.sleep(0.5)

                # Call IconServiceEngine.commit() with a block
                self._commit(block)

            while word_detector.get_hold():
                time.sleep(0.5)
            # Prepare the next iteration
            self._backup_state_db(block, backup_period)
            prev_block: 'Block' = block
            prev_bin_block: 'BinBlock' = bin_block

            if next_main_preps:
                main_preps = next_main_preps
                next_main_preps = None

            if main_preps_as_dict is not None:
                next_main_preps = NodeContainer.from_dict(main_preps_as_dict)

        self._block_reader.close()
        word_detector.stop()

        Logger.debug(tag=self._TAG, msg=f"_run() end: {ret}")
        return ret

    def _commit(self, block: "Block"):
        # if "block" in inspect.signature(self._engine.commit).parameters:
        #     self._engine.commit(block)
        # else:
        #     self._engine.commit(block.height, block.hash, block.hash)
        self._engine.commit(block.height, block.hash, block.hash)

    def _backup_iiss_db(self, iiss_db_backup_path: Optional[str], block_height: int):
        iiss_db_path: str = os.path.join(self._engine._state_db_root_path, "iiss")

        with os.scandir(iiss_db_path) as it:
            for entry in it:
                if entry.is_dir() and entry.name == Storage.CURRENT_IISS_DB_NAME:
                    dst_path: str = os.path.join(
                        iiss_db_backup_path,
                        f"{Storage.IISS_RC_DB_NAME_PREFIX}{block_height - 1}",
                    )
                    if os.path.exists(dst_path):
                        remove_dir(dst_path)
                    shutil.copytree(entry.path, dst_path)
                    break

    def _check_invoke_result(self, tx_results: list):
        """Compare the transaction results from IconServiceEngine
        with the results stored in loopchain db

        If transaction result is not compatible to protocol v3, pass it

        :param tx_results: the transaction results that IconServiceEngine.invoke() returns
        :return: True(same) False(different)
        """

        #     for tx_result in tx_results:
        #         tx_info_in_db: dict = self._block_reader.get_transaction_result_by_hash(
        #             tx_result.tx_hash.hex()
        #         )
        #         tx_result_in_db = tx_info_in_db["result"]
        #
        #         # tx_v2 dose not have transaction result_v3
        #         if "status" not in tx_result_in_db:
        #             continue
        #
        #         # information extracted from db
        #         status: int = int(tx_result_in_db["status"], 16)
        #         tx_hash: bytes = bytes.fromhex(tx_result_in_db["txHash"])
        #         step_used: int = int(tx_result_in_db["stepUsed"], 16)
        #         step_price: int = int(tx_result_in_db["stepPrice"], 16)
        #         event_logs: list = tx_result_in_db["eventLogs"]
        #         step: int = step_used * step_price
        #
        #         if tx_hash != tx_result.tx_hash:
        #             print(f"tx_hash: {tx_hash.hex()} != {tx_result.tx_hash.hex()}")
        #             return False
        #         if status != tx_result.status:
        #             print(f"status: {status} != {tx_result.status}")
        #             return False
        #         if step_used != tx_result.step_used:
        #             print(f"step_used: {step_used} != {tx_result.step_used}")
        #             return False
        #
        #         tx_result_step: int = tx_result.step_used * tx_result.step_price
        #         if step != tx_result_step:
        #             print(f"step: {step} != {tx_result_step}")
        #             return False
        #         if step_price != tx_result.step_price:
        #             print(f"step_price: {step_price} != {tx_result.step_price}")
        #             return False
        #
        #         if not self._check_event_logs(event_logs, tx_result.event_logs):
        #             return False
        #
        return True

    @staticmethod
    def _check_event_logs(event_logs_in_db: list, event_logs_in_tx_result: list):

        if event_logs_in_db is None:
            event_logs_in_db = []

        if event_logs_in_tx_result is None:
            event_logs_in_tx_result = []

        if len(event_logs_in_db) != len(event_logs_in_tx_result):
            return False

        for event_log, _tx_result_event_log in zip(
            event_logs_in_db, event_logs_in_tx_result
        ):
            tx_result_event_log: dict = _tx_result_event_log.to_dict()

            # convert Address to str
            if "score_address" in tx_result_event_log:
                score_address: "Address" = tx_result_event_log["score_address"]
                del tx_result_event_log["score_address"]
                tx_result_event_log["scoreAddress"] = str(score_address)

            # convert Address objects to str objects in 'indexes'
            indexed: list = tx_result_event_log["indexed"]
            for i in range(len(indexed)):
                value = indexed[i]
                indexed[i] = object_to_str(value)

            data: list = tx_result_event_log["data"]
            for i in range(len(data)):
                value = data[i]
                data[i] = object_to_str(value)

            if event_log != tx_result_event_log:
                print(f"{event_log} != {tx_result_event_log}")
                return False

        return True

    def _print_precommit_data(self, block: "Block"):
        """Print the latest updated states stored in IconServiceEngine

        :return:
        """
        precommit_data_manager: PrecommitDataManager = getattr(
            self._engine, "_precommit_data_manager"
        )

        precommit_data: PrecommitData = precommit_data_manager.get(block.hash)
        block_batch: BlockBatch = precommit_data.block_batch
        state_root_hash: bytes = block_batch.digest()

        filename = f"{block.height}-precommit-data.txt"
        with open(filename, "wt") as f:
            for i, key in enumerate(block_batch):
                value: "TransactionBatchValue" = block_batch[key]

                if value:
                    hex_value = value.value.hex() if value.value is not None else None
                    include_state_root_hash = value.include_state_root_hash

                    line = f"{i}: {key.hex()} - {hex_value}, {include_state_root_hash}"
                else:
                    line = f"{i}: {key.hex()} - None"

                print(line)
                f.write(f"{line}\n")

            f.write(f"state_root_hash: {state_root_hash.hex()}\n")

    def _check_calculation_block(self, block: "Block") -> bool:
        """check calculation block"""

        context = IconScoreContext(IconScoreContextType.DIRECT)
        revision = self._engine._get_revision_from_rc(context)
        context.block = block

        if revision < Revision.IISS.value:
            return False

        start_block = context.engine.iiss.get_start_block_of_calc(context)
        return start_block == block.height

    @staticmethod
    def _backup_state_db(block: "Block", backup_period: int):
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

    def _print_status(
            self,
            height: int, start_height: int, count: int,
            commit_state: bytes, state_root_hash: bytes, tx_requests: int):
        self._timer.stop()

        blocks_done = height - start_height + 1
        estimated_time_s: float = estimate_remaining_time_s(
            count, blocks_done, self._timer.duration()
        )

        status = (
            f"{height}",
            f"{commit_state.hex()[:6]}",
            f"{state_root_hash.hex()[:6]}",
            f"{tx_requests}",
            f"{blocks_done}/{count}",
            f"{blocks_done * 100 / count:.2f}%",
            f"{timedelta(seconds=estimated_time_s)}",
        )

        print(f'{" | ".join(status)}\r', flush=True, end="")

    def close(self):
        pass
