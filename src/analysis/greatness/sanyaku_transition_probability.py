"""Estimate future san'yaku attainment from division-and-age states."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from pathlib import Path

from src.analysis.site89.rikishi_bio_data import completed_years
from src.infra.get_bios.api import BioBashoDate, BioStore, load_bio_store
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .eligible_rikishi import parse_date, select_complete_record_population
from .sanyaku_age_distribution import SANYAKU_LEVELS


DEFAULT_HORIZON_BASHO: int | None = None
DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/greatness/sanyaku_transition_probability"
)
DIVISION_ORDER = ("M", "J", "Ms", "Sd", "Jd", "Jk")


class OutcomeStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RIGHT_CENSORED = "right_censored"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RiskObservation:
    rikishi_id: RikId
    division: str
    age: int
    basho_index: int


@dataclass(frozen=True)
class ProbabilityRow:
    division: str
    age: int
    horizon_basho: int | str
    rikishi: int
    success: int
    failure: int
    right_censored: int
    unknown: int
    resolved: int
    resolved_probability: float | str
    lower_bound_probability: float
    upper_bound_probability: float


@dataclass(frozen=True)
class ThresholdProbabilityRow:
    division: str
    age_threshold: int
    condition: str
    horizon_basho: int | str
    rikishi: int
    success: int
    failure: int
    right_censored: int
    unknown: int
    resolved: int
    resolved_probability: float | str
    lower_bound_probability: float
    upper_bound_probability: float


@dataclass(frozen=True)
class TransitionAnalysis:
    complete_record_rikishi: int
    complete_records_missing_birth_date: int
    horizon_basho: int | None
    exact_age: tuple[ProbabilityRow, ...]
    age_threshold: tuple[ThresholdProbabilityRow, ...]


def analyse_transition_probabilities(
    history: History,
    bios: BioStore,
    *,
    epoch: Date | None = None,
    horizon_basho: int | None = DEFAULT_HORIZON_BASHO,
) -> TransitionAnalysis:
    """Estimate eventual or fixed-horizon future san'yaku attainment."""

    if horizon_basho is not None and horizon_basho <= 0:
        raise ValueError("horizon_basho must be positive")

    population = select_complete_record_population(history, epoch=epoch)
    first_sanyaku_index = _first_sanyaku_indices(
        history,
        population.dates,
        population.complete_ids,
    )
    latest_ids = frozenset(history[population.last_basho].banzuke.riks)
    missing_birth_date = sum(
        rikishi_id not in bios.bios or bios[rikishi_id].birth_date is None
        for rikishi_id in population.complete_ids
    )
    observations = _risk_observations(
        history,
        population.dates,
        population.complete_ids,
        first_sanyaku_index,
        bios,
    )

    exact_groups: dict[tuple[str, int], list[RiskObservation]] = defaultdict(list)
    by_division_rikishi: dict[
        str, dict[RikId, list[RiskObservation]]
    ] = defaultdict(lambda: defaultdict(list))
    for observation in observations:
        exact_groups[(observation.division, observation.age)].append(observation)
        by_division_rikishi[observation.division][observation.rikishi_id].append(
            observation
        )

    exact_rows = tuple(
        _probability_row(
            division,
            age,
            cohort,
            history_dates=population.dates,
            first_sanyaku_index=first_sanyaku_index,
            latest_ids=latest_ids,
            bios=bios,
            horizon_basho=horizon_basho,
        )
        for (division, age), cohort in sorted(
            exact_groups.items(),
            key=lambda item: (DIVISION_ORDER.index(item[0][0]), item[0][1]),
        )
    )

    threshold_rows: list[ThresholdProbabilityRow] = []
    for division in DIVISION_ORDER:
        observations_by_rikishi = by_division_rikishi.get(division, {})
        if not observations_by_rikishi:
            continue
        ages = [
            observation.age
            for rikishi_observations in observations_by_rikishi.values()
            for observation in rikishi_observations
        ]
        for threshold in range(min(ages) - 1, max(ages) + 1):
            cohort = [
                min(
                    (
                        observation
                        for observation in rikishi_observations
                        if observation.age > threshold
                    ),
                    key=lambda observation: observation.basho_index,
                )
                for rikishi_observations in observations_by_rikishi.values()
                if any(
                    observation.age > threshold
                    for observation in rikishi_observations
                )
            ]
            values = _outcome_counts(
                cohort,
                history_dates=population.dates,
                first_sanyaku_index=first_sanyaku_index,
                latest_ids=latest_ids,
                bios=bios,
                horizon_basho=horizon_basho,
            )
            threshold_rows.append(
                ThresholdProbabilityRow(
                    division=division,
                    age_threshold=threshold,
                    condition=f"age > {threshold}",
                    horizon_basho=_horizon_label(horizon_basho),
                    **values,
                )
            )

    return TransitionAnalysis(
        complete_record_rikishi=len(population.complete_ids),
        complete_records_missing_birth_date=missing_birth_date,
        horizon_basho=horizon_basho,
        exact_age=exact_rows,
        age_threshold=tuple(threshold_rows),
    )


