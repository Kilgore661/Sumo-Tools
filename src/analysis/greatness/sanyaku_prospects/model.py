from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date


@dataclass(frozen=True)
class ExclusionRow:
    rikishi_id: int
    shikona: str
    reason: str
    first_basho: str
    first_chii: str
    detail: str


@dataclass(frozen=True)
class Population:
    epoch: Date
    cutoff: Date
    dates: tuple[Date, ...]
    history_ids: frozenset[RikId]
    boundary_ids: frozenset[RikId]
    complete_ids: frozenset[RikId]
    birth_dated_ids: frozenset[RikId]
    exclusions: tuple[ExclusionRow, ...]


@dataclass(frozen=True)
class CohortObservation:
    cohort_type: str
    rikishi_id: int
    shikona: str
    division: str
    age: int
    observation_basho: str
    observation_start_date: str
    observation_chii: str
    division_debut_basho: str
    division_debut_age: int
    first_sanyaku_basho: str
    first_sanyaku_chii: str
    outcome: str
    follow_up_basho: int
    intai: str


@dataclass(frozen=True)
class ProbabilityRow:
    division: str
    age: int
    rikishi: int
    success: int
    failure: int
    right_censored: int
    unknown: int
    resolved: int
    resolved_probability: float | str
    lower_bound_probability: float
    upper_bound_probability: float
    cutoff: str


@dataclass(frozen=True)
class OutputPaths:
    root: Path
    population_summary: Path
    population_exclusions: Path
    basho_date_coverage: Path
    cohort_observations: Path
    outcome_summary: Path
    debut_probabilities: Path
    state_probabilities: Path
    manifest: Path
