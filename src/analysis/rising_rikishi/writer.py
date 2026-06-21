"""CSV writing helpers for the rising-rikishi producer."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from src.analysis.rising_rikishi.model import RisingRow, RisingWindow
from src.sumo_core.History import Date


OUTPUT_ROOT = Path("files/output/analysis/rising_rikishi")


def date_file_label(date: Date) -> str:
    """Return the YYYY_MM label used in output filenames."""

    return f"{int(date.year):04d}_{int(date.month):02d}"


def output_path(output_root: Path, window: RisingWindow) -> Path:
    """Return the output path for one end-basho/window-size CSV."""

    filename = f"{date_file_label(window.end_basho)} {window.size:02d}.csv"
    return output_root / filename


def write_rows(rows: Iterable[RisingRow], path: Path) -> None:
    """Write rising-rikishi rows to a CSV file."""

    rows = tuple(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = tuple(RisingRow.__dataclass_fields__.keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
