"""Shared publication helpers for the Elo-89 site-data producers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fieldnames=None) -> Path:
    materialised = tuple(rows)
    if fieldnames is None:
        if not materialised:
            raise ValueError(f"Cannot infer columns for empty CSV: {path}")
        fieldnames = tuple(materialised[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(fieldnames))
        writer.writeheader()
        writer.writerows(materialised)
    return path


def write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def rating_text(value: float | None) -> str:
    return "-" if value is None else f"{value:.0f}"


def delta_text(value: float | None) -> str:
    return "-" if value is None else f"{value:+.0f}"
