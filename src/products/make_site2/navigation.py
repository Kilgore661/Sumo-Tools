"""Navigation tree for the public site.

Copied from make_site as the starting declared navigation model. make_site2 owns
this copy; it should not import the old package because make_site is temporary.
"""

from __future__ import annotations

from .models import NavigationTree


GOATS_HREF = "index.html?page=career_comparisons&skill=equelo&x=date&log=true&rikishi=1123%2C3987%2C1354%2C2%2C3%2C4080"


def nav(
    id: str,
    label: str,
    slug: str,
    *children: NavigationTree,
    page_id: str | None = None,
    href: str | None = None,
) -> NavigationTree:
    return NavigationTree(
        id=id,
        label=label,
        slug=slug,
        children=children,
        page_id=page_id,
        href=href,
    )


PUBLIC_NAVIGATION = NavigationTree(
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
                        page_id="what_this_site_is",
                    ),
                    nav(
                        "site_notes_caveats",
                        "Notes and caveats",
                        "notes-and-caveats",
                    ),
                    nav(
                        "quick_basho_results_browser",
                        "Basho Results",
                        "basho-results",
                        page_id="basho_results_browser",
                    ),
                    nav(
                        "quick_banzuke_changes",
                        "Most Recent Banzuke",
                        "banzuke-changes",
                        page_id="banzuke_changes",
                    ),
                    nav(
                        "career_comparisons",
                        "Rikishi history",
                        "career-comparisons",
                        page_id="career_comparisons",
                    ),
                    nav(
                        "quick_goats",
                        "GOATs",
                        "goats",
                        href=GOATS_HREF,
                    ),
                ),
        nav(
                    "records",
                    "Records",
                    "records",
                    nav(
                        "most_consecutive_bouts",
                        "Most consecutive bouts",
                        "most-consecutive-bouts",
                        page_id="most_consecutive_bouts",
                    ),
                    nav(
                        "most_career_wins",
                        "Most career wins",
                        "most-career-wins",
                        page_id="most_career_wins",
                    ),
                    nav(
                        "highest_equelo",
                        "Highest Equelo",
                        "highest-equelo",
                        page_id="highest_equelo",
                    ),
                    nav(
                        "longest_careers",
                        "Longest careers",
                        "longest-careers",
                        page_id="longest_careers",
                    ),
                ),
        nav(
                    "miscellaneous_stats",
                    "Miscellaneous Stats",
                    "miscellaneous-stats",
                    nav(
                        "banzuke_division_by_era",
                        "Banzuke structure by era",
                        "banzuke-division-by-era",
                        page_id="banzuke_division_by_era",
                    ),
                    nav(
                        "makuuchi_rank_by_era",
                        "Makuuchi structure by era",
                        "makuuchi-rank-by-era",
                        page_id="makuuchi_rank_by_era",
                    ),
                    nav(
                        "history_career_length",
                        "Career length",
                        "career-length",
                        page_id="career_length",
                    ),
                    nav(
                        "rank_at_retirement",
                        "Rank at retirement",
                        "rank-at-retirement",
                        page_id="rank_at_retirement",
                    ),
                ),
        nav(
                    "equelo_ratings",
                    "Equelo Ratings",
                    "equelo-ratings",
                    nav("why_ratings", "Why ratings?", "why-ratings", page_id="why_ratings"),
                    nav("elo_equelo_explanation", "Elo / Equelo explanation", "elo-equelo-explanation"),
                    nav("assumptions_caveats", "Assumptions and caveats", "assumptions-caveats"),
                    nav(
                        "typical_equelo_values",
                        "Typical Equelo ratings",
                        "typical-equelo-values",
                        page_id="typical_equelo_values",
                    ),
                ),
    ),
)

RESEARCH_NAVIGATION = NavigationTree(
    id="research_root",
    label="Research Root",
    slug="",
    children=(
        nav(
                    "current_sumo",
                    "Current Sumo",
                    "current-sumo",
                    nav("current_ratings", "Current ratings", "current-ratings"),
                    nav(
                        "current_leaders",
                        "Current Leaders",
                        "current-leaders",
                        nav("max_average_wins", "Max average wins", "max-average-wins"),
                        nav("max_rating_probability", "Max rating probability", "max-rating-probability"),
                        nav("rating_movers", "Rating movers", "rating-movers"),
                        nav("banzuke_movers", "Banzuke movers", "banzuke-movers"),
                    ),
                    nav(
                        "rating_changes",
                        "Rating changes",
                        "rating-changes",
                        page_id="rating_changes",
                    ),
                ),
        nav(
                    "rikishi",
                    "Rikishi",
                    "rikishi",
                    nav("rikishi_lookup", "Rikishi lookup", "rikishi-lookup"),
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
                ),
        nav(
                    "banzuke_rank",
                    "Banzuke & Rank",
                    "banzuke-rank",
                    nav("chii_notes", "Chii notes", "chii-notes"),
                    nav("current_banzuke", "Current banzuke", "current-banzuke"),
                    nav(
                        "division_stability",
                        "Division persistence",
                        "division-stability",
                        page_id="division_stability",
                    ),
                    nav(
                        "rank_history",
                        "Rank History",
                        "rank-history",
                        nav(
                            "first_chii_appearance",
                            "First chii appearance",
                            "first-chii-appearance",
                            page_id="first_chii_appearance",
                        ),
                        nav("rare_historical_rank_slots", "Rare / historical rank slots", "rare-historical-rank-slots"),
                    ),
                    nav("retirement_rank", "Retirement rank", "retirement-rank"),
                ),
        nav(
                    "performance",
                    "Performance",
                    "performance",
                    nav(
                        "finish_by_chii",
                        "Wins: finish chances",
                        "finish-by-chii",
                        page_id="finish_by_chii",
                    ),
                    nav("win_probability_by_standing_observed", "Win probability by ranks", "win-probability-by-standing"),
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
                        "rating_and_rank",
                        "Rating and Rank",
                        "rating-and-rank",
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
                            "Win probability by ranks",
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
                        nav("v5_landmark_policy", "V5 landmark policy", "v5-landmark-policy"),
                        nav(
                            "lower_rank_rating_stability",
                            "Lower-rank rating stability",
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
                ),
        nav(
                    "data_notes",
                    "Data & Notes",
                    "data-notes",
                    nav("data_sources", "Data sources", "data-sources"),
                    nav("glossary", "Glossary", "glossary"),
                    nav("chii_banzuke_quirks", "Chii / banzuke quirks", "chii-banzuke-quirks"),
                    nav("known_limitations", "Known limitations", "known-limitations"),
                    nav("method_notes", "Method notes", "method-notes"),
                ),
        nav(
            "research_lab_archive",
            "Lab / Archive",
            "lab-archive",
        nav("research_charts_not_promoted", "Research charts not yet promoted", "research-charts-not-promoted"),
        nav("legacy_v9_pending", "Legacy v9 exhibits pending reimplementation", "legacy-v9-pending"),
        nav("deprecated_superseded", "Deprecated / superseded outputs", "deprecated-superseded"),
        nav(
            "standings_by_wins",
            "Rolling wins-based ranking",
            "standings-by-wins",
            page_id="standings_by_wins",
        ),
        ),
    ),
)

# Compatibility alias for older code/tests that still import NAVIGATION.
NAVIGATION = PUBLIC_NAVIGATION
