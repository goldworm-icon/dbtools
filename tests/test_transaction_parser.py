import unittest

from icondbtools.libs.block_database_raw_reader import TransactionParser


class TestTransactionParser(unittest.TestCase):
    def test_transaction_parsing_v3(self):
        # Transactions in testnet (BH 56)
        # Shorten the 'content' data (as it is too long)
        v3_transactions: list = [{'version': '0x3', 'from': 'hx6e1dd0d4432620778b54b2bbc21ac3df961adf89',
                                  'to': 'cx0000000000000000000000000000000000000001', 'stepLimit': '0x70000000',
                                  'timestamp': '0x592401ffd2d8e', 'nid': '0x50', 'dataType': 'deploy',
                                  'data': {'contentType': 'application/zip',
                                           'content': '0x504b0304140000000800'},
                                  'signature': 'I9iNfiAO6Op0vn7ql3XUbtbk0FbH31bfD6w0cMCGmkBbB7b18aGrrPW5rH0D6jfPae6MSwh2J7iI6IVoFsj4UwA=',
                                  'txHash': 'ed7d1b12fecc6d7819c6e152590efefdc699d9e2c944c0c05f262cfa0a0bf59f'}]
        tx_v3_hash: bytes = b'ed7d1b12fecc6d7819c6e152590efefdc699d9e2c944c0c05f262cfa0a0bf59f'
        for transaction in v3_transactions:
            actual_txhash: bytes = TransactionParser.get_tx_hash_key_from_transaction(transaction)
            self.assertEqual(tx_v3_hash, actual_txhash)

    def test_transaction_parsing_v2(self):
        # Transactions in Mainnet (BH 3900)
        v2_transactions: list = [
            {'from': 'hx6fa11d37bdd65ad0035f258cf6ad94680af78450', 'to': 'hxe2fac977efc0318d6cf52646611e285614b2a196',
             'value': '0x30ca024f987b900000', 'fee': '0x2386f26fc10000', 'timestamp': '1524482271584000',
             'tx_hash': 'f5fc9095f7fb14cd4f28ee164dc0a8e152ae3a2c8bf9b772a3ef7a4db431ebf9',
             'signature': 'QeJq3wjMnwJaz4MPCyPdjuV1xe5E5aZxU4PdoM5xfXkQhbwrk3A8sxhdjA2+YN6bKObBs8YSqEN3IpIbk7lRoAA=',
             'method': 'icx_sendTransaction'}]
        tx_v2_hash: bytes = b'f5fc9095f7fb14cd4f28ee164dc0a8e152ae3a2c8bf9b772a3ef7a4db431ebf9'
        for transaction in v2_transactions:
            actual_txhash: bytes = TransactionParser.get_tx_hash_key_from_transaction(transaction)
            self.assertEqual(tx_v2_hash, actual_txhash)

    def test_transaction_parsing_genesis(self):
        # Success case: Incase of genesis transaction, do not parse transaction (as there is no tx hash)
        # Transactions in Mainnet (BH 0)
        # Shorten 'message' data
        genesis_transactions: list = [{'accounts': [
            {'name': 'god', 'address': 'hx54f7853dc6481b670caf69c5a27c7c8fe5be8269',
             'balance': '0x2961fff8ca4a62327800000'},
            {'name': 'treasury', 'address': 'hx1000000000000000000000000000000000000000', 'balance': '0x0'}],
            'message': "Hyperconnect the world"}]
        for transaction in genesis_transactions:
            actual_txhash = TransactionParser.get_tx_hash_key_from_transaction(transaction)
            self.assertIsNone(actual_txhash)


