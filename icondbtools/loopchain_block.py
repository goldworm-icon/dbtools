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

from iconservice.base.address import AddressPrefix, Address


class LoopchainBlock(object):
    def __init__(self,
                 version: str=None,
                 prev_block_hash: bytes=None,
                 merkle_tree_hash: bytes=None,
                 timestamp: int=0,
                 block_hash: bytes=None,
                 height: int=-1,
                 peer_id: 'Address'=None,
                 commit_state: bytes=None):
        super().__init__()

        self.version: str = version
        self.prev_block_hash: bytes = prev_block_hash
        self.merkle_tree_root_hash: bytes = merkle_tree_hash
        self.timestamp: int = timestamp
        self.block_hash: bytes = block_hash
        self.height: int = height
        self.peer_id: 'Address' = peer_id
        self.commit_state: bytes = commit_state

        self.transactions = None

    @staticmethod
    def from_dict(block: dict) -> 'LoopchainBlock':
        version: str = block['version']
        prev_block_hash: bytes = bytes.fromhex(block['prev_block_hash'])
        merkle_tree_root_hash: bytes = bytes.fromhex(block['merkle_tree_root_hash'])
        timestamp: int = block['time_stamp']
        block_hash: bytes = bytes.fromhex(block['block_hash'])
        height: int = block['height']

        peer_id = block['peer_id']
        if peer_id:
            peer_id: 'Address' = Address.from_string(peer_id)
        else:
            peer_id = None

        try:
            commit_state: bytes = bytes.fromhex(block['commit_state']['icon_dex'])
        except:
            commit_state: bytes = b''

        loopchain_block = LoopchainBlock(
            version=version,
            prev_block_hash=prev_block_hash,
            merkle_tree_hash=merkle_tree_root_hash,
            timestamp=timestamp,
            block_hash=block_hash,
            height=height,
            peer_id=peer_id,
            commit_state=commit_state)

        loopchain_block.transactions: dict = block['confirmed_transaction_list']

        return loopchain_block
