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
PRODUCT_ROOT = REPO_ROOT / "src" / "products" / "make_site"


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
                "welcome_site_orientation",
                "Welcome / site orientation",
                "welcome-site-orientation",
                nav("what_this_site_is", "What this site is", "what-this-site-is"),
                nav("latest_updates", "What is new / latest updates", "latest-updates"),
                nav("featured_current_pages", "Featured current pages", "featured-current-pages"),
                nav("interpretation_warnings", "Known caveats and interpretation warnings", "interpretation-warnings"),
            ),
            nav(
                "quick_entry_points",
                "Quick entry points",
                "quick-entry-points",
                nav("latest_standings_quick", "Latest standings", "latest-standings"),
                nav("banzuke_changes_quick", "Banzuke changes", "banzuke-changes"),
                nav("rikishi_lookup_quick", "Rikishi lookup", "rikishi-lookup"),
                nav("rank_outcomes_quick", "Rank outcomes", "rank-outcomes"),
                nav("ratings_models_quick", "Ratings and models", "ratings-and-models"),
            ),
        ),
        nav(
            "current_sumo",
            "Current Sumo",
            "current-sumo",
            nav(
                "latest_tables",
                "Latest Tables",
                "latest-tables",
                nav("current_rating_standings_table", "Current rating / standings table", "current-rating-standings-table"),
                nav("date_navigation", "Date navigation", "date-navigation"),
                nav("division_filters", "Division filters", "division-filters"),
                nav("sortable_columns", "Sortable columns", "sortable-columns"),
                nav("shikona_click_through", "Shikona click-through to rikishi pages", "shikona-click-through"),
                nav("table_notes", "Table notes / column definitions", "table-notes"),
                nav(
                    "analyst_columns",
                    "Analyst columns",
                    "analyst-columns",
                    nav("elo_equelo", "Elo / Equelo", "elo-equelo"),
                    nav("expected_wins", "Expected wins", "expected-wins"),
                    nav("probability_derived_values", "Probability-derived values", "probability-derived-values"),
                    nav("current_score", "Current score", "current-score"),
                    nav("latest_rating", "Latest rating", "latest-rating"),
                    nav("new_projected_chii", "New / projected chii", "new-projected-chii"),
                    nav("delta_elo", "Delta Elo", "delta-elo"),
                    nav("delta_banzuke", "Delta banzuke", "delta-banzuke"),
                    nav("delta_chii_audited", "Delta chii, only if audited", "delta-chii-audited"),
                    nav("rank_relative_values", "Rank-relative values such as vChii", "rank-relative-values"),
                ),
            ),
            nav(
                "standings_by_wins",
                "Standings by Wins",
                "standings-by-wins",
                nav("window_selector", "Window selector", "window-selector"),
                nav("division_selector", "Division selector", "division-selector"),
                nav("combined_separated_views", "Combined / separated views", "combined-separated-views"),
                page_id="standings_by_wins",
            ),
            nav(
                "current_basho",
                "Current Basho",
                "current-basho",
                nav("latest_results", "Latest results", "latest-results"),
                nav("day_view", "Day view", "day-view"),
                nav("basho_view", "Basho view", "basho-view"),
                nav("rikishi_result_links", "Rikishi result links", "rikishi-result-links"),
            ),
            nav(
                "current_banzuke",
                "Current Banzuke",
                "current-banzuke",
                nav("current_banzuke_browser", "Current banzuke browser", "current-banzuke-browser"),
                nav("current_banzuke_division_view", "Division view", "division-view"),
                nav("rank_slot_view", "Rank slot view", "rank-slot-view"),
                nav("current_banzuke_rikishi_links", "Rikishi links", "rikishi-links"),
            ),
            nav(
                "banzuke_changes",
                "Banzuke Changes",
                "banzuke-changes",
                nav("new_banzuke_change_report", "New-banzuke change report", "new-banzuke-change-report"),
                nav("mechanical_changes", "Mechanical changes", "mechanical-changes"),
                nav("promotions", "Promotions", "promotions"),
                nav("demotions", "Demotions", "demotions"),
                nav("notable_changes", "Notable changes / headlines", "notable-changes"),
                nav("detailed_filtered_report", "Detailed filtered report", "detailed-filtered-report"),
                page_id="banzuke_changes",
            ),
            nav(
                "current_leaders",
                "Current Leaders",
                "current-leaders",
                nav("max_average_wins", "Max average wins", "max-average-wins"),
                nav("max_rating_probability", "Max rating probability", "max-rating-probability"),
                nav("highest_rated_rikishi", "Highest-rated rikishi", "highest-rated-rikishi"),
                nav("biggest_rating_movers", "Biggest rating movers", "biggest-rating-movers"),
                nav("biggest_banzuke_movers", "Biggest banzuke movers", "biggest-banzuke-movers"),
                nav("unusual_current_rikishi", "Unusual current rikishi by expected wins / probability", "unusual-current-rikishi"),
            ),
        ),
        nav(
            "rikishi",
            "Rikishi",
            "rikishi",
            nav(
                "rikishi_lookup",
                "Rikishi Lookup",
                "rikishi-lookup",
                nav("search_by_shikona", "Search by shikona", "search-by-shikona"),
                nav("current_rank_division", "Current rank / division", "current-rank-division"),
                nav("profile_link", "Profile link", "profile-link"),
                nav("shikona_history", "Shikona history, if available", "shikona-history"),
            ),
            nav(
                "rikishi_profile",
                "Rikishi Profile",
                "rikishi-profile",
                nav(
                    "profile_summary",
                    "Summary",
                    "summary",
                    nav("profile_current_chii", "Current chii", "current-chii"),
                    nav("profile_current_rating", "Current rating", "current-rating"),
                    nav("profile_career_high", "Career high", "career-high"),
                    nav("profile_recent_record", "Recent record", "recent-record"),
                    nav("profile_current_trend", "Current trend", "current-trend"),
                ),
                nav(
                    "career_timeline",
                    "Career Timeline",
                    "career-timeline",
                    nav("rank_chii_calendar_time", "Rank / chii over calendar time", "rank-chii-calendar-time"),
                    nav("rank_chii_basho_count", "Rank / chii by basho count", "rank-chii-basho-count"),
                    nav("division_history", "Division history", "division-history"),
                    nav("career_high_markers", "Career high markers", "career-high-markers"),
                ),
                nav(
                    "rating_timeline",
                    "Rating Timeline",
                    "rating-timeline",
                    nav("elo_equelo_calendar_time", "Elo / Equelo over calendar time", "elo-equelo-calendar-time"),
                    nav("daily_rating_movement", "Daily rating movement", "daily-rating-movement"),
                    nav("bout_level_rating_movement", "Bout-level rating movement", "bout-level-rating-movement"),
                    nav("rating_deltas", "Rating deltas", "rating-deltas"),
                ),
                nav(
                    "combined_career_view",
                    "Combined Career View",
                    "combined-career-view",
                    nav("chii_rating_dual_axes", "Chii + rating on dual y-axes", "chii-rating-dual-axes"),
                    nav("rank_and_rating_together", "Rank movement and rating movement together", "rank-and-rating-together"),
                    nav("calendar_time_mode", "Calendar-time mode", "calendar-time-mode"),
                    nav("basho_count_mode", "Basho-count mode", "basho-count-mode"),
                ),
                nav(
                    "performance_context",
                    "Performance Context",
                    "performance-context",
                    nav("profile_recent_form", "Recent form", "recent-form"),
                    nav("profile_rank_trend", "Rank trend", "rank-trend"),
                    nav("profile_rating_trend", "Rating trend", "rating-trend"),
                    nav("profile_expected_wins", "Expected wins", "expected-wins"),
                    nav("similar_chii_observed_outcomes", "Observed outcomes from similar chii", "similar-chii-observed-outcomes"),
                ),
            ),
            nav(
                "career_comparisons",
                "Career Comparisons",
                "career-comparisons",
                nav("comparable_careers", "Comparable careers", "comparable-careers"),
                nav("fast_rising_prospects", "Fast-rising prospects", "fast-rising-prospects"),
                nav("journeymen", "Journeymen", "journeymen"),
                nav("newcomer_context", "Newcomer context", "newcomer-context"),
            ),
            nav(
                "career_facts",
                "Career Facts",
                "career-facts",
                nav("career_high_table", "Career high table", "career-high-table"),
                nav("first_appearance_debut_context", "First appearance / debut context", "first-appearance-debut-context"),
                nav("career_rank_at_retirement", "Rank at retirement", "rank-at-retirement"),
                nav("career_length", "Career length", "career-length"),
            ),
        ),
        nav(
            "banzuke_rank",
            "Banzuke & Rank",
            "banzuke-rank",
            nav(
                "chii_explained",
                "Chii Explained",
                "chii-explained",
                nav("what_m3e_means", "What M3e means", "what-m3e-means"),
                nav("division_number_side_annotation", "Division, number, side, annotation", "division-number-side-annotation"),
                nav("sideless_chii", "Sideless chii", "sideless-chii"),
                nav("chii_ordering", "Chii ordering", "chii-ordering"),
                nav("rank_movement_glossary", "Rank movement glossary", "rank-movement-glossary"),
                nav("promotion_demotion_basics", "Promotion / demotion basics", "promotion-demotion-basics"),
            ),
            nav(
                "rank_current_banzuke",
                "Current Banzuke",
                "current-banzuke",
                nav("official_looking_banzuke_browser", "Official-looking banzuke browser", "official-looking-banzuke-browser"),
                nav("rank_banzuke_division_filters", "Division filters", "division-filters"),
                nav("rank_slots", "Rank slots", "rank-slots"),
                nav("east_west_layout", "East / west layout", "east-west-layout"),
            ),
            nav(
                "rank_banzuke_changes",
                "Banzuke Changes",
                "banzuke-changes",
                nav("rank_current_banzuke_change_report", "Current banzuke change report", "current-banzuke-change-report"),
                nav("new_banzuke_headlines", "New banzuke headlines", "new-banzuke-headlines"),
                nav("rank_promotions_demotions", "Promotions and demotions", "promotions-demotions"),
                nav("mechanical_fact_view", "Mechanical fact view", "mechanical-fact-view"),
                nav("editorial_interpretation_view", "Editorial / interpretation view", "editorial-interpretation-view"),
            ),
            nav(
                "banzuke_structure_over_time",
                "Banzuke Structure Over Time",
                "banzuke-structure-over-time",
                nav("division_sizes_over_time", "Division sizes over time", "division-sizes-over-time"),
                nav("banzuke_population_history", "Banzuke population history", "banzuke-population-history"),
                nav("changes_to_sizes_of_divisions", "Changes to sizes of divisions", "changes-to-sizes-of-divisions"),
                nav("banzuke_division_by_era", "Banzuke Division by Era", "banzuke-division-by-era", page_id="banzuke_division_by_era"),
            ),
            nav(
                "makuuchi_structure",
                "Makuuchi Structure",
                "makuuchi-structure",
                nav("makuuchi_rank_by_era", "Makuuchi Rank by Era", "makuuchi-rank-by-era", page_id="makuuchi_rank_by_era"),
                nav("rank_structure_changes", "Rank structure changes", "rank-structure-changes"),
                nav("sanyaku_maegashira_population", "Sanyaku / maegashira population history", "sanyaku-maegashira-population"),
            ),
            nav(
                "rank_slot_history",
                "Rank Slot History",
                "rank-slot-history",
                nav("first_chii_appearance", "First chii appearance", "first-chii-appearance"),
                nav("y1e_history", "Y1e history", "y1e-history"),
                nav("historical_rare_ranks", "Historical / rare ranks", "historical-rare-ranks"),
                nav("curated_rank_explanation", "Curated-rank explanation", "curated-rank-explanation"),
            ),
            nav(
                "division_movement",
                "Division Movement",
                "division-movement",
                nav("division_stability", "Division Stability", "division-stability", page_id="division_stability"),
                nav("promotion_demotion_frequency", "Promotion / demotion frequency", "promotion-demotion-frequency"),
                nav("movement_between_divisions", "Movement between divisions", "movement-between-divisions"),
            ),
            nav(
                "retirement_and_rank",
                "Retirement and Rank",
                "retirement-and-rank",
                nav("rank_at_retirement", "Rank at retirement", "rank-at-retirement"),
                nav("retirement_rank_distribution", "Retirement-rank distribution", "retirement-rank-distribution"),
                nav("bg_intai_ambiguity", "Bg / intai ambiguity caveats", "bg-intai-ambiguity"),
            ),
        ),
        nav(
            "performance",
            "Performance",
            "performance",
            nav(
                "rank_outcomes",
                "Rank Outcomes",
                "rank-outcomes",
                nav("finish_by_chii", "Finish by Chii", "finish-by-chii", page_id="finish_by_chii"),
                nav("average_finish_by_chii", "Average finish by chii", "average-finish-by-chii"),
                nav("threshold_views", "Threshold views", "threshold-views"),
                nav("top_records_from_rank", "Top records from a rank", "top-records-from-rank"),
                nav("bottom_records_from_rank", "Bottom records from a rank", "bottom-records-from-rank"),
                nav("expected_record_from_rank", "Expected record from rank context", "expected-record-from-rank"),
                nav("rank_outcomes_division_filters", "Division filters", "division-filters"),
                nav("sample_size_display", "Sample-size display", "sample-size-display"),
            ),
            nav(
                "matchups",
                "Matchups",
                "matchups",
                nav("observed_matchup_probabilities", "Observed matchup probabilities", "observed-matchup-probabilities"),
                nav("sideless_chii_matchup_traces", "Sideless chii matchup traces", "sideless-chii-matchup-traces"),
                nav("pair_support_sample_size", "Pair support / sample size", "pair-support-sample-size"),
                nav("confidence_intervals", "Confidence intervals", "confidence-intervals"),
                nav("curated_rank_domain", "Curated rank domain", "curated-rank-domain"),
                nav("matchups_division_filters", "Division filters", "division-filters"),
            ),
            nav(
                "observed_expectations",
                "Observed Expectations",
                "observed-expectations",
                nav("usually_happens_from_rank", "What usually happens from this rank?", "usually-happens-from-rank"),
                nav("usually_happens_against_rank", "What usually happens against this opponent rank?", "usually-happens-against-rank"),
                nav("rank_outcome_explorer", "Rank outcome explorer", "rank-outcome-explorer"),
                nav("support_aware_interpretation", "Support-aware interpretation", "support-aware-interpretation"),
            ),
            nav(
                "performance_patterns",
                "Performance Patterns",
                "performance-patterns",
                nav("current_form_vs_expectation", "Current form versus historical expectation", "current-form-vs-expectation"),
                nav("performance_rank_trend", "Rank trend", "rank-trend"),
                nav("over_underperformance", "Overperformance / underperformance, if method is defined", "over-underperformance"),
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
                nav("what_rating_measures", "What rating is trying to measure", "what-rating-measures"),
                nav("rating_versus_banzuke_rank", "Rating versus banzuke rank", "rating-versus-banzuke-rank"),
                nav("what_ratings_do_not_prove", "What ratings do not prove", "what-ratings-do-not-prove"),
            ),
            nav(
                "current_ratings",
                "Current Ratings",
                "current-ratings",
                nav("current_elo_equelo_table", "Current Elo / Equelo table", "current-elo-equelo-table"),
                nav("rating_leaders", "Rating leaders", "rating-leaders"),
                nav("rating_probability_leaders", "Rating probability leaders", "rating-probability-leaders"),
                nav("rating_changes", "Rating changes", "rating-changes"),
                nav("ratings_date_navigation", "Date navigation", "date-navigation"),
            ),
            nav(
                "rating_and_rank",
                "Rating and Rank",
                "rating-and-rank",
                nav("elo_equelo_vs_chii", "Elo / Equelo vs chii", "elo-equelo-vs-chii"),
                nav("rating_vs_rank_validation", "Rating-vs-rank validation", "rating-vs-rank-validation"),
                nav("mean_rating_by_chii", "Mean rating by chii", "mean-rating-by-chii"),
                nav("mean_expected_wins_by_chii", "Mean expected wins by chii", "mean-expected-wins-by-chii"),
                nav("mean_probability_value_by_chii", "Mean probability-derived value by chii", "mean-probability-value-by-chii"),
                nav("normalised_probability_value_by_chii", "Normalised probability-derived value by chii", "normalised-probability-value-by-chii"),
                nav("intro_rating_table_chart", "Intro rating table / chart", "intro-rating-table-chart"),
            ),
            nav(
                "observed_vs_modelled",
                "Observed vs Modelled",
                "observed-vs-modelled",
                nav("win_probability_by_standing", "Win Probability by Standing", "win-probability-by-standing", page_id="win_probability_by_standing"),
                nav("difference_residual_chart", "Difference / residual chart, later", "difference-residual-chart"),
                nav("support_aware_comparison", "Support-aware comparison", "support-aware-comparison"),
                nav("consistency_checks", "Consistency checks", "consistency-checks"),
            ),
            nav(
                "model_diagnostics",
                "Model Diagnostics",
                "model-diagnostics",
                nav("inflation_by_rank_chii", "Inflation by rank / chii", "inflation-by-rank-chii"),
                nav("rating_spread_variants", "Rating spread variants", "rating-spread-variants"),
                nav("rating_distribution", "Rating distribution", "rating-distribution"),
                nav("estimators", "Estimators", "estimators"),
                nav("mean_rating_vs_banzuke_size", "Mean rating vs banzuke size", "mean-rating-vs-banzuke-size"),
                nav("calibration_reports", "Calibration reports", "calibration-reports"),
                nav("probability_calibration", "Probability calibration", "probability-calibration"),
                nav("drift_over_time", "Drift over time", "drift-over-time"),
            ),
            nav(
                "methodology",
                "Methodology",
                "methodology",
                nav("elo_explanation", "Elo explanation", "elo-explanation"),
                nav("equelo_explanation", "Equelo explanation", "equelo-explanation"),
                nav("bkq_legacy_model_explanation", "BKQ / legacy model explanation", "bkq-legacy-model-explanation"),
                nav("formulae", "Formulae", "formulae"),
                nav("parameters", "Parameters", "parameters"),
                nav("assumptions", "Assumptions", "assumptions"),
                nav("teleological_risk_caveats", "Teleological-risk caveats", "teleological-risk-caveats"),
                nav("research_only_outputs", "Why some outputs are research only", "research-only-outputs"),
            ),
            nav(
                "research_archive",
                "Research Archive",
                "research-archive",
                nav("fixed_v1_rating_curve_charts", "Fixed-v1 rating curve charts", "fixed-v1-rating-curve-charts"),
                nav("one_shot_simulation_charts", "One-shot simulation charts", "one-shot-simulation-charts"),
                nav("expt3_predicted_distribution", "Expt3 predicted probability distribution", "expt3-predicted-distribution"),
                nav("calibration_experiments", "Calibration experiments", "calibration-experiments"),
                nav("model_failures_dead_ends", "Model failures and dead ends", "model-failures-dead-ends"),
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
                nav("history_division_sizes", "Division sizes over time", "division-sizes-over-time"),
                nav("history_changes_division_sizes", "Changes to sizes of divisions", "changes-to-sizes-of-divisions"),
                nav("history_banzuke_population", "Banzuke population", "banzuke-population"),
                nav("history_mean_rating_banzuke_size", "Mean rating vs banzuke size", "mean-rating-banzuke-size"),
            ),
            nav(
                "career_lifecycle",
                "Career Lifecycle",
                "career-lifecycle",
                nav("career_length_count", "Career length count", "career-length-count"),
                nav("career_length_probability", "Career length probability", "career-length-probability"),
                nav("cumulative_career_length_probability", "Cumulative career length probability", "cumulative-career-length-probability"),
                nav("history_retirement_rank_distribution", "Retirement-rank distribution", "retirement-rank-distribution"),
            ),
            nav(
                "rank_history",
                "Rank History",
                "rank-history",
                nav("history_first_chii_appearance", "First chii appearance", "first-chii-appearance"),
                nav("history_y1e_history", "Y1e history", "y1e-history"),
                nav("historical_rank_slots", "Historical rank slots", "historical-rank-slots"),
                nav("history_makuuchi_structure", "Makuuchi rank structure over time", "makuuchi-rank-structure-over-time"),
            ),
            nav(
                "recruitment_retirement",
                "Recruitment and Retirement",
                "recruitment-retirement",
                nav("recruitment_patterns_future", "Recruitment patterns, future", "recruitment-patterns-future"),
                nav("retirement_patterns", "Retirement patterns", "retirement-patterns"),
                nav("division_entry_exit_patterns", "Division entry / exit patterns", "division-entry-exit-patterns"),
            ),
            nav(
                "historical_exhibits",
                "Historical Exhibits",
                "historical-exhibits",
                nav("history_banzuke_division_by_era", "Banzuke division by era", "banzuke-division-by-era"),
                nav("history_makuuchi_by_era", "Makuuchi by era", "makuuchi-by-era"),
                nav("long_term_rank_population_charts", "Long-term rank population charts", "long-term-rank-population-charts"),
            ),
        ),
        nav(
            "data_methods",
            "Data & Methods",
            "data-methods",
            nav(
                "data_source",
                "Data Source",
                "data-source",
                nav("where_data_comes_from", "Where the data comes from", "where-data-comes-from"),
                nav("update_policy", "Update policy", "update-policy"),
                nav("currentness_policy", "Currentness policy", "currentness-policy"),
                nav("parsed_history", "Parsed history", "parsed-history"),
                nav("known_source_limitations", "Known source limitations", "known-source-limitations"),
            ),
            nav(
                "glossary",
                "Glossary",
                "glossary",
                nav("glossary_basho", "Basho", "basho"),
                nav("glossary_banzuke", "Banzuke", "banzuke"),
                nav("glossary_chii", "Chii", "chii"),
                nav("glossary_rikishi", "Rikishi", "rikishi"),
                nav("glossary_shikona", "Shikona", "shikona"),
                nav("glossary_division", "Division", "division"),
                nav("glossary_record", "Record", "record"),
                nav("glossary_fusen", "Fusen / non-fought outcomes", "fusen-non-fought-outcomes"),
                nav("glossary_east_west", "East / west", "east-west"),
                nav("glossary_sideless_chii", "Sideless chii", "sideless-chii"),
            ),
            nav(
                "known_limitations",
                "Known Limitations",
                "known-limitations",
                nav("missing_ambiguous_data", "Missing or ambiguous data", "missing-ambiguous-data"),
                nav("historical_rank_quirks", "Historical rank quirks", "historical-rank-quirks"),
                nav("retirement_ambiguity", "Retirement ambiguity", "retirement-ambiguity"),
                nav("parser_limitations", "Parser limitations", "parser-limitations"),
                nav("model_limitations", "Model limitations", "model-limitations"),
                nav("what_not_to_infer", "What not to infer", "what-not-to-infer"),
            ),
            nav(
                "method_notes",
                "Method Notes",
                "method-notes",
                nav("how_historical_data_is_parsed", "How historical data is parsed", "how-historical-data-is-parsed"),
                nav("how_outputs_are_generated", "How outputs are generated", "how-outputs-are-generated"),
                nav("how_confidence_intervals_are_computed", "How confidence intervals are computed", "how-confidence-intervals-are-computed"),
                nav("how_curated_domains_are_chosen", "How curated domains are chosen", "how-curated-domains-are-chosen"),
                nav("observed_vs_model_projection", "Difference between observed data and model projections", "observed-vs-model-projection"),
            ),
            nav(
                "technical_appendix",
                "Technical Appendix",
                "technical-appendix",
                nav("parser_validation_notes", "Parser and validation notes", "parser-validation-notes"),
                nav("warning_logs_summary", "Warning logs summary, not raw logs", "warning-logs-summary"),
                nav("persistence_reports_promoted", "Persistence reports if promoted", "persistence-reports-promoted"),
                nav("data_quality_notes", "Data-quality notes", "data-quality-notes"),
            ),
        ),
        nav(
            "lab_archive",
            "Lab / Archive",
            "lab-archive",
            nav(
                "experimental_charts",
                "Experimental Charts",
                "experimental-charts",
                nav("misc_legacy_charts", "Miscellaneous legacy charts that do not yet have public framing", "misc-legacy-charts"),
                nav("old_model_diagnostics", "Old model diagnostics", "old-model-diagnostics"),
                nav("prototype_charts", "Prototype charts", "prototype-charts"),
            ),
            nav(
                "internal_diagnostics",
                "Internal Diagnostics",
                "internal-diagnostics",
                nav("parser_warning_summaries", "Parser warning summaries", "parser-warning-summaries"),
                nav("weirdness_reports", "Weirdness reports, if ever exposed", "weirdness-reports"),
                nav("raw_downloaded_html_not_nav", "Raw downloaded HTML should not be public navigation", "raw-downloaded-html-not-nav"),
            ),
            nav(
                "deprecated_superseded",
                "Deprecated / Superseded",
                "deprecated-superseded",
                nav("broken_unaudited_columns", "Broken or unaudited columns", "broken-unaudited-columns"),
                nav("delta_chii_until_fixed", "Delta chii, until fixed", "delta-chii-until-fixed"),
                nav("old_ranking_index_caveats", "Old ranking/index behavior caveats", "old-ranking-index-caveats"),
                nav("research_outputs_provenance", "Research outputs retained for provenance", "research-outputs-provenance"),
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
    base_route="/sumo-tools/",
    output_root=OUTPUT_ROOT / "make_site",
)
