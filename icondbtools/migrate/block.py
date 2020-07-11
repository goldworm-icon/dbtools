# -*- coding: utf-8 -*-

from enum import IntEnum, auto
from typing import Dict, List, Any

from iconservice.base.address import Address

from ..libs.loopchain_block import LoopchainBlock
from ..utils import pack
from ..utils.transaction import tx_dict_to_params


class Block(object):
    class Index(IntEnum):
        VERSION = auto()
        HEIGHT = auto()
        TIMESTAMP = auto()
        BLOCK_HASH = auto()
        PREV_BLOCK_HASH = auto()
        LEADER = auto()
        STATE_HASH = auto()
        TXS = auto()

    def __init__(
        self,
        version: str = None,
        height: int = -1,
        timestamp: int = -1,
        block_hash: bytes = None,
        prev_block_hash: bytes = None,
        leader: "Address" = None,
        state_hash: bytes = None,
        transactions: List[Dict[str, Any]] = None,
    ):
        self.version = version
        self.height = height
        self.timestamp: int = timestamp
        self.block_hash = block_hash
        self.prev_block_hash = prev_block_hash
        self.leader = leader
        self.state_hash: bytes = state_hash
        self.transactions: List[Dict[str, Any]] = transactions
        """
        :param transactions: transactions which contains items have already been converted to object
        """

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = pack.decode(data)
        assert isinstance(obj, list)

        return cls(
            version=obj[cls.Index.VERSION],
            height=obj[cls.Index.HEIGHT],
            timestamp=obj[cls.Index.TIMESTAMP],
            block_hash=obj[cls.Index.BLOCK_HASH],
            prev_block_hash=obj[cls.Index.PREV_BLOCK_HASH],
            leader=obj[cls.Index.LEADER],
            state_hash=obj[cls.Index.STATE_HASH],
            transactions=obj[cls.Index.TXS],
        )

    @classmethod
    def from_loopchain_block(cls, loopchain_block: LoopchainBlock) -> "Block":
        transactions = [
            tx_dict_to_params(tx_dict, loopchain_block.timestamp)
            for tx_dict in loopchain_block.transactions
        ]

        return cls(
            version=loopchain_block.version,
            height=loopchain_block.height,
            timestamp=loopchain_block.timestamp,
            block_hash=loopchain_block.block_hash,
            prev_block_hash=loopchain_block.prev_block_hash,
            leader=loopchain_block.leader,
            state_hash=loopchain_block.state_hash,
            transactions=transactions,
        )

    def to_bytes(self) -> bytes:
        obj = [
            self.version,
            self.height,
            self.timestamp,
            self.block_hash,
            self.prev_block_hash,
            self.leader,
            self.state_hash,
            self.transactions,
        ]
        return pack.encode(obj)
