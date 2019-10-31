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

from pprint import pprint
from iconservice.utils.msgpack_for_db import MsgPackForDB
from iconservice.prep.data.term import Term
from icondbtools.command.command import Command
from icondbtools.libs.state_database_reader import StateDatabaseReader
from collections import namedtuple

KeyInfo = namedtuple('KeyInfo', 'name, key, from_func')


class CommandDbinfo(Command):
    PREP_PREFIX: bytes = b'prep'
    COMMAND_LIST = [
        KeyInfo(name='TERM', key=PREP_PREFIX + b'term', from_func=Term.from_list)
    ]

    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = 'dbinfo'
        desc = 'Print the information of instance in statedb'

        # create the parser for block
        parser_block = sub_parser.add_parser(name, parents=[common_parser], help=desc)
        parser_block.set_defaults(func=self.run)

    def get_list_idx(self):

        while True:
            print('Enter the number to check information')

            for i in range(len(self.COMMAND_LIST)):
                print(f'{i} : {self.COMMAND_LIST[i].name}')

            try:
                picked_number = int(input())

                if 0 <= picked_number < len(self.COMMAND_LIST):
                    break

            except ValueError:
                print('Entered wrong number')

        return picked_number

    def run(self, args):
        db_path: str = args.db

        state_reader = StateDatabaseReader()
        state_reader.open(db_path)

        picked_number = self.get_list_idx()

        value = state_reader.get_by_key(self.COMMAND_LIST[picked_number].key)

        if value is not None:
            pprint(self.COMMAND_LIST[picked_number].from_func(MsgPackForDB.loads(value)))
        else:
            print(f'value is not exist, key = {self.COMMAND_LIST[picked_number].key}')

        state_reader.close()
