# -*- coding: utf-8 -*-

import os
import random

from icondbtools.data.vote import Vote
from icondbtools.utils import pack


def test_vote(address, timestamp):
    rep = address
    height = random.randint(0, 9999)
    block_hash = os.urandom(32)
    round = random.randint(0, 100)

    expected = Vote(
        rep=rep,
        block_height=height,
        block_hash=block_hash,
        timestamp=timestamp,
        round=round,
    )

    data = expected.to_bytes()
    assert isinstance(data, bytes)
    assert len(data) > 0
    vote = Vote.from_bytes(data)

    assert vote == expected
    assert vote.rep == rep
    assert vote.height == height
    assert vote.block_hash == block_hash
    assert vote.timestamp == timestamp
    assert vote.round == round


def test_votes(address, timestamp):
    rep = address
    height = random.randint(0, 9999)
    block_hash = os.urandom(32)
    round = random.randint(0, 100)

    vote = Vote(
        rep=rep,
        block_height=height,
        block_hash=block_hash,
        timestamp=timestamp,
        round=round,
    )

    expected = [vote]
    data = pack.encode(expected)
    votes = pack.decode(data)
    assert votes == expected
