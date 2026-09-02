"""Produce the Career Comparisons trajectory contract from Elo-89."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.History import History

from .common import write_json


def produce_career_comparisons(
    *, history: History, ratings: Elo89Artifacts, output_root: Path
) -> tuple[Path, Path]:
    dates = tuple(sorted(history))
    names = FullShikonaStore.from_sources(history)
    names.assert_complete_for(
        rikishi for date in dates for rikishi in history(date).banzuke.riks
    )
    points: dict[str, list[list[object]]] = {}
    for date in dates:
        state = history(date)
        for rikishi in sorted(state.banzuke.riks, key=int):
            points.setdefault(str(int(rikishi)), []).append(
                [
                    str(date),
                    str(names.full_shikona(rikishi)),
                    str(state.banzuke.get_chii(rikishi)),
                    ratings.start_rating(date, rikishi),
                ]
            )
    payload = {
        "schema_version": 1,
        "columns": ("date", "shikona", "chii", "rating"),
        "date_range": {"start": str(dates[0]), "end": str(dates[-1])},
        "points_by_rikishi": points,
    }
    data_path = output_root / "trajectory_master.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    data_path.write_bytes(data_bytes)
    counts = [len(value) for value in points.values()]
    report_path = write_json(
        output_root / "trajectory_master_report.json",
        {
            "data_file": data_path.name,
            "schema_version": 1,
            "rikishi_count": len(points),
            "point_count": sum(counts),
            "missing_rating_count": sum(
                point[3] is None for values in points.values() for point in values
            ),
            "max_points_per_rikishi": max(counts, default=0),
            "raw_bytes": len(data_bytes),
            "gzip_bytes": len(gzip.compress(data_bytes)),
        },
    )
    return data_path, report_path
