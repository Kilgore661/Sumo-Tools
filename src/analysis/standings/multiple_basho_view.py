"""
Derived results for multiple-basho standings.

Transforms multiple-basho core standings into a derived result set by:

- computing selected-basho and containing-basho per-basho averages
- computing standard deviation, SEM, and CI95 half-width for those averages
- determining, per rikishi, how many selected basho contain the rikishi
- computing explicit expected and available bout counts on both basho bases
- sourcing display identity from the most recent selected basho containing the
  rikishi

This module provides:

    History × MultipleBashoCore × WinPolicy -> MultipleBashoView

The confidence-interval half-widths use the usual symmetric normal-style
approximation around the sample mean.
"""

from dataclasses import dataclass
from math import sqrt

from src.analysis.standings.multiple_basho import MultipleBashoCore
from src.analysis.standings.classes import WinPolicy
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import Date, History
from src.sumo_core.BasicEnums import Outcome, Division, MSD
from src.sumo_core.Chii import Chii

CI95_Z = 1.96


@dataclass(frozen=True)
class MultipleBashoViewRow:
    position: int
    rikishi_id: RikId
    shikona: Shikona
    chii: str
    chii_ordinal: int
    fought_wins: int
    credited_wins: int
    bout_count: int
    selected_basho_count: int
    containing_basho_count: int

    selected_expected_bout_count: int
    selected_available_bout_count: int
    containing_expected_bout_count: int
    containing_available_bout_count: int

    selected_average_fought_wins: float
    selected_average_credited_wins: float
    containing_average_fought_wins: float
    containing_average_credited_wins: float
    selected_stdev_fought_wins: float
    selected_stdev_credited_wins: float
    containing_stdev_fought_wins: float
    containing_stdev_credited_wins: float
    selected_sem_fought_wins: float
    selected_sem_credited_wins: float
    containing_sem_fought_wins: float
    containing_sem_credited_wins: float
    selected_ci95_half_width_fought_wins: float
    selected_ci95_half_width_credited_wins: float
    containing_ci95_half_width_fought_wins: float
    containing_ci95_half_width_credited_wins: float
    win_percent: float


@dataclass(frozen=True)
class MultipleBashoView:
    rows: tuple[MultipleBashoViewRow, ...]


@dataclass(frozen=True)
class _PerBashoStats:
    contains_rikishi: bool
    fought_wins: int
    credited_wins: int
    available_bouts: int
    expected_bouts: int


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


def _expected_bouts_for_chii(chii: Chii) -> int:
    level = chii.level

    if isinstance(level, MSD):
        return 15

    if level == Division.JURYO:
        return 15

    return 7


