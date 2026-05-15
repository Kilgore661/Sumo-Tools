"""Paths and build configuration for the public site."""

from __future__ import annotations

from pathlib import Path

from .classes import SiteBuildConfig


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = REPO_ROOT / "files" / "output"
ANALYSIS_ROOT = REPO_ROOT / "src" / "analysis"
PRODUCT_ROOT = REPO_ROOT / "src" / "products" / "make_site"
BCR_OUTPUT_ROOT = OUTPUT_ROOT / "bcr"
BASHO_RESULTS_OUTPUT_ROOT = OUTPUT_ROOT / "basho_results"
STANDINGS_PUBLISHER_DATA = OUTPUT_ROOT / "standings" / "publisher" / "latest_data"
WIN_PROBABILITY_SITE_BUNDLE = (
    OUTPUT_ROOT / "probability" / "matchups" / "site" / "win_probability_by_standing"
)
DIVISION_STABILITY_SITE_BUNDLE = (
    OUTPUT_ROOT / "persistence" / "site" / "division_stability"
)
DIVISION_STABILITY_SITE_OUTPUT_DIR = "banzuke-rank/division-stability/data"
CAREER_LENGTH_SITE_OUTPUT_DIR = "sumo-history/career-lifecycle/career-length/data"
RANK_AT_RETIREMENT_SITE_OUTPUT_DIR = (
    "sumo-history/career-lifecycle/rank-at-retirement/data"
)
TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR = (
    "ratings-models/rating-and-rank/typical-equelo-values/data"
)
BASHO_RESULTS_SITE_OUTPUT_DIR = "sumo-history/basho-results/data"


BUILD_CONFIG = SiteBuildConfig(
    base_route="/sumo-tools/",
    output_root=OUTPUT_ROOT / "make_site",
)
