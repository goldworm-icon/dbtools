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
import logging
import shutil

import plyvel
import timeit

HASH_LEN: int = 64
PRT_SIZE: int = 100_000


class PruneDatabase:
    """Prune block data from leveldb managed by loopchain
    """

    def __init__(self, db_path: str, dest_path: str, remain_blocks: int):
        self._db_path: str = db_path
        self._dest_db_path: str = dest_path
        self._remain_blocks: int = remain_blocks

    def run(self):
        logging.warning(f"run Start")
        start_time = timeit.default_timer()
        self._ready()
        self._prune_db()
        self._recover_blocks()
        end_time = timeit.default_timer()
        logging.warning(f"run Done {end_time - start_time}sec")

    def _ready(self):
        logging.warning(f"ready Init")
        logging.warning(f"copy dir {self._db_path} to {self._dest_db_path}")
        shutil.copytree(self._db_path, self._dest_db_path)
        logging.warning(f"ready Release")

    def _prune_db(self):
        logging.warning(f"prune_db Init")
        new_db = plyvel.DB(name=self._dest_db_path)

        index = 0

        for k, v in new_db.iterator():
            if len(k) == HASH_LEN and v != b'':
                new_db.delete(k)
                new_db.put(k, b'')

            # DEBUG
            if index % PRT_SIZE == 0:
                logging.warning(f"prune_db process: {index}")
            index += 1

        new_db.close()
        logging.warning(f"prune_db Release")

    @classmethod
    def _get_last_block_bh(cls, src_db) -> int:
        last_block_hash: bytes = src_db.get(b'last_block_key')
        last_block_bytes: bytes = src_db.get(last_block_hash)
        last_block_str: str = bytes.decode(last_block_bytes)
        last_block: dict = json.loads(last_block_str)

        if isinstance(last_block["height"], int):
            return last_block["height"]
        else:
            return int(last_block["height"], 0)

    def _recover_blocks(self):
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path)

        last_block_bh: int = self._get_last_block_bh(src_db)
        recover_bh_start: int = last_block_bh - self._remain_blocks
        self._recover_block(
            block_height=0,
            src_db=src_db,
            new_db=new_db
        )
        for i in range(recover_bh_start, last_block_bh):
            self._recover_block(
                block_height=i,
                src_db=src_db,
                new_db=new_db
            )
        new_db.close()

    @classmethod
    def _recover_block(cls, block_height: int, src_db, new_db):
        key: bytes = b'block_height_key' + block_height.to_bytes(12, 'big')
        block_hash: bytes = src_db.get(key)
        block_data_bytes: bytes = src_db.get(block_hash)
        new_db.put(block_hash, block_data_bytes)

        if block_height == 0:
            return

        block_data_str: str = bytes.decode(block_data_bytes)
        block_data: dict = json.loads(block_data_str)
        if "confirmed_transaction_list" in block_data:
            txs: list = block_data["confirmed_transaction_list"]
        else:
            txs: list = block_data["transactions"]
        for tx in txs:
            if "tx_hash" in tx:
                tx_hash: bytes = tx["tx_hash"].encode()
            else:
                tx_hash: bytes = tx["txHash"].encode()

            tx_data_bytes: bytes = src_db.get(tx_hash)
            new_db.put(tx_hash, tx_data_bytes)


def main():
    prune_db = PruneDatabase(
        db_path="../db_icon_dex",
        dest_path="../new_icon_dex_v1",
        remain_blocks=86400
    )
    prune_db.run()


if __name__ == "__main__":
    main()
