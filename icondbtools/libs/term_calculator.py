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


class Term:
    def __init__(self, seq: int, start_height: int, end_height: int, number: int):
        self.seq = seq
        self.start_height = start_height
        self.end_height = end_height
        self.number = number


class TermCalculator:
    DECENTRALIZATION_START_BH = 10_362_083
    DECENTRALIZATION_TERM_PERIOD = 43_120
    RRE_VOTE_START_BH = 7_597_282
    PRE_VOTE_TERM_PERIOD = 43_200
    PRE_VOTE_END_BH = 7_597_282 + 64 * PRE_VOTE_TERM_PERIOD

    def calc_decentralization_term_info_by_block(self, block_height: int) -> Term:
        """
        Calculate sequence, start BH, and end BH
        of the term period the input block belongs to
        It is only for MainNet

        :param block_height: target block height
        :return: sequence which start is 1, start BH, end BH, and number of the term period the block belongs to
        """
        if block_height < self.DECENTRALIZATION_START_BH:
            print(f"BH-{block_height} is less then DECENTRALIZATION START BH-{self.DECENTRALIZATION_START_BH}.")
            exit(1)

        value = block_height - self.DECENTRALIZATION_START_BH
        seq = value // self.DECENTRALIZATION_TERM_PERIOD + 1
        start_height = (seq - 1) * self.DECENTRALIZATION_TERM_PERIOD + self.DECENTRALIZATION_START_BH
        end_height = start_height + self.DECENTRALIZATION_TERM_PERIOD - 1
        number = block_height - start_height + 1  # what number of the term period the input block is

        term = Term(seq, start_height, end_height, number)
        return term
