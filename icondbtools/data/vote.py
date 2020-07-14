# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import IntEnum, auto
from typing import Optional

from iconservice.base.address import Address

from ..utils import pack
from ..utils.convert_type import str_to_int, convert_hex_str_to_bytes


class Vote(pack.Serializable):

    class Index(IntEnum):
        REP = auto()
        HEIGHT = auto()
        HASH = auto()
        TIMESTAMP = auto()
        ROUND = auto()

    @classmethod
    def get_ext_type(cls) -> int:
        return pack.ExtType.VOTE.value

    def __init__(
        self,
        rep: Address,
        block_height: int,
        block_hash: bytes,
        timestamp: int,
        round: int,
    ):
        self.rep = rep
        self.height = block_height
        self.block_hash = block_hash
        self.timestamp = timestamp
        self.round = round

    def __str__(self):
        return (
            f"rep={self.rep} "
            f"height={self.height} "
            f"hash={self.block_hash} " 
            f"timestamp={self.timestamp} "
            f"round={self.round}"
        )

    def __eq__(self, other):
        return (
            self.rep == other.rep and
            self.height == other.height and
            self.block_hash == other.block_hash and
            self.timestamp == other.timestamp and
            self.round == other.round
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "Vote":
        """
            {
                "blockHash’: ‘0xd5cc6d2d6998dd6d6f9c544232956bcf1108003b5253e8383d7628a10939913a’,
                "blockHeight’: ‘0x9e1ce3’,
                ‘rep’: ‘hxd0d9b0fee857de26fd1e8b15209ca15b14b851b2’,
                ‘round_‘: 1,
                ‘signature’: ‘SDsaAJ6FZdgdFeS0eBVxj/CGCcvIghkqBiUmKRFcup9VSBVo5K+oJHgvNjL7CSBCj1+AHrERDKHYdROyIhxbmAE=’,
                ‘timestamp’: ‘0x5960a8b1afc92’
            }

        :param data:
        :return:
        """
        rep: Address = Address.from_string(data["rep"])
        height: int = str_to_int(data["blockHeight"])
        block_hash: bytes = convert_hex_str_to_bytes(data["blockHash"])
        timestamp: int = str_to_int(data["timestamp"])

        # Block 0.4: round_
        # Block 0.5: round
        round_: int = data.get("round", data.get("round_"))
        return Vote(
            rep=rep,
            block_height=height,
            block_hash=block_hash,
            timestamp=timestamp,
            round=round_,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "Vote":
        obj: object = pack.decode(data)
        assert isinstance(obj, list)

        return cls(*obj)

    def to_bytes(self) -> bytes:
        obj = [
            self.rep,
            self.height,
            self.block_hash,
            self.timestamp,
            self.round,
        ]

        return pack.encode(obj)
