"""Opt-in real-data smoke test for birth-date coverage by basho."""

from __future__ import annotations

import csv
from tempfile import TemporaryDirectory
from pathlib import Path

from src.infra.get_bios.api import load_bio_store
from src.infra.live_store.api import get_history

from .birth_date_coverage import (
    birth_date_coverage_by_basho,
    write_birth_date_coverage_csv,
)
from .average_age_by_division import (
    average_age_by_division,
    exact_basho_start_dates,
    write_average_age_by_division_csv,
)


def main() -> None:
    history = get_history()
    rows = birth_date_coverage_by_basho(history, load_bio_store())
    if not rows:
        raise RuntimeError("Smoke test requires a non-empty live History")
    if len(rows) != len(history):
        raise RuntimeError("Smoke-test output does not contain one row per basho")
    if not any(row.exact_birth_date for row in rows):
        raise RuntimeError("Smoke-test output contains no exact birth dates")
    if not any(row.missing_exact_birth_date for row in rows):
        raise RuntimeError("Smoke-test output contains no missing birth dates")

    with TemporaryDirectory(prefix="ages_birth_date_coverage_") as temporary:
        output = Path(temporary) / "birth_date_coverage_by_basho.csv"
        write_birth_date_coverage_csv(rows, output)
        with output.open(newline="", encoding="utf-8") as stream:
            written = list(csv.DictReader(stream))
        if len(written) != len(rows):
            raise RuntimeError("Smoke-test CSV row count does not match the analysis")

        average_rows = average_age_by_division(
            history,
            load_bio_store(),
            exact_basho_start_dates(history),
        )
        if not average_rows or not all(
            row.banzuke_rikishi == row.exact_birth_date + row.missing_exact_birth_date
            for row in average_rows
        ):
            raise RuntimeError("Average-age rows are empty or do not reconcile")
        average_output = Path(temporary) / "average_age_by_division.csv"
        write_average_age_by_division_csv(average_rows, average_output)
        with average_output.open(newline="", encoding="utf-8") as stream:
            if len(list(csv.DictReader(stream))) != len(average_rows):
                raise RuntimeError("Average-age CSV row count does not match the analysis")

    print(f"PASS: {len(rows)} basho from {rows[0].basho} to {rows[-1].basho}")
    print(
        "Latest banzuke: "
        f"{rows[-1].banzuke_rikishi} rikishi; "
        f"{rows[-1].missing_exact_birth_date} without exact birth dates"
    )


if __name__ == "__main__":
    main()
