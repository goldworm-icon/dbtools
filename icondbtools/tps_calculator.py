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

from .block_database_reader import BlockDatabaseReader


class TPSCalculator(object):
    """Calculate TPS based on confirmed transactions in blockchain

    """
    def __init__(self):
        self._block_reader = BlockDatabaseReader()

    def open(self, db_path: str):
        self._block_reader.open(db_path)

    def run(self, start: int, end: int, span_us: int = -1):
        tx_count: int = 0
        end = self._validate_end_height(end)

        start_us: int = 0
        end_us: int = 1
        period_us: int = 0
        total_period_us: int = 0
        prev_timestamp_us: int = 0

        print(f'{"height":>8} | {"txs":>8} | {"total txs":>10} | {"period_s":>16} | {"total period_s":>16}')
        self._print_horizon_line('-', 80)

        for height in range(start, end + 1):
            block: dict = self._block_reader.get_block_by_block_height(height)

            timestamp_us: int = block['time_stamp']

            if height == start:
                start_us = timestamp_us
            elif height == end:
                end_us = timestamp_us
            else:
                period_us = timestamp_us - prev_timestamp_us

            # Calculate tps with blocks only in the given span
            if span_us < timestamp_us - start_us:
                end_us = prev_timestamp_us
                break

            tx_list: list = block['confirmed_transaction_list']
            count = len(tx_list)
            tx_count += count
            total_period_us += period_us
            prev_timestamp_us = timestamp_us

            print(f'{height:>8} | {count:>8} | {tx_count:>10} | {period_us / 10**6:>16} | {total_period_us / 10**6:>16}')

        self._print_result(tx_count, start_us, end_us, start, end)

    def _validate_end_height(self, end: int):
        last_block: dict = self._block_reader.get_last_block()
        last_height: int = last_block['height']

        if 0 <= end <= last_height:
            return end

        return last_height

    def _print_result(self, tx_count: int,
                      start_us: int, end_us: int,
                      start_height: int, end_height: int):
        # Print the result
        period_us: int = end_us - start_us
        tps: int = tx_count * 10**6 / period_us
        blocks: int = end_height - start_height + 1

        print(f'tps: {tps}\n'
              f'transactions: {tx_count}\n'
              f'blocks: {blocks}\n'
              f'period: {period_us / 10**6} seconds, {period_us} microseconds')
        self._print_horizon_line('-', 51)

    @staticmethod
    def _print_horizon_line(c: str, count: int):
        print(c * count)

    def close(self):
        self._block_reader.close()
