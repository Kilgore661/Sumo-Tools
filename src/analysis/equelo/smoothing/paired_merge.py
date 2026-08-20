"""Pair east and west values in a persisted boundary-merge dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .paired_merge_chart import write_paired_merge_chart


RATING_COLUMNS = (
    "mj_resolved_rating",
    "aligned_lower_resolved_rating",
    "pre_smoothing_rating",
)


@dataclass(frozen=True)
class PairedMergeOutputs:
    data_csv: Path
    metadata_json: Path
    chart_html: Path


def build_paired_merge(
    source_csv: Path,
    output_csv: Path,
) -> PairedMergeOutputs:
    """Write paired merged data and render it without changing values."""

    with source_csv.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    if not source_rows:
        raise ValueError(f"Boundary-merge CSV contains no rows: {source_csv}")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    order: list[str] = []
    for row in source_rows:
        pair = _pair_label(row["chii"])
        if pair not in grouped:
            order.append(pair)
        grouped[pair].append(row)

    rows = []
    for pair in order:
        members = grouped[pair]
        rows.append({
            "rank_pair": pair,
            "division": members[0]["division"],
            "member_chii": " | ".join(row["chii"] for row in members),
            "member_count": len(members),
            **{
                column: _mean_available(row[column] for row in members)
                for column in RATING_COLUMNS
            },
            "source": " | ".join(dict.fromkeys(row["source"] for row in members)),
        })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    chart_html = write_paired_merge_chart(output_csv)
    metadata_json = output_csv.with_suffix(".metadata.json")
    metadata_json.write_text(json.dumps({
        "kind": "equelo_paired_boundary_merge_candidate",
        "generated_at": datetime.now().astimezone().isoformat(),
        "input": _file_reference(source_csv),
        "pairing": {
            "key": "literal chii with terminal east/west side removed",
            "aggregation": "unweighted mean of available east/west values",
            "missing_policy": "one available side is retained; no available side remains blank",
            "smoothing_applied": False,
        },
        "outputs": {
            "data_csv": _file_reference(output_csv),
            "chart_html": _file_reference(chart_html),
            "row_count": len(rows),
        },
    }, indent=2), encoding="utf-8")
    return PairedMergeOutputs(output_csv, metadata_json, chart_html)


def _pair_label(chii: str) -> str:
    return chii[:-1] if chii.endswith(("e", "w")) else chii


def _mean_available(values) -> float | None:
    available = [float(value) for value in values if value != ""]
    return sum(available) / len(available) if available else None


def _file_reference(path: Path) -> dict[str, object]:
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = build_paired_merge(args.source_csv, args.output_csv)
    print(f"Data: {outputs.data_csv}")
    print(f"Metadata: {outputs.metadata_json}")
    print(f"Chart: {outputs.chart_html}")


if __name__ == "__main__":
    main()
