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

from icondbtools.command.command import Command
from icondbtools.libs.score_database_manager import ScoreDatabaseManager


class CommandArray(Command):

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'array'
        desc = 'Get arrayDB size'

        parser = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser.add_argument(
            '--score', type=str, required=True, help='score address ex) cx63af7f2e073985a9e9965765e809f66da3b0f238')
        parser.add_argument(
            '--name', type=str, required=True, help='user address ex) subDB name')
        parser.set_defaults(func=self.run)

    def run(self, args):
        db_path: str = args.db
        score_address: 'Address' = Address.from_string(args.score)
        name: str = args.name

        manager = ScoreDatabaseManager()
        manager.open(db_path, score_address)

        value: bytes = manager.get_array_db_size(name)
        if value is None:
            size = 0
        else:
            size: int = int.from_bytes(value, 'big')
        print(f'size : {size}')

        manager.close()
