"""Publish Banzuke Changes with Elo-89 ratings in its established shape."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.analysis.elo_model_selection.model import rank_pair
from src.analysis.elo89.api import Elo89Artifacts
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
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
    with (structural_source_root / "data" / "banzuke_change_report.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        source_rows = tuple(csv.DictReader(stream))
    date = config["current_date"]
    history_date = _date(date)
    if history_date in history:
        annotations = banzuke_annotations(history, history_date)
    else:
        latest_history_date = max(history)
        previous_date = _date(config["previous_date"])
        if history_date <= latest_history_date or previous_date != latest_history_date:
            raise ValueError(
                "Banzuke Changes date is not the published successor to History: "
                f"current={date}, previous={config['previous_date']}, "
                f"History ends={latest_history_date}"
            )
        annotations = banzuke_annotations(
            history,
            history_date,
            banzuke=_banzuke_from_rows(source_rows),
        )
    snapshot_date = max(candidate for candidate in ratings.basho_end_ratings if candidate < date)
    snapshot = ratings.basho_end_ratings[snapshot_date]
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


def _date(value: str) -> Date:
    year, month = value.split("/", 1)
    return Date.from_ints(int(year), int(month))


def _banzuke_from_rows(rows: tuple[dict[str, str], ...]) -> Banzuke:
    """Reconstruct the published current banzuke carried by the BCR artifact."""

    ranks: dict[RikId, Chii] = {}
    shikona: dict[RikId, Shikona] = {}
    for row in rows:
        for side in ("east", "west"):
            raw_rid = row.get(f"{side}_rikishi_id", "")
            raw_chii = row.get(f"{side}_chii", "")
            raw_shikona = row.get(f"{side}_shikona", "")
            if not raw_rid and not raw_chii and not raw_shikona:
                continue
            if not raw_rid or not raw_chii or not raw_shikona:
                raise ValueError(
                    f"Incomplete {side} banzuke identity in Banzuke Changes row"
                )
            rikishi_id = RikId(int(raw_rid))
            rank = Chii.from_str(raw_chii)
            name = Shikona(raw_shikona)
            if rikishi_id in ranks and (
                ranks[rikishi_id] != rank or shikona[rikishi_id] != name
            ):
                raise ValueError(
                    f"Conflicting Banzuke Changes rows for rikishi {rikishi_id}"
                )
            ranks[rikishi_id] = rank
            shikona[rikishi_id] = name
    if not ranks:
        raise ValueError("Banzuke Changes report contains no current banzuke")
    return Banzuke(
        riks=Riks(ranks),
        rikchii=RikChii(ranks),
        rikshik=RikShikona(shikona),
    )
