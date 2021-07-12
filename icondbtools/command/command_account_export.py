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

import json
import os
import subprocess
from typing import Optional, List, Tuple

from iconservice.base.address import Address
from iconservice.icon_constant import Revision
from iconservice.icx.icx_account import Account

from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader
from .command_total_balance import is_account_key

revision_array = [
    0, 0, 0, 0, 0,
    7597282,  # 5
    10359896,
    11591624,
    13331717,
    22657836,
    23079811,
    23870738,
    31035336,
]


class CommandAccountExport(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "account_export"
        desc = "Export the information of all account"

        # create the parser for account
        parser_account = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_account.add_argument(
            "--rc-dbtool",
            type=str,
            help="Path of reward calculator dbtool",
        )
        parser_account.set_defaults(func=self.run)

    def run(self, args):
        """Export the info of all account

        :param args:
        :return:
        """
        db_path: str = args.db
        rc_dbtool_path: str = args.rc_dbtool
        if db_path[-1] == os.path.sep:
            db_path = db_path[:-1]
        path, _ = os.path.split(db_path)
        rc_db_path: str = os.path.join(path, "rc", "IScore")
        reader = StateDatabaseReader()

        try:
            reader.open(db_path)
            block = reader.get_last_block()
            height = block.height
            revision = get_revision(height)
            print(f"BH: {height}, Revision: {revision}")

            result = {
                "blockHeight": height,
                "status": {
                    "totalSupply": reader.get_total_supply(),
                    "totalStake": reader.get_total_stake(),
                },
                "accounts": {},
            }

            iterator = reader.iterator

            print(f"> Read account information from {db_path}")
            i = 0
            errors = 0
            for key, value in iterator:
                try:
                    if is_account_key(key):
                        address = Address.from_bytes(key)
                        account = reader.get_account(address, block.height, revision)
                        result["accounts"][str(address)] = get_account_info(account, revision)
                        i += 1
                    else:
                        continue
                except BaseException as e:
                    print(f"error {e}")
                    errors += 1

            print(f"> Get IScore information from {rc_db_path} via {rc_dbtool_path}")
            iscore_file = "./iscore.json"
            cmd = f"{rc_dbtool_path} iscore -dbroot {rc_db_path} -output {iscore_file}"
            popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            popen.communicate()
            print(f"> Merge account and IScore information")
            with open(iscore_file, 'r', encoding='utf-8') as jf:
                iscore: dict = json.load(jf)
                for key, value in iscore.items():
                    if key in result["accounts"]:
                        result["accounts"][key]["iscore"] = value

            filename = f'./icon1_account_info_{height:08d}.json'
            with open(filename, 'w', encoding='utf-8') as jf:
                json.dump(result, jf, indent=2)
            print(f"Get {i} accounts and {errors} errors. Check result file: {filename}")
        finally:
            reader.close()


def get_account_info(account: 'Account', revision: int) -> dict:
    info = {"balance": account.balance}
    if account.stake_part is not None:
        info.update(get_stake(account, revision))
    if account.delegation_part is not None:
        info.update(get_delegation(account))

    return info


def get_stake(account: 'Account', revision: int) -> dict:
    stake: int = account.stake
    unstake: int = account.unstake
    unstake_block_height: int = account.unstake_block_height
    unstakes_info: Optional[List[Tuple[int, int]]] = account.unstakes_info

    data = {}

    if stake > 0:
        data["stake"] = stake

    if revision < Revision.MULTIPLE_UNSTAKE.value:
        if unstake_block_height:
            data["unstakes"] = [
                {
                    "unstake": unstake,
                    "unstakeBlockHeight": unstake_block_height,
                }
            ]

    elif revision >= Revision.MULTIPLE_UNSTAKE.value:
        if unstakes_info:
            data["unstakes"] = [
                {
                    "unstake": unstakes_data[0],
                    "unstakeBlockHeight": unstakes_data[1],
                }
                for unstakes_data in unstakes_info
            ]
    return data


def get_delegation(account: 'Account') -> dict:
    data = {}
    delegation_list: list = []
    for address, value in account.delegations:
        delegation_list.append({"address": str(address), "value": hex(value)})

    if len(delegation_list) > 0:
        data["delegations"] = delegation_list
    return data


def get_revision(height: int) -> int:
    for idx, value in enumerate(revision_array):
        if height < value:
            return idx - 1

    return idx
