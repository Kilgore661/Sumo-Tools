"""
Derived results for multiple-basho standings.

Transforms multiple-basho core standings into a derived result set by:

- computing window-based and presence-based per-basho averages
- computing standard deviation, SEM, and CI95 half-width for those averages
- determining, per rikishi, how many selected basho they were present for
- sourcing display identity from the most recent selected basho in which the
  rikishi was present

This module provides:

    History × MultipleBashoCore × WinsMode -> MultipleBashoView

The confidence-interval half-widths use the usual symmetric normal-style
approximation around the sample mean.
"""

from dataclasses import dataclass
from math import sqrt

from src.analysis.standings.multiple_basho import MultipleBashoCore, WinsMode
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import Date, History
from src.sumo_core.BasicEnums import Outcome

CI95_Z = 1.96


@dataclass(frozen=True)
class MultipleBashoViewRow:
    position: int
    rikishi_id: RikId
    shikona: Shikona
    chii: str
    chii_ordinal: int
    real_wins: int
    all_wins: int
    bout_count: int
    selected_basho_count: int
    basho_present_count: int
    window_average_real_wins: float
    window_average_all_wins: float
    presence_average_real_wins: float
    presence_average_all_wins: float
    window_stdev_real_wins: float
    window_stdev_all_wins: float
    presence_stdev_real_wins: float
    presence_stdev_all_wins: float
    window_sem_real_wins: float
    window_sem_all_wins: float
    presence_sem_real_wins: float
    presence_sem_all_wins: float
    window_ci95_half_width_real_wins: float
    window_ci95_half_width_all_wins: float
    presence_ci95_half_width_real_wins: float
    presence_ci95_half_width_all_wins: float


@dataclass(frozen=True)
class MultipleBashoView:
    rows: tuple[MultipleBashoViewRow, ...]


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _sample_stdev(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0

    mean_value = _mean(values)
    variance = sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance)


