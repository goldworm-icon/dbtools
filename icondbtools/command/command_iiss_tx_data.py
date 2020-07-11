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

from enum import Enum

from iconservice.base.address import Address, AddressPrefix
from .command import Command
from ..data.transaction_result import TransactionResult
from ..libs.block_database_reader import BlockDatabaseReader
from ..libs.loopchain_block import LoopchainBlock


class IISSTXType(Enum):
    NONE = 0
    DELEGATION = 1
    REGISTER_PREP = 2
    UNREGISTER_PREP = 3


class CommandIISSTXData(Command):
    """Extract the transactions which affect I-Score amount in a given block height range
    """

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "iisstxdata"
        desc = (
            "Extract the transactions which affect I-Score amount in a given block height range \n"
            "(setDelegation, registerPRep, unregisterPRep"
        )

        # create the parser for account
        parser_iiss_tx_data = sub_parser.add_parser(
            name, parents=[common_parser], help=desc
        )
        parser_iiss_tx_data.add_argument(
            "--start", type=int, default=0, help="start height", required=True
        )
        parser_iiss_tx_data.add_argument(
            "--count", type=int, default=0, help="the number of blocks", required=True
        )

        parser_iiss_tx_data.set_defaults(func=self.run)

    def run(self, args):
        """Extract the information

        :param args:
        :return:
        """
        db_path: str = args.db
        start: int = args.start
        count: int = args.count

        # output
        total_tx: int = 0
        total_delegation_tx: int = 0
        total_register_prep_tx: int = 0
        total_unregister_prep_tx: int = 0

        reader = BlockDatabaseReader()

        try:
            reader.open(db_path)

            height = start
            for _ in range(count):
                block_dict: dict = reader.get_block_by_block_height(height)
                block = LoopchainBlock.from_dict(block_dict)

                for transaction in block.transactions:
                    if not self._is_succeeded_transaction(reader, transaction):
                        continue

                    iiss_tx_type = self._get_iiss_tx_type(transaction)

                    if iiss_tx_type == IISSTXType.DELEGATION:
                        total_delegation_tx += 1
                    elif iiss_tx_type == IISSTXType.REGISTER_PREP:
                        total_register_prep_tx += 1
                    elif iiss_tx_type == IISSTXType.UNREGISTER_PREP:
                        total_unregister_prep_tx += 1

                    total_tx += 1

                height += 1

        finally:
            reader.close()

        print(
            f"[ IISS TX from BH-{start} to BH={start + count - 1}\n"
            f"total_tx: {total_tx}\n"
            f"total_iiss_tx: {total_delegation_tx + total_register_prep_tx + total_unregister_prep_tx}\n"
            f"total_delegation_tx: {total_delegation_tx}\n"
            f"total_register_prep_tx: {total_register_prep_tx}\n"
            f"total_unregister_prep_tx_tx: {total_unregister_prep_tx}"
        )

    @classmethod
    def _is_succeeded_transaction(
        cls, reader: "BlockDatabaseReader", transaction: dict
    ):
        try:
            tx_result_data: dict = reader.get_transaction_result_by_hash(
                transaction["txHash"]
            )
            result_data: dict = tx_result_data["result"]
            tx_result = TransactionResult.from_dict(result_data)
            return tx_result.status == 1
        except:
            pass

        return False

    @classmethod
    def _get_iiss_tx_type(cls, transaction: dict) -> "IISSTXType":
        iiss_tx_methods = {
            "setDelegation": IISSTXType.DELEGATION,
            "registerPRep": IISSTXType.REGISTER_PREP,
            "unregisterPRep": IISSTXType.UNREGISTER_PREP,
        }

        try:
            data_type: str = transaction["dataType"]
            if data_type == "call":
                to: "Address" = Address.from_string(transaction["to"])
                if to == Address.from_prefix_and_int(AddressPrefix.CONTRACT, 0):
                    data: dict = transaction["data"]
                    method: str = data["method"]
                    return iiss_tx_methods.get(method, IISSTXType.NONE)
        except:
            pass

        return IISSTXType.NONE
