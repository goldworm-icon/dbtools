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

from iconcommons.icon_config import IconConfig
from iconservice.base.block import Block
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.iconscore.icon_score_result import TransactionResult

from . import utils
from .block_reader import BlockReader
from .loopchain_block import LoopchainBlock


class IconServiceValidator(object):
    def __init__(self):
        self._block_reader = BlockReader()
        self._engine = IconServiceEngine()

    def open(self,
             fee: bool=True,
             audit: bool=True,
             deployer_whitelist: bool=False,
             score_package_validator: bool=False,
             builtin_score_owner: str=''):
        conf = IconConfig('', default_icon_config)
        conf.update_conf({
            ConfigKey.SERVICE_FEE: fee,
            ConfigKey.SERVICE_AUDIT: audit,
            ConfigKey.SERVICE_DEPLOYER_WHITELIST: deployer_whitelist,
            ConfigKey.SERVICE_SCORE_PACKAGE_VALIDATOR: score_package_validator,
            ConfigKey.BUILTIN_SCORE_OWNER: builtin_score_owner
        })

        self._engine.open(conf)

    def run(self,
            db_path: str,
            start_height: int=0,
            count: int=99999999,
            stop_on_error: bool=True):
        self._block_reader.open(db_path)

        print('block_height | commit_state | state_root_hash')

        for i in range(start_height, start_height + count):
            block_dict: dict = self._block_reader.get_block_hash_by_block_height(i)
            if block_dict is None:
                print(f'last block: {i - 1}')
                break

            loopchain_block = LoopchainBlock.from_dict(block_dict)
            block: 'Block' = utils.create_block(loopchain_block)

            transaction_results, state_root_hash = self._invoke(loopchain_block)
            commit_state: bytes = self._block_reader.get_commit_state(block_dict, b'')

            # "commit_state" is the field name of state_root_hash in loopchain block
            print(f'{i} | {commit_state.hex()} | {state_root_hash.hex()}')

            if commit_state:
                if stop_on_error and commit_state != state_root_hash:
                    print(block_dict)
                    break

            self._engine.commit(block)

        self._block_reader.close()

    def _invoke(self, loopchain_block: 'LoopchainBlock') -> ('TransactionResult', bytes):
        block: 'Block' = utils.create_block(loopchain_block)
        tx_requests: list = utils.create_transaction_requests(loopchain_block)

        return self._engine.invoke(block, tx_requests)

    def close(self):
        self._engine.close()


def main():
    loopchain_db_path = '../data/icon_dex'

    executor = IconServiceValidator()
    executor.open(builtin_score_owner='hx677133298ed5319607a321a38169031a8867085c')
    executor.run(loopchain_db_path, 0, 1)
    executor.close()


if __name__ == '__main__':
    main()
