"""Page registry and site factory helpers."""

from __future__ import annotations

from typing import Mapping

from .classes import (
    CustomView,
    NavigationTree,
    OptionKind,
    OptionSpec,
    OptionValue,
    OptionsModel,
    Page,
    PageRegistry,
    Site,
    StandaloneHtmlView,
    TableAppView,
)
from .site_assets import BANZUKE_CHANGES_ASSETS, GLOBAL_ASSETS, STANDINGS_ASSETS
from .site_config import ANALYSIS_ROOT, OUTPUT_ROOT
from .site_data_refs import (
    BANZUKE_CHANGES_DATA,
    STANDINGS_DATA,
    WIN_PROBABILITY_BY_STANDING_DATA,
    career_length_data_refs,
    rank_at_retirement_data_refs,
    typical_equelo_values_data_refs,
)
from .site_navigation import NAVIGATION
from .site_refs import view
from src.analysis.equelo.fixed_v1.v5_landmarks import V5LandmarkOutputs
from src.analysis.sumo_history.career_lifecycle.career_length import CareerLengthOutputs
from src.analysis.sumo_history.career_lifecycle.rank_at_retirement import (
    RankAtRetirementOutputs,
)


WIN_PROBABILITY_BY_STANDING_OPTIONS = OptionsModel(
    options=(
        OptionSpec(
            id="source",
            label="Source",
            kind=OptionKind.ENUM,
            default="observed",
            values=(
                OptionValue(value="observed", label="Observed"),
                OptionValue(value="equelo", label="Equelo"),
                OptionValue(value="combined", label="Combined"),
            ),
        ),
    )
)


PAGES = PageRegistry(
    pages={
        "banzuke_changes": Page(
            id="banzuke_changes",
            title="Banzuke Changes",
            summary="New-banzuke change report.",
            view=TableAppView(
                entrypoint=view(
                    id="banzuke_changes_index",
                    source_path=ANALYSIS_ROOT / "banzuke_compare" / "files" / "index.html",
                )
            ),
            assets=BANZUKE_CHANGES_ASSETS,
            data=BANZUKE_CHANGES_DATA,
        ),
        "standings_by_wins": Page(
            id="standings_by_wins",
            title="Standings by Wins",
            summary="Rolling recent-performance standings by wins.",
            view=TableAppView(
                entrypoint=view(
                    id="standings_by_wins_index",
                    source_path=ANALYSIS_ROOT / "standings" / "files" / "index.html",
                )
            ),
            assets=STANDINGS_ASSETS,
            data=STANDINGS_DATA,
        ),
        "finish_by_chii": Page(
            id="finish_by_chii",
            title="Finish by Chii",
            summary="Historical finishing outcomes grouped by chii.",
            view=StandaloneHtmlView(
                source=view(
                    id="finish_by_chii_html",
                    source_path=OUTPUT_ROOT / "misc" / "finish_by_chii_1958_2026.html",
                )
            ),
        ),
        "banzuke_division_by_era": Page(
            id="banzuke_division_by_era",
            title="Banzuke Division by Era",
            summary="Historical banzuke division structure by era.",
            view=StandaloneHtmlView(
                source=view(
                    id="banzuke_division_by_era_html",
                    source_path=OUTPUT_ROOT / "banzuke_division_era_chart.html",
                )
            ),
        ),
        "makuuchi_rank_by_era": Page(
            id="makuuchi_rank_by_era",
            title="Makuuchi Rank by Era",
            summary="Historical Makuuchi rank structure by era.",
            view=StandaloneHtmlView(
                source=view(
                    id="makuuchi_rank_by_era_html",
                    source_path=OUTPUT_ROOT / "rank_era_chart.html",
                )
            ),
        ),
        "division_stability": Page(
            id="division_stability",
            title="Division Stability",
            summary="Historical continuity within divisions.",
            view=StandaloneHtmlView(
                source=view(
                    id="division_stability_html",
                    source_path=OUTPUT_ROOT
                    / "persistence"
                    / "division_persistence (1958-2026, num_basho=10).html",
                )
            ),
        ),
        "win_probability_by_standing": Page(
            id="win_probability_by_standing",
            title="Win Probability by Standing",
            summary="Probability of winning as a function of standing.",
            options=WIN_PROBABILITY_BY_STANDING_OPTIONS,
            view=CustomView(kind="standing_win_probability"),
            data=WIN_PROBABILITY_BY_STANDING_DATA,
        ),
    }
)


