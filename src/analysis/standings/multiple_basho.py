"""
Core domain logic for multiple-basho standings.

Defines the core result types and computes aggregated win and bout totals
for a contiguous window of basho under a specified wins policy.

This module is concerned only with domain calculation:

    History × selected_dates -> MultipleBashoCore

It does not perform I/O, persistence, argument parsing, derived metric
calculation, or final presentation.
"""

from dataclasses import dataclass
from enum import Enum, auto

from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


class WinsMode(Enum):
    REAL = auto()
    ALL = auto()


@dataclass(frozen=True)
class MultipleBashoCoreRow:
    rikishi_id: RikId
    real_wins: int
    all_wins: int
    bout_count: int


@dataclass(frozen=True)
class MultipleBashoCore:
    selected_dates: tuple[Date, ...]
    rows: tuple[MultipleBashoCoreRow, ...]


def get_multiple_basho_core(
    history: History,
    selected_dates: tuple[Date, ...],
) -> MultipleBashoCore:
    totals: dict[RikId, dict[str, object]] = {}

    for date in selected_dates:
        basho = history(date)

        for rid in basho.banzuke.riks:
            if rid not in totals:
                totals[rid] = {
                    "rikishi_id": rid,
                    "real_wins": 0,
                    "all_wins": 0,
                    "bout_count": 0,
                }

        for daily_results in basho.summary.values():
            for bout in daily_results.results_lookup.values():
                r1 = bout.rikishi1
                r2 = bout.rikishi2

                if r1 not in totals:
                    totals[r1] = {
                        "rikishi_id": r1,
                        "real_wins": 0,
                        "all_wins": 0,
                        "bout_count": 0,
                    }
                if r2 not in totals:
                    totals[r2] = {
                        "rikishi_id": r2,
                        "real_wins": 0,
                        "all_wins": 0,
                        "bout_count": 0,
                    }

                totals[r1]["bout_count"] = int(totals[r1]["bout_count"]) + 1
                totals[r2]["bout_count"] = int(totals[r2]["bout_count"]) + 1

                if bout.outcome1 == Outcome.W:
                    totals[r1]["real_wins"] = int(totals[r1]["real_wins"]) + 1
                    totals[r1]["all_wins"] = int(totals[r1]["all_wins"]) + 1
                elif bout.outcome1 == Outcome.FS:
                    totals[r1]["all_wins"] = int(totals[r1]["all_wins"]) + 1

                if bout.outcome2 == Outcome.W:
                    totals[r2]["real_wins"] = int(totals[r2]["real_wins"]) + 1
                    totals[r2]["all_wins"] = int(totals[r2]["all_wins"]) + 1
                elif bout.outcome2 == Outcome.FS:
                    totals[r2]["all_wins"] = int(totals[r2]["all_wins"]) + 1

    ordered_rikishi_ids = sorted(totals.keys(), key=int)
    rows = tuple(
        MultipleBashoCoreRow(
            rikishi_id=rid,
            real_wins=int(totals[rid]["real_wins"]),
            all_wins=int(totals[rid]["all_wins"]),
            bout_count=int(totals[rid]["bout_count"]),
        )
        for rid in ordered_rikishi_ids
    )

    return MultipleBashoCore(
        selected_dates=selected_dates,
        rows=rows,
    )
