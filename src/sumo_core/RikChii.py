"""
Canonical transitional mapping from RikId to NewFoo.

NOTE:
- File name: RikChii.py
- Class name: RikNewFoo (temporary)
- Will be renamed to RikChii once migration is complete

Represents a partial function:

    RikId → NewFoo

This is implemented as a dictionary with function-call syntax.
"""

from __future__ import annotations

from RikId import RikId
from Chii import NewFoo


class RikNewFoo(dict):
    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for rid, foo in mapping.items():
                instance[rid] = foo

        return instance

    def __call__(self, rid: RikId):
        return self.get(rid)
