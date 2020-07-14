# -*- coding: utf-8 -*-

__all__ = ("ExtType", "encode", "decode", "Meta")

from abc import ABCMeta, abstractmethod
from enum import Enum

import msgpack

from iconservice.base.address import Address, MalformedAddress, AddressPrefix


class ExtType(Enum):
    ADDRESS = 0
    MALFORMED_ADDRESS = 1
    BIGINT = 2
    VOTE = 3


# Do not access this variable directly
registry = {}


class Meta(ABCMeta):
    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        register_class(cls)
        return cls


def register_class(cls):
    ext_type = cls.get_ext_type()
    if isinstance(ext_type, int):
        registry[ext_type] = cls
        print(registry)


class Serializable(metaclass=Meta):
    @classmethod
    @abstractmethod
    def get_ext_type(cls) -> ExtType:
        pass

    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes):
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass


def encode(obj: object) -> bytes:
    return msgpack.packb(obj, default=default, use_bin_type=True)


def decode(data: bytes) -> object:
    return msgpack.unpackb(data, ext_hook=ext_hook, raw=False)


def default(obj: object) -> msgpack.ExtType:
    if isinstance(obj, Address):
        code = (
            ExtType.MALFORMED_ADDRESS
            if isinstance(obj, MalformedAddress)
            else ExtType.ADDRESS
        )
        return msgpack.ExtType(code.value, obj.to_bytes_including_prefix())
    elif isinstance(obj, int):
        return msgpack.ExtType(ExtType.BIGINT.value, obj.to_bytes(32, "big", signed=True))
    else:
        return msgpack.ExtType(obj.get_ext_type(), obj.to_bytes())

    # raise TypeError(f"Unknown type: {repr(obj)}")


def ext_hook(code: int, data: bytes):
    if code == ExtType.ADDRESS.value:
        return Address.from_bytes_including_prefix(data)
    elif code == ExtType.MALFORMED_ADDRESS.value:
        return MalformedAddress(AddressPrefix.EOA, data[1:])
    elif code == ExtType.BIGINT.value:
        return int.from_bytes(data, "big", signed=True)
    elif code in registry:
        cls = registry[code]
        return cls.from_bytes(data)

    return msgpack.ExtType(code, data)
