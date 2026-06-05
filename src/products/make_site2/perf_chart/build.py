"""Build master data for the Career Comparisons performance chart."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.api import EqueloLookup, EqueloTiming
from src.infra.get_bios.make_public_shikona import make_public_shikona
from src.sumo_core.BasicPrimitives import RikId, Shikona
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
    equelo_lookup: EqueloLookup | None = None,
) -> MasterDataOutput:
    """Write all-rikishi career-comparison trajectory data and a size report."""

    output_root.mkdir(parents=True, exist_ok=True)
    resolved_lookup = equelo_lookup if equelo_lookup is not None else EqueloLookup.load(history)
    payload = build_master_payload(history=history, equelo_lookup=resolved_lookup)

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
    equelo_lookup: EqueloLookup,
) -> dict[str, object]:
    """Return compact all-rikishi trajectory rows keyed by rikishi id."""

    dates = tuple(sorted(history.keys()))
    return {
        "schema_version": 1,
        "columns": ("date", "shikona", "chii", "equelo"),
        "date_range": date_range(dates),
        "points_by_rikishi": make_js_input(
            history=history,
            dates=dates,
            equelo_lookup=equelo_lookup,
            public_shikona_by_rikid=make_public_shikona(history),
        ),
    }


def make_js_input(
    *,
    history: History,
    dates: tuple[Date, ...],
    equelo_lookup: EqueloLookup,
    public_shikona_by_rikid: dict[RikId, Shikona],
) -> dict[str, list[list[object]]]:
    """Return the browser trajectory input expected by Career Comparisons."""

    points_by_rikishi: dict[str, list[list[object]]] = {}

    for date in dates:
        basho = history(date)
        for rikishi_id in sorted(basho.banzuke.riks, key=int):
            chii = basho.banzuke.rikchii[rikishi_id]
            shikona = public_shikona_by_rikid[rikishi_id]
            rating = equelo_lookup.get_equelo(
                rikid=rikishi_id,
                date=date,
                when=EqueloTiming.BEFORE,
            )
            key = str(int(rikishi_id))
            points_by_rikishi.setdefault(key, []).append(
                [str(date), str(shikona), str(chii), rating]
            )

    return points_by_rikishi


def date_range(dates: tuple[Date, ...]) -> dict[str, str]:
    return {"start": str(dates[0]), "end": str(dates[-1])}


def build_size_report(*, payload: dict[str, object], data_bytes: bytes) -> dict[str, object]:
    points_by_rikishi = payload["points_by_rikishi"]
    point_counts = [len(points) for points in points_by_rikishi.values()]
    missing_equelo_count = sum(
        1
        for points in points_by_rikishi.values()
        for point in points
        if point[3] is None
    )
    return {
        "data_file": MASTER_DATA_FILE_NAME,
        "schema_version": payload["schema_version"],
        "rikishi_count": len(points_by_rikishi),
        "point_count": sum(point_counts),
        "missing_equelo_count": missing_equelo_count,
        "max_points_per_rikishi": max(point_counts),
        "raw_bytes": len(data_bytes),
        "gzip_bytes": len(gzip.compress(data_bytes)),
    }
