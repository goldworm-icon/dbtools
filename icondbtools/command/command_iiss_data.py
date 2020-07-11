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

from .command import Command
from ..libs.iiss_data_reader import IISSDataReader, BPCountResult, TXCountResult
from ..libs.block_database_reader import BlockDatabaseReader


class CommandIISSData(Command):
    """Extract the information from iiss_data_db (iiss_rc_db)
     """

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "iissdata"
        desc = "Print the number of TXData and BPData from iiss data db"

        # create the parser for account
        parser_iiss_data = sub_parser.add_parser(
            name, parents=[common_parser], help=desc
        )
        parser_iiss_data.set_defaults(func=self.run)

    def run(self, args):
        """Extract the information

        :param args:
        :return:
        """
        db_path: str = args.db
        reader = IISSDataReader()

        try:
            reader.open(db_path)

            tx_count_result: TXCountResult = reader.count_tx()
            bp_count_result: BPCountResult = reader.count_bp()

            print(f"[ TX_INFO ]\n{tx_count_result}\n")
            print(f"[ BP_INFO ]\n{bp_count_result}")

        finally:
            reader.close()
