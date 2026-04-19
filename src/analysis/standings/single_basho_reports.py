"""
Persistence and reporting for single-basho standings outputs.

Writes standings view data to external artefacts such as CSV files.

This module is responsible only for rendering/persistence and contains no
standings calculation logic.
"""

import csv
from pathlib import Path

from src.analysis.standings.single_basho_view import SingleBashoStandingsView


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
