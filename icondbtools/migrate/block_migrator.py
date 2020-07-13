# -*- coding: utf-8 -*-

import plyvel

from .block import Block
from ..libs.block_database_raw_reader import BlockDatabaseRawReader
from ..libs.loopchain_block import LoopchainBlock
from iconcommons.logger import Logger


TAG = "MGT"


def get_db_key_by_height(height: int) -> bytes:
    return bytes(1) + int.to_bytes(height, 8, "big")


class BlockMigrator(object):
    MAX_BYTES_TO_CACHE = 1_000_000

    def __init__(self):
        self._block_reader = BlockDatabaseRawReader()
        self._new_db = None
        self._write_batch = None
        self._bytes_to_write = 0

    def open(self, db_path: str, new_db_path: str):
        self._block_reader.open(db_path)

        new_db = plyvel.DB(new_db_path, create_if_missing=True)
        self._write_batch = new_db.write_batch()
        self._bytes_to_write = 0

    def close(self):
        self._block_reader.close()
        self._bytes_to_write = 0

        if self._new_db:
            self._new_db.close()
            self._new_db = None

    def run(self, start: int, end: int):
        for height in range(start, end + 1):
            # Read an original block data from loopchain db
            loopchain_block = self._read_loopchain_block(height)

            # Convert loopchain block to binary block
            block = self._convert_block(loopchain_block)

            # Write binary block data to write_batch of target db
            self._write_block(block)

            # Write write_batch to the target db
            if self._bytes_to_write >= self.MAX_BYTES_TO_CACHE:
                self._flush()

        # Write data remaining in write_batch to the target db
        self._flush()

    def _read_loopchain_block(self, height: int) -> LoopchainBlock:
        data: bytes = self._block_reader.get_block_by_height(height)
        if not data:
            raise TypeError(f"No block data: BH={height}")

        return LoopchainBlock.from_bytes(data)

    @classmethod
    def _convert_block(cls, loopchain_block: LoopchainBlock) -> Block:
        block = Block.from_loopchain_block(loopchain_block)
        print(block)

        return block

    def _write_block(self, block: Block):
        key: bytes = get_db_key_by_height(block.height)
        value: bytes = block.to_bytes()
        self._write_batch.put(key, value)

        self._bytes_to_write += len(value)

    def _flush(self):
        if self._bytes_to_write > 0:
            self._write_batch.write()
            self._bytes_to_write = 0
