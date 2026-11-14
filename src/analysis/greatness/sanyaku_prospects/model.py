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
    outcome_evidence: str
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
class RankStateObservation:
    rikishi_id: int
    shikona: str
    basho: str
    start_date: str
    age: int
    division: str
    rank_number: int
    chii: str
    first_sanyaku_basho: str
    first_sanyaku_chii: str
    outcome: str
    outcome_evidence: str
    follow_up_basho: int
    intai: str


@dataclass(frozen=True)
class RankStateProbabilityRow:
    division: str
    rank_number: int
    age: int
    observations: int
    unique_rikishi: int
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
class CareerChartPoint:
    rikishi_id: int
    shikona: str
    basho: str
    date: str
    age: int
    exact_age: float
    division: str
    rank_number: int
    chii: str
    point_kind: str
    probability: float | str
    cohort_observations: int | str
    cohort_rikishi: int | str
    cohort_success: int | str
    cohort_failure: int | str
    cohort_unresolved: int | str
    cohort_resolved: int | str
    support_tier: str


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
    rank_state_observations: Path
    rank_state_probabilities: Path
    career_chart_points: Path
    career_charts: tuple[Path, ...]
    manifest: Path