SITE = Site(
    id="sumo_lab",
    title="Gaspode-san's Sumo Lab",
    navigation=NAVIGATION,
    pages=PAGES,
    global_assets=GLOBAL_ASSETS,
)


def site_with_career_length(outputs: CareerLengthOutputs) -> Site:
    pages = dict(PAGES.pages)
    pages["career_length"] = Page(
        id="career_length",
        title="Career Length",
        summary="Observed rikishi career lengths from banzuke appearances.",
        view=CustomView(kind="career_length"),
        data=career_length_data_refs(outputs),
    )
    return Site(
        id=SITE.id,
        title=SITE.title,
        navigation=_with_page_id(
            NAVIGATION,
            target_id="history_career_length",
            page_id="career_length",
        ),
        pages=PageRegistry(pages=pages),
        global_assets=SITE.global_assets,
    )


def site_with_career_lifecycle(
    career_outputs: CareerLengthOutputs,
    retirement_outputs: RankAtRetirementOutputs,
    typical_equelo_outputs: V5LandmarkOutputs,
) -> Site:
    pages = dict(PAGES.pages)
    pages["career_length"] = Page(
        id="career_length",
        title="Career Length",
        summary="Observed rikishi career lengths from banzuke appearances.",
        view=CustomView(kind="career_length"),
        data=career_length_data_refs(career_outputs),
    )
    pages["rank_at_retirement"] = Page(
        id="rank_at_retirement",
        title="Rank at Retirement",
        summary="Final observed rank group for retired rikishi.",
        view=CustomView(kind="rank_at_retirement"),
        data=rank_at_retirement_data_refs(retirement_outputs),
    )
    pages["typical_equelo_values"] = Page(
        id="typical_equelo_values",
        title="Typical Equelo Ratings",
        summary="Approximate rating landmarks for familiar rank labels.",
        view=CustomView(kind="typical_equelo_values"),
        data=typical_equelo_values_data_refs(typical_equelo_outputs),
    )
    pages["v5_landmark_policy"] = Page(
        id="v5_landmark_policy",
        title="V5 Landmark Policy",
        summary="Placeholder for the v5 rating landmark policy.",
        view=CustomView(kind="tbd_page"),
    )
    pages["lower_rank_rating_stability"] = Page(
        id="lower_rank_rating_stability",
        title="Lower-Rank Rating Stability",
        summary="Placeholder for lower-rank Equelo stability notes.",
        view=CustomView(kind="tbd_page"),
    )
    return Site(
        id=SITE.id,
        title=SITE.title,
        navigation=_with_page_ids(
            NAVIGATION,
            {
                "typical_equelo_values": "typical_equelo_values",
                "v5_landmark_policy": "v5_landmark_policy",
                "lower_rank_rating_stability": "lower_rank_rating_stability",
                "history_career_length": "career_length",
                "rank_at_retirement": "rank_at_retirement",
            },
        ),
        pages=PageRegistry(pages=pages),
        global_assets=SITE.global_assets,
    )


def _with_page_id(
    node: NavigationTree,
    *,
    target_id: str,
    page_id: str,
) -> NavigationTree:
    return NavigationTree(
        id=node.id,
        label=node.label,
        slug=node.slug,
        children=tuple(
            _with_page_id(child, target_id=target_id, page_id=page_id)
            for child in node.children
        ),
        page_id=page_id if node.id == target_id else node.page_id,
    )


def _with_page_ids(
    node: NavigationTree,
    page_ids: Mapping[str, str],
) -> NavigationTree:
    return NavigationTree(
        id=node.id,
        label=node.label,
        slug=node.slug,
        children=tuple(_with_page_ids(child, page_ids) for child in node.children),
        page_id=page_ids.get(node.id, node.page_id),
    )
