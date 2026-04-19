"""
Persistence and reporting for multiple-basho derived standings outputs.

Writes multiple-basho derived results to external artefacts such as CSV files
and manages run-specific output paths.

This module is responsible only for rendering/persistence and contains no core
or derived standings calculation logic.
"""

import csv
from pathlib import Path

from src.analysis.standings.config import OUTPUT_DIR
from src.analysis.standings.multiple_basho_view import MultipleBashoView


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_output_dir(run_stamp: str) -> Path:
    return OUTPUT_DIR / run_stamp


def ensure_run_output_dir(run_stamp: str) -> Path:
    out_dir = run_output_dir(run_stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def multiple_basho_run_file(
    run_stamp: str,
    date: str,
    direction: str,
    num_basho: int,
    wins: str,
) -> Path:
    filename = f"multiple basho standings view ({date}, {direction}, {num_basho}, {wins}).csv"
    return run_output_dir(run_stamp) / filename


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
        "real_wins",
        "all_wins",
        "bout_count",
        "selected_basho_count",
        "basho_present_count",
        "window_average_real_wins",
        "window_average_all_wins",
        "presence_average_real_wins",
        "presence_average_all_wins",
        "window_stdev_real_wins",
        "window_stdev_all_wins",
        "presence_stdev_real_wins",
        "presence_stdev_all_wins",
        "window_sem_real_wins",
        "window_sem_all_wins",
        "presence_sem_real_wins",
        "presence_sem_all_wins",
        "window_ci95_half_width_real_wins",
        "window_ci95_half_width_all_wins",
        "presence_ci95_half_width_real_wins",
        "presence_ci95_half_width_all_wins",
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
                    "selected_basho_count": row.selected_basho_count,
                    "basho_present_count": row.basho_present_count,
                    "window_average_real_wins": row.window_average_real_wins,
                    "window_average_all_wins": row.window_average_all_wins,
                    "presence_average_real_wins": row.presence_average_real_wins,
                    "presence_average_all_wins": row.presence_average_all_wins,
                    "window_stdev_real_wins": row.window_stdev_real_wins,
                    "window_stdev_all_wins": row.window_stdev_all_wins,
                    "presence_stdev_real_wins": row.presence_stdev_real_wins,
                    "presence_stdev_all_wins": row.presence_stdev_all_wins,
                    "window_sem_real_wins": row.window_sem_real_wins,
                    "window_sem_all_wins": row.window_sem_all_wins,
                    "presence_sem_real_wins": row.presence_sem_real_wins,
                    "presence_sem_all_wins": row.presence_sem_all_wins,
                    "window_ci95_half_width_real_wins": row.window_ci95_half_width_real_wins,
                    "window_ci95_half_width_all_wins": row.window_ci95_half_width_all_wins,
                    "presence_ci95_half_width_real_wins": row.presence_ci95_half_width_real_wins,
                    "presence_ci95_half_width_all_wins": row.presence_ci95_half_width_all_wins,
                }
            )
