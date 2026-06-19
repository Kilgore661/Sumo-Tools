"""Dump fixed-point aggregate contributions for extreme-rating exploration."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import (
    SimulationMode,
    SimulationObserver,
    SimulationResult,
    simulate,
)
from src.analysis.equelo.fixed_v2.build import (
    fixed_point_ratings,
    load_bios,
    make_chii_initialiser,
    oracle_collapse_mode,
)
from src.analysis.equelo.fixed_v2.model import K_CONFIG, K_POLICY, OUTPUT_ROOT, Q
from src.infra.live_store.api import get_history
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult


DEFAULT_OUTPUT_PATH = (
    OUTPUT_ROOT
    / "exploration"
    / "extreme_ratings"
    / "fixed_point_aggregate_contributions.csv"
)
DEFAULT_SUMMARY_OUTPUT_PATH = (
    OUTPUT_ROOT
    / "exploration"
    / "extreme_ratings"
    / "fixed_point_aggregate_summary_by_chii.csv"
)


@dataclass
class ChiiAggregateSummary:
    chii: str
    chii_ordinal: int
    count: int = 0
    entry_count: int = 0
    non_entry_count: int = 0
    rating_total: float = 0.0
    min_basho_start_rating: float | None = None
    max_basho_start_rating: float | None = None
    first_date: str | None = None
    last_date: str | None = None

    def add(self, *, date: str, basho_start_rating: float, entry: bool) -> None:
        self.count += 1
        if entry:
            self.entry_count += 1
        else:
            self.non_entry_count += 1

        self.rating_total += basho_start_rating
        self.min_basho_start_rating = (
            basho_start_rating
            if self.min_basho_start_rating is None
            else min(self.min_basho_start_rating, basho_start_rating)
        )
        self.max_basho_start_rating = (
            basho_start_rating
            if self.max_basho_start_rating is None
            else max(self.max_basho_start_rating, basho_start_rating)
        )
        self.first_date = date if self.first_date is None else min(self.first_date, date)
        self.last_date = date if self.last_date is None else max(self.last_date, date)

    @property
    def mean_basho_start_rating(self) -> float:
        return self.rating_total / self.count


class EntryContributionObserver(SimulationObserver):
    """Record which rikishi were initialised as entries in each basho."""

    def __init__(self) -> None:
        self.entries_by_date: dict[Date, set[RikId]] = defaultdict(set)

    def on_basho_start(
        self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke
    ) -> None:
        del date, ratings, banzuke

    def on_entry(
        self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]
    ) -> None:
        del rating, ratings
        self.entries_by_date[date].add(rikid)

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
        del date, rikid, rating, n, delta, delta_per_rikishi, abs_delta_per_rikishi, closed

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
        del (
            date,
            day,
            bout,
            delta,
            r1_before,
            r2_before,
            r1_after,
            r2_after,
            rating_mass_before,
            rating_mass_after,
        )

    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None:
        del date, day, bout

    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        del date, day, ratings

    def on_basho_end(
        self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke
    ) -> None:
        del date, ratings, banzuke


def compute_fixed_v2_contribution_context() -> tuple[
    History, SimulationResult, EntryContributionObserver
]:
    """Run the fixed_v2 final simulation pass with entry instrumentation."""

    raw_history = get_history()
    oracle = make_oracle(
        raw_history,
        load_bios(),
        collapse_mode=oracle_collapse_mode(),
    )
    params = build_elo_params(
        k_policy=K_POLICY,
        q=Q,
        config_path=K_CONFIG,
    )
    observer = EntryContributionObserver()
    result = simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=make_chii_initialiser(fixed_point_ratings()),
        mode=SimulationMode.CLOSED,
        observer=observer,
    )
    return oracle.history, result, observer


def write_fixed_point_aggregate_contributions(
    *,
    history: History,
    result: SimulationResult,
    observer: EntryContributionObserver,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Write one CSV row for each observation used by Expt2 aggregation."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "chii",
                "chii_ordinal",
                "date",
                "rikishi_id",
                "basho_start_rating",
                "entry",
            ]
        )

        for date in sorted(history.keys()):
            start_ratings = result.basho_start_ratings[date]
            entries = observer.entries_by_date.get(date, set())
            banzuke = history[date].banzuke

            for rikid, chii in sorted(
                banzuke.rikchii.items(),
                key=lambda item: (item[1].ordinal(), int(item[0])),
            ):
                writer.writerow(
                    [
                        str(chii),
                        chii.ordinal(),
                        str(date),
                        int(rikid),
                        start_ratings[rikid],
                        str(rikid in entries).lower(),
                    ]
                )

    return output_path


def write_fixed_point_aggregate_summary(
    *,
    contributions_path: Path,
    output_path: Path = DEFAULT_SUMMARY_OUTPUT_PATH,
) -> Path:
    """Summarise aggregate contributions by exact chii."""

    summaries: dict[int, ChiiAggregateSummary] = {}

    with contributions_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ordinal = int(row["chii_ordinal"])
            summary = summaries.get(ordinal)
            if summary is None:
                summary = ChiiAggregateSummary(
                    chii=row["chii"],
                    chii_ordinal=ordinal,
                )
                summaries[ordinal] = summary

            summary.add(
                date=row["date"],
                basho_start_rating=float(row["basho_start_rating"]),
                entry=row["entry"] == "true",
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "chii",
                "chii_ordinal",
                "count",
                "entry_count",
                "non_entry_count",
                "mean_basho_start_rating",
                "min_basho_start_rating",
                "max_basho_start_rating",
                "first_date",
                "last_date",
            ]
        )
        for summary in sorted(summaries.values(), key=lambda item: item.chii_ordinal):
            writer.writerow(
                [
                    summary.chii,
                    summary.chii_ordinal,
                    summary.count,
                    summary.entry_count,
                    summary.non_entry_count,
                    summary.mean_basho_start_rating,
                    summary.min_basho_start_rating,
                    summary.max_basho_start_rating,
                    summary.first_date,
                    summary.last_date,
                ]
            )

    return output_path


def build_fixed_point_aggregate_contribution_dump(
    output_path: Path = DEFAULT_OUTPUT_PATH,
    summary_output_path: Path = DEFAULT_SUMMARY_OUTPUT_PATH,
) -> tuple[Path, Path]:
    """Build exploratory fixed-point aggregate contribution and summary CSVs."""

    history, result, observer = compute_fixed_v2_contribution_context()
    contributions_path = write_fixed_point_aggregate_contributions(
        history=history,
        result=result,
        observer=observer,
        output_path=output_path,
    )
    summary_path = write_fixed_point_aggregate_summary(
        contributions_path=contributions_path,
        output_path=summary_output_path,
    )
    return contributions_path, summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dump fixed_v2 aggregate contributions for extreme-rating exploration."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Contribution CSV path to write.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT_PATH,
        help="Summary CSV path to write.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contributions_path, summary_path = build_fixed_point_aggregate_contribution_dump(
        output_path=args.output,
        summary_output_path=args.summary_output,
    )
    print(f"Wrote fixed-point aggregate contributions: {contributions_path}")
    print(f"Wrote fixed-point aggregate summary: {summary_path}")


if __name__ == "__main__":
    main()
