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
import plyvel

from icondbtools.utils.utils import remove_dir, make_dir

TMP_ROOT_PATH = "tmp"


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
        self._ready_v1()
        self._make_new_db_v1()

    def run_v2(self):
        self._ready_v2()
        self._make_new_db_v2()

    def _ready_v1(self):
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path, create_if_missing=True)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db", create_if_missing=True)

        block_height_key = b'block_height_key'
        for key, value in src_db.iterator():
            if key.startswith(block_height_key):
                # hash or # block height key mapper
                tmp_db.put(key, value)
            new_db.put(key, value)

        tmp_db.close()
        new_db.close()
        src_db.close()

    def _make_new_db_v1(self):
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db")

        last_block_bh: int = self._get_last_block_bh(src_db)

        prune_bh = last_block_bh - self._remain_blocks
        for i in range(last_block_bh):
            self._put_block_to_new_db(
                tmp_db=tmp_db,
                new_db=new_db,
                prune_bh=prune_bh,
                index=i
            )

        tmp_db.close()
        new_db.close()
        src_db.close()

    def _ready_v2(self):
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path, create_if_missing=True)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db", create_if_missing=True)

        hash_len = 64
        block_height_key = b'block_height_key'
        for key, value in src_db.iterator():
            if len(key) == hash_len or key.startswith(block_height_key):
                # hash or # block height key mapper
                tmp_db.put(key, value)
            else:
                new_db.put(key, value)

        tmp_db.close()
        new_db.close()
        src_db.close()

    def _make_new_db_v2(self):
        src_db = plyvel.DB(name=self._db_path)
        new_db = plyvel.DB(name=self._dest_db_path)
        tmp_db = plyvel.DB(name=f"{TMP_ROOT_PATH}/tmp_db")

        last_block_bh: int = self._get_last_block_bh(src_db)

        prune_bh = last_block_bh - self._remain_blocks
        for i in range(last_block_bh):
            block_data_bytes: bytes = self._put_block_to_new_db(
                tmp_db=tmp_db,
                new_db=new_db,
                prune_bh=prune_bh,
                index=i
            )

            if i > 0:
                block_data_str: str = bytes.decode(block_data_bytes)
                block_data: dict = json.loads(block_data_str)
                txs: list = block_data["transactions"]
                for tx in txs:
                    tx_hash: bytes = tx["txHash"].encode()
                    tx_data: bytes = tmp_db.get(tx_hash)
                    if i < prune_bh:
                        new_db.put(tx_hash, b'')
                    else:
                        new_db.put(tx_hash, tx_data)

        tmp_db.close()
        new_db.close()
        src_db.close()

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
    def _put_block_to_new_db(cls, tmp_db, new_db, prune_bh: int, index: int) -> bytes:
        key: bytes = b'block_height_key' + index.to_bytes(12, 'big')
        block_hash: bytes = tmp_db.get(key)
        block_data_bytes: bytes = tmp_db.get(block_hash)
        if index < prune_bh:
            new_db.put(block_hash, block_data_bytes)
        else:
            new_db.put(block_hash, b'')
        return block_data_bytes


def main():
    prune_db = PruneDatabase(
        db_path="../db_7100_icon_dex",
        dest_path="../new_icon_dex",
        remain_blocks=86400
    )
    prune_db.run_v1()
    prune_db.clear()
    prune_db.debug_prt("../new_icon_dex")


if __name__ == "__main__":
    main()
