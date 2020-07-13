# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional
from iconservice.base.address import Address
from ..migrate.block import Block


def create_transaction_requests(converted_tx_params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        convert_transaction_to_request(tx_param) for tx_param in converted_tx_params
    ]


def convert_transaction_to_request(params: dict) -> Dict:
    return {
        "method": "icx_sendTransaction",
        "params": params,
    }


def _create_block_validators(block_dict: dict, leader: Optional["Address"]) -> Optional[List["Address"]]:
    if "prevVotes" not in block_dict:
        return None

    validators: List["Address"] = []

    for item in block_dict["prevVotes"]:
        if not isinstance(item, dict):
            continue

        vote = Vote.from_dict(item)
        if leader != vote.rep:
            validators.append(vote.rep)

    return validators


def _create_prev_block_votes(
    block_dict: dict, leader: Optional["Address"], main_preps: Optional["NodeContainer"]
) -> Optional[List[Tuple["Address", int]]]:
    if "prevVotes" not in block_dict:
        return None

    if main_preps is None:
        return None

    ret: List[Tuple["Address", int]] = []
    prev_votes = {}

    # Parse prevVotes
    for item in block_dict["prevVotes"]:
        if not isinstance(item, dict):
            continue

        vote = Vote.from_dict(item)
        prev_votes[vote.rep] = vote

    for main_prep in main_preps:
        address: "Address" = main_prep.address

        if address == leader:
            # Skip it if address is a leader address
            continue

        vote_result = 1 if address in prev_votes else 0
        ret.append((address, vote_result))

    return ret
