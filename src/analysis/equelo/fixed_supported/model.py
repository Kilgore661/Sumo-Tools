"""Model constants for fixed-supported Equelo artifacts."""

from __future__ import annotations

from pathlib import Path

from src.analysis.equelo.config_main import INITIAL_ELO
from src.analysis.equelo.fixed_v2.model import K_CONFIG, K_POLICY, Q


MODEL_VERSION = "fixed_supported"
OUTPUT_ROOT = Path("files/output/Equelo/fixed_supported")

MASTER_MAP_FILE_NAME = "master_chii_initial_rating_map.csv"
MASTER_MAP_METADATA_FILE_NAME = "master_chii_initial_rating_map_metadata.json"
METADATA_FILE_NAME = "metadata.json"
DAY_END_RATINGS_FILE_NAME = "day_end_ratings.json"
ENTRANT_INITIAL_RATINGS_FILE_NAME = "entrant_initial_ratings.json"

LANDMARKS_OUTPUT_DIR = OUTPUT_ROOT / "landmarks"
TYPICAL_EQUELO_VALUES_SOURCE_ROOT = (
    LANDMARKS_OUTPUT_DIR / "site" / "typical_equelo_values"
)

SUPPORT_COLLAPSE_POLICY = "rank_family_support_collapse"
SUPPORT_MEASURE = "collapsed_appearance_count"
SUPPORT_THRESHOLD = 60
COMPLETION_POLICY = "nearest_supported_chii_by_ordinal"
COMPLETION_TIE_BREAK = "stronger_lower_ordinal"
BASE_CONVENTION = INITIAL_ELO


def policy_metadata() -> dict[str, object]:
    """Return fixed-supported policy metadata for generated artifacts."""

    return {
        "model_version": MODEL_VERSION,
        "support_collapse_policy": SUPPORT_COLLAPSE_POLICY,
        "support_measure": SUPPORT_MEASURE,
        "support_threshold": SUPPORT_THRESHOLD,
        "completion_policy": COMPLETION_POLICY,
        "completion_tie_break": COMPLETION_TIE_BREAK,
        "base_convention": BASE_CONVENTION,
        "q": Q,
        "k_policy": K_POLICY,
        "k_config": str(K_CONFIG),
    }

