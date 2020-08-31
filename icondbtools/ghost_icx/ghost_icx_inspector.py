# -*- coding: utf-8 -*-

__all__ = "GhostICXFinder"

import json
from typing import List, Dict, Any

from iconservice.base.address import Address
from iconservice.icx.coin_part import CoinPartFlag
from ..libs.state_database_reader import StateDatabaseReader


class Unstake(object):
    def __init__(self, amount: int, block_height: int):
        self._amount = amount
        self._block_height = block_height

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def block_height(self) -> int:
        return self._block_height

    def to_list(self) -> List[int]:
        return [self._amount, self._block_height]


class Target(object):
    def __init__(self, address: Address):
        self._address = address
        self._unstakes: List[Unstake] = []
        self.old_unstake_format = True

    def __len__(self) -> int:
        return len(self._unstakes)

    @property
    def address(self) -> Address:
        return self._address

    @property
    def total_unstake(self) -> int:
        return sum(unstake.amount for unstake in self._unstakes)

    def add_unstake(self, amount: int, block_height: int):
        self._unstakes.append(Unstake(amount, block_height))

    def get_unstake(self, index: int) -> Unstake:
        return self._unstakes[index]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": str(self._address),
            "total_unstake": self.total_unstake,
            "old_unstake_format": self.old_unstake_format,
            "unstakes": self._unstakes
        }


class GhostICXInspector(object):
    """Inspect the information about invisible ghost icx

    Inspect the information about invisible ghost icx with given address list and state-db
    and print the result
    """

    def __init__(self):
        self._block = None
        self._targets: List[Target] = []
        self._reader = StateDatabaseReader()

    def open(self, db_path: str):
        self._reader.open(db_path)

    def close(self):
        self._reader.close()

    def run(self, path: str):
        """

        :param path: file path containing address list to inspect
        """
        self._block = self._reader.get_last_block()

        with open(path, "rt") as f:
            while True:
                text = f.readline()
                if text == "":
                    break

                address = Address.from_string(text.rstrip())
                self._inspect_account(address)

        self._print_result()

    def _inspect_account(self, address: Address):
        coin_part = self._reader.get_coin_part(address)
        stake_part = self._reader.get_stake_part(address)

        if (
                CoinPartFlag.HAS_UNSTAKE in coin_part.flags
                or stake_part.total_unstake == 0
        ):
            # There is no invisible ghost ICX in this account
            return

        target = Target(address)
        target.old_unstake_format = (stake_part.unstake_block_height > 0)
        self._targets.append(target)

        if target.old_unstake_format:
            target.add_unstake(stake_part.unstake, stake_part.unstake_block_height)
        else:
            for unstake_info in stake_part.unstakes_info:
                target.add_unstake(
                    amount=unstake_info[0], block_height=unstake_info[1])

    def _print_result(self):
        result = {
            "block_height": self._block.height,
            "target_count": len(self._targets),
            "total_unstake": sum(target.total_unstake for target in self._targets),
            "targets": self._targets
        }

        text: str = json.dumps(result, indent=4, cls=_CustomEncoder)
        print(text)


class _CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Target):
            return o.to_dict()
        elif isinstance(o, Unstake):
            return o.to_list()

        return json.JSONEncoder.default(self, o)
