# -*- coding: utf-8 -*-

__all__ = ("encode", "decode")

from enum import Enum

import msgpack
from iconservice.base.address import Address, MalformedAddress, AddressPrefix


class ExtType(Enum):
    ADDRESS = 0
    MalformedAddress = 1


def encode(obj: object) -> bytes:
    return msgpack.packb(obj, default=default, use_bin_type=True)


def decode(data: bytes) -> object:
    return msgpack.unpackb(data, ext_hook=ext_hook, raw=False)


def default(obj) -> msgpack.ExtType:
    if isinstance(obj, Address):
        code = (
            ExtType.MalformedAddress
            if isinstance(obj, MalformedAddress)
            else ExtType.ADDRESS
        )
        return msgpack.ExtType(code.value, obj.to_bytes_including_prefix())

    raise TypeError(f"Unknown type: {repr(obj)}")


def ext_hook(code, data):
    if code == ExtType.ADDRESS.value:
        return Address.from_bytes_including_prefix(data)
    elif code == ExtType.MalformedAddress.value:
        return MalformedAddress(AddressPrefix.EOA, data[1:])

    return msgpack.ExtType(code, data)
