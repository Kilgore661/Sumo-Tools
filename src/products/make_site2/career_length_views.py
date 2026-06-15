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


LONGEST_POPULATION_FIELD = "longest_population"


def materialize_career_length_longest_views(*, output_root: Path) -> None:
    """Create ranked Longest population views consumed directly by the runtime."""

    route_data_root = output_root / CAREER_LENGTH_ROUTE_DATA_DIR
    longest_path = route_data_root / "longest.csv"
    source_rows = _read_rows(longest_path)
    all_rows = _ranked_rows(source_rows, population="all")
    non_active_rows = _ranked_rows(
        [row for row in source_rows if not _is_active(row.get("active"))],
        population="non_active",
    )
    _write_rows([*all_rows, *non_active_rows], longest_path)
    _write_rows(non_active_rows, route_data_root / "longest_non_active.csv")


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _ranked_rows(rows: list[dict[str, str]], *, population: str) -> list[dict[str, object]]:
    return [
        {"rank": rank, LONGEST_POPULATION_FIELD: population, **_without_generated_fields(row)}
        for rank, row in enumerate(rows, start=1)
    ]


def _without_generated_fields(row: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in row.items()
        if key not in {"rank", LONGEST_POPULATION_FIELD}
    }


def _write_rows(rows: list[dict[str, object]], path: Path) -> None:
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: list[dict[str, object]]) -> tuple[str, ...]:
    if not rows:
        return ("rank", LONGEST_POPULATION_FIELD)
    return tuple(rows[0].keys())


def _is_active(value: object) -> bool:
    return value is True or str(value).strip().lower() in {"true", "1", "yes"}
