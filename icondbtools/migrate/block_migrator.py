# -*- coding: utf-8 -*-

from datetime import timedelta

import plyvel

from icondbtools.migrate.block import Block
from icondbtools.fastsync.block_reader import Bucket
from icondbtools.libs.block_database_raw_reader import BlockDatabaseRawReader
from icondbtools.libs.loopchain_block import LoopchainBlock
from icondbtools.migrate.preps import PReps
from icondbtools.utils.timer import Timer

TAG = "MGT"


def make_block_height_key(height: int) -> bytes:
    return Bucket.BLOCK_HEIGHT.value + int.to_bytes(height, 8, "big")


def make_preps_key(reps_hash: bytes) -> bytes:
    return Bucket.PREPS.value + reps_hash


class BlockMigrator(object):
    """Migrate block data to a new db

    Process
    1. Read block data from loopchain db
    2. Convert loopchain block to binary block
    3. Write binary block data to a new db
    """

    MAX_BYTES_TO_CACHE = 1_000_000

    def __init__(self):
        self._block_reader = BlockDatabaseRawReader()
        self._new_db = None
        self._write_batch = None

        # Status
        self._bytes_to_write = 0
        self._start_height = -1
        self._blocks = -1
        self._blocks_done = 0
        self._timer = Timer()

    def open(self, db_path: str, new_db_path: str):
        self._block_reader.open(db_path)

        new_db = plyvel.DB(new_db_path, create_if_missing=True)
        self._write_batch = new_db.write_batch()
        self._bytes_to_write = 0
        self._new_db = new_db

    def close(self):
        self._block_reader.close()
        self._bytes_to_write = 0

        if self._new_db:
            self._new_db.close()
            self._new_db = None

    def get_last_block(self) -> Block:
        it = self._new_db.iterator(
            prefix=Bucket.BLOCK_HEIGHT.value, reverse=True, include_key=False
        )
        v = next(it)
        it.close()

        return Block.from_bytes(v)

    def run(self, start: int, count: int):
        try:
            self._start_height = start
            self._blocks = count

            self._migrate_preps()
            self._run(start, end=start + count)
        except Exception as e:
            raise e
        finally:
            # Write data remaining in write_batch to the target db
            self._flush()
            self._timer.stop()
            self._print_status()

    def _run(self, start: int, end: int):
        """
        :param start: start block to migrate
        :param end: end block to migrate, exclusive
        """
        self._timer.start()

        for height in range(start, end):
            # Read an original block data from loopchain db
            loopchain_block = self._read_loopchain_block(height)

            # Convert loopchain block to binary block
            block = self._convert_block(loopchain_block)

            # Write binary block data to write_batch of target db
            self._write_block(block)

            # Write write_batch to the target db
            if self._bytes_to_write >= self.MAX_BYTES_TO_CACHE:
                self._flush()
                self._timer.stop()
                self._print_status()

    def _read_loopchain_block(self, height: int) -> LoopchainBlock:
        data: bytes = self._block_reader.get_block_by_height(height)
        if not data:
            raise TypeError(f"No block data: BH={height}")

        return LoopchainBlock.from_bytes(data)

    @classmethod
    def _convert_block(cls, loopchain_block: LoopchainBlock) -> Block:
        block = Block.from_loopchain_block(loopchain_block)
        return block

    def _write_block(self, block: Block):
        key: bytes = make_block_height_key(block.height)
        value: bytes = block.to_bytes()
        self._write_batch.put(key, value)

        self._bytes_to_write += len(value)
        self._blocks_done += 1

    def _flush(self):
        if self._bytes_to_write > 0:
            self._write_batch.write()
            self._write_batch.clear()
            self._bytes_to_write = 0

    def _print_status(self):
        blocks_done = self._blocks_done
        height = self._start_height + (blocks_done - 1)

        percent: float = blocks_done * 100.0 / self._blocks
        eta = int(self._timer.duration() * (self._blocks - blocks_done) / blocks_done)

        status = (
            f"{percent:.1f}%",
            f"{height}",
            f"{blocks_done}/{self._blocks}",
            f"{timedelta(seconds=eta)}",
        )

        print(" ".join(status), flush=True)

    def _migrate_preps(self):
        reps_data: dict = self._block_reader.get_reps_data()
        for key, value in reps_data.items():
            preps_key: bytes = make_preps_key(key)
            preps = PReps.from_json_bytes(value)
            value = preps.to_bytes()
            self._write_batch.put(preps_key, value)


if __name__ == '__main__':
    bm = BlockMigrator()
    bm.open(db_path="../db_icon_dex", new_db_path="../newdb")
    bm.run(22600000, 100000)
