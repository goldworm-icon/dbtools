# -*- coding: utf-8 -*-

from enum import IntEnum, auto
from typing import Dict, List, Any, Optional, Iterable

from iconservice.base.address import Address
from ..libs.loopchain_block import LoopchainBlock
from icondbtools.data.vote import Vote
from ..utils import pack
from ..utils.convert_type import bytes_to_hex
from ..utils.transaction import tx_dict_to_params


class Block(object):
    """Block containing block data from loopchain db

    All field values are already converted to each original type compared to LoopchainBlock
    """

    class Index(IntEnum):
        VERSION = 0
        HEIGHT = auto()
        TIMESTAMP = auto()
        BLOCK_HASH = auto()
        PREV_BLOCK_HASH = auto()
        LEADER = auto()
        STATE_HASH = auto()
        PREV_VOTES = auto()
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
        prev_votes: Optional[List[Vote]] = None,
        transactions: List[Dict[str, Any]] = None,
    ):
        """
        :param transactions: transactions which contains items have already been converted to object
        """

        self.version = version
        self.height = height
        self.timestamp: int = timestamp
        self.block_hash = block_hash
        self.prev_block_hash = prev_block_hash
        self.leader = leader
        self.state_hash: bytes = state_hash
        self.prev_votes: Optional[List[Vote]] = prev_votes
        self.transactions: List[Dict[str, Any]] = transactions

    def __str__(self):
        return (
            f"version={self.version} "
            f"height={self.height} "
            f"timestamp={self.timestamp} "
            f"block_hash={bytes_to_hex(self.block_hash)} "
            f"prev_block_hash={bytes_to_hex(self.prev_block_hash)} "
            f"leader={self.leader} "
            f"state_hash={bytes_to_hex(self.state_hash)} "
            f"prev_votes={self.prev_votes} "
            f"transactions={self.transactions}"
        )

    def __dir__(self) -> Iterable[str]:
        return (
            "version",
            "height",
            "timestamp",
            "block_hash",
            "prev_block_hash",
            "leader",
            "state_hash",
            "prev_votes",
            "transactions",
        )

    def __eq__(self, other):
        try:
            for attr in dir(self):
                if getattr(self, attr) != getattr(other, attr):
                    return False
        except:
            return False

        return True

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = pack.decode(data)
        assert isinstance(obj, list)
        return cls(*obj)

    @classmethod
    def from_loopchain_block(cls, loopchain_block: LoopchainBlock) -> "Block":
        prev_votes: Optional[list] = loopchain_block.prev_votes
        if prev_votes is not None:
            prev_votes = [
                Vote.from_dict(data) for data in prev_votes if isinstance(data, dict)
            ]

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
            prev_votes=prev_votes,
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
            self.prev_votes,
            self.transactions,
        ]
        return pack.encode(obj)
