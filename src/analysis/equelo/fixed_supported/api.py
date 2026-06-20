"""Cheap access API for fixed-supported Equelo artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from .master_map import (
    MasterChiiInitialRatingRow,
    load_master_chii_initial_rating_map as load_master_map_rows,
)
from .model import (
    DAY_END_RATINGS_FILE_NAME,
    ENTRANT_INITIAL_RATINGS_FILE_NAME,
    MASTER_MAP_FILE_NAME,
    MASTER_MAP_METADATA_FILE_NAME,
    METADATA_FILE_NAME,
    OUTPUT_ROOT,
    TYPICAL_EQUELO_VALUES_SOURCE_ROOT,
)


DayEndRatings = dict[str, dict[str, dict[str, float]]]
EntrantInitialRatings = dict[str, float]


def master_chii_initial_rating_map_path(output_root: Path = OUTPUT_ROOT) -> Path:
    """Return the canonical master chii initial-rating map path."""

    return output_root / MASTER_MAP_FILE_NAME


def master_chii_initial_rating_map_metadata_path(
    output_root: Path = OUTPUT_ROOT,
) -> Path:
    """Return the canonical master-map metadata path."""

    return output_root / MASTER_MAP_METADATA_FILE_NAME


def day_end_ratings_path(output_root: Path = OUTPUT_ROOT) -> Path:
    """Return the canonical fixed-supported day-end ratings path."""

    return output_root / DAY_END_RATINGS_FILE_NAME


def entrant_initial_ratings_path(output_root: Path = OUTPUT_ROOT) -> Path:
    """Return the compatibility chii-initial-ratings JSON path."""

    return output_root / ENTRANT_INITIAL_RATINGS_FILE_NAME


def metadata_path(output_root: Path = OUTPUT_ROOT) -> Path:
    """Return the canonical fixed-supported metadata path."""

    return output_root / METADATA_FILE_NAME


def typical_equelo_values_path(output_root: Path = OUTPUT_ROOT) -> Path:
    """Return the canonical site-facing Typical Equelo Values CSV path."""

    if output_root == OUTPUT_ROOT:
        root = TYPICAL_EQUELO_VALUES_SOURCE_ROOT
    else:
        root = output_root / "landmarks" / "site" / "typical_equelo_values"
    return root / "typical_equelo_values.csv"


def load_master_chii_initial_rating_map(
    output_root: Path = OUTPUT_ROOT,
) -> tuple[MasterChiiInitialRatingRow, ...]:
    """Load the canonical master chii initial-rating map."""

    return load_master_map_rows(master_chii_initial_rating_map_path(output_root))


def load_master_chii_initial_rating_map_metadata(
    output_root: Path = OUTPUT_ROOT,
) -> dict:
    """Load master-map metadata."""

    return _load_json(master_chii_initial_rating_map_metadata_path(output_root))


def load_day_end_ratings(output_root: Path = OUTPUT_ROOT) -> DayEndRatings:
    """Load fixed-supported day-end ratings."""

    return _load_json(day_end_ratings_path(output_root))


def load_entrant_initial_ratings(
    output_root: Path = OUTPUT_ROOT,
) -> EntrantInitialRatings:
    """Load fixed-supported chii initial ratings keyed by ordinal string."""

    return _load_json(entrant_initial_ratings_path(output_root))


def load_metadata(output_root: Path = OUTPUT_ROOT) -> dict:
    """Load fixed-supported process-rating metadata."""

    return _load_json(metadata_path(output_root))


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
