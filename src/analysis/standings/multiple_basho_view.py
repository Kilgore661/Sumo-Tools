"""
Derived results for multiple-basho standings.

Transforms multiple-basho core standings into a derived result set by:

- computing average-based metrics over the selected basho window
- determining, per rikishi, how many selected basho they were present for
- sourcing display identity from the most recent selected basho in which the
  rikishi was present, rather than from a single anchor basho

This module provides:

    History × anchor_date × MultipleBashoCore × WinsMode -> MultipleBashoView

The resulting object is still pre-presentation data. It is intended to be
written to CSV now and rendered more fully later.
"""

from dataclasses import dataclass

from src.analysis.standings.multiple_basho import MultipleBashoCore, WinsMode
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import Date, History


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


@dataclass(frozen=True)
class MultipleBashoView:
    rows: tuple[MultipleBashoViewRow, ...]


def _count_basho_present(
    history: History,
    selected_dates: tuple[Date, ...],
    rikishi_id: RikId,
) -> int:
    count = 0

    for date in selected_dates:
        basho = history(date)
        if rikishi_id in basho.banzuke.riks:
            count += 1

    return count


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
    anchor_date: Date,
    core: MultipleBashoCore,
    wins_mode: WinsMode,
) -> MultipleBashoView:
    _ = anchor_date
    selected_basho_count = len(core.selected_dates)

    sortable_rows: list[dict[str, object]] = []

    for row in core.rows:
        rid = row.rikishi_id
        display_basho = _latest_selected_basho_with_rikishi(history, core.selected_dates, rid)
        basho_present_count = _count_basho_present(history, core.selected_dates, rid)
        chii = display_basho.banzuke.get_chii(rid)

        if chii is None:
            raise ValueError(
                f"Rikishi {int(rid)} is on selected basho banzuke but has no chii in display basho."
            )

        window_average_real_wins = row.real_wins / selected_basho_count
        window_average_all_wins = row.all_wins / selected_basho_count

        if basho_present_count == 0:
            presence_average_real_wins = 0.0
            presence_average_all_wins = 0.0
        else:
            presence_average_real_wins = row.real_wins / basho_present_count
            presence_average_all_wins = row.all_wins / basho_present_count

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
                "window_average_real_wins": window_average_real_wins,
                "window_average_all_wins": window_average_all_wins,
                "presence_average_real_wins": presence_average_real_wins,
                "presence_average_all_wins": presence_average_all_wins,
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
            )
        )

    return MultipleBashoView(rows=tuple(view_rows))
