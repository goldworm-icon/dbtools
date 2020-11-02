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

import plyvel
import timeit

from icondbtools.utils.utils import remove_dir, make_dir

TMP_ROOT_PATH: str = "tmp"
WB_SIZE: int = 5_000
PRT_SIZE: int = 10_000


class PruneDatabase:
    """Prune block data from leveldb managed by loopchain
    """

    def __init__(self, db_path: str, dest_path: str, remain_blocks: int):
        self._db_path: str = db_path
        self._dest_db_path: str = dest_path
        self._remain_blocks: int = remain_blocks

        remove_dir(TMP_ROOT_PATH)
        make_dir(TMP_ROOT_PATH)

    def run_v1(self):
        start_time = timeit.default_timer()

        logging.warning(f"run_v1 Start")
        self._ready_v1()
        self._make_new_db_v1()
        end_time = timeit.default_timer()
        logging.warning(f"run_v1 Done {end_time - start_time}sec")

    def run_v2(self):
        start_time = timeit.default_timer()
        logging.warning(f"run_v2 Start")
        self._ready_v2()
        self._make_new_db_v2()
        end_time = timeit.default_timer()
        logging.warning(f"run_v2 Done {end_time - start_time}sec")

    def _ready_v1(self):
        logging.warning(f"ready_v1 Init")
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path, create_if_missing=True)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db", create_if_missing=True)

        logging.warning(f"ready_v1 Process Start")
        block_height_key = b'block_height_key'
        total_cnt: int = 0

        tmp_db_cache: dict = {}
        new_db_cache: dict = {}

        for key, value in src_db.iterator():
            if key.startswith(block_height_key):
                # hash or # block height key mapper
                tmp_db_cache[key] = value
                self._db_put_batch_with_clear(tmp_db, tmp_db_cache)
            new_db_cache[key] = value
            self._db_put_batch_with_clear(new_db, new_db_cache)
            total_cnt += 1

            # DEBUG
            if total_cnt % PRT_SIZE == 0:
                logging.warning(f"ready_v1 total_cnt: {total_cnt}")

        self._db_put_batch(tmp_db, tmp_db_cache)
        self._db_put_batch(new_db, new_db_cache)

        logging.warning(f"ready_v1 Process Done")
        logging.warning(f"ready_v1 total_cnt: {total_cnt}")

        tmp_db.close()
        new_db.close()
        src_db.close()
        logging.warning(f"ready_v1 Release")

    def _make_new_db_v1(self):
        logging.warning(f"make_new_db_v1 Init")
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db")

        last_block_bh: int = self._get_last_block_bh(src_db)

        logging.warning(f"make_new_db_v1 Process Start")
        prune_bh = last_block_bh - self._remain_blocks

        new_db_cache: dict = {}

        prune_cnt: int = 0
        for i in range(prune_bh):
            key: bytes = b'block_height_key' + i.to_bytes(12, 'big')
            block_hash: bytes = tmp_db.get(key)
            if 0 < i:
                new_db_cache[block_hash] = b''
                self._db_put_batch_with_clear(new_db, new_db_cache)
                prune_cnt += 1

                # DEBUG
                if prune_cnt % PRT_SIZE == 0:
                    logging.warning(f"make_new_db_v1 prune_cnt: {prune_cnt}")

        self._db_put_batch(new_db, new_db_cache)

        logging.warning(f"make_new_db_v1 Process Done")
        logging.warning(f"make_new_db_v1 prune_cnt: {prune_cnt}")

        tmp_db.close()
        new_db.close()
        src_db.close()
        logging.warning(f"ready_v1 Release")

    def _ready_v2(self):
        logging.warning(f"ready_v2 Init")
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path, create_if_missing=True)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db", create_if_missing=True)

        logging.warning(f"ready_v2 Process Start")
        hash_len = 64
        block_height_key = b'block_height_key'
        total_cnt: int = 0

        tmp_db_cache: dict = {}
        new_db_cache: dict = {}

        for key, value in src_db.iterator():
            if len(key) == hash_len or key.startswith(block_height_key):
                # hash or # block height key mapper
                tmp_db_cache[key] = value
                self._db_put_batch_with_clear(tmp_db, tmp_db_cache)
            else:
                new_db_cache[key] = value
                self._db_put_batch_with_clear(new_db, new_db_cache)
            total_cnt += 1

            # DEBUG
            if total_cnt % PRT_SIZE == 0:
                logging.warning(f"ready_v2 total_cnt: {total_cnt}")

        self._db_put_batch(tmp_db, tmp_db_cache)
        self._db_put_batch(new_db, new_db_cache)

        logging.warning(f"ready_v2 Process Done")
        logging.warning(f"ready_v2 total_cnt: {total_cnt}")

        tmp_db.close()
        new_db.close()
        src_db.close()
        logging.warning(f"ready_v2 Release")

    def _make_new_db_v2(self):
        logging.warning(f"make_new_db_v2 Init")
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db")

        last_block_bh: int = self._get_last_block_bh(src_db)

        logging.warning(f"make_new_db_v2 Process Start")
        prune_bh = last_block_bh - self._remain_blocks
        b_prune_cnt: int = 0
        t_prune_cnt: int = 0

        new_db_cache: dict = {}

        for i in range(last_block_bh):
            key: bytes = b'block_height_key' + i.to_bytes(12, 'big')
            block_hash: bytes = tmp_db.get(key)
            block_data_bytes: bytes = tmp_db.get(block_hash)
            if 0 < i < prune_bh:
                new_db_cache[block_hash] = b''
                b_prune_cnt += 1
            else:
                new_db_cache[block_hash] = block_data_bytes
            self._db_put_batch_with_clear(new_db, new_db_cache)

            if i > 0:
                block_data_str: str = bytes.decode(block_data_bytes)
                block_data: dict = json.loads(block_data_str)
                txs: list = block_data["transactions"]
                for tx in txs:
                    tx_hash: bytes = tx["txHash"].encode()
                    tx_data: bytes = tmp_db.get(tx_hash)
                    if i < prune_bh:
                        new_db_cache[tx_hash] = b''
                        t_prune_cnt += 1
                    else:
                        new_db_cache[tx_hash] = tx_data
                    self._db_put_batch_with_clear(new_db, new_db_cache)

            # DEBUG
            if i % PRT_SIZE == 0:
                logging.warning(f"make_new_db_v2 process: {i}")

        self._db_put_batch(new_db, new_db_cache)

        logging.warning(f"make_new_db_v2 Process Done")
        logging.warning(f"make_new_db_v2 b_prune_cnt: {b_prune_cnt}")
        logging.warning(f"make_new_db_v2 t_prune_cnt: {t_prune_cnt}")

        tmp_db.close()
        new_db.close()
        src_db.close()
        logging.warning(f"ready_v2 Release")

    def clear(self):
        remove_dir(TMP_ROOT_PATH)

    @classmethod
    def debug_prt(cls, src_db_path: str):
        make_dir(TMP_ROOT_PATH)
        new_db = plyvel.DB(name=src_db_path)
        with open(f"debug_prt.txt", "w") as f:
            for key, value in new_db.iterator():
                f.writelines(f"key: {key}, value: {value} \n")

    @classmethod
    def _get_last_block_bh(cls, src_db) -> int:
        last_block_hash: bytes = src_db.get(b'last_block_key')
        last_block_bytes: bytes = src_db.get(last_block_hash)
        last_block_str: str = bytes.decode(last_block_bytes)
        last_block: dict = json.loads(last_block_str)
        return int(last_block["height"], 0)

    @classmethod
    def _db_put_batch(cls, db, db_cache):
        with db.write_batch() as wb:
            for k, v in db_cache.items():
                wb.put(k, v)

    @classmethod
    def _db_put_batch_with_clear(cls, db, db_cache):
        if len(db_cache) > WB_SIZE:
            cls._db_put_batch(db, db_cache)
            db_cache.clear()


def main():
    prune_db = PruneDatabase(
        db_path="../db_7100_icon_dex",
        dest_path="../new_icon_dex",
        remain_blocks=10
    )
    prune_db.run_v2()
    prune_db.clear()
    prune_db.debug_prt("../new_icon_dex")


if __name__ == "__main__":
    main()
