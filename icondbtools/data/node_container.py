# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, List, Dict, Iterable, Optional

from iconservice.icon_constant import PRepResultState
from .node import Node

if TYPE_CHECKING:
    from iconservice.base.address import Address


class NodeContainer(object):
    def __init__(self, state: "PRepResultState", nodes: Dict["Address", "Node"]):
        self._state: "PRepResultState" = state
        self._nodes: Dict["Address", "Node"] = nodes

    def __contains__(self, address: "Address") -> bool:
        return address in self._nodes

    def __iter__(self) -> Iterable["Node"]:
        for node in self._nodes.values():
            yield node

    @property
    def state(self) -> "PRepResultState":
        return self._state

    @classmethod
    def from_dict(cls, data: dict):
        state: "PRepResultState" = PRepResultState(data["state"])
        nodes: Dict["Address", "Node"] = {}

        preps: List = data["preps"]
        for prep in preps:
            node = Node.from_dict(prep)
            nodes[node.address] = node

        return NodeContainer(state, nodes)

    @classmethod
    def from_list(cls, preps: list) -> Optional['NodeContainer']:
        if not preps:
            return None

        state: 'PRepResultState' = PRepResultState.NORMAL
        nodes: Dict['Address', 'Node'] = {}

        for prep in preps:
            node = Node.from_dict(prep)
            nodes[node.address] = node

        return NodeContainer(state, nodes)
