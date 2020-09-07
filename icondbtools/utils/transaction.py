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

from typing import Union

from icondbtools.libs.loopchain_block import LoopchainBlock
from icondbtools.utils.convert_type import str_to_int
from iconservice.base.address import Address
from iconservice.base.address import MalformedAddress
from iconservice.base.exception import InvalidParamsException


def create_transaction_requests(loopchain_block: "LoopchainBlock") -> list:
    tx_requests = []

    if loopchain_block.height == 0:
        request = convert_genesis_transaction_to_request(
            loopchain_block.transactions[0]
        )
        tx_requests.append(request)
    else:
        for tx_dict in loopchain_block.transactions:
            request = convert_transaction_to_request(loopchain_block, tx_dict)
            tx_requests.append(request)

    return tx_requests


def convert_transaction_to_request(loopchain_block: "LoopchainBlock", tx_dict: dict):
    return {
        "method": "icx_sendTransaction",
        "params": tx_dict_to_params(tx_dict, loopchain_block.timestamp),
    }


def tx_dict_to_params(tx_dict: dict, block_timestamp: int) -> dict:
    params = {}

    if "from" in tx_dict:
        params["from"] = Address.from_string(tx_dict["from"])
    if "to" in tx_dict:
        params["to"] = convert_to_address(tx_dict["to"])

    if "tx_hash" in tx_dict:
        params["txHash"] = bytes.fromhex(tx_dict["tx_hash"])
    else:
        params["txHash"] = bytes.fromhex(tx_dict["txHash"])

    if "timestamp" in tx_dict:
        params["timestamp"] = str_to_int(tx_dict["timestamp"])
    else:
        params["timestamp"] = block_timestamp

    int_keys = ["version", "fee", "nid", "value", "nonce", "stepLimit"]
    for key in int_keys:
        if key in tx_dict:
            params[key] = int(tx_dict[key], 16)

    object_keys = ["dataType", "data", "signature"]
    for key in object_keys:
        if key in tx_dict:
            params[key] = tx_dict[key]

    data_type: str = tx_dict.get("dataType", "")
    if data_type == "base":
        params["data"] = convert_base_transaction(tx_dict["data"])

    return params


def convert_base_transaction(data: dict) -> dict:
    ret = {"prep": {}, "result": {}}
    prep = data["prep"]
    for key in prep:
        ret["prep"][key] = int(prep[key], 16)

    result = data["result"]
    for key in result:
        ret["result"][key] = int(result[key], 16)

    return ret


def convert_to_address(to: str) -> Union["Address", "MalformedAddress"]:
    try:
        address = Address.from_string(to)
    except InvalidParamsException:
        address = MalformedAddress.from_string(to)

    return address


def convert_genesis_transaction_to_request(tx_dict: dict):
    accounts = tx_dict["accounts"]
    request = {
        "method": "icx_sendTransaction",
        "params": {
            "txHash": bytes.fromhex(
                "692f49cde2fe90aa8d04541c2f794e5bf8dcb51c777037909d676d6dd52be1dc"
            )
        },
        "genesisData": {"accounts": accounts},
    }

    for account in accounts:
        account["address"] = Address.from_string(account["address"])
        account["balance"] = int(account["balance"], 16)

    return request
