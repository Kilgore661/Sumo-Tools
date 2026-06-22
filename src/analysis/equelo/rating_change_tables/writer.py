"""Writers for production Rating Changes table artifacts."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .model import (
    DEFAULT_WINDOW,
    INDEX_FILE_NAME,
    RatingChangeRow,
    RatingChangesIndexEntry,
)


FIELDNAMES = [
    "rikishi_id",
    "shikona",
    "division_id",
    "chii_at_start",
    "chii_ordinal_at_start",
    "chii_at_end",
    "chii_ordinal_at_end",
    "rating_at_start",
    "rating_at_end",
    "delta",
    "expected_bouts",
    "delta_per_expected_bout",
    "normalised_delta_per_expected_bout",
    "actual_bouts",
    "delta_per_actual_bout",
    "normalised_delta_per_actual_bout",
]


def write_payload(rows: Iterable[RatingChangeRow], output_path: Path) -> Path:
    """Write one Rating Changes CSV payload with a stable header."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    return output_path


def write_index(
    *,
    entries: Iterable[RatingChangesIndexEntry],
    output_root: Path,
    default_n: int = DEFAULT_WINDOW,
) -> Path:
    """Write the site-facing Rating Changes indexed-source file."""

    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / INDEX_FILE_NAME
    payload = {
        "default_n": str(default_n),
        "entries": [
            {
                "n": str(entry.n),
                "label": entry.label,
                "target_date": entry.target_date,
                "start_date": entry.start_date,
                "payload_path": entry.payload_path,
            }
            for entry in entries
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
