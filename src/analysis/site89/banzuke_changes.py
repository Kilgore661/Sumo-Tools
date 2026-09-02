"""Publish Banzuke Changes with Elo-89 ratings in its established shape."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.analysis.elo_model_selection.model import rank_pair
from src.analysis.elo89.api import Elo89Artifacts
from src.sumo_core.Chii import Chii

from .common import write_csv, write_json


def produce_banzuke_changes(
    *, structural_source_root: Path, ratings: Elo89Artifacts, output_root: Path
) -> tuple[Path, Path]:
    """Replace the legacy report's rating columns; all other fields are neutral facts."""

    config = json.loads((structural_source_root / "site_config.json").read_text(encoding="utf-8"))
    date = config["current_date"]
    snapshot_date = max(candidate for candidate in ratings.basho_end_ratings if candidate < date)
    snapshot = ratings.basho_end_ratings[snapshot_date]
    with (structural_source_root / "data" / "banzuke_change_report.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        source_rows = tuple(csv.DictReader(stream))
    rows = []
    for source in source_rows:
        row = {
            key.replace("_equelo", "_rating"): value
            for key, value in source.items()
            if not key.endswith("_equelo")
        }
        for side in ("east", "west"):
            rid = source.get(f"{side}_rikishi_id", "")
            chii = source.get(f"{side}_chii", "")
            if not rid or not chii:
                value = None
            else:
                value = snapshot.get(rid)
                if value is None:
                    value = ratings.prior.get(rank_pair(Chii.from_str(chii)))
            row[f"{side}_rating"] = "" if value is None else f"{value:.0f}"
        rows.append(row)
    fields = tuple(
        key.replace("_equelo", "_rating") for key in (source_rows[0] if source_rows else ())
    )
    csv_path = write_csv(
        output_root / "data" / "banzuke_change_report.csv", rows, fields
    )
    config_path = write_json(output_root / "site_config.json", config)
    return config_path, csv_path
