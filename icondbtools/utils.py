# -*- coding: utf-8 -*-
# Copyright 2018 ICON Foundation Inc.
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

from iconservice.base.address import Address, MalformedAddress
from iconservice.base.block import Block

from .loopchain_block import LoopchainBlock
from .transaction import Transaction


def create_transaction_requests(loopchain_block: 'LoopchainBlock') -> list:
    tx_requests = []

    if loopchain_block.height == 0:
        request = convert_genesis_transaction_to_request(
            loopchain_block.transactions[0])
        tx_requests.append(request)
    else:
        for tx_dict in loopchain_block.transactions:
            request = convert_transaction_to_request(loopchain_block, tx_dict)
            tx_requests.append(request)

    return tx_requests


def convert_transaction_to_request(loopchain_block: 'LoopchainBlock', tx_dict: dict):
    params = {}
    request = {'method': 'icx_sendTransaction', 'params': params}

    params['from'] = Address.from_string(tx_dict['from'])
    params['to'] = MalformedAddress.from_string(tx_dict['to'])

    if 'tx_hash' in tx_dict:
        params['txHash'] = tx_dict['tx_hash']
    else:
        params['txHash'] = tx_dict['txHash']

    if 'timestamp' in tx_dict:
        params['timestamp'] = str_to_int(tx_dict['timestamp'])
    else:
        params['timestamp'] = loopchain_block.timestamp

    int_keys = ['version', 'fee', 'nid', 'value', 'nonce', 'stepLimit']
    for key in int_keys:
        if key in tx_dict:
            params[key] = int(tx_dict[key], 16)

    object_keys = ['dataType', 'data', 'signature']
    for key in object_keys:
        if key in tx_dict:
            params[key] = tx_dict[key]

    return request


def convert_genesis_transaction_to_request(tx_dict: dict):
    accounts = tx_dict['accounts']
    request = {
        'method': 'icx_sendTransaction',
        'params': {
            'txHash': bytes.fromhex('692f49cde2fe90aa8d04541c2f794e5bf8dcb51c777037909d676d6dd52be1dc')
        },
        'genesisData': {'accounts': accounts}
    }

    for account in accounts:
        account['address'] = Address.from_string(account['address'])
        account['balance'] = int(account['balance'], 16)

    return request


def create_block(loopchain_block: 'LoopchainBlock') -> 'Block':
    return Block(
        block_height=loopchain_block.height,
        block_hash=loopchain_block.block_hash,
        timestamp=loopchain_block.timestamp,
        prev_hash=loopchain_block.prev_block_hash)


def str_to_int(value: str) -> int:
    if value.startswith('0x') or value.startswith('-0x'):
        base = 16
    else:
        base = 10

    return int(value, base)
