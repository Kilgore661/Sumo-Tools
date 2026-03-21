"""
Mapping from RikId to Performance.

Represents a partial function:

    RikId -> Performance

Implemented as a dictionary with function-call syntax.
"""

from __future__ import annotations

from RikId import RikId
from Performance import Performance


class Performances(dict):
    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for rid, perf in mapping.items():
                instance[rid] = perf

        return instance

    def __call__(self, rid: RikId):
        return self.get(rid)
