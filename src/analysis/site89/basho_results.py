"""Produce Basho Results Browser files from post-1988 History and Elo-89."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.analysis.banzuke_compare.banzuke_diff import (
    calculate_local_deltas,
    division_for_chii,
    rank_level_movement_marker,
)
from src.analysis.banzuke_compare.report_view import format_delta as format_banzuke_delta
from src.analysis.banzuke_compare.shikona_links import graph_shikona_for
from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.sumo_history.basho_results.build import DIVISION_IDS, DIVISION_LABELS
from src.analysis.sumo_history.basho_results.dates import (
    basho_label,
    next_history_date,
    payload_file_name,
    previous_represented_date,
    represented_dates,
    status_for_date,
)
from src.analysis.sumo_history.basho_results.records import format_result_with_prizes
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.History import History

from .common import delta_text, rating_text, write_csv, write_json
from .shikona_annotations import current_basho_annotations


FIELDS = (
    "basho", "division_id", "division_label", "rikishi_id", "shikona",
    "graph_shikona", "chii", "chii_ordinal", "score",
    "previous_delta_direction", "previous_delta", "previous_result",
    "previous_rank_level_movement", "previous_chii", "previous_chii_ordinal",
    "previous_rating", "rating", "rating_delta", "nu_chii", "nu_chii_ordinal",
    "highest_chii", "promotion_kind", "promotion_status", "promotion_required",
    "promotion_previous_result",
)


def produce_basho_results(
    *, history: History, ratings: Elo89Artifacts, output_root: Path
) -> tuple[Path, ...]:
    dates = represented_dates(history)
    names = FullShikonaStore.from_sources(history)
    entries = []
    paths = []
    for date in dates:
        rows = _rows(history, date, ratings, names)
        paths.append(write_csv(output_root / "by-basho" / payload_file_name(date), rows, FIELDS))
        entries.append(
            {
                "basho": str(date),
                "year": int(date.year),
                "month": int(date.month),
                "label": basho_label(date),
                "status": status_for_date(history, dates, date),
                "latest_day": int(history(date).summary.last_defined()),
                "payload_path": f"data/by-basho/{payload_file_name(date)}",
            }
        )
    index = write_json(
        output_root / "basho_results_index.json",
        {
            "schema": "sumo-tools.basho-results.index.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "default_basho": "" if not entries else entries[-1]["basho"],
            "entries": entries,
        },
    )
    return (index, *paths)


def _rows(history, date, ratings, names):
    dates = represented_dates(history)
    previous_date = previous_represented_date(dates, date)
    next_date = next_history_date(history, date)
    current = history(date)
    previous = None if previous_date is None else history(previous_date)
    following = None if next_date is None else history(next_date)
    deltas = {} if previous is None else calculate_local_deltas(previous.banzuke, current.banzuke)
    annotations = current_basho_annotations(history, date)
    rows = []
    for rid in sorted(current.banzuke.riks, key=lambda value: current.banzuke.get_chii(value)):
        chii = current.banzuke.get_chii(rid)
        old_chii = previous.banzuke.rikchii.get(rid) if previous is not None else None
        new_chii = following.banzuke.rikchii.get(rid) if following is not None else None
        start = ratings.start_rating(date, rid)
        end = ratings.end_rating(date, rid)
        movement = deltas.get(rid)
        shikona = names.full_shikona(rid)
        row = {
                "basho": str(date),
                "division_id": DIVISION_IDS[division_for_chii(chii)],
                "division_label": DIVISION_LABELS[division_for_chii(chii)],
                "rikishi_id": str(int(rid)),
                "shikona": shikona,
                "graph_shikona": graph_shikona_for(rid, shikona),
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "score": format_result_with_prizes(rid, chii, current.summary),
                "previous_delta_direction": "-" if movement is None else "↑" if movement > 0 else "↓" if movement < 0 else "",
                "previous_delta": "-" if movement is None else format_banzuke_delta(movement),
                "previous_result": "-" if previous is None or old_chii is None else format_result_with_prizes(rid, old_chii, previous.summary),
                "previous_rank_level_movement": rank_level_movement_marker(old_chii, chii),
                "previous_chii": "-" if old_chii is None else str(old_chii),
                "previous_chii_ordinal": "-" if old_chii is None else old_chii.ordinal(),
                "previous_rating": rating_text(start),
                "rating": rating_text(end),
                "rating_delta": delta_text(None if start is None or end is None else end - start),
                "nu_chii": "-" if new_chii is None else str(new_chii),
                "nu_chii_ordinal": "-" if new_chii is None else new_chii.ordinal(),
            }
        annotation = annotations.get(rid)
        row.update(
            annotation.csv_fields() if annotation is not None else {
                "highest_chii": "false",
                "promotion_kind": "",
                "promotion_status": "",
                "promotion_required": "",
                "promotion_previous_result": "",
            }
        )
        rows.append(row)
    return rows
