"""CSV and metadata output for clean Elo simulations."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.sumo_core.History import History

from .simulate import SimulationResult


@dataclass(frozen=True)
class OutputPaths:
    base_output_root: Path
    output_root: Path
    basho_directory: Path
    manifest_json: Path
    basho_csvs: tuple[Path, ...]


def write_outputs(
    *,
    result: SimulationResult,
    history: History,
    output_root: Path,
    start_date,
    q: float,
    count_absences: bool,
    initial_policy_metadata: dict[str, object],
    k_policy_metadata: dict[str, object],
) -> OutputPaths:
    base_root = Path(output_root)
    generated_at, root = _create_run_directory(base_root)
    basho_directory = root / "basho"
    basho_directory.mkdir()

    basho_csvs = tuple(
        _write_basho_csv(
            path=basho_directory / f"{int(date.year):04d}_{int(date.month):02d}.csv",
            date=date,
            snapshot=snapshot,
            history=history,
            count_absences=count_absences,
        )
        for date, snapshot in sorted(result.basho_ratings.items())
    )

    manifest_path = _write_manifest(
        root / "manifest.json",
        result=result,
        start_date=start_date,
        q=q,
        count_absences=count_absences,
        initial_policy_metadata=initial_policy_metadata,
        k_policy_metadata=k_policy_metadata,
        basho_csvs=basho_csvs,
        generated_at=generated_at,
        base_output_root=base_root,
        run_directory=root,
    )
    return OutputPaths(
        base_output_root=base_root,
        output_root=root,
        basho_directory=basho_directory,
        manifest_json=manifest_path,
        basho_csvs=basho_csvs,
    )


def _write_basho_csv(
    *,
    path: Path,
    date,
    snapshot,
    history: History,
    count_absences: bool,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    banzuke = history[date].banzuke
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = [
            "rikid",
            "shikona",
            "chii",
            "chii_ordinal",
            "initial_rating_before_normalisation",
            "initial_rating_after_normalisation",
            "final_rating",
        ]
        if count_absences:
            header.extend(
                [
                    "recorded_appearances",
                    "expected_appearances",
                    "inferred_absences",
                    "raw_absence_rating_adjustment",
                ]
            )
        header.extend(
            [
                "initial_normalisation_adjustment",
                "final_normalisation_adjustment",
            ]
        )
        writer.writerow(header)
        for rikid in sorted(snapshot.final_ratings):
            shikona = banzuke.rikshik.get(rikid)
            chii = banzuke.rikchii.get(rikid)
            row = [
                int(rikid),
                "" if shikona is None else str(shikona),
                "" if chii is None else str(chii),
                "" if chii is None else chii.ordinal(),
                _number(snapshot.initial_before_normalisation[rikid]),
                _number(snapshot.initial_after_normalisation[rikid]),
                _number(snapshot.final_ratings[rikid]),
            ]
            if count_absences:
                row.extend(
                    [
                    snapshot.recorded_appearances[rikid],
                    snapshot.expected_appearances[rikid],
                    snapshot.inferred_absences[rikid],
                    _number(snapshot.absence_rating_adjustments[rikid]),
                    ]
                )
            row.extend(
                [
                    _number(snapshot.initial_normalisation_adjustment),
                    _number(snapshot.final_normalisation_adjustment),
                ]
            )
            writer.writerow(row)
    return path


def _write_manifest(
    path: Path,
    *,
    result: SimulationResult,
    start_date,
    q: float,
    count_absences: bool,
    initial_policy_metadata: dict[str, object],
    k_policy_metadata: dict[str, object],
    basho_csvs: tuple[Path, ...],
    generated_at: datetime,
    base_output_root: Path,
    run_directory: Path,
) -> Path:
    payload = {
        "model": "clean_elo",
        "generated_at": generated_at.isoformat(),
        "base_output_root": str(base_output_root),
        "run_directory": str(run_directory),
        "start_date": str(start_date),
        "target_mean": result.target_mean,
        "q": q,
        "count_absences": count_absences,
        "initial_rating_policy": initial_policy_metadata,
        "k_policy": k_policy_metadata,
        "rated_bout_count": result.rated_bout_count,
        "ignored_fusen_count": result.ignored_fusen_count,
        "inferred_absence_count": result.inferred_absence_count,
        "basho_csvs": [str(item) for item in basho_csvs],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _number(value: float) -> str:
    return f"{value:.12f}"


def _create_run_directory(base_root: Path) -> tuple[datetime, Path]:
    base_root.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    while True:
        run_id = generated_at.strftime("%Y-%m-%d_%H-%M-%S")
        run_directory = base_root / run_id
        try:
            run_directory.mkdir()
        except FileExistsError:
            generated_at += timedelta(seconds=1)
            continue
        return generated_at, run_directory
