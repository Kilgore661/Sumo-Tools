"""
Persistence and reporting for single-basho standings outputs.

Writes single-basho standings view data to external artefacts such as CSV
files, and manages run-specific output paths and convenience copies.

This module is responsible only for rendering/persistence and contains no
standings calculation logic.
"""

import csv
from pathlib import Path

from src.analysis.standings.config import OUTPUT_DIR
from src.analysis.standings.single_basho_view import SingleBashoStandingsView


SINGLE_BASHO_DIRNAME = "single_basho"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def single_basho_output_dir() -> Path:
    return OUTPUT_DIR / SINGLE_BASHO_DIRNAME


def single_basho_runs_dir() -> Path:
    return single_basho_output_dir() / "runs"


def single_basho_run_output_dir(run_stamp: str) -> Path:
    return single_basho_runs_dir() / run_stamp


def ensure_single_basho_run_output_dir(run_stamp: str) -> Path:
    out_dir = single_basho_run_output_dir(run_stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def single_basho_run_csv_file(
    run_stamp: str,
    date: str,
    wins: str,
) -> Path:
    filename = f"single basho standings view ({date}, {wins}).csv"
    return single_basho_run_output_dir(run_stamp) / filename


def single_basho_run_json_file(run_stamp: str) -> Path:
    return single_basho_run_output_dir(run_stamp) / "run.json"


def latest_single_basho_csv_file() -> Path:
    return OUTPUT_DIR / "single_basho_latest.csv"


def latest_single_basho_json_file() -> Path:
    return OUTPUT_DIR / "single_basho_latest_run.json"


def write_single_basho_standings_view_csv(
    view: SingleBashoStandingsView,
    output_file: Path,
) -> None:
    fieldnames = [
        "position",
        "rikishi_id",
        "shikona",
        "chii",
        "chii_ordinal",
        "real_wins",
        "all_wins",
        "bout_count",
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in view.rows:
            writer.writerow(
                {
                    "position": row.position,
                    "rikishi_id": int(row.rikishi_id),
                    "shikona": str(row.shikona),
                    "chii": row.chii,
                    "chii_ordinal": row.chii_ordinal,
                    "real_wins": row.real_wins,
                    "all_wins": row.all_wins,
                    "bout_count": row.bout_count,
                }
            )
