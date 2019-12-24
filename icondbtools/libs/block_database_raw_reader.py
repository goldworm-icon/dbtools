import json
from typing import Optional

import plyvel


class TransactionParser:
    @staticmethod
    def get_tx_hash_from_transaction(transaction: dict) -> Optional[bytes]:
        """
        Parsing transaction which is recorded on the block and return tx_hash
        :return: transaction hash. If genesis transaction, return None
        """
        tx_hash: Optional[bytes] = None
        version: Optional[str] = transaction.get("version")
        if version is None and transaction.get("tx_hash") is None:
            # Incase of Genesis transaction
            return tx_hash

        if version == "0x3":
            tx_hash: bytes = transaction["txHash"].encode(encoding="UTF-8")
        elif version is None and transaction.get("tx_hash") is not None:
            # Incase of tx v2
            tx_hash: bytes = transaction["tx_hash"].encode(encoding="UTF-8")
        return tx_hash


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

    def get_transaction_by_hash(self, tx_hash: bytes) -> bytes:
        transaction: bytes = self._db.get(tx_hash)
        return transaction

    @staticmethod
    def get_transactions_from_block(block: bytes) -> list:
        block: dict = json.loads(block)
        version: str = block["version"]
        if version == "0.1a":
            transactions = block["confirmed_transaction_list"]
        elif version == "0.3" or version == "0.4":
            transactions = block["transactions"]
        else:
            raise ValueError(f"Not Considered block version. {version}")

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
