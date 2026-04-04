from dataclasses import dataclass, field
import csv
from pathlib import Path

from ...sumo_core.History import Date
from ...sumo_core.Banzuke import Banzuke
from ...sumo_core.Summary import BoutResult
from ...sumo_core.BasicPrimitives import RikId, Day

from .EloParams import EloParams
from .config import OUTPUT_ROOT


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
    basho_summary_csv_path: Path | None = None
    retirements_csv_path: Path | None = None


class DiagnosticsCollector:
    def __init__(self, params: EloParams, closed: bool = False) -> None:
        self.params = params
        self.closed = closed
        self._basho_rows: list[BashoSummaryRow] = []
        self._retirement_rows: list[RetirementRow] = []
        self._current_basho_abs_updates: list[float] = []
        self._max_abs_mean_deviation_from_b = 0.0
        self._max_abs_bout_mass_change = 0.0
        self._ignored_fusen_count = 0
        self._ignored_blank_count = 0
        self._entry_count = 0
        self._retirement_count = 0

    def on_basho_start(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        self._current_basho_abs_updates = []

    def on_entry(self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]) -> None:
        self._entry_count += 1

    def on_retirement(
        self,
        date: Date,
        rikid: RikId,
        rating: float,
        n: int,
        delta: float,
        delta_per_rikishi: float,
        abs_delta_per_rikishi: float,
        closed: bool,
    ) -> None:
        self._retirement_count += 1
        self._retirement_rows.append(
            RetirementRow(
                date=date,
                rikid=rikid,
                rating=rating,
                n=n,
                delta=delta,
                delta_per_rikishi=delta_per_rikishi,
                abs_delta_per_rikishi=abs_delta_per_rikishi,
            )
        )

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
        rating_mass_before: float,
        rating_mass_after: float,
    ) -> None:
        self._current_basho_abs_updates.append(abs(delta))
        abs_mass_change = abs(rating_mass_after - rating_mass_before)
        if abs_mass_change > self._max_abs_bout_mass_change:
            self._max_abs_bout_mass_change = abs_mass_change

    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None:
        if bout.decision == "fusen":
            self._ignored_fusen_count += 1
        elif bout.decision == "blank":
            self._ignored_blank_count += 1

    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        pass

    def on_basho_end(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        basho_end_ratings = [ratings[rid] for rid in banzuke.riks]
        n_rikishi = len(basho_end_ratings)
        rating_mass = sum(basho_end_ratings)
        mean_rating = rating_mass / n_rikishi if n_rikishi else self.params.b
        mean_deviation = abs(mean_rating - self.params.b)
        if mean_deviation > self._max_abs_mean_deviation_from_b:
            self._max_abs_mean_deviation_from_b = mean_deviation
        mean_abs_bout_update = (
            sum(self._current_basho_abs_updates) / len(self._current_basho_abs_updates)
            if self._current_basho_abs_updates else 0.0
        )
        self._basho_rows.append(
            BashoSummaryRow(
                date=date,
                n_rikishi=n_rikishi,
                rating_mass=rating_mass,
                mean_rating=mean_rating,
                mean_abs_bout_update=mean_abs_bout_update,
            )
        )

    def finalise(self) -> RatingsDiagnostics:
        basho_path = self._write_basho_summary_csv(self._basho_rows)
        retirements_path = self._write_retirements_csv(self._retirement_rows)
        diagnostics = RatingsDiagnostics(
            basho_rows=self._basho_rows,
            retirement_rows=self._retirement_rows,
            notes=[],
            basho_summary_csv_path=basho_path,
            retirements_csv_path=retirements_path,
        )
        diagnostics.notes.append('"fusen" is ignored as a rating event.')
        diagnostics.notes.append('"blank" is ignored as a rating event.')
        diagnostics.notes.append(
            "Closed retirement handling is enabled."
            if self.closed else "Retirement handling is not yet implemented."
        )
        diagnostics.notes.append(
            f"Maximum absolute deviation of basho-end mean rating from b: {self._max_abs_mean_deviation_from_b:.12f}"
        )
        diagnostics.notes.append(
            f"Maximum absolute change in rating mass across a scored bout: {self._max_abs_bout_mass_change:.12f}"
        )
        diagnostics.notes.append(f"Total new-entry events: {self._entry_count}")
        diagnostics.notes.append(f"Total retirements observed: {self._retirement_count}")
        diagnostics.notes.append(f'Total ignored "fusen" bouts: {self._ignored_fusen_count}')
        diagnostics.notes.append(f'Total ignored "blank" bouts: {self._ignored_blank_count}')
        return diagnostics

    def _suffix(self) -> str:
        return "_closed" if self.closed else ""

    def _write_basho_summary_csv(self, rows: list[BashoSummaryRow]) -> Path:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_ROOT / f"basho_summary{self._suffix()}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "n_rikishi", "rating_mass", "mean_rating", "mean_abs_bout_update"])
            for row in rows:
                writer.writerow([str(row.date), row.n_rikishi, row.rating_mass, row.mean_rating, row.mean_abs_bout_update])
        return path

    def _write_retirements_csv(self, rows: list[RetirementRow]) -> Path:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_ROOT / f"retirements{self._suffix()}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "rikid", "rating", "n", "delta", "delta_per_rikishi", "abs_delta_per_rikishi"])
            for row in rows:
                writer.writerow([str(row.date), int(row.rikid), row.rating, row.n, row.delta, row.delta_per_rikishi, row.abs_delta_per_rikishi])
        return path
