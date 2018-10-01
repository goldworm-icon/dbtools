# -*- coding: utf-8 -*-
# Copyright 2018 theloop Inc.
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

import json
import sys
import time
from typing import Optional

import plyvel


class BlockReader(object):
    """Read block data from leveldb managed by loopchain
    """

    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db:
            self._db.close()
            self._db = None

    def get_block_hash_by_block_height(self, block_height: int) -> Optional[dict]:
        key_prefix = b'block_height_key'
        block_height_key = key_prefix + block_height.to_bytes(12, 'big')

        key: bytes = self._db.get(block_height_key)
        if key is None:
            return

        return self.get_block_by_key(key)

    def get_block_by_block_hash(self, block_hash: str) -> Optional[dict]:
        """

        :param block_hash: ex) 'd7c3ebf769b4988cf83225240d2f2208efc21dd69650fd494906a3336291c9a0'
        :return: bytes including utf-8 encoded text in json format
        """
        return self.get_block_by_key(block_hash.encode())

    def get_block_by_key(self, key: bytes) -> Optional[dict]:
        """key is utf-8 encoded bytes of block_hash hexa string

        :param key: ex) b'd7c3ebf769b4988cf83225240d2f2208efc21dd69650fd494906a3336291c9a0'
        :return:
        """

        value: bytes = self._db.get(key)
        block: dict = json.loads(value)
        return block

    def get_last_block(self) -> Optional[dict]:
        last_block_key = b'last_block_key'
        key: bytes = self._db.get(last_block_key)
        return self.get_block_by_key(key)

    def get_state_root_hash_by_block_height(self, block_height: int) -> Optional[bytes]:
        block: dict = self.get_block_hash_by_block_height(block_height)
        return self._get_state_root_hash(block)

    def get_state_root_hash_by_block_hash(self, block_hash: str) -> Optional[bytes]:
        block: dict = self.get_block_by_block_hash(block_hash)
        return self._get_state_root_hash(block)

    @staticmethod
    def get_commit_state(block: dict, default_value: bytes=None) -> Optional[bytes]:
        try:
            return bytes.fromhex(block['commit_state']['icon_dex'])
        except:
            pass

        return default_value


def main():
    reader = BlockReader()
    reader.open('/home/goldworm/work/icon/db_data/testnet_db')

    start_height = int(sys.argv[1])
    read_blocks(reader, start_height=start_height, count=1)
    # read_last_block(reader)
    # print(reader.get_state_root_hash_by_block_height(100))
    # print(reader.get_state_root_hash_by_block_height(23366))

    reader.close()


def read_blocks(reader, start_height: int, count: int):
    start_time = time.time()

    with open('blocks.txt', 'wt') as f:
        for i in range(start_height, start_height + count):
            block: dict = reader.get_block_hash_by_block_height(i)
            if block is None:
                print(f'last block: {i - 1}')
                break

            if i % 100 == 0:
                print(f'block: {i}')

            f.write(f'{block}\n')

    end_time = time.time()
    print(f'elapsed time: {end_time - start_time}')


def read_last_block(reader):
    start = time.time()

    block: dict = reader.get_last_block()
    print(block)

    end = time.time()
    print(f'elapsed time: {end - start}')


if __name__ == '__main__':
    main()
