from __future__ import annotations

import csv
from pathlib import Path

from .metrics import MetricsRow


def write_ratings_table(path: Path, rows: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = ["event", *[f"player_{index}" for index in range(len(rows[0]))]]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for iteration, ratings in enumerate(rows):
            writer.writerow([iteration, *[f"{rating:.6f}" for rating in ratings]])


def write_metrics_table(path: Path, rows: list[MetricsRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "event",
        "mean_gap_rmse",
        "sample_gap_rmse",
        "mean_gap_rmse_slope",
        "stable_now",
        "stable_window_met",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "event": row["event"],
                    "mean_gap_rmse": f"{float(row['mean_gap_rmse']):.6f}",
                    "sample_gap_rmse": f"{float(row['sample_gap_rmse']):.6f}",
                    "mean_gap_rmse_slope": f"{float(row['mean_gap_rmse_slope']):.6f}",
                    "stable_now": int(bool(row["stable_now"])),
                    "stable_window_met": int(bool(row["stable_window_met"])),
                }
            )
