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
from iconservice.fee.deposit import Deposit
from iconservice.utils.msgpack_for_db import MsgPackForDB

from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader

MSG_PACK_DEPOSIT_DATA_LENGTH = 11


class CommandTotalBalance(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "totalbalance"
        desc = "Print the sum of whole account's balance"

        parser_account = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_account.set_defaults(func=self.run)

    def run(self, args):
        """Print the account info of a given address

        :param args:
        :return:
        """
        db_path: str = args.db

        reader = StateDatabaseReader()
        total_balance = 0
        total_staked = 0
        active_account_count = 0
        staking_account_count = 0
        total_deposit = 0
        deposit_count = 0

        address = None

        try:
            reader.open(db_path)
            iterator = reader.iterator

            i = 0
            errors = 0
            for key, value in iterator:
                try:
                    if is_account_key(key):
                        address = Address.from_bytes(key)
                        coin_part = reader.get_coin_part(address)
                        stake_part = reader.get_stake_part(address)
                        if coin_part is not None:
                            active_account_count += 1
                            total_balance += coin_part.balance
                        if stake_part is not None:
                            staking_account_count += 1
                            total_staked += stake_part.total_stake
                    elif is_fee2_key(key):
                        if is_deposit(value):
                            deposit = Deposit.from_bytes(value)
                            total_deposit += deposit.deposit_amount
                            deposit_count += 1
                    else:
                        continue

                except BaseException:
                    errors += 1

                i += 1

            full_balance = total_balance + total_staked + total_deposit
            total_supply = reader.get_total_supply()
            print(
                f"total supply : {total_supply:30,}\n"
                f"total balance: {full_balance:30,}\n"
                f"      balance: {total_balance:30,}\n"
                f"      staked : {total_staked:30,}\n"
                f"      deposit: {total_deposit:30,}\n"
                f"diff         : {full_balance - total_supply:,}\n"
                f"active account count : {active_account_count:,}\n"
                f"staking account count : {staking_account_count:,}\n"
                f"deposit         count : {deposit_count:,}\n"
                f"errors: {errors}"
            )
        except Exception as e:
            print(f"address: {address}")
            print(e)
        finally:
            reader.close()


def is_account_key(key: bytes) -> bool:
    key_length = len(key)
    if key_length == 20:
        return True
    elif key_length == 21:
        if key[0] == 1:
            return True
    return False


def is_fee2_key(key: bytes) -> bool:
    key_length = len(key)
    if key_length == 33:
        if key[0] == 2:
            return True
    return False


def is_deposit(value: bytes) -> bool:
    data = MsgPackForDB.loads(value)
    if len(data) == MSG_PACK_DEPOSIT_DATA_LENGTH:
        return True
    return False
