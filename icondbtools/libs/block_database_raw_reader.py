import json
from typing import Optional

import plyvel

from ..libs import TRANSACTION_COUNT_KEY, NID_KEY, LAST_BLOCK_KEY, PREPS_KEY_PREFIX, BLOCK_HEIGHT_KEY_PREFIX
from ..utils.convert_type import bytes_to_hex


class TransactionParser:
    @staticmethod
    def get_tx_hash_key_from_transaction(transaction: dict) -> Optional[bytes]:
        """
        Parsing transaction which is recorded on the block and return tx_hash
        :return: utf-8 encoded hex string transaction hash. If genesis transaction, return None
        """
        for key in ("txHash", "tx_hash"):
            tx_hash: Optional[str] = transaction.get(key)
            if tx_hash:
                return tx_hash.encode(encoding="UTF-8")


class BlockDatabaseRawReader(object):
    """Read block data from Leveldb managed by Loopchain

    Glossary
    * hash: ex) block_hash, tx_hash in bytes
    * hash_key: block_hash -> hex string without "0x" prefix -> utf-8 encoded hex data
        ex) block_hash_key, tx_hash_key
    """

    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db:
            self._db.close()
            self._db = None

    def get_transaction_by_hash(self, tx_hash: bytes) -> bytes:
        """
        :param tx_hash: tx_hash in bytes not utf-8 encoded hex
        :return: transaction data including the transaction result
        """
        key: bytes = self.convert_hash_to_key(tx_hash)
        return self.get_data_by_key(key)

    def get_transaction_by_key(self, tx_hash_key: bytes) -> bytes:
        return self.get_data_by_key(tx_hash_key)

    def get_transaction_result_by_hash(self, tx_hash: bytes) -> bytes:
        """Transaction_result is contained in tx["result"]

        :param tx_hash: tx_hash in bytes not utf-8 encoded hex
        :return: transaction data including the transaction result
        """
        return self.get_transaction_by_hash(tx_hash)

    @staticmethod
    def get_transactions_from_block(block: bytes) -> list:
        block: dict = json.loads(block)
        version: str = block["version"]
        if version == "0.1a":
            transactions = block["confirmed_transaction_list"]
        else:
            transactions: Optional[list] = block.get("transactions")
        if transactions is None:
            raise ValueError(f"Cannot find transactions from the block."
                             f" check the block version {version}")

        return transactions

    def get_last_block(self) -> Optional[bytes]:
        """Get last block in bytes

        :return: block in bytes
        """
        block_hash_key: bytes = self.get_last_block_hash_key()
        return self.get_data_by_key(block_hash_key)

    def get_last_block_hash_key(self) -> Optional[bytes]:
        """Get last block hash in bytes"""
        return self.get_data_by_key(LAST_BLOCK_KEY)

    def get_block_by_height(self, block_height: int) -> Optional[bytes]:
        """Get block in bytes by block height     

        :param block_height: block height in integer
        :return: block in bytes
        """
        block_hash_key: bytes = self.get_block_hash_key_by_height(block_height)
        if block_hash_key is None:
            return

        return self.get_data_by_key(block_hash_key)

    def get_block_hash_key_by_height(self, block_height: int) -> Optional[bytes]:
        """Get block hash in bytes by block height

        :param block_height: block height in integer
        :return: block hash
        """
        block_height_key: bytes = self.get_block_height_key(block_height)
        return self.get_data_by_key(block_height_key)

    def get_block_by_hash(self, block_hash: bytes) -> Optional[bytes]:
        """Get block in bytes by block hash

        :param block_hash: block_hash in bytes not utf-8 encoded hash
        :return: block in bytes
        """
        key: bytes = self.convert_hash_to_key(block_hash)
        return self.get_data_by_key(key)

    def get_block_by_key(self, block_hash_key: bytes) -> Optional[bytes]:
        return self.get_data_by_key(block_hash_key)

    def get_data_by_key(self, key: bytes) -> Optional[bytes]:
        return self._db.get(key)

    @staticmethod
    def get_block_height_key(block_height: int) -> bytes:
        """Get block height key in bytes

        :param block_height: block height in integer
        :return: block height key
        """
        return BLOCK_HEIGHT_KEY_PREFIX + block_height.to_bytes(12, 'big')

    @staticmethod
    def convert_hash_to_key(data_hash: bytes) -> bytes:
        """Convert hash to loopchain-style key format

        * bytes -> hex string without '0x' -> utf-8 encoding
        * Related keys: block, transaction, transaction_result

        :param data_hash:
        :return: utf-8 encoded key
        """
        return bytes_to_hex(data_hash, prefix="").encode("utf-8")

    def get_nid(self) -> Optional[bytes]:
        """Get NID"""
        return self._db.get(NID_KEY)

    def get_transaction_count(self) -> Optional[bytes]:
        """Get transaction count"""
        return self.get_data_by_key(TRANSACTION_COUNT_KEY)

    def get_reps(self, reps_hash: bytes) -> Optional[bytes]:
        key = PREPS_KEY_PREFIX + reps_hash
        reps = self._db.get(key)
        if reps is None:
            return b"{}"
        return reps
