# Copyright 2020 ICON Foundation
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

from enum import IntEnum
from typing import Optional

import plyvel

from ..migrate.block import Block
from ..utils.convert_type import bytes_to_hex


class Bucket(IntEnum):
    BLOCK_HEIGHT = 0
    BLOCK_HASH = 1


class BlockDatabaseReader(object):
    """Read block data from compact block database

    Compact database is created by "migrate" sub-command

    LevelDB data structure
    b"0x00" + height.to_bytes(8, "big"): block data im msgpack format
    b"0x01" + block_hash(32): height.to_bytes(8, "big")
    """

    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db:
            self._db.close()
            self._db = None

    def get_block_by_height(self, block_height: int) -> Optional[Block]:
        key: bytes = self._get_key_by_height(block_height)
        return self._get_block(key)

    def get_block_by_hash(self, block_hash: bytes) -> Optional[Block]:
        key: Optional[bytes] = self._get_key_by_block_hash(block_hash)
        return self._get_block(key)

    def _get_block(self, key: Optional[bytes]) -> Optional[Block]:
        if key is None:
            return None

        value: bytes = self._db.get(key)
        if value is None:
            return None

        return Block.from_bytes(value)

    @classmethod
    def _get_key_by_height(cls, height: int) -> bytes:
        return Bucket.BLOCK_HEIGHT.value.to_bytes(1, "big") + height.to_bytes(8, "big")

    def _get_key_by_block_hash(self, block_hash: bytes) -> Optional[bytes]:
        key: bytes = self._get_key(Bucket.BLOCK_HASH, block_hash)
        key_data: Optional[bytes] = self._db.get(key)

        return self._get_key(Bucket.BLOCK_HEIGHT, key_data)

    @classmethod
    def _get_key(cls, bucket: Bucket, key_data: bytes) -> Optional[bytes]:
        if key_data is None:
            return None

        return bucket.value.to_bytes(1, "big") + key_data
