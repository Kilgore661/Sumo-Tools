"""Read fixed v1 Equelo rating artefacts."""

from __future__ import annotations

import json
from pathlib import Path

from .model import (
    DAY_END_RATINGS_FILE_NAME,
    ENTRANT_INITIAL_RATINGS_FILE_NAME,
    METADATA_FILE_NAME,
    OUTPUT_ROOT,
)


DayEndRatings = dict[str, dict[str, dict[str, float]]]
EntrantInitialRatings = dict[str, float]


def load_metadata(output_root: Path = OUTPUT_ROOT) -> dict:
    """Load fixed v1 metadata."""

    path = output_root / METADATA_FILE_NAME
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_day_end_ratings(output_root: Path = OUTPUT_ROOT) -> DayEndRatings:
    """Load fixed v1 day-end ratings."""

    path = output_root / DAY_END_RATINGS_FILE_NAME
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_entrant_initial_ratings(output_root: Path = OUTPUT_ROOT) -> EntrantInitialRatings:
    """Load fixed v1 entrant initial ratings keyed by chii ordinal string."""

    path = output_root / ENTRANT_INITIAL_RATINGS_FILE_NAME
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
