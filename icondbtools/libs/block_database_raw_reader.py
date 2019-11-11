import plyvel


class BlockDatabaseRawReader(object):
    """Read block data from Leveldb managed by Loopchain"""

    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db:
            self._db.close()
            self._db = None

    def get_last_block(self) -> bytes:
        """Get last block in bytes

        :return: block in bytes
        """
        last_block_key = b'last_block_key'
        block_hash: bytes = self._db.get(last_block_key)
        block: bytes = self._db.get(block_hash)
        return block

    def get_block_by_height(self, block_height: int) -> bytes:
        """Get block in bytes by block height     

        :param block_height: block height in integer
        :return: block in bytes
        """
        block_height_key: bytes = self.get_block_height_key(block_height)
        block_hash: bytes = self._db.get(block_height_key)
        if block_hash is None:
            return

        block: bytes = self._db.get(block_hash)
        return block

    @staticmethod
    def get_block_height_key(block_height: int) -> bytes:
        """Get block height key in bytes

        :param block_height: block height in integer
        :return: block height key
        """
        prefix_block_height_key: bytes = b'block_height_key'
        block_height_key: bytes = prefix_block_height_key + block_height.to_bytes(12, 'big')
        return block_height_key
