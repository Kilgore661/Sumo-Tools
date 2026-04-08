from pdb import set_trace

"""Diagnostics collection for Expt1 runs.

The simulation API does not return diagnostics. Instead, a caller may attach a
collector implementing the observer hooks used here. This keeps programmatic
simulation results separate from audit/log artefacts.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path

from ....sumo_core.Banzuke import Banzuke
from ....sumo_core.BasicPrimitives import RikId, Day
from ....sumo_core.History import Date
from ....sumo_core.Summary import BoutResult

from .params import EloParams
from ..config_main import OUTPUT_ROOT


@dataclass(frozen=True)
class BashoSummaryRow:
    date: Date
    n_rikishi: int
    rating_mass: float
    mean_rating: float
    mean_abs_bout_update: float


@dataclass(frozen=True)
class RetirementRow:
    date: Date
    rikid: RikId
    rating: float
    n: int
    delta: float
    delta_per_rikishi: float
    abs_delta_per_rikishi: float


@dataclass(frozen=True)
class DiagnosticsSummary:
    """Structured summary of one simulation run.

    This object is intended for logging and audit, not as the main simulation
    result contract.
    """

    basho_rows: list[BashoSummaryRow] = field(default_factory=list)
    retirement_rows: list[RetirementRow] = field(default_factory=list)
    max_abs_mean_deviation_from_b: float = 0.0
    max_abs_bout_mass_change: float = 0.0
    ignored_fusen_count: int = 0
    ignored_blank_count: int = 0
    entry_count: int = 0
    retirement_count: int = 0
    max_abs_adjustment_pre_1989: float = 0.0
    max_abs_adjustment_post_1989: float = 0.0
    basho_summary_csv_path: Path | None = None
    retirements_csv_path: Path | None = None
    run_log_path: Path | None = None


class DiagnosticsCollector:
    """Observer that records Expt1 diagnostics and persists them to disk.

    The collector is mode-aware:

    * ``OPEN`` means departures simply leave the active universe
    * ``CLOSED`` means departures are redistributed uniformly over the active
      survivors so that the active-universe mean is preserved at basho
      boundaries
    """

    def __init__(
        self,
        params: EloParams,
        mode_name: str,
        k_policy: str,
        k_value: float | None = None,
        k_config_path: Path | None = None,
    ) -> None:
        self.params = params
        self.mode_name = mode_name
        self.k_policy = k_policy
        self.k_value = k_value
        self.k_config_path = k_config_path
        self._basho_rows: list[BashoSummaryRow] = []
        self._retirement_rows: list[RetirementRow] = []
        self._current_basho_abs_updates: list[float] = []
        self._max_abs_mean_deviation_from_b = 0.0
        self._max_abs_bout_mass_change = 0.0
        self._ignored_fusen_count = 0
        self._ignored_blank_count = 0
        self._entry_count = 0
        self._retirement_count = 0
        self._max_abs_adjustment_pre_1989 = 0.0
        self._max_abs_adjustment_post_1989 = 0.0

    def on_basho_start(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        del date, ratings, banzuke
        self._current_basho_abs_updates = []

    def on_entry(self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]) -> None:
        del date, rikid, rating, ratings
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
        del closed
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

        if n > 0:
            if date.year < 1989:
                if abs_delta_per_rikishi > self._max_abs_adjustment_pre_1989:
                    self._max_abs_adjustment_pre_1989 = abs_delta_per_rikishi
            else:
                if abs_delta_per_rikishi > self._max_abs_adjustment_post_1989:
                    self._max_abs_adjustment_post_1989 = abs_delta_per_rikishi

    def on_day_start(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        del date, day, ratings

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
        del date, day, bout, r1_before, r2_before, r1_after, r2_after
        self._current_basho_abs_updates.append(abs(delta))
        abs_mass_change = abs(rating_mass_after - rating_mass_before)
        if abs_mass_change > self._max_abs_bout_mass_change:
            self._max_abs_bout_mass_change = abs_mass_change

    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None:
        del date, day
        if bout.decision == "fusen":
            self._ignored_fusen_count += 1
        elif bout.decision == "blank":
            self._ignored_blank_count += 1

    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        del date, day, ratings

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

    def finalise(self) -> DiagnosticsSummary:
        basho_path = self._write_basho_summary_csv(self._basho_rows)
        retirements_path = self._write_retirements_csv(self._retirement_rows)
        run_log_path = self._write_run_log()
        return DiagnosticsSummary(
            basho_rows=self._basho_rows,
            retirement_rows=self._retirement_rows,
            max_abs_mean_deviation_from_b=self._max_abs_mean_deviation_from_b,
            max_abs_bout_mass_change=self._max_abs_bout_mass_change,
            ignored_fusen_count=self._ignored_fusen_count,
            ignored_blank_count=self._ignored_blank_count,
            entry_count=self._entry_count,
            retirement_count=self._retirement_count,
            max_abs_adjustment_pre_1989=self._max_abs_adjustment_pre_1989,
            max_abs_adjustment_post_1989=self._max_abs_adjustment_post_1989,
            basho_summary_csv_path=basho_path,
            retirements_csv_path=retirements_path,
            run_log_path=run_log_path,
        )

    def _suffix(self) -> str:
        return f"_{self.mode_name.lower()}"

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

    def _write_run_log(self) -> Path:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_ROOT / f"run_log{self._suffix()}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("Expt1 diagnostics log\n")
            f.write(f"mode: {self.mode_name}\n")
            f.write(f"baseline b: {self.params.b}\n")
            f.write(f"q: {self.params.q}\n")
            f.write(f"k policy: {self.k_policy}\n")
            if self.k_policy == "constant":
                f.write(f"k value: {self.k_value}\n")
            elif self.k_config_path is not None:
                f.write(f"k config path: {self.k_config_path}\n")
            f.write(f"max abs basho-end mean deviation from b: {self._max_abs_mean_deviation_from_b:.12f}\n")
            f.write(f"max abs rating-mass change across scored bout: {self._max_abs_bout_mass_change:.12f}\n")
            f.write(f"entry events: {self._entry_count}\n")
            f.write(f"retirement events: {self._retirement_count}\n")
            f.write(f"ignored fusen bouts: {self._ignored_fusen_count}\n")
            f.write(f"ignored blank bouts: {self._ignored_blank_count}\n")
            f.write(
                "max abs retiree redistribution per rikishi, pre-1989: "
                f"{self._max_abs_adjustment_pre_1989:.12f}\n"
            )
            f.write(
                "max abs retiree redistribution per rikishi, 1989+: "
                f"{self._max_abs_adjustment_post_1989:.12f}\n"
            )
            f.write("open mode meaning: departures leave the active universe without redistribution\n")
            f.write("closed mode meaning: departures are redistributed uniformly over active survivors\n")
        return path
