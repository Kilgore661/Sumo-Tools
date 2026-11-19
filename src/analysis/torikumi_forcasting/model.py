"""Data contracts for the greedy torikumi-forecasting experiment."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.sumo_core.BasicPrimitives import Pair, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


@dataclass(frozen=True)
class Standing:
    rikid: RikId
    shikona: str
    chii: Chii
    wins: int
    heya: str
    synthetic_heya: bool
    position: int


@dataclass(frozen=True)
class ForecastCase:
    basho: Date
    day: int
    standings: tuple[Standing, ...]
    prior_pairs: frozenset[Pair]
    actual_pairs: frozenset[Pair]
    actual_unmatched: tuple[RikId, ...]


@dataclass(frozen=True)
class CandidateRejection:
    opponent: RikId
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class UnpairedDiagnostic:
    rikishi: RikId
    rejections: tuple[CandidateRejection, ...]


@dataclass(frozen=True)
class ForecastPair:
    east: Standing
    west: Standing

    @property
    def pair(self) -> Pair:
        return Pair(self.east.rikid, self.west.rikid)


@dataclass(frozen=True)
class GreedyForecast:
    pairs: tuple[ForecastPair, ...]
    unpaired: tuple[Standing, ...]
    diagnostics: tuple[UnpairedDiagnostic, ...]
    success: bool


@dataclass(frozen=True)
class ConstrainedForecast:
    status: str
    pairs: tuple[ForecastPair, ...]
    unpaired: tuple[Standing, ...]
    objective_cost: int | None
    best_objective_bound: float | None
    solve_seconds: float


@dataclass(frozen=True)
class CaseResult:
    case: ForecastCase
    forecast: GreedyForecast
    split: str
    recovered_pairs: int
    pair_recovery_rate: float
    unmatched_correct: bool | None
    exact: bool


@dataclass(frozen=True)
class ConstrainedCaseResult:
    case: ForecastCase
    forecast: ConstrainedForecast
    split: str
    recovered_pairs: int
    pair_recovery_rate: float
    unmatched_correct: bool | None
    exact: bool


@dataclass(frozen=True)
class CaseExclusion:
    basho: Date
    day: int
    population_size: int
    actual_unmatched_count: int
    parity_minimum: int
    reason: str


@dataclass(frozen=True)
class AnalysisResult:
    selected_first_basho: Date
    selected_last_basho: Date
    included_basho_count: int
    excluded_incomplete_basho_count: int
    first_day: int
    holdout_first_basho: Date | None
    cases: tuple[CaseResult, ...]
    exclusions: tuple[CaseExclusion, ...]


@dataclass(frozen=True)
class ConstrainedAnalysisResult:
    selected_first_basho: Date
    selected_last_basho: Date
    included_basho_count: int
    excluded_incomplete_basho_count: int
    first_day: int
    holdout_first_basho: Date | None
    cases: tuple[ConstrainedCaseResult, ...]
    exclusions: tuple[CaseExclusion, ...]


@dataclass(frozen=True)
class OutputPaths:
    run_directory: Path
    cases_csv: Path
    excluded_cases_csv: Path
    forecast_pairs_csv: Path
    heya_diagnostics_csv: Path
    failure_diagnostics_csv: Path
    report_md: Path
    manifest_json: Path
