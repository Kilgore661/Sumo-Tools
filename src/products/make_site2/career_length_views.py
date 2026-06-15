"""Build-time helpers for Career Length site-facing views."""

from __future__ import annotations

import csv
from pathlib import Path

from src.analysis.sumo_history.constants import TOP_N_LIMIT


CAREER_LENGTH_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "career-lifecycle"
    / "career-length"
    / "data"
)

LONGEST_POPULATION_FIELD = "longest_population"


def materialize_career_length_longest_views(
    *,
    output_root: Path,
    source_root: Path,
) -> None:
    """Create ranked Longest population views consumed directly by the runtime."""

    route_data_root = output_root / CAREER_LENGTH_ROUTE_DATA_DIR
    source_rows = _read_rows(_source_rikishi_csv(source_root))
    all_rows = _ranked_rows(_longest(source_rows), population="all")
    non_active_rows = _ranked_rows(
        _longest([row for row in source_rows if not _is_active(row.get("active"))]),
        population="non_active",
    )
    _write_rows([*all_rows, *non_active_rows], route_data_root / "longest.csv")
    _write_rows(non_active_rows, route_data_root / "longest_non_active.csv")


def _source_rikishi_csv(source_root: Path) -> Path:
    return source_root.parents[1] / f"{source_root.name}_rikishi.csv"


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _ranked_rows(rows: list[dict[str, str]], *, population: str) -> list[dict[str, object]]:
    return [
        {"rank": rank, LONGEST_POPULATION_FIELD: population, **_without_generated_fields(row)}
        for rank, row in enumerate(rows, start=1)
    ]


def _longest(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=_longest_sort_key)[:TOP_N_LIMIT]


def _longest_sort_key(row: dict[str, str]) -> tuple[float, int, int]:
    return (
        -float(row["participation_years"]),
        int(row["first_index"]),
        int(row["rikishi_id"]),
    )


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
