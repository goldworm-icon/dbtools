# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional, Tuple, Set

from iconservice.base.address import Address
from iconservice.base.block import Block

from icondbtools.data.vote import Vote
from ..data.node_container import NodeContainer
from ..migrate.block import Block as BinBlock


def create_transaction_requests(
    converted_tx_params: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    return [
        {"method": "icx_sendTransaction", "params": params}
        for params in converted_tx_params
    ]


def create_iconservice_block(bin_block: BinBlock) -> Block:
    return Block(
        block_height=bin_block.height,
        block_hash=bin_block.block_hash,
        timestamp=bin_block.timestamp,
        prev_hash=bin_block.prev_block_hash,
    )


def create_block_validators(
    prev_votes: Optional[List[Vote]], leader: Optional[Address],
) -> Optional[List[Address]]:
    if prev_votes is None:
        return None

    validators: List[Address] = []

    for vote in prev_votes:
        assert isinstance(vote, Vote)
        if leader != vote.rep:
            validators.append(vote.rep)

    return validators


def create_prev_block_votes(
    prev_votes: Optional[List[Vote]],
    leader: Optional[Address],
    main_preps: Optional["NodeContainer"],
) -> Optional[List[Tuple[Address, int]]]:
    if prev_votes is None:
        return None

    if main_preps is None:
        return None

    ret: List[Tuple[Address, int]] = []
    votes: Set[Address] = set()

    for vote in prev_votes:
        assert isinstance(vote, Vote)
        votes.add(vote.rep)

    for main_prep in main_preps:
        address: Address = main_prep.address

        if address == leader:
            # Skip it if address is a leader address
            continue

        vote_result = 1 if address in votes else 0
        ret.append((address, vote_result))

    return ret
