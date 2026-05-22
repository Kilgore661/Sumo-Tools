"""Canonical make_site2 site definition.

This copies the useful public-site declaration shape from make_site, but stops
before the old ViewSpec/rendering dispatch. Each page points at an ArtifactRef
that can later be resolved into the Publication UI Model.
"""

from __future__ import annotations

from .models import ArtifactRef, PageDefinition, PageRegistry, PageStatus, SiteDefinition
from .navigation import NAVIGATION


def artifact(id: str, kind: str, *, producer: str | None = None) -> ArtifactRef:
    return ArtifactRef(id=id, kind=kind, producer=producer)


PAGES = PageRegistry(
    pages={
        "banzuke_changes": PageDefinition(
            id="banzuke_changes",
            title="Banzuke Changes",
            summary="New-banzuke change report.",
            status=PageStatus.PROMOTED,
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
            status=PageStatus.PROMOTED,
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
            status=PageStatus.PROMOTED,
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
            status=PageStatus.PROMOTED,
            artifact=artifact("banzuke_division_by_era", "chart"),
        ),
        "makuuchi_rank_by_era": PageDefinition(
            id="makuuchi_rank_by_era",
            title="Makuuchi Rank by Era",
            summary="Historical Makuuchi rank structure by era.",
            status=PageStatus.PROMOTED,
            artifact=artifact("makuuchi_rank_by_era", "chart"),
        ),
        "division_stability": PageDefinition(
            id="division_stability",
            title="Division Stability",
            summary="Historical continuity within divisions.",
            status=PageStatus.PROMOTED,
            artifact=artifact("division_stability", "chart"),
        ),
        "first_chii_appearance": PageDefinition(
            id="first_chii_appearance",
            title="First Chii Appearance",
            summary="Earliest observed bout appearance at <a href=\"sumodb.de\">SumoDB</a>for each chii.",
            status=PageStatus.PROMOTED,
            artifact=artifact("first_chii_appearance", "chart"),
        ),
        "win_probability_by_standing": PageDefinition(
            id="win_probability_by_standing",
            title="Win Probability by Standing",
            summary="Probability of winning as a function of standing.",
            status=PageStatus.PROMOTED,
            artifact=artifact(
                "win_probability_by_standing",
                "chart",
                producer="probability.matchups",
            ),
        ),
        "basho_results_browser": PageDefinition(
            id="basho_results_browser",
            title="Basho Results",
            summary="Historical and current basho results by division.",
            status=PageStatus.PROMOTED,
            artifact=artifact(
                "basho_results_browser",
                "table",
                producer="sumo_history.basho_results",
            ),
        ),
        "rank_at_retirement": PageDefinition(
            id="rank_at_retirement",
            title="Rank at Retirement",
            summary="Final observed rank group for retired rikishi.",
            status=PageStatus.PROMOTED,
            artifact=artifact(
                "rank_at_retirement",
                "chart",
                producer="sumo_history.career_lifecycle.rank_at_retirement",
            ),
        ),
        "career_length": PageDefinition(
            id="career_length",
            title="Career Length",
            summary="Observed rikishi career lengths from banzuke appearances.",
            status=PageStatus.PROMOTED,
            artifact=artifact(
                "career_length",
                "chart",
                producer="sumo_history.career_lifecycle.career_length",
            ),
        ),
        "typical_equelo_values": PageDefinition(
            id="typical_equelo_values",
            title="Typical Equelo Ratings",
            summary="Approximate rating landmarks for familiar rank labels.",
            status=PageStatus.PROMOTED,
            artifact=artifact(
                "typical_equelo_values",
                "sectioned_table",
                producer="equelo.fixed_v2.v5_landmarks",
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
