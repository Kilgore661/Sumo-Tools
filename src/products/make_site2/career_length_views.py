"""Build-time helpers for Career Length site-facing views."""

from __future__ import annotations

import csv
from pathlib import Path


CAREER_LENGTH_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "career-lifecycle"
    / "career-length"
    / "data"
)


def materialize_career_length_longest_views(*, output_root: Path) -> None:
    """Create ranked Longest view CSVs consumed directly by the runtime."""

    route_data_root = output_root / CAREER_LENGTH_ROUTE_DATA_DIR
    longest_path = route_data_root / "longest.csv"
    rows = _read_rows(longest_path)
    _write_ranked_rows(rows, longest_path)
    _write_ranked_rows(
        [row for row in rows if not _is_active(row.get("active"))],
        route_data_root / "longest_non_active.csv",
    )


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_ranked_rows(rows: list[dict[str, str]], path: Path) -> None:
    fieldnames = _ranked_fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            ranked = {key: value for key, value in row.items() if key != "rank"}
            writer.writerow({"rank": rank, **ranked})


def _ranked_fieldnames(rows: list[dict[str, str]]) -> tuple[str, ...]:
    if not rows:
        return ("rank",)
    return ("rank", *(key for key in rows[0].keys() if key != "rank"))


def _is_active(value: object) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes"}
