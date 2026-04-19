"""
Persistence and reporting for multiple-basho standings outputs.

Writes derived standings data to CSV files and manages run-specific output
folders so that each run can be reconstructed from its artefact location and
filename.

This module is responsible only for rendering/persistence and contains no
standings calculation logic.
"""

import csv
from datetime import datetime
from pathlib import Path

from src.analysis.standings.multiple_basho_view import MultipleBashoView
from .helpers import escape_date


OUTPUT_DIR = Path("files/output/standings")


def multiple_basho_run_output_dir(run_stamp: str) -> Path:
    return OUTPUT_DIR / run_stamp


def ensure_multiple_basho_run_output_dir(run_stamp: str) -> Path:
    out_dir = multiple_basho_run_output_dir(run_stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def new_run_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def default_multiple_basho_output_file(
    run_stamp: str,
    date,
    direction: str,
    num_basho: int,
    wins: str,
) -> Path:
    filename = (
        f"multiple basho standings view "
        f"({escape_date(date)}, {direction}, {num_basho}, {wins}).csv"
    )
    return multiple_basho_run_output_dir(run_stamp) / filename


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
                }
            )
