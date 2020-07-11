# -*- coding: utf-8 -*-


import os
from icondbtools.utils import pack
from iconservice.base.address import MalformedAddress, AddressPrefix


def test_encode_and_decode(create_address, block_hash, tx_hash):
    expected = [
        0,
        "hello",
        b"hello",
        True,
        None,
        "",
        MalformedAddress(AddressPrefix.EOA, os.urandom(14)),
        {
            tx_hash: {
                "name": "hello",
                "age": 30,
                "wallet": create_address(),
                "validators": [create_address() for _ in range(10)],
            },
        },
        [0, "hello", b"hello", False, None],
    ]

    data = pack.encode(expected)
    assert pack.decode(data) == expected
