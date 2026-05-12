"""Write Basho Results Browser producer outputs."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from src.analysis.sumo_history.basho_results.classes import (
    BashoResultsIndex,
    BashoResultsRow,
)
from src.analysis.sumo_history.basho_results.dates import payload_file_name
from src.sumo_core.History import Date


OUTPUT_ROOT = Path("files/output/basho_results")
INDEX_FILE_NAME = "basho_results_index.json"

CSV_FIELDNAMES = (
    "basho",
    "division_id",
    "division_label",
    "rikishi_id",
    "shikona",
    "graph_shikona",
    "chii",
    "chii_ordinal",
    "score",
    "previous_delta_direction",
    "previous_delta",
    "previous_result",
    "previous_chii",
    "previous_chii_ordinal",
    "previous_equelo",
    "equelo",
    "delta_equelo",
    "nu_chii",
    "nu_chii_ordinal",
)


def write_index(index: BashoResultsIndex, output_root: Path = OUTPUT_ROOT) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / INDEX_FILE_NAME
    payload = {
        "schema": index.schema,
        "generated_at": index.generated_at,
        "default_basho": index.default_basho,
        "entries": [asdict(entry) for entry in index.entries],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_payload(
    date: Date,
    rows: tuple[BashoResultsRow, ...],
    output_root: Path = OUTPUT_ROOT,
) -> Path:
    payload_dir = output_root / "by-basho"
    payload_dir.mkdir(parents=True, exist_ok=True)
    path = payload_dir / payload_file_name(date)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    return path

