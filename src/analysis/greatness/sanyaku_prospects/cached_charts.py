"""Render career charts from a previously rebuilt analysis bundle."""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import date
from pathlib import Path

from src.analysis.site89.rikishi_bio_data import completed_years
from src.infra.get_bios.api import BioStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii

from .career_charts import _exact_age, _support_tier, write_career_charts
from .model import CareerChartPoint


def render_cached_career_charts(
    *,
    output_root: Path,
    bios: BioStore,
    rikishi_ids: tuple[int, ...],
) -> tuple[Path, ...]:
    """Build requested charts without loading History or recomputing cohorts."""
    requested = tuple(dict.fromkeys(rikishi_ids))
    if not requested:
        raise ValueError("Specify at least one --chart-rikishi-id, or use --rebuild")

    observations_path = output_root / "rank_state_observations.csv"
    probabilities_path = output_root / "probability_by_rank_state_age.csv"
    coverage_path = output_root / "basho_date_coverage.csv"
    required = (observations_path, probabilities_path, coverage_path)
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Cached analysis artifacts are missing: "
            f"{', '.join(missing)}. Run once with --rebuild."
        )

    requested_set = set(requested)
    observations: dict[int, list[dict[str, str]]] = {rikishi_id: [] for rikishi_id in requested}
    with observations_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            rikishi_id = int(row["rikishi_id"])
            if rikishi_id in requested_set:
                observations[rikishi_id].append(row)

    absent = [rikishi_id for rikishi_id in requested if not observations[rikishi_id]]
    if absent:
        labels = ", ".join(str(rikishi_id) for rikishi_id in absent)
        raise ValueError(
            "Cached charts require eligible birth-dated rikishi IDs present in "
            f"the rebuilt bundle: {labels}"
        )

    probability_lookup = {}
    with probabilities_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = (row["division"], int(row["rank_number"]), int(row["age"]))
            probability_lookup[key] = row

    with coverage_path.open(newline="", encoding="utf-8") as stream:
        coverage = {row["basho"]: row["start_date"] for row in csv.DictReader(stream)}

    points: list[CareerChartPoint] = []
    for rikishi_id in requested:
        bio = bios[RikId(rikishi_id)]
        birth_date = bio.birth_date.value
        career = observations[rikishi_id]
        for observation in career:
            probability = probability_lookup[
                (
                    observation["division"],
                    int(observation["rank_number"]),
                    int(observation["age"]),
                )
            ]
            start_date = date.fromisoformat(observation["start_date"])
            resolved = int(probability["resolved"])
            points.append(
                CareerChartPoint(
                    rikishi_id=rikishi_id,
                    shikona=observation["shikona"],
                    basho=observation["basho"],
                    date=observation["start_date"],
                    age=int(observation["age"]),
                    exact_age=_exact_age(birth_date, start_date),
                    division=observation["division"],
                    rank_number=int(observation["rank_number"]),
                    chii=observation["chii"],
                    point_kind="cohort_probability",
                    probability=_optional_float(probability["resolved_probability"]),
                    cohort_observations=int(probability["observations"]),
                    cohort_rikishi=int(probability["unique_rikishi"]),
                    cohort_success=int(probability["success"]),
                    cohort_failure=int(probability["failure"]),
                    cohort_unresolved=(
                        int(probability["right_censored"]) + int(probability["unknown"])
                    ),
                    cohort_resolved=resolved,
                    support_tier=_support_tier(resolved),
                )
            )

        event_basho, event_chii = _event_from_cached_observations(career, rikishi_id)
        if event_basho:
            if event_basho not in coverage or not coverage[event_basho]:
                raise ValueError(f"Cached date coverage is missing for {event_basho}")
            start_date = date.fromisoformat(coverage[event_basho])
            chii = Chii.from_str(event_chii)
            points.append(
                CareerChartPoint(
                    rikishi_id=rikishi_id,
                    shikona=str(bio.latest_shikona()),
                    basho=event_basho,
                    date=start_date.isoformat(),
                    age=completed_years(birth_date, start_date),
                    exact_age=_exact_age(birth_date, start_date),
                    division=chii.level.as_abbreviation(),
                    rank_number=chii.number,
                    chii=event_chii,
                    point_kind="sanyaku_attainment",
                    probability=1.0,
                    cohort_observations="",
                    cohort_rikishi="",
                    cohort_success="",
                    cohort_failure="",
                    cohort_unresolved="",
                    cohort_resolved="",
                    support_tier="attained",
                )
            )

    points_tuple = tuple(points)
    _write_points(output_root / "career_chart_points.csv", points_tuple)
    return write_career_charts(output_root / "career_charts", points_tuple)


def _event_from_cached_observations(
    career: list[dict[str, str]], rikishi_id: int
) -> tuple[str, str]:
    events = {
        (row["first_sanyaku_basho"], row["first_sanyaku_chii"])
        for row in career
        if row["first_sanyaku_basho"]
    }
    if len(events) > 1:
        raise ValueError(f"Cached san'yaku events disagree for rikishi {rikishi_id}")
    return next(iter(events), ("", ""))


def _optional_float(value: str) -> float | str:
    return "" if value == "" else float(value)


def _write_points(path: Path, points: tuple[CareerChartPoint, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(CareerChartPoint.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(point) for point in points)
