"""
Mapping from RikId to Shikona.

Represents a partial function:

    RikId -> Shikona
"""

from __future__ import annotations

from RikId import RikId
from Shikona import Shikona


class RikShikona(dict):
    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for rid, shik in mapping.items():
                instance[rid] = shik

        return instance

    def __call__(self, rid: RikId):
        return self.get(rid)
