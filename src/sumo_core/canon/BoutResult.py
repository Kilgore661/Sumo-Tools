"""
BoutResult value object for sumo history.

Represents the recorded result of a single bout.

A BoutResult contains:
- the two participating rikishi
- the outcome recorded for each
- the decision mechanism
- the display symbol

The two rikishi must be distinct, and the two outcomes must form one of the
established valid combinations.
"""

from __future__ import annotations

from dataclasses import dataclass

from RikId import RikId
from Pair import Pair
from Outcome import Outcome
from Decision import Decision
from Symbol import Symbol


@dataclass
class BoutResult:
    rikishi1: RikId
    outcome1: Outcome
    rikishi2: RikId
    outcome2: Outcome
    decision: Decision
    symbol: Symbol

    def __post_init__(self):
        """
        Validate the structure of the bout result.

        The two rikishi must be distinct, and the two recorded outcomes
        must be mutually consistent.
        """
        _ = Pair(self.rikishi1, self.rikishi2)
        self._validate_outcome_consistency()

    def _validate_outcome_consistency(self):
        """
        Ensure that the pair of outcomes is one of the established valid forms.

        Valid combinations are:
        - {W, L}
        - {FS, FP}
        - {DRAW, DRAW}
        """
        outcome_pair = {self.outcome1, self.outcome2}

        valid_pairs = [
            {Outcome.W, Outcome.L},
            {Outcome.FS, Outcome.FP},
            {Outcome.DRAW, Outcome.DRAW},
        ]

        if outcome_pair not in valid_pairs:
            raise ValueError(
                f"Invalid outcome combination: {self.outcome1}, {self.outcome2}"
            )
