"""Validate and pack canonical Prospects outputs for make_site89."""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History
from src.analysis.prospects.eligibility import history_fingerprint

from .common import write_json


POINT_COLUMNS = (
    "basho", "date", "age", "exact_age", "division", "rank_number", "chii",
    "point_kind", "probability", "cohort_observations", "cohort_rikishi",
    "cohort_success", "cohort_failure", "cohort_unresolved",
    "cohort_resolved", "support_tier",
)
INTEGER_FIELDS = {
    "age", "rank_number", "cohort_observations", "cohort_rikishi",
    "cohort_success", "cohort_failure", "cohort_unresolved", "cohort_resolved",
}
FLOAT_FIELDS = {"exact_age", "probability"}


def produce_prospects_site_data(
    *, history: History, prospects_root: Path, output_root: Path
) -> tuple[Path, Path]:
    manifest_path = prospects_root / "manifest.json"
    points_path = prospects_root / "career_trajectory_points.csv"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dates = tuple(sorted(history))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported Prospects schema")
    if manifest.get("epoch") != str(dates[0]) or manifest.get("cutoff") != str(dates[-1]):
        raise ValueError("Prospects History scope does not match site89 production")
    if manifest.get("sources", {}).get("represented_history_sha256") != history_fingerprint(history):
        raise ValueError("Prospects History fingerprint does not match site89 production")

    grouped: dict[str, list[list[object]]] = {}
    with points_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            rikishi_id = row["rikishi_id"]
            grouped.setdefault(rikishi_id, []).append(
                [_value(field, row[field]) for field in POINT_COLUMNS]
            )

    names = FullShikonaStore.from_sources(history)
    names.assert_complete_for(RikId(int(rikishi_id)) for rikishi_id in grouped)
    rikishi = []
    for rikishi_id in sorted(grouped, key=int):
        points = grouped[rikishi_id]
        rikishi.append(
            {
                "id": int(rikishi_id),
                "shikona": str(names.full_shikona(RikId(int(rikishi_id)))),
                "first_basho": points[0][0],
                "last_basho": points[-1][0],
            }
        )
    payload = {
        "schema_version": 1,
        "source": {
            "analysis": "src.analysis.prospects",
            "epoch": manifest["epoch"],
            "cutoff": manifest["cutoff"],
            "sources": manifest.get("sources", {}),
        },
        "columns": POINT_COLUMNS,
        "rikishi": rikishi,
        "points_by_rikishi": grouped,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    data_path = output_root / "trajectory_master.json"
    data_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    data_path.write_bytes(data_bytes)
    all_points = [point for points in grouped.values() for point in points]
    kind_index = POINT_COLUMNS.index("point_kind")
    report_path = write_json(
        output_root / "trajectory_master_report.json",
        {
            "schema_version": 1,
            "data_file": data_path.name,
            "rikishi_count": len(grouped),
            "point_count": len(all_points),
            "attainment_count": sum(point[kind_index] == "sanyaku_attainment" for point in all_points),
            "max_points_per_rikishi": max((len(points) for points in grouped.values()), default=0),
            "raw_bytes": len(data_bytes),
            "gzip_bytes": len(gzip.compress(data_bytes)),
        },
    )
    return data_path, report_path


def _value(field: str, value: str) -> object:
    if value == "":
        return None
    if field in INTEGER_FIELDS:
        return int(value)
    if field in FLOAT_FIELDS:
        return float(value)
    return value
