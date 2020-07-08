# -*- coding: utf-8 -*-

from ..libs.loopchain_block import LoopchainBlock
from iconservice.base.address import Address
import msgpack


class Block(object):
    def __init__(self,
                 version: str = None,
                 height: int = -1,
                 timestamp: int = -1,
                 block_hash: bytes = None,
                 prev_block_hash: bytes = None,
                 leader: 'Address' = None,
                 state_hash: bytes = None,
                 transactions: list = None):
        self.version = version
        # self.height = height
        self.block_hash = block_hash
        # self.prev_block_hash = prev_block_hash
        self.timestamp: int = timestamp
        self.leader = leader
        self.state_hash: bytes = state_hash
        self.transactions = transactions

    @classmethod
    def from_bytes(cls, data: bytes, height: int, prev_block_hash: bytes):
        pass

    @classmethod
    def from_loopchain_block(cls, loopchain_block: LoopchainBlock):
        pass

    def to_bytes(self) -> bytes:
        msg.pa
