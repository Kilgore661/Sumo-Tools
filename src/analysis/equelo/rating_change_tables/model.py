"""Data model for production Rating Changes tables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_WINDOWS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 12)
DEFAULT_WINDOW: int = 6
OUTPUT_ROOT = Path("files/output/analysis/equelo/rating_change_tables")
INDEX_FILE_NAME = "rating_changes_index.json"


@dataclass(frozen=True)
class BoutMetrics:
    """Per-rikishi movement metrics accumulated over one basho."""

    actual_bouts: int
    normalised_delta: float


@dataclass(frozen=True)
class RatingChangeRow:
    """One row in a produced Rating Changes CSV payload."""

    rikishi_id: int
    shikona: str
    division_id: str
    chii_at_start: str
    chii_ordinal_at_start: int | str
    chii_at_end: str
    chii_ordinal_at_end: int | str
    rating_at_start: str
    rating_at_end: str
    delta: str
    expected_bouts: int
    delta_per_expected_bout: str
    normalised_delta_per_expected_bout: str
    actual_bouts: int
    delta_per_actual_bout: str
    normalised_delta_per_actual_bout: str


@dataclass(frozen=True)
class RatingChangesIndexEntry:
    """One selectable source entry in the site-facing Rating Changes index."""

    n: int
    label: str
    target_date: str
    start_date: str
    payload_path: str


@dataclass(frozen=True)
class RatingChangesOutputs:
    """Paths written by the Rating Changes producer."""

    output_root: Path
    index_path: Path
    payload_paths: tuple[Path, ...]
