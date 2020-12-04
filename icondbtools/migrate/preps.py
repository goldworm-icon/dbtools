# -*- coding: utf-8 -*-

from enum import IntEnum, auto

from ..utils import pack
import json


class PRep:
    """
    All field values are already converted to each original type compared to LoopchainBlock
    """

    class Index(IntEnum):
        VERSION = 0
        REP_ID = auto()
        P2P_ENDPOINT = auto()

    def __init__(
            self,
            version: str = None,
            rep_id: str = None,
            p2p_endpoint: str = None
    ):
        self.version: str = version
        self.rep_id: str = rep_id
        self.p2p_endpoint: str = p2p_endpoint

    def __str__(self):
        return (
            f"version={self.version} "
            f"rep_id={self.rep_id} "
            f"p2p_endpoint={self.p2p_endpoint} "
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = pack.decode(data)
        assert isinstance(obj, list)
        return cls(*obj)

    @classmethod
    def from_dict(cls, data: dict):
        rep_id: str = data.get("id")
        p2p_endpoint: str = data.get("p2pEndpoint")
        return cls(
            version=None,
            rep_id=rep_id,
            p2p_endpoint=p2p_endpoint
        )

    def to_bytes(self) -> bytes:
        obj = [
            self.version,
            self.rep_id,
            self.p2p_endpoint,
        ]
        return pack.encode(obj)

    def to_dict(self) -> dict:
        return {
            "id": self.rep_id,
            "p2pEndpoint": self.p2p_endpoint
        }


class PReps:
    """
    All field values are already converted to each original type compared to LoopchainBlock
    """

    def __init__(self, container: list):
        self._container: list = container

    @classmethod
    def from_json_bytes(cls, data: bytes):
        container = []
        json_data = data.decode()
        datas: list = json.loads(json_data)
        for data in datas:
            container.append(PRep.from_dict(data))
        return cls(container=container)

    @classmethod
    def from_bytes(cls, data: bytes):
        container = []
        objs: list = pack.decode(data)
        for obj in objs:
            container.append(PRep.from_bytes(obj))
        return cls(container=container)

    def to_bytes(self) -> bytes:
        obj = [item.to_bytes() for item in self._container]
        return pack.encode(obj)

    def to_list(self) -> list:
        return [item.to_dict() for item in self._container]
