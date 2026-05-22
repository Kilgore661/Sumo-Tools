"""Compatibility facade for the canonical public-site definition."""

from __future__ import annotations

from .site_assets import BANZUKE_CHANGES_ASSETS, GLOBAL_ASSETS, STANDINGS_ASSETS
from .site_config import (
    ANALYSIS_ROOT,
    BCR_OUTPUT_ROOT,
    BUILD_CONFIG,
    CAREER_LENGTH_SITE_OUTPUT_DIR,
    OUTPUT_ROOT,
    PRODUCT_ROOT,
    RANK_AT_RETIREMENT_SITE_OUTPUT_DIR,
    REPO_ROOT,
    STANDINGS_PUBLISHER_DATA,
    TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR,
    WIN_PROBABILITY_SITE_BUNDLE,
)
from .site_data_refs import (
    BANZUKE_CHANGES_DATA,
    STANDINGS_DATA,
    WIN_PROBABILITY_BY_STANDING_DATA,
    career_length_data_refs,
    rank_at_retirement_data_refs,
    typical_equelo_values_data_refs,
)
from .site_navigation import NAVIGATION, nav
from .site_pages import (
    PAGES,
    SITE,
    WIN_PROBABILITY_BY_STANDING_OPTIONS,
    site_with_career_length,
    site_with_career_lifecycle,
)
from .site_refs import asset, data, data_media_type, published_data_refs, view

__all__ = [
    "ANALYSIS_ROOT",
    "BANZUKE_CHANGES_ASSETS",
    "BANZUKE_CHANGES_DATA",
    "BCR_OUTPUT_ROOT",
    "BUILD_CONFIG",
    "CAREER_LENGTH_SITE_OUTPUT_DIR",
    "GLOBAL_ASSETS",
    "NAVIGATION",
    "OUTPUT_ROOT",
    "PAGES",
    "PRODUCT_ROOT",
    "RANK_AT_RETIREMENT_SITE_OUTPUT_DIR",
    "REPO_ROOT",
    "SITE",
    "STANDINGS_ASSETS",
    "STANDINGS_DATA",
    "STANDINGS_PUBLISHER_DATA",
    "TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR",
    "WIN_PROBABILITY_BY_STANDING_DATA",
    "WIN_PROBABILITY_BY_STANDING_OPTIONS",
    "WIN_PROBABILITY_SITE_BUNDLE",
    "asset",
    "career_length_data_refs",
    "data",
    "data_media_type",
    "nav",
    "published_data_refs",
    "rank_at_retirement_data_refs",
    "site_with_career_length",
    "site_with_career_lifecycle",
    "typical_equelo_values_data_refs",
    "view",
]
