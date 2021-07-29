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

from icondbtools.command.command import Command
from icondbtools.libs.term_calculator import TermCalculator, Term


class RevInfo:
    def __init__(self, revision: int, height: int, desc: str):
        self._revision = revision
        self._height = height
        self._desc = desc

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def height(self) -> int:
        return self._height

    @property
    def desc(self) -> str:
        return self._desc

    def __str__(self):
        return f"rev={self._revision} bh={self._height} desc={self._desc}"


rev_infos = (
    RevInfo(0, 0, "GENESIS"),
    RevInfo(2, 0, "TWO"),
    RevInfo(3, 0, "THREE"),
    RevInfo(4, 0, "FOUR"),
    RevInfo(5, 7_597_282, "IISS_PREVOTE"),
    RevInfo(6, 10_359_896, "DECENTRALIZATION"),
    RevInfo(7, 11_591_624, "FIX_TOTAL_ELECTED_PREP_DELEGATED"),
    RevInfo(8, 13_331_717, "REALTIME_P2P_ENDPOINT_UPDATE"),
    RevInfo(9, 22_657_836, "MULTIPLE_UNSTAKE, STRICT_SCORE_DECORATOR_CHECK"),
    RevInfo(10, 23_079_811, "FIX_UNSTAKE_BUG, LOCK_ADDRESS"),
    RevInfo(11, 23_870_738, "FIX_BALANCE_BUG"),
    RevInfo(12, 31_035_336, "BURN_V2_ENABLED, USE_RLP"),
)


def _get_rev_info(height: int) -> RevInfo:
    cur_ri = rev_infos[0]
    for ri in rev_infos:
        if height < ri.height:
            break
        cur_ri = ri
    return cur_ri


class CommandTerm(Command):
    def __init__(self, sub_parser, common_parser):
        self.add_parser(sub_parser, common_parser)

    def add_parser(self, sub_parser, common_parser):
        name = "term"
        desc = "Print information of the block and period the block belongs to for only MainNet"

        parser_term = sub_parser.add_parser(name, help=desc)
        parser_term.add_argument(
            "height", type=int, default=-1, help="target block height"
        )
        parser_term.set_defaults(func=self.run)

    def run(self, args):
        height: int = args.height
        term_calc = TermCalculator()
        if height > -1:
            term: Term = term_calc.calc_decentralization_term_info_by_block(height)
            ri = _get_rev_info(height)
            print(
                f"Decentralization info of the block and period the block belongs to for only MainNet\n"
                f"- seq: {term.seq} (start at 1)\n"
                f"- term period: {term_calc.DECENTRALIZATION_TERM_PERIOD}\n"
                f"- start BH: {term.start_height}\n"
                f"- end BH: {term.end_height}\n"
                f"- {term.number} block from start BH-{term.start_height}\n"
                f"- Rev: {ri}"
            )
        else:
            print(
                f"Pre-vote\n"
                f"- start BH: {term_calc.RRE_VOTE_START_BH}\n"
                f"- end BH: {term_calc.PRE_VOTE_END_BH}\n"
                f"- term period: {term_calc.PRE_VOTE_TERM_PERIOD}\n\n"
                f"Decentralization\n"
                f"- start BH: {term_calc.DECENTRALIZATION_START_BH}\n"
                f"- term period: {term_calc.DECENTRALIZATION_TERM_PERIOD}"
            )
