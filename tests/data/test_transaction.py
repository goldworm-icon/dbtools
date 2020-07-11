# -*- coding: utf-8 -*-
# Copyright 2020 ICON Foundation
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

from icondbtools.data.transaction import Transaction
from icondbtools.utils.convert_type import bytes_to_hex
from iconservice.base.address import Address
from iconservice.utils import icx_to_loop


class TestTransaction(object):
    def test_from_dict(self, address, block_hash, tx_hash, timestamp):
        from_ = address
        to = Address.from_string("cx0000000000000000000000000000000000000000")
        version = 0x3
        nid = 0x1
        step_limit = 0x1A2C0
        data_type = "call"
        signature = "Ot+ouYw5Fdb4XkfODSv+8X3q7Kn8Fse4D51nLmzY62cPgR/5HZ26JTMCxO6D44pbbCumy8vS6e70XdB+ddL/mwA="
        method = "setStake"
        params = {"value": hex(icx_to_loop(2))}

        tx_data = {
            "version": hex(version),
            "nid": hex(nid),
            "from": str(from_),
            "to": str(to),
            "stepLimit": hex(step_limit),
            "timestamp": hex(timestamp),
            "dataType": data_type,
            "data": {"method": method, "params": params},
            "signature": signature,
            "txHash": bytes_to_hex(tx_hash),
        }

        tx = Transaction.from_dict(tx_data)
        assert tx.version == version
        assert tx.nid == nid
        assert tx.from_ == from_
        assert tx.to == to
        assert tx.value == 0
        assert tx.timestamp == timestamp
        assert tx._step_limit == step_limit
        assert tx.tx_hash == tx_hash
        assert tx.nonce is None
        assert tx.data_type == data_type
        assert isinstance(tx.data, Transaction.CallData)
        assert tx.data.method == method
        assert tx.data.params == params
