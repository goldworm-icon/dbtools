import random
import os
import pytest

from icondbtools.migrate.block import Block
from icondbtools.data.vote import Vote


def test_block(address, timestamp):
    height = random.randint(0, 9999)
    block_hash: bytes = os.urandom(32)
    prev_block_hash: bytes = os.urandom(32)
    state_hash: bytes = os.urandom(32)

    prev_votes = [
        Vote(address, height, block_hash, timestamp, 0)
        for _ in range(22)
    ]

    expected = Block(
        version="0.5",
        height=height,
        timestamp=timestamp,
        block_hash=block_hash,
        prev_block_hash=prev_block_hash,
        leader=address,
        state_hash=state_hash,
        prev_votes=prev_votes,
        transactions=None
    )

    data: bytes = expected.to_bytes()
    block = Block.from_bytes(data)
    assert block == expected
