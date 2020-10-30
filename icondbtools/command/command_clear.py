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
from icondbtools.utils.utils import remove_dir


class CommandClear(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "clear"
        desc = "Remove .score and .statedb"

        # create the parser for clear
        parser_clear = sub_parser.add_parser(name, help=desc)
        parser_clear.set_defaults(func=self.run)

    def run(self, args):
        """Clear .score and .statedb

        :param args:
        :return:
        """
        paths = [".score", ".statedb"]
        for path in paths:
            remove_dir(path)
