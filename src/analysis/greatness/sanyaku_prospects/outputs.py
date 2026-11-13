from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .model import OutputPaths, Population


def write_bundle(
    *,
    output_root: Path,
    population: Population,
    coverage,
    observations,
    debut_probabilities,
    state_probabilities,
    source_manifest: dict[str, str],
) -> OutputPaths:
    output_root.mkdir(parents=True, exist_ok=True)
    paths = OutputPaths(
        root=output_root,
        population_summary=output_root / "population_summary.csv",
        population_exclusions=output_root / "population_exclusions.csv",
        basho_date_coverage=output_root / "basho_date_coverage.csv",
        cohort_observations=output_root / "cohort_observations.csv",
        outcome_summary=output_root / "outcome_summary.csv",
        debut_probabilities=output_root / "probability_by_division_debut_age.csv",
        state_probabilities=output_root / "probability_by_division_state_age.csv",
        manifest=output_root / "manifest.json",
    )
    exclusion_counts = Counter(row.reason for row in population.exclusions)
    debut_ids = {row.rikishi_id for row in observations if row.cohort_type == "division_debut"}
    state_ids = {row.rikishi_id for row in observations if row.cohort_type == "division_state"}
    summary = (
        ("history_rikishi", len(population.history_ids)),
        ("boundary_incumbents", len(population.boundary_ids)),
        ("complete_record_rikishi", len(population.complete_ids)),
        ("complete_records_with_bio", len(population.complete_ids) - exclusion_counts["missing_bio"]),
        ("complete_records_missing_bio", exclusion_counts["missing_bio"]),
        ("complete_records_with_birth_date", len(population.birth_dated_ids)),
        ("complete_records_missing_birth_date", exclusion_counts["missing_birth_date"]),
        ("qualifying_debut_rikishi", len(debut_ids)),
        ("qualifying_state_rikishi", len(state_ids)),
    )
    _write_dicts(paths.population_summary, ("measure", "count"), ({"measure": k, "count": v} for k, v in summary))
    _write_dataclasses(paths.population_exclusions, population.exclusions)
    _write_dicts(
        paths.basho_date_coverage,
        ("basho", "start_date", "source", "daily_dates", "consistent", "warning"),
        (
            {
                "basho": str(row.basho),
                "start_date": "" if row.start_date is None else row.start_date.isoformat(),
                "source": row.source,
                "daily_dates": row.daily_dates,
                "consistent": row.consistent,
                "warning": row.warning,
            }
            for row in coverage.values()
        ),
    )
    _write_dataclasses(paths.cohort_observations, observations)
    outcome_rows = []
    for cohort_type in ("division_debut", "division_state"):
        counts = Counter(row.outcome for row in observations if row.cohort_type == cohort_type)
        for outcome in ("success", "failure", "right_censored", "unknown"):
            outcome_rows.append({"cohort_type": cohort_type, "outcome": outcome, "count": counts[outcome]})
    _write_dicts(paths.outcome_summary, ("cohort_type", "outcome", "count"), outcome_rows)
    _write_dataclasses(paths.debut_probabilities, debut_probabilities)
    _write_dataclasses(paths.state_probabilities, state_probabilities)

    manifest = {
        "schema_version": 1,
        "analysis": "division and age as predictors of eventual sanyaku attainment",
        "sources": source_manifest,
        "epoch": str(population.epoch),
        "cutoff": str(population.cutoff),
        "age_policy": "completed years on exact basho Day 1",
        "sanyaku": ["K", "S", "O", "Y"],
        "risk_divisions": ["M", "J", "Ms", "Sd", "Jd", "Jk"],
        "outcomes": ["success", "failure", "right_censored", "unknown"],
        "headline_counts": dict(summary),
        "artifacts": [path.name for path in paths.__dict__.values() if isinstance(path, Path) and path != output_root and path.name != "manifest.json"],
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return paths


def _write_dataclasses(path: Path, rows) -> None:
    rows = tuple(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    _write_dicts(path, tuple(rows[0].__dataclass_fields__), (asdict(row) for row in rows))


def _write_dicts(path: Path, fields, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
