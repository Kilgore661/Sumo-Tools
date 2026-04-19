"""
Presentation-oriented enrichment for single-basho standings.

Transforms core standings into a date-correct standings view by attaching
banzuke-derived display data for the given basho, including shikona and
both forms of chii:

- string form for human-readable output
- ordinal form for sorting and logic

This module provides:

    BashoState × SingleBashoStandings -> SingleBashoStandingsView
"""

from dataclasses import dataclass

from src.analysis.standings.single_basho import (
    SingleBashoStandings,
)
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.Chii import Chii


@dataclass(frozen=True)
class SingleBashoStandingsViewRow:
    position: int
    rikishi_id: RikId
    shikona: Shikona
    chii: str
    chii_ordinal: int
    real_wins: int
    all_wins: int
    bout_count: int


@dataclass(frozen=True)
class SingleBashoStandingsView:
    rows: tuple[SingleBashoStandingsViewRow, ...]


def get_single_basho_standings_view(
    basho: BashoState,
    standings: SingleBashoStandings,
) -> SingleBashoStandingsView:
    view_rows: list[SingleBashoStandingsViewRow] = []

    for row in standings.rows:
        rid = row.rikishi_id
        chii: Chii = basho.banzuke.get_chii(rid)

        view_rows.append(
            SingleBashoStandingsViewRow(
                position=row.position,
                rikishi_id=rid,
                shikona=basho.banzuke.get_shik(rid),
                chii=str(chii),
                chii_ordinal=chii.ordinal(),
                real_wins=row.real_wins,
                all_wins=row.all_wins,
                bout_count=row.bout_count,
            )
        )

    return SingleBashoStandingsView(rows=tuple(view_rows))
