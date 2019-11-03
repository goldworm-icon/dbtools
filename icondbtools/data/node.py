# -*- coding: utf-8 -*-

from iconservice.base.address import Address


class Node(object):
    def __init__(self, address: 'Address', p2p_endpoint: str):
        self._address = address
        self._p2p_endpoint = p2p_endpoint

    @property
    def address(self) -> 'Address':
        return self._address

    @property
    def p2p_endpoint(self) -> str:
        return self._p2p_endpoint

    @classmethod
    def from_dict(cls, data: dict) -> 'Node':
        address: 'Address' = data["id"]
        p2p_endpoint: str = data["p2pEndpoint"]

        return Node(address, p2p_endpoint)
