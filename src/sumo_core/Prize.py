"""
Prize enum for sumo history.

Represents special prizes awarded in a basho.

Members:
- SHUKUN    : Outstanding Performance Prize
- KANTO     : Fighting Spirit Prize
- GINO      : Technique Prize
"""

from __future__ import annotations

from enum import Enum


class Prize(Enum):
    SHUKUN = "Shukun-sho"
    KANTO = "Kanto-sho"
    GINO = "Gino-sho"

    def __str__(self) -> str:
        return self.value
