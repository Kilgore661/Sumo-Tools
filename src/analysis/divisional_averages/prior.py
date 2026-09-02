"""Load P1 and derive the fixed P2 divisional targets from it."""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import fmean

from src.sumo_core.Chii import Chii

from .division import division_name
from .model import DIVISIONS


def load_p1(path: Path) -> tuple[dict[Chii, float], dict[Chii, int]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"Empty P1 prior: {path}")
    ratings = {Chii.from_str(row["chii"]): float(row["rating"]) for row in rows}
    support = {
        Chii.from_str(row["chii"]): int(row["observations"])
        for row in rows
    }
    if len(ratings) != len(rows):
        raise ValueError(f"Duplicate chii in P1 prior: {path}")
    return ratings, support


def divisional_targets(p1: dict[Chii, float]) -> dict[str, float]:
    """Return unweighted literal-chii means, one for each P1 division."""

    grouped = {
        division: [rating for chii, rating in p1.items() if division_name(chii) == division]
        for division in DIVISIONS
    }
    missing = [division for division, ratings in grouped.items() if not ratings]
    if missing:
        raise ValueError(f"P1 has no chii for divisions: {', '.join(missing)}")
    return {division: fmean(grouped[division]) for division in DIVISIONS}

