"""Typed evidence and results for the Elo89a viability experiment."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.analysis.prediction.bouts import RatedBout
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


class ExperimentArm(str, Enum):
    """The paired replay variants in the Elo89a experiment."""

    CONTROL = "control"
    ELO89A = "elo89a"


@dataclass(frozen=True, slots=True)
class NonAppearanceCount:
    """Recorded non-appearances for one rikishi in one basho."""

    fusen_pai: int
    absences: int

    @property
    def total(self) -> int:
        return self.fusen_pai + self.absences


NonAppearanceLedger = dict[Date, dict[RikId, NonAppearanceCount]]


@dataclass(frozen=True)
class ReplayEvidence:
    """Immutable historical evidence prepared once for repeated replay."""

    dates: tuple[Date, ...]
    rated_bouts_by_date: dict[Date, tuple[RatedBout, ...]]
    non_appearances: NonAppearanceLedger
    raw_result_count: int
    rated_bout_count: int
    excluded_fusen_count: int
    excluded_draw_count: int


@dataclass(frozen=True, slots=True)
class BashoAdjustment:
    """Population and penalty accounting for one arm and basho."""

    arm: str
    date: str
    active_count: int
    new_rikishi_count: int
    departing_rikishi_count: int
    fusen_pai_count: int
    absence_count: int
    penalised_rikishi_count: int
    total_deducted_mass: float
    target_mean: float
    raw_start_mean: float
    start_adjustment: float
    normalised_start_mean: float
    raw_end_mean: float
    end_adjustment: float
    normalised_end_mean: float


@dataclass(frozen=True)
class ReplayResult:
    """Basho-boundary ratings and accounting from one complete replay."""

    arm: ExperimentArm
    target_mean: float
    basho_start_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)
    basho_end_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)
    adjustments: tuple[BashoAdjustment, ...] = ()


@dataclass(frozen=True, slots=True)
class IterationRow:
    """Convergence diagnostics for one completed solver iteration."""

    arm: str
    iteration: int
    max_prior_change: float
    max_change_chii: str
    max_change_chii_ordinal: int
    max_change_observation_count: int
    mean_recentering_adjustment: float
    minimum_recentering_adjustment: float
    maximum_recentering_adjustment: float


@dataclass(frozen=True, slots=True)
class IterationPrior:
    """One chii value retained from one completed solver iteration."""

    arm: str
    iteration: int
    chii: str
    ordinal: int
    observations: int
    rating: float


@dataclass(frozen=True)
class FixedPointResult:
    """Complete fixed-point result for one experimental arm."""

    arm: ExperimentArm
    priors: dict[Chii, float]
    support: dict[Chii, int]
    converged: bool
    iterations: int
    final_delta: float
    iteration_rows: tuple[IterationRow, ...]
    iteration_priors: tuple[IterationPrior, ...]
    replay: ReplayResult
