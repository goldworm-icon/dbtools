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

from typing import Optional

from iconservice.base.address import Address
from icondbtools.utils.convert_type import convert_hex_str_to_int, convert_hex_str_to_bytes


class Vote(object):
    def __init__(self, rep: 'Address', block_height: int, block_hash: bytes, timestamp: int, round: int):
        self.rep = rep
        self.height = block_height
        self.block_hash = block_hash
        self.timestamp = timestamp
        self.round = round

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> 'Vote':
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
        rep: 'Address' = Address.from_string(data["rep"])
        height: int = convert_hex_str_to_int(data["blockHeight"])
        block_hash: bytes = convert_hex_str_to_bytes(data["blockHash"])
        timestamp: int = convert_hex_str_to_int(data["timestamp"])
        round_: int = data["round_"]

        return Vote(rep=rep, block_height=height, block_hash=block_hash, timestamp=timestamp, round=round_)
