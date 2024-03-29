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
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

from icondbtools.command.command import Command
from icondbtools.libs.iiss_data_reader import IISSDataReader
from icondbtools.libs.state_database_reader import StateDatabaseReader
from icondbtools.libs.term_calculator import TermCalculator, Term
from iconservice.base.address import Address
from iconservice.icon_constant import Revision
from iconservice.icx.icx_account import Account
from iconservice.icx.issue.storage import RegulatorVariable
from iconservice.iiss.reward_calc.msg_data import TxData, TxType, DelegationTx

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
            type=Path,
            help="Path of reward calculator dbtool",
        )
        parser_account.set_defaults(func=self.run)

    def run(self, args):
        """Export the info of all account

        :param args:
        :return:
        """
        db_path = Path(args.db).resolve()
        if db_path.is_dir() is False:
            raise ValueError("There is no state DB")
        iiss_db_path = db_path.parent / "iiss" / "current_db"
        if iiss_db_path.is_dir():
            export_iiss_data = True
        rc_db_path = db_path.parent / "rc" / "IScore"
        if rc_db_path.is_dir() is False:
            raise ValueError("There is no RC DB")
        rc_dbtool_path: Path = args.rc_dbtool.resolve()
        if rc_dbtool_path.is_file() is False:
            raise ValueError("There is no RC dbtool")

        reader = StateDatabaseReader()

        try:
            reader.open(str(db_path))
            block = reader.get_last_block()
            height = block.height
            revision = get_revision(height)
            print(f"BH: {height}, Revision: {revision}")
            term_calc = TermCalculator()
            term: Term = term_calc.calc_decentralization_term_info_by_block(height)
            result = {
                "blockHeight": height,
                "termHeight": term.start_height,
                "status": {
                    "totalSupply": reader.get_total_supply(),
                    "totalStake": reader.get_total_stake(),
                },
            }

            bs = reader.get_by_key(b'regulator_variable')
            if bs is not None:
                rv = RegulatorVariable.from_bytes(bs)
                result["issue"] = {
                    "issuedICX": rv.current_calc_period_issued_icx,
                    "prevIssuedICX": rv.prev_calc_period_issued_icx,
                    "overIssuedIScore": rv.over_issued_iscore,
                }

            if export_iiss_data:
                print(f"> Read IISS data from {iiss_db_path}")
                result["front"] = {}
                iiss_reader = IISSDataReader()
                iiss_reader.open(str(iiss_db_path))
                iterator = iiss_reader.tx_iterator
                iiss_event = []
                for key, value in iterator:
                    tx = TxData.from_bytes(value)
                    iiss_event.append(iiss_tx_to_json(tx))
                if len(iiss_event) > 0:
                    result["front"]["event"] = iiss_event

            print(f"> Read account information from {db_path}")
            result["accounts"] = {}
            i = 0
            errors = 0
            iterator = reader.iterator
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


def iiss_tx_to_json(tx: TxData) -> dict:
    jso = {
        "height": tx.block_height,
        "address": str(tx.address),
        "type": tx.type,
    }
    if tx.type == TxType.DELEGATION:
        jso["data"] = [{"address": str(x.address), "value": x.value} for x in tx.data.delegation_info]
    return jso
