# src/analysis/equelo/diagnostics.py

from dataclasses import dataclass, field

from ...sumo_core.History import Date
from ...sumo_core.Banzuke import Banzuke
from ...sumo_core.Summary import BoutResult
from ...sumo_core.BasicPrimitives import RikId, Day

from .EloParams import EloParams


@dataclass
class BashoSummaryRow:
    date: Date
    n_rikishi: int
    rating_mass: float
    mean_rating: float
    mean_abs_bout_update: float


@dataclass
class RetirementRow:
    date: Date
    rikid: RikId
    rating: float
    n: int
    delta: float
    delta_per_rikishi: float
    abs_delta_per_rikishi: float


@dataclass
class RatingsDiagnostics:
    basho_rows: list[BashoSummaryRow] = field(default_factory=list)
    retirement_rows: list[RetirementRow] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class DiagnosticsCollector:
    def __init__(self, params: EloParams) -> None:
        self.params = params

    def on_basho_start(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        pass

    def on_entry(self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]) -> None:
        pass

    def on_day_start(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        pass

    def on_bout(
        self,
        date: Date,
        day: Day,
        bout: BoutResult,
        delta: float,
        r1_before: float,
        r2_before: float,
        r1_after: float,
        r2_after: float,
        rating_mass_after: float,
    ) -> None:
        pass

    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None:
        pass

    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        pass

    def on_basho_end(self, date: Date, ratings: dict[RikId, float]) -> None:
        pass

    def finalise(self) -> RatingsDiagnostics:
        return RatingsDiagnostics()
