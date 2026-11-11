"""CSV output for CPR analysis."""

from __future__ import annotations

import csv
import math
from dataclasses import fields
from pathlib import Path
from typing import Iterable

from .model import CPRRow


def write_csv(rows: Iterable[CPRRow], path: Path) -> Path:
    """Write CPR rows with explicit extended-real and N/A values."""

    materialised = tuple(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = tuple(field.name for field in fields(CPRRow))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in materialised:
            writer.writerow(
                {
                    name: _format(getattr(row, name))
                    for name in fieldnames
                }
            )
    return path


def _format(value: object) -> object:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        if value == math.inf:
            return "+inf"
        if value == -math.inf:
            return "-inf"
        return f"{value:.12f}"
    return value
