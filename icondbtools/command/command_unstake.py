# -*- coding: utf-8 -*-
# Copyright 2020 ICON Foundation Inc.
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

from iconservice.base.address import Address
from iconservice.icx.stake_part import StakePart

from icondbtools.command.command import Command
from icondbtools.libs.block_database_reader import BlockDatabaseReader
from icondbtools.libs.state_database_reader import StateDatabaseReader


class CommandUnstake(Command):
    """Get unstake account

    """

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'unstake'
        desc = 'Get list of account which has unstake'

        # create the parser for balance
        parser_unstake = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_unstake.add_argument('--to', type=str, help='write result to file')
        parser_unstake.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db

        reader = StateDatabaseReader()
        try:
            reader.open(db_path)

            results = {}
            iter_results = reader.iterate_stake_part(self._cmp_unstake)
            for result in iter_results:
                coin_part = reader.get_coin_part(result[0])
                stake_part = result[1]
                value = {"balance": coin_part.balance}
                value.update(stake_part.to_dict())
                results[str(result[0])] = value

        finally:
            if args.to:
                with open(args.to, 'w') as fp:
                    json.dump(results, fp=fp, indent=2)
            else:
                print(json.dumps(results, indent=2))
            print(f"Found {len(results)} accounts")
            reader.close()

    def _cmp_unstake(self, stake_part: StakePart) -> bool:
        if stake_part.unstake_block_height != 0:
            return True
        return False


class CommandUnstakePreprocess(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'unstake_preprocess'
        desc = 'Preprocess the unstake account'

        # create the parser for balance
        parser_unstake = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_unstake.add_argument('--unstake', type=str, required=True, help='list of account which has unstake ')
        parser_unstake.add_argument('--to', type=str, help='write result to file')
        parser_unstake.set_defaults(func=self.run)

    def run(self, args):
        with open(args.unstake) as f:
            unstake: dict = json.load(f)

        db_path: str = args.db

        reader = StateDatabaseReader()
        try:
            reader.open(db_path)
            for k in unstake.keys():
                coin_part = reader.get_coin_part(Address.from_string(k))
                unstake[k]["balance_init"] = coin_part.balance
                unstake[k]["balance_diff"] = unstake[k]["balance"] - coin_part.balance
        finally:
            if args.to:
                with open(args.to, 'w') as fp:
                    json.dump(unstake, fp=fp, indent=2)
            else:
                print(json.dumps(unstake, indent=2))
            reader.close()


class CommandUnstakeBug(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'unstake_bug'
        desc = 'Check the account of ICX earned by unstake bug'

        # create the parser for balance
        parser_unstake = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_unstake.add_argument('-s', '--start', type=int, required=True, help='start height to check')
        parser_unstake.add_argument('-e', '--end', type=int, default=-1, help='end height to check, inclusive')
        parser_unstake.add_argument('--unstake', type=str, required=True, help='list of account which has unstake ')
        parser_unstake.add_argument('--to', type=str, help='write result to file')
        parser_unstake.set_defaults(func=self.run)

    def run(self, args):
        with open(args.unstake) as f:
            unstake: dict = json.load(f)

        db_path: str = args.db
        start: int = args.start
        end: str = args.end

        block_reader = BlockDatabaseReader()
        block_reader.open(db_path)

        if end == -1:
            last_block: dict = block_reader.get_last_block()
            end = int(last_block.get("height", "0x0"), 0)

        i = 0
        for block_height in range(start+1, end+1):
            if i % 300 == 0:
                print(block_height)

            block = block_reader.get_block_by_block_height(block_height)
            transactions = block.get("transactions", None)
            for tx_index, tx in enumerate(transactions):
                if tx.get("dataType") == "base":
                    # skip base transaction
                    continue

                target = ""
                from_ = tx.get("from", "")
                to = tx.get("to", "")
                if from_ in unstake:
                    target = from_
                elif to in unstake:
                    target = to

                if target == "":
                    # skip tx touch no unstake account
                    continue

                if "error_count" in unstake[target]:
                    data_type = tx.get("dataType", "")
                    if data_type == "call" and tx["data"]["method"] in ("setStake", "setDelegation"):
                        # only setStake and setDelegation
                        pass
                    else:
                        continue
                else:
                    # pass first TX after unstake expired
                    pass

                for key in ("txHash", "tx_hash"):
                    tx_hash = tx.get(key, None)
                    if tx_hash:
                        break

                if tx_hash is None:
                    print(f"invalid TX: {tx_index} {block}")

                tx_result = block_reader.get_transaction_result_by_hash(tx_hash)
                if tx_result is None or tx_result["result"]["status"] != "0x1":
                    # skip failed transaction
                    continue

                value = unstake[target]
                if block_height >= value.get("unstake_block_height", end+1):
                    # increase TX count which called after unstake lockup expired
                    error_count = value.get("error_count", 0)
                    error_count += 1
                    value["error_count"] = error_count

            i += 1

        result = {}
        sum = 0
        for k, v in unstake.items():
            if "error_count" in v:
                v["error_amount"] = v["error_count"] * v["unstake"]
                result[k] = v
                sum += v["error_amount"]

        if args.to:
            with open(args.to, 'w') as fp:
                json.dump(result, fp=fp, indent=2)
        else:
            print(json.dumps(result, indent=2))

        print(f"Found {len(result)} accounts and {sum:,} loop")


class CommandUnstakeValidate(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'unstake_validate'
        desc = 'validate unstake error results generated by sync command'

        # create the parser for balance
        parser_unstake = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_unstake.add_argument('--unstake', type=str, required=True, help='unstake error result file')
        parser_unstake.set_defaults(func=self.run)

    def run(self, args):
        with open(args.unstake) as f:
            unstake: dict = json.load(f)

        db_path: str = args.db

        block_reader = BlockDatabaseReader()
        block_reader.open(db_path)

        i = 0
        tx_count = 0
        tx_fail = 0
        tx_result_error = 0
        for k, v in unstake.items():
            for tx_value in v["transactions"]:
                tx_count += 1
                tx_result: dict = block_reader.get_transaction_result_by_hash(tx_value[0])
                if tx_result is None:
                    print(f"Can't find TX result: {tx_value[0]} for {k}, error amount {tx_value[1]}")
                    tx_result_error += 1
                elif tx_result["result"]["status"] != "0x1":
                    print(f"Failed TX: {tx_value[0]} for {k}, error amount {tx_value[1]}")
                    tx_fail += 1
            i += 1
        print(f"Validate {tx_count} TXs for {i} accounts. Found {tx_fail} failed TX and {tx_result_error} no result")