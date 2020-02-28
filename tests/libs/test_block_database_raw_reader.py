# -*- coding: utf-8 -*-
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

import pytest

from icondbtools.libs.block_database_raw_reader import BlockDatabaseRawReader


class TestBlockDatabaseRawReader(object):
    @pytest.fixture(scope="class")
    def reader(self) -> BlockDatabaseRawReader:
        print("reader() start")
        db_path = "/Users/goldworm/work/icon/db-data/mainnet/db/"

        reader = BlockDatabaseRawReader()
        reader.open(db_path)

        yield reader

        reader.close()
        print("reader() end")

    def test_convert_hash_to_key(self, reader, tx_hash):
        tx_hash_key = reader.convert_hash_to_key(tx_hash)
        assert isinstance(tx_hash_key, bytes)
        assert len(tx_hash_key) == 64

    def test_get_last_block_hash_key(self, reader):
        block_hash_key = reader.get_last_block_hash_key()
        assert isinstance(block_hash_key, bytes)
        assert len(block_hash_key) == 64
