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

from icondbtools.command.command import Command
from icondbtools.libs.invalid_transaction_checker import InvalidTransactionChecker


class CommandInvalidTx(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'invalidtx'
        desc = 'Check whether invalid transaction are present or not'

        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument('--start', type=int, default=1, required=False)
        parser.add_argument('--end', type=int, default=-1, required=False)
        parser.set_defaults(func=self.run)

    def run(self, args):
        """Check whether invalid transaction are present or not
        for example transactions that are processed without any fees

        :param args:
        :return:
        """
        db_path: str = args.db
        start: int = args.start
        end: int = args.end

        checker = InvalidTransactionChecker()
        try:
            checker.open(db_path)
            checker.run(start, end)
        finally:
            checker.close()