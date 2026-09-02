"""Publish Elo-89's P1 rank-pair prior as public rating landmarks."""

from __future__ import annotations

from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts

from .common import write_csv


def produce_typical_rating_values(*, ratings: Elo89Artifacts, output_root: Path) -> Path:
    groups = (
        ("Sanyaku", ((label, f"{label}1") for label in ("Y", "O", "S", "K"))),
        ("Maegashira", ((f"M{number}", f"M{number}") for number in range(1, 18))),
        ("Other", ((label, label) for label in ("J1", "Ms1", "Sd1", "Jd1", "Jd100"))),
    )
    rows = []
    for table_order, (table, labels) in enumerate(groups, start=1):
        for row_order, (label, pair) in enumerate(labels, start=1):
            if pair not in ratings.prior:
                raise ValueError(f"Elo-89 P1 prior has no public landmark for {pair}")
            rows.append(
                {
                    "table": table,
                    "table_order": table_order,
                    "row_order": row_order,
                    "label": label,
                    "rating": round(ratings.prior[pair]),
                    "support_count": 1,
                    "support_chii": pair,
                    "policy": "canonical paired P1 entrant rating",
                }
            )
    return write_csv(output_root / "typical_rating_values.csv", rows)
