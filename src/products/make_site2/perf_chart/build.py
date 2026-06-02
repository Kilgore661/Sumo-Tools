"""Build master data for the Career Comparisons performance chart."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path

from src.analysis.sumo_history.basho_results.ratings import RatingLookup
from src.sumo_core.History import Date, History


MASTER_DATA_FILE_NAME = "trajectory_master.json"
MASTER_REPORT_FILE_NAME = "trajectory_master_report.json"


@dataclass(frozen=True, kw_only=True)
class MasterDataOutput:
    data_path: Path
    report_path: Path


def write_master_data(
    *,
    history: History,
    output_root: Path,
    ratings: RatingLookup | None = None,
) -> MasterDataOutput:
    """Write all-rikishi career-comparison trajectory data and a size report."""

    output_root.mkdir(parents=True, exist_ok=True)
    resolved_ratings = ratings if ratings is not None else RatingLookup.load()
    payload = build_master_payload(history=history, ratings=resolved_ratings)

    data_path = output_root / MASTER_DATA_FILE_NAME
    data_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    data_path.write_bytes(data_bytes)

    report = build_size_report(payload=payload, data_bytes=data_bytes)
    report_path = output_root / MASTER_REPORT_FILE_NAME
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return MasterDataOutput(data_path=data_path, report_path=report_path)


def build_master_payload(
    *,
    history: History,
    ratings: RatingLookup,
) -> dict[str, object]:
    """Return compact all-rikishi trajectory rows keyed by rikishi id."""

    dates = tuple(sorted(history.keys()))
    points_by_rikishi: dict[str, list[list[object]]] = {}

    for index, date in enumerate(dates):
        previous_date = dates[index - 1] if index else None
        basho = history(date)
        for rikishi_id in sorted(basho.banzuke.riks, key=int):
            chii = basho.banzuke.rikchii[rikishi_id]
            shikona = basho.banzuke.rikshik[rikishi_id]
            rating = ratings.start_rating(
                history=history,
                previous_date=previous_date,
                rikishi_id=rikishi_id,
                chii=chii,
            )
            key = str(int(rikishi_id))
            points_by_rikishi.setdefault(key, []).append(
                [str(date), str(shikona), str(chii), float(rating)]
            )

    return {
        "schema_version": 1,
        "columns": ("date", "shikona", "chii", "equelo"),
        "date_range": date_range(dates),
        "points_by_rikishi": points_by_rikishi,
    }


def date_range(dates: tuple[Date, ...]) -> dict[str, str]:
    return {"start": str(dates[0]), "end": str(dates[-1])}


def build_size_report(*, payload: dict[str, object], data_bytes: bytes) -> dict[str, object]:
    points_by_rikishi = payload["points_by_rikishi"]
    point_counts = [len(points) for points in points_by_rikishi.values()]
    return {
        "data_file": MASTER_DATA_FILE_NAME,
        "schema_version": payload["schema_version"],
        "rikishi_count": len(points_by_rikishi),
        "point_count": sum(point_counts),
        "max_points_per_rikishi": max(point_counts),
        "raw_bytes": len(data_bytes),
        "gzip_bytes": len(gzip.compress(data_bytes)),
    }
