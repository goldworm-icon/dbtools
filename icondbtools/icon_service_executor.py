# -*- coding: utf-8 -*-

from iconservice.icon_config import IconConfig
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.base.block import Block
from iconservice.iconscore.icon_score_result import TransactionResult
from .block_reader import BlockReader


class IconServiceExecutor(object):
    def __init__(self):
        self._block_reader = BlockReader()
        self._engine = IconServiceEngine()

    def open(self, fee: bool=True,
             audit: bool=True,
             deployerWhiteList: bool=False,
             scorePackageValidator: bool=False):
        pass

    def run(self, db_path: str, start_height: int=0, count: int=99999999):
        self._block_reader.open(db_path)

        print('block_height | commit_state | state_root_hash')

        for i in range(start_height, start_height + count):
            block: dict = self._block_reader.get_block_hash_by_block_height(i)
            if block is None:
                print(f'last block: {i - 1}')
                break

            transaction_results, state_root_hash = self._invoke(block)
            commit_state: bytes = self._block_reader.get_commit_state(block, b'')

            print(f'{i} | {commit_state.hex()} | {state_root_hash.hex()}')

            if commit_state:
                if commit_state != state_root_hash:
                    print(block)
                    break

        self._block_reader.close()

    def _invoke(self, loopchain_block: dict):
        pass

    def close(self):
        if self._engine:
            self._engine.close()
