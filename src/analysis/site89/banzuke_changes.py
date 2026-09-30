"""Publish Banzuke Changes with Elo-89 ratings in its established shape."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.analysis.elo_model_selection.model import rank_pair
from src.analysis.elo89.api import Elo89Artifacts
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .common import write_csv, write_json
from .shikona_annotations import banzuke_annotations


def produce_banzuke_changes(
    *,
    history: History,
    structural_source_root: Path,
    ratings: Elo89Artifacts,
    output_root: Path,
) -> tuple[Path, Path]:
    """Publish structural facts, Elo-89 ratings and current annotations."""

    config = json.loads(
        (structural_source_root / "site_config.json").read_text(encoding="utf-8")
    )
    date = config["current_date"]
    year, month = date.split("/", 1)
    history_date = Date.from_ints(int(year), int(month))
    if history_date not in history:
        raise ValueError(f"Banzuke Changes date {date} is not present in History")
    annotations = banzuke_annotations(history, history_date)
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
            annotation = annotations.get(RikId(int(rid))) if rid else None
            if annotation is None:
                row.update(
                    {
                        f"{side}_highest_chii": "false",
                        f"{side}_promotion_kind": "",
                        f"{side}_promotion_status": "",
                        f"{side}_promotion_required": "",
                        f"{side}_promotion_previous_result": "",
                    }
                )
            else:
                row.update(annotation.csv_fields(f"{side}_"))
        rows.append(row)
    fields = tuple(
        key.replace("_equelo", "_rating") for key in (source_rows[0] if source_rows else ())
    ) + tuple(
        f"{side}_{field}"
        for side in ("east", "west")
        for field in (
            "highest_chii",
            "promotion_kind",
            "promotion_status",
            "promotion_required",
            "promotion_previous_result",
        )
    )
    csv_path = write_csv(
        output_root / "data" / "banzuke_change_report.csv", rows, fields
    )
    config_path = write_json(output_root / "site_config.json", config)
    return config_path, csv_path