def _sem(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return _sample_stdev(values) / sqrt(len(values))


def _ci95_half_width(values: list[float]) -> float:
    return CI95_Z * _sem(values)


def _wins_for_basho(
    history: History,
    date: Date,
    rikishi_id: RikId,
) -> tuple[int, int, bool]:
    basho = history(date)
    present = rikishi_id in basho.banzuke.riks

    real_wins = 0
    all_wins = 0

    for daily_results in basho.summary.values():
        for bout in daily_results.results_lookup.values():
            if bout.rikishi1 == rikishi_id:
                if bout.outcome1 == Outcome.W:
                    real_wins += 1
                    all_wins += 1
                elif bout.outcome1 == Outcome.FS:
                    all_wins += 1
            elif bout.rikishi2 == rikishi_id:
                if bout.outcome2 == Outcome.W:
                    real_wins += 1
                    all_wins += 1
                elif bout.outcome2 == Outcome.FS:
                    all_wins += 1

    return real_wins, all_wins, present


def _latest_selected_basho_with_rikishi(
    history: History,
    selected_dates: tuple[Date, ...],
    rikishi_id: RikId,
):
    for date in reversed(selected_dates):
        basho = history(date)
        if rikishi_id in basho.banzuke.riks:
            return basho

    raise ValueError(
        f"Rikishi {int(rikishi_id)} appears in multiple-basho core but in no selected basho."
    )


def get_multiple_basho_view(
    history: History,
    core: MultipleBashoCore,
    wins_mode: WinsMode,
) -> MultipleBashoView:
    selected_basho_count = len(core.selected_dates)

    sortable_rows: list[dict[str, object]] = []

    for row in core.rows:
        rid = row.rikishi_id
        display_basho = _latest_selected_basho_with_rikishi(history, core.selected_dates, rid)

        window_real_wins_by_basho: list[float] = []
        window_all_wins_by_basho: list[float] = []
        presence_real_wins_by_basho: list[float] = []
        presence_all_wins_by_basho: list[float] = []

        for date in core.selected_dates:
            real_wins, all_wins, present = _wins_for_basho(history, date, rid)
            window_real_wins_by_basho.append(float(real_wins))
            window_all_wins_by_basho.append(float(all_wins))

            if present:
                presence_real_wins_by_basho.append(float(real_wins))
                presence_all_wins_by_basho.append(float(all_wins))

        basho_present_count = len(presence_real_wins_by_basho)
        chii = display_basho.banzuke.get_chii(rid)

        if chii is None:
            raise ValueError(
                f"Rikishi {int(rid)} is on selected basho banzuke but has no chii in display basho."
            )

        sortable_rows.append(
            {
                "rikishi_id": rid,
                "shikona": display_basho.banzuke.get_shik(rid),
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "real_wins": row.real_wins,
                "all_wins": row.all_wins,
                "bout_count": row.bout_count,
                "selected_basho_count": selected_basho_count,
                "basho_present_count": basho_present_count,
                "window_average_real_wins": _mean(window_real_wins_by_basho),
                "window_average_all_wins": _mean(window_all_wins_by_basho),
                "presence_average_real_wins": _mean(presence_real_wins_by_basho),
                "presence_average_all_wins": _mean(presence_all_wins_by_basho),
                "window_stdev_real_wins": _sample_stdev(window_real_wins_by_basho),
                "window_stdev_all_wins": _sample_stdev(window_all_wins_by_basho),
                "presence_stdev_real_wins": _sample_stdev(presence_real_wins_by_basho),
                "presence_stdev_all_wins": _sample_stdev(presence_all_wins_by_basho),
                "window_sem_real_wins": _sem(window_real_wins_by_basho),
                "window_sem_all_wins": _sem(window_all_wins_by_basho),
                "presence_sem_real_wins": _sem(presence_real_wins_by_basho),
                "presence_sem_all_wins": _sem(presence_all_wins_by_basho),
                "window_ci95_half_width_real_wins": _ci95_half_width(window_real_wins_by_basho),
                "window_ci95_half_width_all_wins": _ci95_half_width(window_all_wins_by_basho),
                "presence_ci95_half_width_real_wins": _ci95_half_width(presence_real_wins_by_basho),
                "presence_ci95_half_width_all_wins": _ci95_half_width(presence_all_wins_by_basho),
            }
        )

    if wins_mode == WinsMode.REAL:
        primary = "presence_average_real_wins"
        secondary = "presence_average_all_wins"
        tertiary = "real_wins"
        quaternary = "all_wins"
    elif wins_mode == WinsMode.ALL:
        primary = "presence_average_all_wins"
        secondary = "presence_average_real_wins"
        tertiary = "all_wins"
        quaternary = "real_wins"
    else:
        raise ValueError(f"Unsupported wins mode: {wins_mode}")

    ordered = sorted(
        sortable_rows,
        key=lambda row: (
            -float(row[primary]),
            -float(row[secondary]),
            -int(row[tertiary]),
            -int(row[quaternary]),
            int(row["rikishi_id"]),
        ),
    )

    view_rows: list[MultipleBashoViewRow] = []
    previous_primary_value: float | None = None
    previous_position = 0

    for index, row in enumerate(ordered, start=1):
        current_primary_value = float(row[primary])

        if previous_primary_value is not None and abs(current_primary_value - previous_primary_value) < 1e-12:
            position = previous_position
        else:
            position = index
            previous_position = position
            previous_primary_value = current_primary_value

        view_rows.append(
            MultipleBashoViewRow(
                position=position,
                rikishi_id=row["rikishi_id"],
                shikona=row["shikona"],
                chii=row["chii"],
                chii_ordinal=int(row["chii_ordinal"]),
                real_wins=int(row["real_wins"]),
                all_wins=int(row["all_wins"]),
                bout_count=int(row["bout_count"]),
                selected_basho_count=int(row["selected_basho_count"]),
                basho_present_count=int(row["basho_present_count"]),
                window_average_real_wins=float(row["window_average_real_wins"]),
                window_average_all_wins=float(row["window_average_all_wins"]),
                presence_average_real_wins=float(row["presence_average_real_wins"]),
                presence_average_all_wins=float(row["presence_average_all_wins"]),
                window_stdev_real_wins=float(row["window_stdev_real_wins"]),
                window_stdev_all_wins=float(row["window_stdev_all_wins"]),
                presence_stdev_real_wins=float(row["presence_stdev_real_wins"]),
                presence_stdev_all_wins=float(row["presence_stdev_all_wins"]),
                window_sem_real_wins=float(row["window_sem_real_wins"]),
                window_sem_all_wins=float(row["window_sem_all_wins"]),
                presence_sem_real_wins=float(row["presence_sem_real_wins"]),
                presence_sem_all_wins=float(row["presence_sem_all_wins"]),
                window_ci95_half_width_real_wins=float(row["window_ci95_half_width_real_wins"]),
                window_ci95_half_width_all_wins=float(row["window_ci95_half_width_all_wins"]),
                presence_ci95_half_width_real_wins=float(row["presence_ci95_half_width_real_wins"]),
                presence_ci95_half_width_all_wins=float(row["presence_ci95_half_width_all_wins"]),
            )
        )

    return MultipleBashoView(rows=tuple(view_rows))
