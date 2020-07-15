# -*- coding: utf-8 -*-

__all__ = ("encode", "decode")

import msgpack

from iconservice.base.address import Address, MalformedAddress, AddressPrefix
from . import ExtType
from ..libs.vote import Vote


def encode(obj: object) -> bytes:
    return msgpack.packb(obj, default=default, use_bin_type=True)


def decode(data: bytes) -> object:
    return msgpack.unpackb(data, ext_hook=ext_hook, raw=False)


def default(obj) -> msgpack.ExtType:
    if isinstance(obj, Address):
        code = (
            ExtType.MALFORMED_ADDRESS
            if isinstance(obj, MalformedAddress)
            else ExtType.ADDRESS
        )
        return msgpack.ExtType(code.value, obj.to_bytes_including_prefix())
    elif isinstance(obj, Vote):
        return msgpack.ExtType(ExtType.VOTE.value, obj.to_bytes())
    elif isinstance(obj, int):
        return msgpack.ExtType(ExtType.BIGINT.value, obj.to_bytes(32, "big", signed=True))

    raise TypeError(f"Unknown type: {repr(obj)}")


def ext_hook(code: int, data: bytes):
    if code == ExtType.ADDRESS.value:
        return Address.from_bytes_including_prefix(data)
    elif code == ExtType.MALFORMED_ADDRESS.value:
        return MalformedAddress(AddressPrefix.EOA, data[1:])
    elif code == ExtType.VOTE.value:
        return Vote.from_bytes(data)
    elif code == ExtType.BIGINT.value:
        return int.from_bytes(data, "big", signed=True)

    return msgpack.ExtType(code, data)
