"""
Performance value object for sumo history.

Represents a rikishi's performance in a single basho.

A Performance consists of:
- wins      : number of wins
- losses    : number of losses
- absences  : number of absences
- yusho     : whether the rikishi won the tournament
- prizes    : set of special prizes awarded

Invariant:
- wins, losses, absences must be non-negative integers
"""

from __future__ import annotations

from dataclasses import dataclass
from Prize import Prize


@dataclass
class Performance:
    wins: int
    losses: int
    absences: int
    yusho: bool
    prizes: set[Prize]

    def __post_init__(self):
        if self.wins < 0:
            raise ValueError(f"wins must be non-negative, got {self.wins}")

        if self.losses < 0:
            raise ValueError(f"losses must be non-negative, got {self.losses}")

        if self.absences < 0:
            raise ValueError(f"absences must be non-negative, got {self.absences}")
