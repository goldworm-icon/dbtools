# -*- coding: utf-8 -*-
# Copyright 2018 ICON Foundation Inc.
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

from iconservice.base.address import Address
from iconservice.icon_constant import FIXED_FEE


class Transaction(object):
    def __init__(self,
                 version: int=3,
                 from_: 'Address'=None,
                 to: 'Address'=None,
                 value: int=0,
                 nid: int=3,
                 step_limit: int=0,
                 nonce: int=None,
                 timestamp: int=0,
                 signature: str=None,
                 tx_hash: bytes=None,
                 data_type: str=None,
                 data: dict=None):
        self.version = version
        self.from_ = from_
        self.to = to
        self.value = value
        self.nid = nid
        self.step_limit = step_limit
        self.nonce = nonce
        self.timestamp = timestamp
        self.signature = signature
        self.tx_hash = tx_hash
        self.data_type = data_type
        self.data = data

        if self.version == 2:
            self.fee = FIXED_FEE

    @staticmethod
    def from_dict(loopchain_tx: dict) -> 'Transaction':
        from_ = Address.from_string(loopchain_tx['from'])
        to = Address.from_string(loopchain_tx['to'])
        step_limit = int(loopchain_tx['stepLimit'], 16)
        signature: str = loopchain_tx['signature']
        tx_hash: bytes = bytes.fromhex(loopchain_tx['txHash'])
        timestamp: int = int(loopchain_tx['timestamp'], 16)

        if 'version' in loopchain_tx:
            version = int(loopchain_tx['version'], 16)
        else:
            version = 2

        if 'value' in loopchain_tx:
            value = int(loopchain_tx['value'], 16)
        else:
            value = 0

        if 'nid' in loopchain_tx:
            nid = int(loopchain_tx['nid'], 16)
        else:
            # mainnet
            nid = 1

        if 'nonce' in loopchain_tx:
            nonce = int(loopchain_tx['nonce'], 16)
        else:
            nonce = None

        return Transaction(
            version=version,
            nid=nid,
            from_=from_,
            to=to,
            value=value,
            step_limit=step_limit,
            nonce=nonce,
            timestamp=timestamp,
            signature=signature,
            tx_hash=tx_hash)