def _first_sanyaku_indices(
    history: History,
    dates: tuple[Date, ...],
    complete_ids: frozenset[RikId],
) -> dict[RikId, int]:
    first: dict[RikId, int] = {}
    for basho_index, basho in enumerate(dates):
        for rikishi_id, chii in history[basho].banzuke.rikchii.items():
            if rikishi_id in complete_ids and chii.level in SANYAKU_LEVELS:
                first.setdefault(rikishi_id, basho_index)
    return first


def _risk_observations(
    history: History,
    dates: tuple[Date, ...],
    complete_ids: frozenset[RikId],
    first_sanyaku_index: dict[RikId, int],
    bios: BioStore,
) -> tuple[RiskObservation, ...]:
    observations: dict[tuple[RikId, str, int], RiskObservation] = {}
    for basho_index, basho in enumerate(dates):
        for rikishi_id, chii in history[basho].banzuke.rikchii.items():
            if rikishi_id not in complete_ids:
                continue
            if basho_index >= first_sanyaku_index.get(rikishi_id, len(dates)):
                continue
            bio = bios.bios.get(rikishi_id)
            if bio is None or bio.birth_date is None:
                continue
            division = _prospect_division(chii)
            if division is None:
                continue
            as_of = date(int(basho.year), int(basho.month), 1)
            age = completed_years(bio.birth_date.value, as_of)
            observations.setdefault(
                (rikishi_id, division, age),
                RiskObservation(rikishi_id, division, age, basho_index),
            )
    return tuple(observations.values())


def _prospect_division(chii: Chii) -> str | None:
    if chii.level == MSD.MAEGASHIRA:
        return "M"
    return {
        Division.JURYO: "J",
        Division.MAKUSHITA: "Ms",
        Division.SANDANME: "Sd",
        Division.JONIDAN: "Jd",
        Division.JONOKUCHI: "Jk",
    }.get(chii.level)


def _probability_row(
    division: str,
    age: int,
    cohort: list[RiskObservation],
    *,
    history_dates: tuple[Date, ...],
    first_sanyaku_index: dict[RikId, int],
    latest_ids: frozenset[RikId],
    bios: BioStore,
    horizon_basho: int | None,
) -> ProbabilityRow:
    return ProbabilityRow(
        division=division,
        age=age,
        horizon_basho=_horizon_label(horizon_basho),
        **_outcome_counts(
            cohort,
            history_dates=history_dates,
            first_sanyaku_index=first_sanyaku_index,
            latest_ids=latest_ids,
            bios=bios,
            horizon_basho=horizon_basho,
        ),
    )


