"""Canonical provisional public-site definition."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Mapping

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
from src.analysis.sumo_history.career_lifecycle.career_length import (
    CareerLengthOutputs,
)
from src.analysis.sumo_history.career_lifecycle.rank_at_retirement import (
    RankAtRetirementOutputs,
)
from src.analysis.equelo.fixed_v1.v5_landmarks import (
    V5LandmarkOutputs,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = REPO_ROOT / "files" / "output"
ANALYSIS_ROOT = REPO_ROOT / "src" / "analysis"
PRODUCT_ROOT = REPO_ROOT / "src" / "products" / "make_site"
BCR_OUTPUT_ROOT = OUTPUT_ROOT / "bcr"
STANDINGS_PUBLISHER_DATA = OUTPUT_ROOT / "standings" / "publisher" / "latest_data"
WIN_PROBABILITY_SITE_BUNDLE = (
    OUTPUT_ROOT / "probability" / "matchups" / "site" / "win_probability_by_standing"
)
CAREER_LENGTH_SITE_OUTPUT_DIR = "sumo-history/career-lifecycle/career-length/data"
RANK_AT_RETIREMENT_SITE_OUTPUT_DIR = (
    "sumo-history/career-lifecycle/rank-at-retirement/data"
)
TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR = (
    "ratings-models/rating-and-rank/typical-equelo-values/data"
)


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


def data_media_type(source_path: Path) -> str:
    return {
        ".csv": "text/csv",
        ".json": "application/json",
    }[source_path.suffix]


def published_data_refs(
    source_dir: Path,
    output_dir: str,
    id_prefix: str,
) -> tuple[DataRef, ...]:
    return tuple(
        data(
            id=f"{id_prefix}_{source_path.stem}",
            source_path=source_path,
            output_path=str(PurePosixPath(output_dir) / source_path.name),
            media_type=data_media_type(source_path),
        )
        for source_path in sorted(source_dir.iterdir())
        if source_path.suffix in {".csv", ".json"}
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
        id="site_shell_css",
        source_path=PRODUCT_ROOT / "files" / "site-shell.css",
        output_path="site-shell.css",
        media_type="text/css",
    ),
    asset(
        id="site_shell_js",
        source_path=PRODUCT_ROOT / "files" / "site-shell.js",
        output_path="site-shell.js",
        media_type="application/javascript",
    ),
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
        source_path=ANALYSIS_ROOT / "standings" / "files" / "standings.js",
        output_path="current-sumo/standings-by-wins/standings.js",
        media_type="application/javascript",
    ),
)


STANDINGS_DATA = published_data_refs(
    source_dir=STANDINGS_PUBLISHER_DATA,
    output_dir="current-sumo/standings-by-wins/data",
    id_prefix="standings",
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
        / "banzuke_change_report.js",
        output_path="current-sumo/banzuke-changes/banzuke_change_report.js",
        media_type="application/javascript",
    ),
)


BANZUKE_CHANGES_DATA = (
    data(
        id="banzuke_changes_site_config",
        source_path=BCR_OUTPUT_ROOT / "site_config.json",
        output_path="current-sumo/banzuke-changes/site_config.json",
        media_type="application/json",
    ),
    data(
        id="banzuke_change_report",
        source_path=BCR_OUTPUT_ROOT / "data" / "banzuke_change_report.csv",
        output_path="current-sumo/banzuke-changes/data/banzuke_change_report.csv",
        media_type="text/csv",
    ),
)


WIN_PROBABILITY_BY_STANDING_DATA = (
    data(
        id="win_probability_by_standing_page_config",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "page.json",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/page.json"
        ),
        media_type="application/json",
    ),
    data(
        id="observed_standing_win_probability",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "observed_trace_points.csv",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/observed_trace_points.csv"
        ),
        media_type="text/csv",
    ),
    data(
        id="equelo_standing_win_probability",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "equelo_trace_points.csv",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/equelo_trace_points.csv"
        ),
        media_type="text/csv",
    ),
    data(
        id="win_probability_by_standing_metadata",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "metadata.json",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/metadata.json"
        ),
        media_type="application/json",
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


def career_length_data_refs(outputs: CareerLengthOutputs) -> tuple[DataRef, ...]:
    return (
        data(
            id="career_length_page_config",
            source_path=outputs.page_json,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/page.json",
            media_type="application/json",
        ),
        data(
            id="career_length_distribution",
            source_path=outputs.distribution_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/distribution.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_pmf",
            source_path=outputs.pmf_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/pmf.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_cdf",
            source_path=outputs.cdf_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/cdf.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_survival",
            source_path=outputs.survival_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/survival.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_longest",
            source_path=outputs.longest_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/longest.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_metadata",
            source_path=outputs.metadata_json,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/metadata.json",
            media_type="application/json",
        ),
    )


def rank_at_retirement_data_refs(
    outputs: RankAtRetirementOutputs,
) -> tuple[DataRef, ...]:
    return (
        data(
            id="rank_at_retirement_page_config",
            source_path=outputs.page_json,
            output_path=f"{RANK_AT_RETIREMENT_SITE_OUTPUT_DIR}/page.json",
            media_type="application/json",
        ),
        data(
            id="rank_at_retirement_distribution",
            source_path=outputs.distribution_csv,
            output_path=f"{RANK_AT_RETIREMENT_SITE_OUTPUT_DIR}/distribution.csv",
            media_type="text/csv",
        ),
        data(
            id="rank_at_retirement_metadata",
            source_path=outputs.metadata_json,
            output_path=f"{RANK_AT_RETIREMENT_SITE_OUTPUT_DIR}/metadata.json",
            media_type="application/json",
        ),
    )


def typical_equelo_values_data_refs(
    outputs: V5LandmarkOutputs,
) -> tuple[DataRef, ...]:
    return (
        data(
            id="typical_equelo_values_page_config",
            source_path=outputs.page_json,
            output_path=f"{TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR}/page.json",
            media_type="application/json",
        ),
        data(
            id="typical_equelo_values_csv",
            source_path=outputs.site_landmarks_csv,
            output_path=(
                f"{TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR}/"
                "typical_equelo_values.csv"
            ),
            media_type="text/csv",
        ),
        data(
            id="typical_equelo_values_metadata",
            source_path=outputs.site_metadata_json,
            output_path=f"{TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR}/metadata.json",
            media_type="application/json",
        ),
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


def nav(
    id: str,
    label: str,
    slug: str,
    *children: NavigationTree,
    page_id: str | None = None,
) -> NavigationTree:
    return NavigationTree(
        id=id,
        label=label,
        slug=slug,
        children=children,
        page_id=page_id,
    )


NAVIGATION = NavigationTree(
    id="root",
    label="Root",
    slug="",
    children=(
        nav(
            "home",
            "Home",
            "home",
            nav(
                "site_orientation",
                "What this site is",
                "what-this-site-is",
            ),
            nav(
                "featured_latest",
                "Featured / latest exhibits",
                "featured-latest-exhibits",
            ),
            nav(
                "site_notes_caveats",
                "Notes and caveats",
                "notes-and-caveats",
            ),
        ),
        nav(
            "current_sumo",
            "Current Sumo",
            "current-sumo",
            nav(
                "banzuke_changes",
                "Banzuke Changes",
                "banzuke-changes",
                page_id="banzuke_changes",
            ),
            nav(
                "standings_by_wins",
                "Standings by Wins",
                "standings-by-wins",
                page_id="standings_by_wins",
            ),
            nav("current_ratings", "Current Ratings", "current-ratings"),
            nav(
                "current_leaders",
                "Current Leaders",
                "current-leaders",
                nav("max_average_wins", "Max average wins", "max-average-wins"),
                nav("max_rating_probability", "Max rating probability", "max-rating-probability"),
                nav("rating_movers", "Rating movers", "rating-movers"),
                nav("banzuke_movers", "Banzuke movers", "banzuke-movers"),
            ),
        ),
        nav(
            "rikishi",
            "Rikishi",
            "rikishi",
            nav("rikishi_lookup", "Rikishi Lookup", "rikishi-lookup"),
            nav(
                "rikishi_profile",
                "Rikishi Profile",
                "rikishi-profile",
                nav("profile_summary", "Summary", "summary"),
                nav("career_rank_chii_timeline", "Career rank/chii timeline", "career-rank-chii-timeline"),
                nav("rating_timeline", "Rating timeline", "rating-timeline"),
                nav("combined_chii_rating_view", "Combined chii + rating view", "combined-chii-rating-view"),
                nav("daily_bout_rating_movement", "Daily / bout-level rating movement", "daily-bout-rating-movement"),
            ),
            nav("career_comparisons", "Career Comparisons", "career-comparisons"),
        ),
        nav(
            "banzuke_rank",
            "Banzuke & Rank",
            "banzuke-rank",
            nav("chii_notes", "Chii Notes", "chii-notes"),
            nav("current_banzuke", "Current Banzuke", "current-banzuke"),
            nav(
                "banzuke_structure_over_time",
                "Banzuke Structure Over Time",
                "banzuke-structure-over-time",
                nav(
                    "banzuke_division_by_era",
                    "Banzuke Division by Era",
                    "banzuke-division-by-era",
                    page_id="banzuke_division_by_era",
                ),
                nav(
                    "makuuchi_rank_by_era",
                    "Makuuchi Rank by Era",
                    "makuuchi-rank-by-era",
                    page_id="makuuchi_rank_by_era",
                ),
            ),
            nav(
                "division_stability",
                "Division Stability",
                "division-stability",
                page_id="division_stability",
            ),
            nav(
                "rank_history",
                "Rank History",
                "rank-history",
                nav("first_chii_appearance", "First chii appearance", "first-chii-appearance"),
                nav("rare_historical_rank_slots", "Rare / historical rank slots", "rare-historical-rank-slots"),
            ),
            nav("retirement_rank", "Retirement Rank", "retirement-rank"),
        ),
        nav(
            "performance",
            "Performance",
            "performance",
            nav(
                "finish_by_chii",
                "Finish by Chii",
                "finish-by-chii",
                page_id="finish_by_chii",
            ),
            nav("win_probability_by_standing_observed", "Win Probability by Standing", "win-probability-by-standing"),
            nav(
                "career_outcomes",
                "Career Outcomes",
                "career-outcomes",
                nav("career_length", "Career length", "career-length"),
                nav("career_length_probability", "Career length probability", "career-length-probability"),
                nav(
                    "cumulative_career_length_probability",
                    "Cumulative career length probability",
                    "cumulative-career-length-probability",
                ),
            ),
            nav(
                "rank_outcomes",
                "Rank Outcomes",
                "rank-outcomes",
                nav("average_finish_by_chii", "Average finish by chii", "average-finish-by-chii"),
                nav("threshold_top_record_views", "Threshold / top-record views", "threshold-top-record-views"),
            ),
        ),
        nav(
            "ratings_models",
            "Ratings & Models",
            "ratings-models",
            nav(
                "rating_overview",
                "Rating Overview",
                "rating-overview",
                nav("why_ratings", "Why ratings?", "why-ratings"),
                nav("elo_equelo_explanation", "Elo / Equelo explanation", "elo-equelo-explanation"),
                nav("assumptions_caveats", "Assumptions and caveats", "assumptions-caveats"),
            ),
            nav(
                "rating_and_rank",
                "Rating and Rank",
                "rating-and-rank",
                nav("typical_equelo_values", "Typical Equelo Ratings", "typical-equelo-values"),
                nav("rating_vs_chii", "Rating vs chii", "rating-vs-chii"),
                nav("mean_rating_by_chii", "Mean rating by chii", "mean-rating-by-chii"),
                nav("expected_wins_by_chii", "Expected wins by chii", "expected-wins-by-chii"),
                nav(
                    "probability_values_by_chii",
                    "Probability-derived values by chii",
                    "probability-values-by-chii",
                ),
            ),
            nav(
                "observed_vs_modelled",
                "Observed vs Modelled",
                "observed-vs-modelled",
                nav(
                    "win_probability_by_standing",
                    "Win Probability by Standing",
                    "win-probability-by-standing",
                    page_id="win_probability_by_standing",
                ),
                nav("model_consistency_checks", "Model consistency checks", "model-consistency-checks"),
                nav("residual_difference_views", "Residual / difference views, later", "residual-difference-views"),
            ),
            nav(
                "model_diagnostics",
                "Model Diagnostics",
                "model-diagnostics",
                nav("rating_distribution", "Rating distribution", "rating-distribution"),
                nav("inflation_drift_by_chii", "Inflation / drift by chii", "inflation-drift-by-chii"),
                nav("estimators", "Estimators", "estimators"),
                nav("mean_rating_vs_banzuke_size", "Mean rating vs banzuke size", "mean-rating-vs-banzuke-size"),
                nav("calibration_reports", "Calibration reports", "calibration-reports"),
            ),
            nav(
                "equelo_methodology",
                "Equelo Methodology",
                "equelo-methodology",
                nav("v5_landmark_policy", "V5 Landmark Policy", "v5-landmark-policy"),
                nav(
                    "lower_rank_rating_stability",
                    "Lower-Rank Rating Stability",
                    "lower-rank-rating-stability",
                ),
                nav("initial_rating_curve", "Initial rating curve / fixed-v1 entrant ratings", "initial-rating-curve"),
                nav("monotonicity_story", "Monotonicity story", "monotonicity-story"),
                nav("experiment_research_narrative", "Experiment / research narrative", "experiment-research-narrative"),
            ),
        ),
        nav(
            "sumo_history",
            "Sumo History",
            "sumo-history",
            nav(
                "population_history",
                "Population History",
                "population-history",
                nav("division_sizes_over_time", "Division sizes over time", "division-sizes-over-time"),
                nav("banzuke_population", "Banzuke population", "banzuke-population"),
            ),
            nav(
                "career_lifecycle",
                "Career Lifecycle",
                "career-lifecycle",
                nav("history_career_length", "Career length", "career-length"),
                nav("rank_at_retirement", "Rank at retirement", "rank-at-retirement"),
            ),
            nav(
                "historical_exhibits",
                "Historical Exhibits",
                "historical-exhibits",
                nav("historical_banzuke_division_by_era", "Banzuke division by era", "banzuke-division-by-era"),
                nav("historical_makuuchi_rank_by_era", "Makuuchi rank by era", "makuuchi-rank-by-era"),
            ),
        ),
        nav(
            "data_notes",
            "Data & Notes",
            "data-notes",
            nav("data_sources", "Data Sources", "data-sources"),
            nav("glossary", "Glossary", "glossary"),
            nav("chii_banzuke_quirks", "Chii / banzuke quirks", "chii-banzuke-quirks"),
            nav("known_limitations", "Known Limitations", "known-limitations"),
            nav("method_notes", "Method Notes", "method-notes"),
        ),
        nav(
            "lab_archive",
            "Lab / Archive",
            "lab-archive",
            nav("research_charts_not_promoted", "Research charts not yet promoted", "research-charts-not-promoted"),
            nav("legacy_v9_pending", "Legacy v9 exhibits pending reimplementation", "legacy-v9-pending"),
            nav("deprecated_superseded", "Deprecated / superseded outputs", "deprecated-superseded"),
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


BUILD_CONFIG = SiteBuildConfig(
    base_route="/sumo-tools/",
    output_root=OUTPUT_ROOT / "make_site",
)
