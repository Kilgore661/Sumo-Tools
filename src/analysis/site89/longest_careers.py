"""Derive the two Longest Careers populations outside the site assembler."""

from __future__ import annotations

import csv
from pathlib import Path

from src.analysis.sumo_history.constants import TOP_N_LIMIT

from .common import write_csv


def produce_longest_careers(*, career_rikishi_csv: Path, output_root: Path) -> Path:
    with career_rikishi_csv.open(newline="", encoding="utf-8") as stream:
        source = list(csv.DictReader(stream))
    rows = [
        *_ranked(_longest(source), "all"),
        *_ranked(_longest([row for row in source if not _active(row["active"])]), "non_active"),
    ]
    return write_csv(output_root / "longest.csv", rows)


def _ranked(rows, population):
    return [
        {
            "rank": rank,
            "longest_population": population,
            **{
                key: ("-" if key == "last_appearance" and _active(row["active"]) else value)
                for key, value in row.items()
                if key not in {"rank", "longest_population"}
            },
        }
        for rank, row in enumerate(rows, start=1)
    ]


def _longest(rows):
    return sorted(
        rows,
        key=lambda row: (-float(row["participation_years"]), int(row["first_index"]), int(row["rikishi_id"])),
    )[:TOP_N_LIMIT]


def _active(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}
