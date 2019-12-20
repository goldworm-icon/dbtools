import json
from typing import Optional, Union

import plyvel


class TransactionGenerator:
    def __init__(self, loopchain_db):
        self._db = loopchain_db
        self._transactions: Optional[list] = None

    def close(self):
        # Todo: should close?
        if self._db:
            self._db.close()
            self._db = None

    @property
    def transactions(self):
        return self._transactions

    @transactions.setter
    def transactions(self, transactions: list):
        self._transactions = transactions

    def _get_tx_by_hash(self, tx_hash: str):
        tx_hash: bytes = tx_hash.encode(encoding="UTF-8")
        tx = self._db.get(tx_hash)
        return tx_hash, tx

    def __iter__(self):
        assert self._transactions is not None
        for transaction in self._transactions:
            yield self._get_tx_by_hash(transaction["txHash"])


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

    @property
    def db(self):
        return self._db

    @staticmethod
    def get_transactions_from_block(block: bytes) -> list:
        block: dict = json.loads(block)
        transactions = []
        # Todo: check the means of duprecating "confirmed_transaction_list"
        if block.get("confirmed_transaction_list") is None:
            transactions = block["transactions"]
        return transactions

    def get_last_block(self) -> Optional[bytes]:
        """Get last block in bytes

        :return: block in bytes
        """
        last_block_key: bytes = b'last_block_key'
        block_hash: bytes = self._db.get(last_block_key)
        block: bytes = self._db.get(block_hash)
        return block

    def get_block_by_height(self, block_height: int) -> Optional[bytes]:
        """Get block in bytes by block height     

        :param block_height: block height in integer
        :return: block in bytes
        """
        block_hash: bytes = self.get_hash_by_height(block_height)
        if block_hash is None:
            return
        block: bytes = self._db.get(block_hash)
        return block

    def get_hash_by_height(self, block_height: int) -> Optional[bytes]:
        """Get block hash in bytes by block height

        :param block_height: block height in integer
        :return: block hash
        """
        block_height_key: bytes = self.get_block_height_key(block_height)
        block_hash: bytes = self._db.get(block_height_key)
        return block_hash

    def get_block_by_hash(self, block_hash: bytes) -> Optional[bytes]:
        """Get block in bytes by block hash

        :param block_hash:
        :return: block in bytes
        """
        block_hash: bytes = block_hash.hex().encode()
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
