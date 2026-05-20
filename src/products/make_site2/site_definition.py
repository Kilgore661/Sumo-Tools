"""Canonical make_site2 site definition.

This copies the useful public-site declaration shape from make_site, but stops
before the old ViewSpec/rendering dispatch. Each page points at an ArtifactRef
that can later be resolved into the Publication UI Model.
"""

from __future__ import annotations

from .models import ArtifactRef, PageDefinition, PageRegistry, SiteDefinition
from .navigation import NAVIGATION


def artifact(id: str, kind: str, *, producer: str | None = None) -> ArtifactRef:
    return ArtifactRef(id=id, kind=kind, producer=producer)


PAGES = PageRegistry(
    pages={
        "banzuke_changes": PageDefinition(
            id="banzuke_changes",
            title="Banzuke Changes",
            summary="New-banzuke change report.",
            artifact=artifact(
                "banzuke_changes",
                "table_app",
                producer="banzuke_compare",
            ),
        ),
        "standings_by_wins": PageDefinition(
            id="standings_by_wins",
            title="Standings by Wins",
            summary="Rolling recent-performance standings by wins.",
            artifact=artifact(
                "standings_by_wins",
                "table_app",
                producer="standings",
            ),
        ),
        "finish_by_chii": PageDefinition(
            id="finish_by_chii",
            title="Finish by Chii",
            summary="Historical finishing outcomes grouped by chii.",
            artifact=artifact(
                "finish_by_chii",
                "chart",
                producer="misc.finish_by_chii",
            ),
        ),
        "banzuke_division_by_era": PageDefinition(
            id="banzuke_division_by_era",
            title="Banzuke Division by Era",
            summary="Historical banzuke division structure by era.",
            artifact=artifact("banzuke_division_by_era", "chart"),
        ),
        "makuuchi_rank_by_era": PageDefinition(
            id="makuuchi_rank_by_era",
            title="Makuuchi Rank by Era",
            summary="Historical Makuuchi rank structure by era.",
            artifact=artifact("makuuchi_rank_by_era", "chart"),
        ),
        "division_stability": PageDefinition(
            id="division_stability",
            title="Division Stability",
            summary="Historical continuity within divisions.",
            artifact=artifact("division_stability", "chart"),
        ),
        "first_chii_appearance": PageDefinition(
            id="first_chii_appearance",
            title="First Chii Appearance",
            summary="Earliest observed bout appearance for each chii.",
            artifact=artifact("first_chii_appearance", "chart"),
        ),
        "win_probability_by_standing": PageDefinition(
            id="win_probability_by_standing",
            title="Win Probability by Standing",
            summary="Probability of winning as a function of standing.",
            artifact=artifact("win_probability_by_standing", "chart"),
        ),
        "basho_results_browser": PageDefinition(
            id="basho_results_browser",
            title="Basho Results",
            summary="Historical and current basho results by division.",
            artifact=artifact(
                "basho_results_browser",
                "table",
                producer="sumo_history.basho_results",
            ),
        ),
    }
)


SITE = SiteDefinition(
    id="sumo_lab",
    title="Gaspode-san's\nSumo Lab",
    navigation=NAVIGATION,
    pages=PAGES,
)
