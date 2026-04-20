"""
Persistence and reporting for multiple-basho derived standings outputs.

Writes multiple-basho derived results to external artefacts such as CSV files,
and manages run-specific output paths and convenience copies.

This module is responsible only for rendering/persistence and contains no core
or derived standings calculation logic.
"""

import csv
from pathlib import Path

from src.analysis.standings.config import OUTPUT_DIR
from src.analysis.standings.multiple_basho_view import MultipleBashoView


MULTIPLE_BASHO_DIRNAME = "multiple_basho"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def multiple_basho_output_dir() -> Path:
    return OUTPUT_DIR / MULTIPLE_BASHO_DIRNAME


def multiple_basho_runs_dir() -> Path:
    return multiple_basho_output_dir() / "runs"


def multiple_basho_run_output_dir(run_stamp: str) -> Path:
    return multiple_basho_runs_dir() / run_stamp


def ensure_multiple_basho_run_output_dir(run_stamp: str) -> Path:
    out_dir = multiple_basho_run_output_dir(run_stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def multiple_basho_run_csv_file(
    run_stamp: str,
    date: str,
    direction: str,
    num_basho: int,
    wins: str,
) -> Path:
    filename = f"multiple basho standings view ({date}, {direction}, {num_basho}, {wins}).csv"
    return multiple_basho_run_output_dir(run_stamp) / filename


def multiple_basho_run_json_file(run_stamp: str) -> Path:
    return multiple_basho_run_output_dir(run_stamp) / "run.json"


def latest_multiple_basho_csv_file() -> Path:
    return OUTPUT_DIR / "multiple_basho_latest.csv"


def latest_multiple_basho_json_file() -> Path:
    return OUTPUT_DIR / "multiple_basho_latest_run.json"


def write_multiple_basho_view_csv(
    view: MultipleBashoView,
    output_file: Path,
) -> None:
    fieldnames = [
        "position",
        "rikishi_id",
        "shikona",
        "chii",
        "chii_ordinal",
        "fought_wins",
        "credited_wins",
        "bout_count",
        "selected_basho_count",
        "containing_basho_count",
        "selected_expected_bout_count",
        "selected_available_bout_count",
        "containing_expected_bout_count",
        "containing_available_bout_count",
        "selected_average_fought_wins",
        "selected_average_credited_wins",
        "containing_average_fought_wins",
        "containing_average_credited_wins",
        "selected_stdev_fought_wins",
        "selected_stdev_credited_wins",
        "containing_stdev_fought_wins",
        "containing_stdev_credited_wins",
        "selected_sem_fought_wins",
        "selected_sem_credited_wins",
        "containing_sem_fought_wins",
        "containing_sem_credited_wins",
        "selected_ci95_half_width_fought_wins",
        "selected_ci95_half_width_credited_wins",
        "containing_ci95_half_width_fought_wins",
        "containing_ci95_half_width_credited_wins",
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
                    "fought_wins": row.fought_wins,
                    "credited_wins": row.credited_wins,
                    "bout_count": row.bout_count,
                    "selected_basho_count": row.selected_basho_count,
                    "containing_basho_count": row.containing_basho_count,
                    "selected_expected_bout_count": row.selected_expected_bout_count,
                    "selected_available_bout_count": row.selected_available_bout_count,
                    "containing_expected_bout_count": row.containing_expected_bout_count,
                    "containing_available_bout_count": row.containing_available_bout_count,
                    "selected_average_fought_wins": row.selected_average_fought_wins,
                    "selected_average_credited_wins": row.selected_average_credited_wins,
                    "containing_average_fought_wins": row.containing_average_fought_wins,
                    "containing_average_credited_wins": row.containing_average_credited_wins,
                    "selected_stdev_fought_wins": row.selected_stdev_fought_wins,
                    "selected_stdev_credited_wins": row.selected_stdev_credited_wins,
                    "containing_stdev_fought_wins": row.containing_stdev_fought_wins,
                    "containing_stdev_credited_wins": row.containing_stdev_credited_wins,
                    "selected_sem_fought_wins": row.selected_sem_fought_wins,
                    "selected_sem_credited_wins": row.selected_sem_credited_wins,
                    "containing_sem_fought_wins": row.containing_sem_fought_wins,
                    "containing_sem_credited_wins": row.containing_sem_credited_wins,
                    "selected_ci95_half_width_fought_wins": row.selected_ci95_half_width_fought_wins,
                    "selected_ci95_half_width_credited_wins": row.selected_ci95_half_width_credited_wins,
                    "containing_ci95_half_width_fought_wins": row.containing_ci95_half_width_fought_wins,
                    "containing_ci95_half_width_credited_wins": row.containing_ci95_half_width_credited_wins,
                }
            )
