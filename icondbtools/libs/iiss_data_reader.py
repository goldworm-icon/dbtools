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


from typing import List

import plyvel


class BPCountResult(object):
    def __init__(
        self, count: int, start_height: int, end_height: int, dropped_heights: List[int]
    ):
        self._count = count
        self._start_height = start_height
        self._end_height = end_height
        self._dropped_heights = dropped_heights

    @property
    def count(self) -> int:
        return self._count

    @property
    def start_height(self) -> int:
        return self._start_height

    @property
    def end_height(self) -> int:
        return self._end_height

    @property
    def dropped_heights(self) -> List[int]:
        return self._dropped_heights

    def __str__(self) -> str:
        return (
            f"count: {self._count}\n"
            f"start_height: {self._start_height}\n"
            f"end_height: {self._end_height}\n"
            f"dropped: {len(self._dropped_heights)} {self._dropped_heights}"
        )


class TXCountResult(object):
    def __init__(
        self, count: int, start_index: int, end_index: int, dropped_indices: List[int]
    ):
        self._count = count
        self._start_index = start_index
        self._end_index = end_index
        self._dropped_indices = dropped_indices

    @property
    def count(self) -> int:
        return self._count

    @property
    def start_index(self) -> int:
        return self._start_index

    @property
    def end_index(self) -> int:
        return self._end_index

    @property
    def dropped_indices(self) -> List[int]:
        return self._dropped_indices

    def __str__(self) -> str:
        return (
            f"count: {self._count}\n"
            f"start_index: {self._start_index}\n"
            f"end_index: {self._end_index}\n"
            f"dropped: {len(self._dropped_indices)} {self._dropped_indices}"
        )


class IISSDataReader(object):
    def __init__(self):
        self._db = None

    def open(self, db_path: str):
        self._db = plyvel.DB(db_path)

    def close(self):
        if self._db:
            self._db.close()
            self._db = None

    def count_bp(self) -> "BPCountResult":
        prefix = b"BP"
        start_height = -1
        end_height = -1
        dropped_heights: List[int] = []
        count = 0

        for key, value in self._db.iterator(prefix=prefix):
            height: int = int.from_bytes(key[len(prefix) :], "big", signed=False)

            if start_height < 0:
                start_height = height
            else:
                for h in range(end_height + 1, height):
                    dropped_heights.append(h)

            end_height = height
            count += 1

        return BPCountResult(count, start_height, end_height, dropped_heights)

    def count_tx(self) -> "TXCountResult":
        prefix = b"TX"
        start_index = -1
        end_index = -1
        dropped_indices: List[int] = []
        count = 0

        for key, value in self._db.iterator(prefix=prefix):
            index: int = int.from_bytes(key[len(prefix) :], "big", signed=False)

            if start_index < 0:
                start_index = index
            else:
                for h in range(end_index + 1, index):
                    dropped_indices.append(h)

            end_index = index
            count += 1

        return TXCountResult(count, start_index, end_index, dropped_indices)
