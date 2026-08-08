"""Immutable definition of the first Basic Elo prediction experiment."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date


PROPOSAL_1_START = Date(Year(1989), Month(1))


@dataclass(frozen=True)
class Proposal1Definition:
    """Fixed Basic Elo definition plus reproducible evaluation settings."""

    end_date: Date
    start_date: Date = PROPOSAL_1_START
    q: float = 400.0
    k: float = 35.0
    initial_rating: float = 1500.0
    reference_probability: float = 0.5
    rolling_windows: tuple[int, ...] = (6, 12, 24)
    bootstrap_seed: int = 198901
    bootstrap_resamples: int = 2000
    confidence_level: float = 0.95
