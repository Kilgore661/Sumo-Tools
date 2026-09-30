"""Persist torikumi-prediction observations, aggregates and diagnostics."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from .model import AnalysisResult, OutputPaths
from .model import (
    ClassDayRow,
    ClassDayWinsRow,
    ClassRecordRow,
    Diagnostic,
    Observation,
    OverallClassRow,
)


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/torikumi_prediction")


def write_outputs(
    result: AnalysisResult,
    *,
    source: dict[str, str],
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    generated_at: datetime | None = None,
) -> OutputPaths:
    """Write one immutable timestamped analysis run."""

    timestamp, run_directory = _create_run_directory(output_root, generated_at)
    outputs = OutputPaths(
        run_directory=run_directory,
        observations_csv=run_directory / "observations.csv",
        class_by_day_csv=run_directory / "class_by_day.csv",
        class_by_day_wins_csv=run_directory / "class_by_day_wins.csv",
        class_by_record_csv=run_directory / "class_by_record.csv",
        overall_class_csv=run_directory / "overall_class.csv",
        diagnostics_csv=run_directory / "diagnostics.csv",
        manifest_json=run_directory / "manifest.json",
    )
    _write_dataclass_csv(result.observations, outputs.observations_csv, fields(Observation))
    _write_dataclass_csv(result.class_by_day, outputs.class_by_day_csv, fields(ClassDayRow))
    _write_dataclass_csv(
        result.class_by_day_wins, outputs.class_by_day_wins_csv,
        fields(ClassDayWinsRow),
    )
    _write_dataclass_csv(
        result.class_by_record, outputs.class_by_record_csv,
        fields(ClassRecordRow),
    )
    _write_dataclass_csv(result.overall_class, outputs.overall_class_csv, fields(OverallClassRow))
    _write_dataclass_csv(
        result.diagnostics,
        outputs.diagnostics_csv,
        fields(Diagnostic),
    )

    diagnostic_counts = Counter(row.kind for row in result.diagnostics)
    division_counts = Counter(row.focal_division for row in result.observations)
    manifest = {
        "analysis": "torikumi_prediction",
        "status": "complete",
        "generated_at_utc": timestamp.isoformat(),
        "source": source,
        "history": {
            "selected_first_basho": result.history_first_basho,
            "selected_last_basho": result.history_last_basho,
            "selected_basho_count": result.history_basho_count,
            "included_first_basho": result.included_first_basho,
            "included_last_basho": result.included_last_basho,
            "included_completed_basho_count": result.included_basho_count,
            "excluded_incomplete_basho_count": result.excluded_incomplete_basho_count,
        },
        "contracts": {
            "observation": "one ranked focal endpoint of a scheduled regular bout",
            "class": "side/annotation removed; Y/O/S/K pooled; other levels retain number",
            "record": "official W+FS and L+FP results on earlier days",
            "weighting": "each scheduled ranked focal endpoint has equal weight",
            "missing_opponent_chii": "retained as opponent class Mz",
        },
        "counts": {
            "scheduled_bouts": result.scheduled_bout_count,
            "observations": len(result.observations),
            "observations_by_division": dict(sorted(division_counts.items())),
            "cross_division_observations": sum(row.cross_division for row in result.observations),
            "fusen_observations": sum(row.fusen for row in result.observations),
            "diagnostics": len(result.diagnostics),
            "diagnostics_by_kind": dict(sorted(diagnostic_counts.items())),
        },
        "outputs": {
            field: getattr(outputs, field).name
            for field in outputs.__dataclass_fields__
            if field != "run_directory"
        },
    }
    outputs.manifest_json.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return outputs


def _write_dataclass_csv(
    rows: Iterable[object],
    path: Path,
    dataclass_fields,
) -> None:
    rows = tuple(rows)
    field_names = [field.name for field in dataclass_fields]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _create_run_directory(
    output_root: Path, generated_at: datetime | None
) -> tuple[datetime, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = (generated_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    timestamp = timestamp.replace(microsecond=0)
    while True:
        run_directory = output_root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory
