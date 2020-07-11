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

import unittest

from iconservice.base.address import Address, AddressPrefix

from icondbtools.data.event_log import EventLog


class TestEventLog(unittest.TestCase):
    def test_parse_signature(self):
        signature = "Transfer(Address,Address,int)"
        name, types = EventLog.parse_signature(signature)
        assert name == "Transfer"
        assert types == ["Address", "Address", "int"]

    def test_from_dict_with_transfer_event_log(self):
        signature = "Transfer(Address,Address,int)"
        score_address = Address.from_string(
            "cx4d6f646441a3f9c9b91019c9b98e3c342cceb114"
        )
        indexed_address_0 = Address.from_data(AddressPrefix.EOA, b"address0")
        indexed_address_1 = Address.from_data(AddressPrefix.EOA, b"address1")
        value = 0x8AC7230489E80000

        event_log_data = {
            "scoreAddress": str(score_address),
            "indexed": [
                signature,
                str(indexed_address_0),
                str(indexed_address_1),
                hex(value),
            ],
            "data": [],
        }

        event_log = EventLog.from_dict(event_log_data)
        assert event_log.signature == signature
        assert event_log.score_address == score_address
        assert event_log.indexed[0] == signature
        assert len(event_log.indexed) == 4
        assert event_log.indexed[1] == indexed_address_0
        assert event_log.indexed[2] == indexed_address_1
        assert event_log.indexed[3] == value
        assert len(event_log.data) == 0

    def test_from_dict_with_iscore_claimed_log(self):
        signature = "IScoreClaimed(int,int)"
        score_address = Address.from_string(
            "cx0000000000000000000000000000000000000000"
        )
        iscore = 0x186A0  # unit: iscore
        icx = 0x64  # unit: loop

        event_log_data = {
            "scoreAddress": str(score_address),
            "indexed": [signature],
            "data": [hex(iscore), hex(icx)],
        }

        event_log = EventLog.from_dict(event_log_data)
        assert event_log.signature == signature
        assert event_log.score_address == score_address
        assert len(event_log.indexed) == 1
        assert event_log.indexed[0] == signature
        assert len(event_log.data) == 2
        assert event_log.data[0] == iscore
        assert event_log.data[1] == icx


if __name__ == "__main__":
    unittest.main()
