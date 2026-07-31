"""Run BP4 Makuuchi monotonicity probes over successive tail cutoffs."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.infra.live_store.api import get_history
from src.sumo_core.BasicEnums import MSD
from src.sumo_core.BasicPrimitives import Month, Torikumi, Year
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import DailyResults, ResultLookup, Summary

from .index_probe import BinningPolicy, Index, convert_chii
from .rating_probe import RunningStats
from .simulate import SimulationResult, simulate


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/clean_elo/bp4_cutoff_probe"
)
DEFAULT_FIRST_CUTOFF = 19
DEFAULT_LAST_CUTOFF = 12
LOWEST_OBSERVED_MAEGASHIRA = 18


@dataclass(frozen=True)
class Violation:
    stronger_index: Index
    weaker_index: Index
    stronger_mean: float
    weaker_mean: float

    @property
    def increase(self) -> float:
        return self.weaker_mean - self.stronger_mean


@dataclass(frozen=True)
class CutoffResult:
    first_excluded_m: int
    simulation: SimulationResult
    ratings: dict[Index, RunningStats]
    violations: tuple[Violation, ...]
    removed_bout_count: int


@dataclass(frozen=True)
class ProbeResult:
    start_date: Date
    first_cutoff: int
    last_cutoff: int
    cutoffs: tuple[CutoffResult, ...]


@dataclass(frozen=True)
class OutputPaths:
    run_directory: Path
    ratings_csv: Path
    index_ordinals_csv: Path
    violations_csv: Path
    manifest_json: Path


def run_cutoff_series(
    history: History,
    start_date: Date,
    *,
    first_cutoff: int = DEFAULT_FIRST_CUTOFF,
    last_cutoff: int = DEFAULT_LAST_CUTOFF,
) -> ProbeResult:
    """Run every first-excluded-M cutoff from high to low, inclusively."""
    _validate_cutoff_range(first_cutoff, last_cutoff)
    results = tuple(
        run_cutoff(history, start_date, first_excluded_m=cutoff)
        for cutoff in range(first_cutoff, last_cutoff - 1, -1)
    )
    return ProbeResult(
        start_date=start_date,
        first_cutoff=first_cutoff,
        last_cutoff=last_cutoff,
        cutoffs=results,
    )


def run_cutoff(
    history: History,
    start_date: Date,
    *,
    first_excluded_m: int,
) -> CutoffResult:
    """Replay Elo after removing bouts at the selected M tail."""
    _validate_cutoff(first_excluded_m)
    filtered_history, removed_bouts = filter_tail_bouts(
        history,
        start_date=start_date,
        first_excluded_m=first_excluded_m,
    )
    simulation = simulate(
        history=filtered_history,
        start_date=start_date,
        count_absences=False,
    )
    indices = included_indices(first_excluded_m)
    ratings = collect_bp4_ratings(
        history,
        simulation,
        indices=indices,
    )
    missing = [index.display for index in indices if index not in ratings]
    if missing:
        raise ValueError(
            f"Cutoff M{first_excluded_m} has no observations for: "
            + ", ".join(missing)
        )
    return CutoffResult(
        first_excluded_m=first_excluded_m,
        simulation=simulation,
        ratings=ratings,
        violations=find_violations(indices, ratings),
        removed_bout_count=removed_bouts,
    )


def filter_tail_bouts(
    history: History,
    *,
    start_date: Date,
    first_excluded_m: int,
) -> tuple[History, int]:
    """Remove M``n`` through M18 bouts without replacement."""
    _validate_cutoff(first_excluded_m)
    if first_excluded_m == DEFAULT_FIRST_CUTOFF:
        return history, 0

    filtered = History()
    removed = 0
    start_key = _date_key(start_date)
    for date, basho in history.items():
        filtered_days = {}
        for day, daily in basho.summary.items():
            retained = ResultLookup()
            for pair, bout in daily.results_lookup.items():
                touches_tail = any(
                    _is_excluded_rank(
                        basho.banzuke.rikchii.get(rikid),
                        first_excluded_m,
                    )
                    for rikid in (bout.rikishi1, bout.rikishi2)
                )
                if touches_tail:
                    if _date_key(date) >= start_key:
                        removed += 1
                    continue
                retained[pair] = bout
            filtered_days[day] = DailyResults(
                torikumi=Torikumi(retained.keys()),
                results_lookup=retained,
            )
        filtered[date] = BashoState(
            banzuke=basho.banzuke,
            summary=Summary(
                filtered_days,
                performances=basho.summary.performances,
            ),
        )
    return filtered, removed


def included_indices(first_excluded_m: int) -> tuple[Index, ...]:
    """Return Y/O/S/K followed by retained maegashira BP4 indices."""
    _validate_cutoff(first_excluded_m)
    raw = ("Y1e", "O1e", "S1e", "K1e") + tuple(
        f"M{number}e" for number in range(1, first_excluded_m)
    )
    result = []
    for display in raw:
        conversion = convert_chii(
            Chii.from_str(display),
            BinningPolicy.BP4,
        )
        if not conversion.valid:
            raise RuntimeError(f"Cannot construct BP4 index from {display}")
        result.append(conversion.index)
    return tuple(result)


def collect_bp4_ratings(
    history: History,
    simulation: SimulationResult,
    *,
    indices: tuple[Index, ...],
) -> dict[Index, RunningStats]:
    """Collect one start-of-basho observation per represented rikishi."""
    required = set(indices)
    stats: dict[Index, RunningStats] = {}
    for date in sorted(simulation.basho_ratings, key=_date_key):
        basho = history[date]
        ratings = simulation.basho_ratings[
            date
        ].initial_after_normalisation
        for rikid, rating in ratings.items():
            chii = basho.banzuke.rikchii.get(rikid)
            if chii is None:
                continue
            conversion = convert_chii(chii, BinningPolicy.BP4)
            if not conversion.valid or conversion.index not in required:
                continue
            stats.setdefault(conversion.index, RunningStats()).add(rating)
    return stats


def find_violations(
    indices: tuple[Index, ...],
    ratings: dict[Index, RunningStats],
) -> tuple[Violation, ...]:
    """Return adjacent increases as the BP4 ordinal worsens."""
    violations = []
    for stronger, weaker in zip(indices, indices[1:]):
        stronger_mean = ratings[stronger].mean
        weaker_mean = ratings[weaker].mean
        if weaker_mean > stronger_mean:
            violations.append(
                Violation(
                    stronger_index=stronger,
                    weaker_index=weaker,
                    stronger_mean=stronger_mean,
                    weaker_mean=weaker_mean,
                )
            )
    return tuple(violations)


def run_probe(
    *,
    history: History,
    start_date: Date,
    first_cutoff: int = DEFAULT_FIRST_CUTOFF,
    last_cutoff: int = DEFAULT_LAST_CUTOFF,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> tuple[ProbeResult, OutputPaths]:
    result = run_cutoff_series(
        history,
        start_date,
        first_cutoff=first_cutoff,
        last_cutoff=last_cutoff,
    )
    return result, write_outputs(result, output_root=output_root)


def write_outputs(
    result: ProbeResult,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> OutputPaths:
    generated_at, run_directory = _create_run_directory(output_root)
    ratings_csv = run_directory / "bp4_cutoff_ratings.csv"
    ordinals_csv = run_directory / "bp4_index_ordinals.csv"
    violations_csv = run_directory / "bp4_cutoff_violations.csv"
    manifest_json = run_directory / "manifest.json"

    all_indices = included_indices(result.first_cutoff)
    _write_ratings(ratings_csv, result, all_indices)
    _write_index_ordinals(ordinals_csv, all_indices)
    _write_violations(violations_csv, result)
    _write_manifest(manifest_json, generated_at, result)

    return OutputPaths(
        run_directory=run_directory,
        ratings_csv=ratings_csv,
        index_ordinals_csv=ordinals_csv,
        violations_csv=violations_csv,
        manifest_json=manifest_json,
    )


def _write_ratings(
    path: Path,
    result: ProbeResult,
    all_indices: tuple[Index, ...],
) -> None:
    fields = ["first_excluded_m"] + [
        index.display for index in all_indices
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for cutoff in result.cutoffs:
            row: dict[str, object] = {
                "first_excluded_m": cutoff.first_excluded_m
            }
            row.update(
                {
                    index.display: (
                        _number(cutoff.ratings[index].mean)
                        if index in cutoff.ratings
                        else ""
                    )
                    for index in all_indices
                }
            )
            writer.writerow(row)


def _write_index_ordinals(
    path: Path,
    indices: tuple[Index, ...],
) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["index", "index_ordinal"],
        )
        writer.writeheader()
        for index in indices:
            writer.writerow(
                {
                    "index": index.display,
                    "index_ordinal": index.ordinal,
                }
            )


def _write_violations(path: Path, result: ProbeResult) -> None:
    fields = [
        "first_excluded_m",
        "violation_number",
        "stronger_index",
        "stronger_index_ordinal",
        "stronger_mean",
        "weaker_index",
        "weaker_index_ordinal",
        "weaker_mean",
        "increase",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for cutoff in result.cutoffs:
            for number, violation in enumerate(
                cutoff.violations,
                start=1,
            ):
                writer.writerow(
                    {
                        "first_excluded_m": cutoff.first_excluded_m,
                        "violation_number": number,
                        "stronger_index": (
                            violation.stronger_index.display
                        ),
                        "stronger_index_ordinal": (
                            violation.stronger_index.ordinal
                        ),
                        "stronger_mean": _number(
                            violation.stronger_mean
                        ),
                        "weaker_index": violation.weaker_index.display,
                        "weaker_index_ordinal": (
                            violation.weaker_index.ordinal
                        ),
                        "weaker_mean": _number(violation.weaker_mean),
                        "increase": _number(violation.increase),
                    }
                )


def _write_manifest(
    path: Path,
    generated_at: datetime,
    result: ProbeResult,
) -> None:
    payload = {
        "generated_at_utc": generated_at.isoformat(),
        "requested_start_date": str(result.start_date),
        "binning_policy": "BP4",
        "cutoffs": [
            cutoff.first_excluded_m for cutoff in result.cutoffs
        ],
        "cutoff_definition": (
            "first excluded maegashira number; bouts involving M<n> "
            "through M18 are removed without replacement"
        ),
        "baseline_definition": (
            "first_excluded_m=19 removes nothing"
        ),
        "count_absences": False,
        "rating_observation": (
            "One represented rikishi-basho, associated with current BP4 "
            "index and initial-after-normalisation rating."
        ),
        "sequence": [
            index.display for index in included_indices(result.first_cutoff)
        ],
        "violation_definition": (
            "An adjacent mean-rating increase as BP4 index ordinal worsens."
        ),
        "runs": [
            {
                "first_excluded_m": cutoff.first_excluded_m,
                "last_included_index": (
                    f"M{cutoff.first_excluded_m - 1}"
                ),
                "removed_bout_count": cutoff.removed_bout_count,
                "rated_bout_count": cutoff.simulation.rated_bout_count,
                "violation_count": len(cutoff.violations),
                "violations": [
                    (
                        f"{item.stronger_index.display}->"
                        f"{item.weaker_index.display}"
                    )
                    for item in cutoff.violations
                ],
            }
            for cutoff in result.cutoffs
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _is_excluded_rank(chii, first_excluded_m: int) -> bool:
    return (
        chii is not None
        and chii.level == MSD.MAEGASHIRA
        and first_excluded_m
        <= chii.number
        <= LOWEST_OBSERVED_MAEGASHIRA
    )


def _validate_cutoff(first_excluded_m: int) -> None:
    if not 2 <= first_excluded_m <= DEFAULT_FIRST_CUTOFF:
        raise ValueError("first_excluded_m must be between 2 and 19")


def _validate_cutoff_range(
    first_cutoff: int,
    last_cutoff: int,
) -> None:
    _validate_cutoff(first_cutoff)
    _validate_cutoff(last_cutoff)
    if first_cutoff < last_cutoff:
        raise ValueError("first_cutoff must be at least last_cutoff")


def _number(value: float) -> str:
    return f"{value:.9f}"


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)


def _create_run_directory(root: Path) -> tuple[datetime, Path]:
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    while True:
        run_directory = root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory


def parse_date(value: str) -> Date:
    try:
        year, month = value.split("/")
        return Date(Year(int(year)), Month(int(month)))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY/MM"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run BP4 Makuuchi monotonicity probes while successively "
            "removing lower-maegashira bouts."
        )
    )
    parser.add_argument("--start", required=True, type=parse_date)
    parser.add_argument(
        "--first-cutoff",
        type=int,
        default=DEFAULT_FIRST_CUTOFF,
        help="First runner value. Default: 19.",
    )
    parser.add_argument(
        "--last-cutoff",
        type=int,
        default=DEFAULT_LAST_CUTOFF,
        help="Last runner value. Default: 12.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result, outputs = run_probe(
        history=get_history(),
        start_date=args.start,
        first_cutoff=args.first_cutoff,
        last_cutoff=args.last_cutoff,
        output_root=args.output_root,
    )
    for cutoff in result.cutoffs:
        transitions = ", ".join(
            (
                f"{item.stronger_index.display}->"
                f"{item.weaker_index.display}"
            )
            for item in cutoff.violations
        )
        suffix = "" if not transitions else f": {transitions}"
        print(
            f"{cutoff.first_excluded_m}: "
            f"{len(cutoff.violations)} violations{suffix}"
        )
    print(f"Run directory: {outputs.run_directory}")
    print(f"Ratings: {outputs.ratings_csv}")
    print(f"Violations: {outputs.violations_csv}")


if __name__ == "__main__":
    main()
