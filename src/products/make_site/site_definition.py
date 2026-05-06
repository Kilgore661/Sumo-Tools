"""Canonical provisional public-site definition."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from .classes import (
    AssetRef,
    CustomView,
    DataRef,
    NavigationTree,
    OptionKind,
    OptionSpec,
    OptionValue,
    OptionsModel,
    Page,
    PageRegistry,
    Site,
    SiteBuildConfig,
    StandaloneHtmlView,
    TableAppView,
    ViewRef,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = REPO_ROOT / "files" / "output"
ANALYSIS_ROOT = REPO_ROOT / "src" / "analysis"


def asset(
    id: str,
    source_path: Path,
    output_path: str,
    media_type: str,
) -> AssetRef:
    return AssetRef(
        id=id,
        source_path=source_path,
        output_path=PurePosixPath(output_path),
        media_type=media_type,
    )


def data(
    id: str,
    source_path: Path,
    output_path: str,
    media_type: str,
) -> DataRef:
    return DataRef(
        id=id,
        source_path=source_path,
        output_path=PurePosixPath(output_path),
        media_type=media_type,
    )


def view(
    id: str,
    source_path: Path,
    media_type: str = "text/html",
) -> ViewRef:
    return ViewRef(
        id=id,
        source_path=source_path,
        media_type=media_type,
    )


GLOBAL_ASSETS = (
    asset(
        id="site_wide_css",
        source_path=ANALYSIS_ROOT / "common" / "files" / "site-wide.css",
        output_path="common/files/site-wide.css",
        media_type="text/css",
    ),
    asset(
        id="tool_layout_css",
        source_path=ANALYSIS_ROOT / "common" / "files" / "tool-layout.css",
        output_path="common/files/tool-layout.css",
        media_type="text/css",
    ),
)


STANDINGS_ASSETS = (
    asset(
        id="standings_css",
        source_path=ANALYSIS_ROOT / "standings" / "files" / "standings.css",
        output_path="current-sumo/standings-by-wins/standings.css",
        media_type="text/css",
    ),
    asset(
        id="standings_js",
        source_path=ANALYSIS_ROOT / "standings" / "files" / "standings.js.txt",
        output_path="current-sumo/standings-by-wins/standings.js",
        media_type="application/javascript",
    ),
)


BANZUKE_CHANGES_ASSETS = (
    asset(
        id="banzuke_changes_css",
        source_path=ANALYSIS_ROOT
        / "banzuke_compare"
        / "files"
        / "banzuke_change_report.css",
        output_path="current-sumo/banzuke-changes/banzuke_change_report.css",
        media_type="text/css",
    ),
    asset(
        id="banzuke_changes_js",
        source_path=ANALYSIS_ROOT
        / "banzuke_compare"
        / "files"
        / "banzuke_change_report.js.txt",
        output_path="current-sumo/banzuke-changes/banzuke_change_report.js",
        media_type="application/javascript",
    ),
)


WIN_PROBABILITY_BY_STANDING_DATA = (
    data(
        id="observed_standing_win_probability",
        source_path=OUTPUT_ROOT
        / "probability"
        / "matchups"
        / "observed_sideless_trace_points.csv",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/observed.csv"
        ),
        media_type="text/csv",
    ),
    data(
        id="equelo_standing_win_probability",
        source_path=OUTPUT_ROOT
        / "probability"
        / "matchups"
        / "equelo_sideless_trace_points.csv",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/equelo.csv"
        ),
        media_type="text/csv",
    ),
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


NAVIGATION = NavigationTree(
    id="root",
    label="Root",
    slug="",
    children=(
        NavigationTree(
            id="current_sumo",
            label="Current Sumo",
            slug="current-sumo",
            children=(
                NavigationTree(
                    id="banzuke_changes",
                    label="Banzuke Changes",
                    slug="banzuke-changes",
                    page_id="banzuke_changes",
                ),
                NavigationTree(
                    id="standings_by_wins",
                    label="Standings by Wins",
                    slug="standings-by-wins",
                    page_id="standings_by_wins",
                ),
            ),
        ),
        NavigationTree(
            id="banzuke_rank",
            label="Banzuke & Rank",
            slug="banzuke-rank",
            children=(
                NavigationTree(
                    id="banzuke_structure_over_time",
                    label="Banzuke Structure Over Time",
                    slug="banzuke-structure-over-time",
                    children=(
                        NavigationTree(
                            id="banzuke_division_by_era",
                            label="Banzuke Division by Era",
                            slug="banzuke-division-by-era",
                            page_id="banzuke_division_by_era",
                        ),
                    ),
                ),
                NavigationTree(
                    id="makuuchi_structure",
                    label="Makuuchi Structure",
                    slug="makuuchi-structure",
                    children=(
                        NavigationTree(
                            id="makuuchi_rank_by_era",
                            label="Makuuchi Rank by Era",
                            slug="makuuchi-rank-by-era",
                            page_id="makuuchi_rank_by_era",
                        ),
                    ),
                ),
                NavigationTree(
                    id="division_movement",
                    label="Division Movement",
                    slug="division-movement",
                    children=(
                        NavigationTree(
                            id="division_stability",
                            label="Division Stability",
                            slug="division-stability",
                            page_id="division_stability",
                        ),
                    ),
                ),
            ),
        ),
        NavigationTree(
            id="performance",
            label="Performance",
            slug="performance",
            children=(
                NavigationTree(
                    id="rank_outcomes",
                    label="Rank Outcomes",
                    slug="rank-outcomes",
                    children=(
                        NavigationTree(
                            id="finish_by_chii",
                            label="Finish by Chii",
                            slug="finish-by-chii",
                            page_id="finish_by_chii",
                        ),
                    ),
                ),
            ),
        ),
        NavigationTree(
            id="ratings_models",
            label="Ratings & Models",
            slug="ratings-models",
            children=(
                NavigationTree(
                    id="observed_vs_modelled",
                    label="Observed vs Modelled",
                    slug="observed-vs-modelled",
                    children=(
                        NavigationTree(
                            id="win_probability_by_standing",
                            label="Win Probability by Standing",
                            slug="win-probability-by-standing",
                            page_id="win_probability_by_standing",
                        ),
                    ),
                ),
            ),
        ),
    ),
)


SITE = Site(
    id="sumo_lab",
    title="Gaspode-san's Sumo Lab",
    navigation=NAVIGATION,
    pages=PAGES,
    global_assets=GLOBAL_ASSETS,
)


BUILD_CONFIG = SiteBuildConfig(
    base_route="/site/",
    output_root=OUTPUT_ROOT / "site",
)
