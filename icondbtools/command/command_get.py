# -*- coding: utf-8 -*-

from typing import Optional, Union, Iterator

from iconservice.base.address import Address
from iconservice.iconscore.db import KeyType, Key, ContainerTag
from iconservice.utils import bytes_to_int, int_to_bytes
from .command import Command
from ..libs.state_database_reader import (
    StateDatabaseReader, create_container_db_key,
)


class CommandGet(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "get"
        desc = "Read state data from a given contract"

        # create the parser for the 'sync' command
        parser = sub_parser.add_parser(name, help=desc)
        parser.add_argument(
            "--state-db",
            type=str,
            required=True,
            default=".statedb/icon_dex/",
            help="iconservice state dbpath: .statedb/icon_dex/"
        )
        parser.add_argument(
            "--score",
            type=str,
            required=True,
            help="score address ex) cx63af7f2e073985a9e9965765e809f66da3b0f238",
        )
        parser.add_argument(
            "--container-type",
            type=int,
            required=False,
            default=2,
            help="Container DB Type: 0(ArrayDB), 1(DictDB), 2(VarDB) default(2)"
        )
        parser.add_argument(
            "--sep",
            type=str,
            required=False,
            default=".",
            help="Key separator. default(.)",
        )
        parser.add_argument(
            "--value-type",
            type=str,
            required=False,
            help="Display format: int, str, bytes, hex, address, bool"
        )
        parser.add_argument(
            "key",
            help="Ex: name.0, token.hxd7cf2f6bcbbfa542a08e9cd0e48bf848018a2ec7.value",
        )
        parser.add_argument(
            "--rlp-key",
            action="store_true",
            help="Select key encoding format: rlp-key(true) or bar-key(false)",
        )
        parser.set_defaults(func=self.run)

    def run(self, args) -> int:
        print(args)
        value_type: str = args.value_type
        use_rlp: bool = args.rlp_key
        score = Address.from_string(args.score)
        if not score.is_contract:
            print(f"Error: Invalid score address: {score}")
            return 1

        try:
            reader = StateDatabaseReader()
            reader.open(args.state_db)
            key = _create_container_db_key(score, args)
            value: bytes = reader.get_by_key(key)
            print(f"key={key} use_rlp={use_rlp}")
            print(f"value={_convert_value(value, value_type)}")
        except Exception as e:
            raise e
        finally:
            reader.close()
            pass


def _create_container_db_key(score: Address, args) -> bytes:
    container_type: int = args.container_type
    sep: str = args.sep
    key_arg: str = args.key
    use_rlp: bool = args.rlp_key
    print(container_type, KeyType.ARRAY.value, KeyType.VAR.value, KeyType.DICT.value)

    if container_type == 0:
        key = _create_array_db_key(score, key_arg, sep, use_rlp)
    elif container_type == 1:
        key = _create_dict_db_key(score, key_arg, sep, use_rlp)
    else:
        key = _create_var_db_key(score, key_arg, sep, use_rlp)

    return key


def _create_array_db_key(score: Address, key_arg: str, sep: str, use_rlp: bool) -> bytes:
    str_keys = key_arg.split(sep)
    if len(str_keys) == 1:
        last_key = b"size"
    else:
        last_key = int_to_bytes(int(str_keys[-1], 10))
        str_keys = str_keys[:-1]

    bin_keys = (
        Key(str_key.encode("utf-8"), KeyType.ARRAY)
        for str_key in str_keys
    )
    return create_container_db_key(score, bin_keys, last_key, use_rlp)


def _create_dict_db_key(score: Address, key_arg: str, sep: str, use_rlp: bool) -> bytes:
    str_keys = key_arg.split(sep)
    last_key = str_keys[-1].encode("utf-8")

    bin_keys = (
        Key(str_key.encode("utf-8"), KeyType.DICT)
        for str_key in str_keys[:-1]
    )
    return create_container_db_key(score, bin_keys, last_key, use_rlp)


def _create_var_db_key(score: Address, key_arg: str, sep: str, use_rlp: bool) -> bytes:
    str_keys = key_arg.split(sep)
    last_key = Key(b"", KeyType.DUMMY)
    bin_keys = (
        Key(str_key.encode("utf-8"), KeyType.VAR)
        for str_key in str_keys
    )
    return create_container_db_key(score, bin_keys, last_key, use_rlp)


def _convert_value(value: Optional[bytes], value_type: str) -> Union[int, str, bytes, Address]:
    if value is not None:
        if value_type == "int":
            value = bytes_to_int(value)
        elif value_type == "str":
            value = value.decode("utf-8")
        elif value_type == "address":
            value = Address.from_bytes(value)
        elif value_type == "hex":
            value = value.hex()
        else:
            # In bytes case, do nothing
            pass

    return value
