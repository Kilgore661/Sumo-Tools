"""
DailyResults aggregate for sumo history.

Represents the results recorded for a single day of a basho.

A DailyResults consists of:
- torikumi       : the set of scheduled bouts
- results_lookup : a partial function from Pair to BoutResult

This class intentionally performs no internal validation.
In the established model, the relevant consistency constraints are enforced
at higher aggregate level, not here.
"""

from __future__ import annotations

from dataclasses import dataclass

from Torikumi import Torikumi
from ResultLookup import ResultLookup


@dataclass
class DailyResults:
    torikumi: Torikumi
    results_lookup: ResultLookup