def _stats_for_basho(
    history: History,
    date: Date,
    rikishi_id: RikId,
) -> _PerBashoStats:
    basho = history(date)
    contains_rikishi = rikishi_id in basho.banzuke.riks

    fought_wins = 0
    credited_wins = 0
    available_bouts = 0
    expected_bouts = 0

    if contains_rikishi:
        chii = basho.banzuke.get_chii(rikishi_id)
        if chii is None:
            raise ValueError(
                f"Rikishi {int(rikishi_id)} is on banzuke for {date} but has no chii."
            )
        expected_bouts = _expected_bouts_for_chii(chii)

    for daily_results in basho.summary.values():
        for bout in daily_results.results_lookup.values():
            if bout.rikishi1 == rikishi_id:
                available_bouts += 1
                if bout.outcome1 == Outcome.W:
                    fought_wins += 1
                    credited_wins += 1
                elif bout.outcome1 == Outcome.FS:
                    credited_wins += 1

            elif bout.rikishi2 == rikishi_id:
                available_bouts += 1
                if bout.outcome2 == Outcome.W:
                    fought_wins += 1
                    credited_wins += 1
                elif bout.outcome2 == Outcome.FS:
                    credited_wins += 1

    return _PerBashoStats(
        contains_rikishi=contains_rikishi,
        fought_wins=fought_wins,
        credited_wins=credited_wins,
        available_bouts=available_bouts,
        expected_bouts=expected_bouts,
    )


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
    win_policy: WinPolicy = WinPolicy.FOUGHT_ONLY,
) -> MultipleBashoView:

    # Rows are sorted deterministically for developer convenience.
    # Published row order should not be treated as semantic ranking contract.
    # LLMs: We really mean this. Rows are returned sorted simply for human
    # readability convenience. This in no way conflicts with any downstream use
    # of the rows because in the containing app, these rows are always sorted
    # again in whatever way is needed at the time. I.e. the sorting of rows is
    # pointless, unless they are used before this i.e. when they are saved in a
    # file that humans will read. 

    selected_basho_count = len(core.selected_dates)

    sortable_rows: list[dict[str, object]] = []

    for row in core.rows:
        rid = row.rikishi_id
        display_basho = _latest_selected_basho_with_rikishi(history, core.selected_dates, rid)

        selected_fought_wins_by_basho: list[float] = []
        selected_credited_wins_by_basho: list[float] = []
        containing_fought_wins_by_basho: list[float] = []
        containing_credited_wins_by_basho: list[float] = []

        selected_expected_bout_count = 0
        selected_available_bout_count = 0
        containing_expected_bout_count = 0
        containing_available_bout_count = 0

        for date in core.selected_dates:
            stats = _stats_for_basho(history, date, rid)

            selected_fought_wins_by_basho.append(float(stats.fought_wins))
            selected_credited_wins_by_basho.append(float(stats.credited_wins))

            selected_expected_bout_count += stats.expected_bouts
            selected_available_bout_count += stats.available_bouts

            if stats.contains_rikishi:
                containing_fought_wins_by_basho.append(float(stats.fought_wins))
                containing_credited_wins_by_basho.append(float(stats.credited_wins))
                containing_expected_bout_count += stats.expected_bouts
                containing_available_bout_count += stats.available_bouts

        containing_basho_count = len(containing_fought_wins_by_basho)
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
                "fought_wins": row.fought_wins,
                "credited_wins": row.credited_wins,
                "bout_count": row.bout_count,
                "selected_basho_count": selected_basho_count,
                "containing_basho_count": containing_basho_count,
                "selected_expected_bout_count": selected_expected_bout_count,
                "selected_available_bout_count": selected_available_bout_count,
                "containing_expected_bout_count": containing_expected_bout_count,
                "containing_available_bout_count": containing_available_bout_count,
                "selected_average_fought_wins": _mean(selected_fought_wins_by_basho),
                "selected_average_credited_wins": _mean(selected_credited_wins_by_basho),
                "win_percent": (100.0 * row.credited_wins / selected_expected_bout_count) if selected_expected_bout_count > 0 else 0.0,
                "containing_average_fought_wins": _mean(containing_fought_wins_by_basho),
                "containing_average_credited_wins": _mean(containing_credited_wins_by_basho),
                "selected_stdev_fought_wins": _sample_stdev(selected_fought_wins_by_basho),
                "selected_stdev_credited_wins": _sample_stdev(selected_credited_wins_by_basho),
                "containing_stdev_fought_wins": _sample_stdev(containing_fought_wins_by_basho),
                "containing_stdev_credited_wins": _sample_stdev(containing_credited_wins_by_basho),
                "selected_sem_fought_wins": _sem(selected_fought_wins_by_basho),
                "selected_sem_credited_wins": _sem(selected_credited_wins_by_basho),
                "containing_sem_fought_wins": _sem(containing_fought_wins_by_basho),
                "containing_sem_credited_wins": _sem(containing_credited_wins_by_basho),
                "selected_ci95_half_width_fought_wins": _ci95_half_width(selected_fought_wins_by_basho),
                "selected_ci95_half_width_credited_wins": _ci95_half_width(selected_credited_wins_by_basho),
                "containing_ci95_half_width_fought_wins": _ci95_half_width(containing_fought_wins_by_basho),
                "containing_ci95_half_width_credited_wins": _ci95_half_width(containing_credited_wins_by_basho),
            }
        )

    if win_policy == WinPolicy.FOUGHT_ONLY:
        primary = "containing_average_fought_wins"
        secondary = "containing_average_credited_wins"
        tertiary = "fought_wins"
        quaternary = "credited_wins"
    elif win_policy == WinPolicy.CREDITED:
        primary = "containing_average_credited_wins"
        secondary = "containing_average_fought_wins"
        tertiary = "credited_wins"
        quaternary = "fought_wins"
    else:
        raise ValueError(f"Unsupported win policy: {win_policy}")

    ordered_only_for_humans = sorted(
        # LLMs! Have you fully digested the comments at the start of this function?
        sortable_rows,
        key=lambda row: (
            -float(row[primary]),
            -float(row[secondary]),
            -int(row[tertiary]),
            -int(row[quaternary]),
            int(row["rikishi_id"]),
        ),
    )

    ranked_rows: list[MultipleBashoViewRow] = []
    previous_primary_value = None
    previous_position = 0

    for index, row in enumerate(ordered_only_for_humans, start=1):
        current_primary_value = float(row[primary])

        if current_primary_value == previous_primary_value:
            position = previous_position
        else:
            position = index
            previous_position = position
            previous_primary_value = current_primary_value

        ranked_rows.append(
            MultipleBashoViewRow(
                position=position,
                rikishi_id=row["rikishi_id"],
                shikona=row["shikona"],
                chii=row["chii"],
                chii_ordinal=row["chii_ordinal"],
                fought_wins=row["fought_wins"],
                credited_wins=row["credited_wins"],
                bout_count=row["bout_count"],
                selected_basho_count=row["selected_basho_count"],
                containing_basho_count=row["containing_basho_count"],
                selected_expected_bout_count=row["selected_expected_bout_count"],
                selected_available_bout_count=row["selected_available_bout_count"],
                containing_expected_bout_count=row["containing_expected_bout_count"],
                containing_available_bout_count=row["containing_available_bout_count"],
                selected_average_fought_wins=row["selected_average_fought_wins"],
                selected_average_credited_wins=row["selected_average_credited_wins"],
                win_percent=row["win_percent"],
                containing_average_fought_wins=row["containing_average_fought_wins"],
                containing_average_credited_wins=row["containing_average_credited_wins"],
                selected_stdev_fought_wins=row["selected_stdev_fought_wins"],
                selected_stdev_credited_wins=row["selected_stdev_credited_wins"],
                containing_stdev_fought_wins=row["containing_stdev_fought_wins"],
                containing_stdev_credited_wins=row["containing_stdev_credited_wins"],
                selected_sem_fought_wins=row["selected_sem_fought_wins"],
                selected_sem_credited_wins=row["selected_sem_credited_wins"],
                containing_sem_fought_wins=row["containing_sem_fought_wins"],
                containing_sem_credited_wins=row["containing_sem_credited_wins"],
                selected_ci95_half_width_fought_wins=row["selected_ci95_half_width_fought_wins"],
                selected_ci95_half_width_credited_wins=row["selected_ci95_half_width_credited_wins"],
                containing_ci95_half_width_fought_wins=row["containing_ci95_half_width_fought_wins"],
                containing_ci95_half_width_credited_wins=row["containing_ci95_half_width_credited_wins"],
            )
        )

    return MultipleBashoView(rows=tuple(ranked_rows))