def _outcome_counts(
    cohort: list[RiskObservation],
    *,
    history_dates: tuple[Date, ...],
    first_sanyaku_index: dict[RikId, int],
    latest_ids: frozenset[RikId],
    bios: BioStore,
    horizon_basho: int | None,
) -> dict[str, int | float | str]:
    counts = CounterStatus()
    for observation in cohort:
        status = _outcome_status(
            observation,
            history_dates=history_dates,
            first_sanyaku_index=first_sanyaku_index,
            latest_ids=latest_ids,
            bios=bios,
            horizon_basho=horizon_basho,
        )
        counts.add(status)

    total = len(cohort)
    resolved = counts.success + counts.failure
    unresolved = counts.right_censored + counts.unknown
    return {
        "rikishi": total,
        "success": counts.success,
        "failure": counts.failure,
        "right_censored": counts.right_censored,
        "unknown": counts.unknown,
        "resolved": resolved,
        "resolved_probability": counts.success / resolved if resolved else "",
        "lower_bound_probability": counts.success / total if total else 0.0,
        "upper_bound_probability": (
            (counts.success + unresolved) / total if total else 0.0
        ),
    }


@dataclass
class CounterStatus:
    success: int = 0
    failure: int = 0
    right_censored: int = 0
    unknown: int = 0

    def add(self, status: OutcomeStatus) -> None:
        setattr(self, status.value, getattr(self, status.value) + 1)


def _outcome_status(
    observation: RiskObservation,
    *,
    history_dates: tuple[Date, ...],
    first_sanyaku_index: dict[RikId, int],
    latest_ids: frozenset[RikId],
    bios: BioStore,
    horizon_basho: int | None,
) -> OutcomeStatus:
    event_index = first_sanyaku_index.get(observation.rikishi_id)
    if event_index is not None:
        if horizon_basho is None:
            return OutcomeStatus.SUCCESS
        return (
            OutcomeStatus.SUCCESS
            if event_index - observation.basho_index <= horizon_basho
            else OutcomeStatus.FAILURE
        )

    if (
        horizon_basho is not None
        and observation.basho_index + horizon_basho < len(history_dates)
    ):
        return OutcomeStatus.FAILURE

    bio = bios.bios.get(observation.rikishi_id)
    history_end = BioBashoDate.from_history_date(history_dates[-1])
    if bio is not None and bio.intai is not None and bio.intai <= history_end:
        return OutcomeStatus.FAILURE
    if observation.rikishi_id in latest_ids:
        return OutcomeStatus.RIGHT_CENSORED
    return OutcomeStatus.UNKNOWN


def _horizon_label(horizon_basho: int | None) -> int | str:
    return "eventual" if horizon_basho is None else horizon_basho


def write_outputs(
    analysis: TransitionAnalysis,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_root / "probability_by_division_and_age.csv",
        analysis.exact_age,
        ProbabilityRow,
    )
    _write_csv(
        output_root / "probability_by_division_and_age_threshold.csv",
        analysis.age_threshold,
        ThresholdProbabilityRow,
    )


def _write_csv(path: Path, rows: tuple[object, ...], row_type: type) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=row_type.__dataclass_fields__)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _load_history(path: Path | None) -> History:
    if path is None:
        return get_history()
    archive = path if path.suffix.lower() == ".zip" else path.with_suffix(".zip")
    return load_history_with_annotations(str(archive.with_suffix("")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epoch", type=parse_date)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--bios-json", type=Path, default=DEFAULT_BIOS_JSON)
    parser.add_argument(
        "--horizon-basho",
        type=int,
        help="Optional fixed horizon; omit to estimate eventual attainment.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    analysis = analyse_transition_probabilities(
        _load_history(args.history_zip),
        load_bio_store(args.bios_json),
        epoch=args.epoch,
        horizon_basho=args.horizon_basho,
    )
    write_outputs(analysis, args.output_root)
    print(f"Complete represented records: {analysis.complete_record_rikishi}")
    print(
        "Complete records missing birth date: "
        f"{analysis.complete_records_missing_birth_date}"
    )
    horizon = _horizon_label(analysis.horizon_basho)
    print(f"Horizon: {horizon}")
    print(f"Exact-age rows: {len(analysis.exact_age)}")
    print(f"Age-threshold rows: {len(analysis.age_threshold)}")
    print(f"Output: {args.output_root}")


if __name__ == "__main__":
    main()
