"""
Core domain logic for multiple-basho standings.

Defines the core standings result types and computes ranked totals for a
contiguous window of basho under a specified wins policy.

This module is concerned only with core calculation:

    History × selected_dates -> MultipleBashoCore

It does not perform derived-metric calculation, formatting, persistence, or
argument parsing.
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
    position: int
    rikishi_id: RikId
    real_wins: int
    all_wins: int
    bout_count: int


@dataclass(frozen=True)
class MultipleBashoCore:
    selected_dates: tuple[Date, ...]
    rows: tuple[MultipleBashoCoreRow, ...]


def resolve_date(
    history: History,
    direction: str,
    requested_date: str | None,
) -> Date:
    dates = sorted(history.keys())

    if requested_date is not None:
        matching = [date for date in dates if str(date) == requested_date]
        if not matching:
            raise ValueError(f"Date '{requested_date}' not found in History.")
        return matching[0]

    if direction == "BACKWARDS":
        return dates[-1]

    if direction == "FORWARDS":
        return dates[0]

    raise ValueError(f"Unsupported direction: {direction}")


def resolve_window_dates(
    history: History,
    date: Date,
    direction: str,
    num_basho: int,
) -> tuple[Date, ...]:
    if num_basho <= 0:
        raise ValueError("num_basho must be positive.")

    dates = sorted(history.keys())
    idx = dates.index(date)

    if direction == "BACKWARDS":
        start = max(0, idx - num_basho + 1)
        return tuple(dates[start : idx + 1])

    if direction == "FORWARDS":
        end = min(len(dates), idx + num_basho)
        return tuple(dates[idx:end])

    raise ValueError(f"Unsupported direction: {direction}")


def get_multiple_basho_core(
    history: History,
    selected_dates: tuple[Date, ...],
    wins_mode: WinsMode,
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

    if wins_mode == WinsMode.REAL:
        primary = "real_wins"
        secondary = "all_wins"
    elif wins_mode == WinsMode.ALL:
        primary = "all_wins"
        secondary = "real_wins"
    else:
        raise ValueError(f"Unsupported wins mode: {wins_mode}")

    ordered = sorted(
        totals.values(),
        key=lambda row: (
            -int(row[primary]),
            -int(row[secondary]),
            int(row["rikishi_id"]),
        ),
    )

    ranked_rows: list[MultipleBashoCoreRow] = []
    previous_primary_value = None
    previous_position = 0

    for index, row in enumerate(ordered, start=1):
        current_primary_value = int(row[primary])

        if current_primary_value == previous_primary_value:
            position = previous_position
        else:
            position = index
            previous_position = position
            previous_primary_value = current_primary_value

        ranked_rows.append(
            MultipleBashoCoreRow(
                position=position,
                rikishi_id=row["rikishi_id"],
                real_wins=int(row["real_wins"]),
                all_wins=int(row["all_wins"]),
                bout_count=int(row["bout_count"]),
            )
        )

    return MultipleBashoCore(selected_dates=selected_dates, rows=tuple(ranked_rows))
