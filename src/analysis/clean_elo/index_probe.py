"""Probe the observed chii domain under four binning policies."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from statistics import median

from src.infra.live_store.api import get_history
from src.sumo_core.BasicEnums import Annotation, Division, MSD, Side
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/clean_elo/index_probe")


class BinningPolicy(Enum):
    BP1 = "BP1"
    BP2 = "BP2"
    BP3 = "BP3"
    BP4 = "BP4"


POLICIES = tuple(BinningPolicy)


@dataclass(frozen=True)
class Index:
    """A binned axis value; unlike Chii, some forms need not have a number."""

    level_code: int
    level: str
    number: int | None
    side: str | None
    annotation: str | None

    @property
    def display(self) -> str:
        number = "" if self.number is None else str(self.number)
        side = "" if self.side in (None, "none") else self.side
        annotation = "" if self.annotation is None else self.annotation
        return f"{self.level}{number}{side}{annotation}"

    @property
    def ordinal(self) -> int:
        side_code = {None: 0, "e": 0, "w": 1, "none": 2}[self.side]
        annotation_code = {
            None: 0,
            "YO": 1,
            "HD": 2,
            "OB": 3,
            "TD": 4,
        }[self.annotation]
        number = 0 if self.number is None else self.number
        return (
            self.level_code * 100000
            + number * 100
            + annotation_code * 10
            + side_code
        )

    def sort_key(self) -> tuple[int, int, int, int]:
        side_order = {None: -1, "e": 0, "w": 1, "none": 2}
        annotation_order = {
            None: -1,
            "YO": 1,
            "HD": 2,
            "OB": 3,
            "TD": 4,
        }
        return (
            self.level_code,
            -1 if self.number is None else self.number,
            side_order[self.side],
            annotation_order[self.annotation],
        )


@dataclass(frozen=True)
class Conversion:
    policy: BinningPolicy
    index: Index | None
    failure_reason: str | None = None

    @property
    def valid(self) -> bool:
        return self.index is not None


@dataclass
class ExceptionAggregate:
    policy: BinningPolicy
    chii: Chii | None
    reason: str
    occurrence_count: int = 0
    first_date: Date | None = None
    last_date: Date | None = None
    sample_rikid: RikId | None = None
    details: list["ExceptionDetail"] = field(default_factory=list)

    def add(self, date: Date, day: int, rikid: RikId) -> None:
        self.occurrence_count += 1
        self.details.append(
            ExceptionDetail(
                date=date,
                day=day,
                rikid=rikid,
            )
        )
        if self.first_date is None or _date_key(date) < _date_key(self.first_date):
            self.first_date = date
        if self.last_date is None or _date_key(date) > _date_key(self.last_date):
            self.last_date = date
        if self.sample_rikid is None:
            self.sample_rikid = rikid


@dataclass(frozen=True)
class ExceptionDetail:
    date: Date
    day: int
    rikid: RikId


@dataclass(frozen=True)
class MissingBanzukeOccurrence:
    date: Date
    day: int
    rikid: RikId
    opponent_rikid: RikId
    opponent_chii: Chii | None
    outcome: str
    decision: str
    pair: str


@dataclass(frozen=True)
class ProbeResult:
    start_date: Date
    first_processed_date: Date | None
    last_processed_date: Date | None
    eligible_fight_count: int
    endpoint_occurrence_count: int
    raw_chii_frequencies: Counter[Chii]
    raw_chii_form_frequencies: Counter[str]
    index_frequencies: dict[BinningPolicy, Counter[Index]]
    exceptions: tuple[ExceptionAggregate, ...]
    missing_banzuke_occurrences: tuple[MissingBanzukeOccurrence, ...]


@dataclass(frozen=True)
class ProbeOutputPaths:
    base_output_root: Path
    run_directory: Path
    manifest_json: Path
    policy_summary_csv: Path
    index_frequencies_csv: Path
    frequency_bands_csv: Path
    chii_forms_csv: Path
    chii_index_map_csv: Path
    conversion_exceptions_csv: Path
    missing_banzuke_occurrences_csv: Path


def convert_chii(chii: Chii, policy: BinningPolicy) -> Conversion:
    """Convert one Chii to the Index type required by ``policy``."""
    level_code = chii.ordinal() // 100000
    level = chii.level.as_abbreviation()

    if policy == BinningPolicy.BP1:
        return Conversion(
            policy=policy,
            index=Index(
                level_code=level_code,
                level=level,
                number=chii.number,
                side=_side_component(chii.side),
                annotation=_annotation_component(chii.ann),
            ),
        )

    if policy == BinningPolicy.BP2:
        if chii.side == Side.NONE:
            return Conversion(
                policy=policy,
                index=None,
                failure_reason="BP2 requires an east or west side",
            )
        return Conversion(
            policy=policy,
            index=Index(
                level_code=level_code,
                level=level,
                number=chii.number,
                side=_side_component(chii.side),
                annotation=None,
            ),
        )

    if policy == BinningPolicy.BP3:
        return Conversion(
            policy=policy,
            index=Index(
                level_code=level_code,
                level=level,
                number=chii.number,
                side=None,
                annotation=None,
            ),
        )

    if policy == BinningPolicy.BP4:
        numbered = not (
            isinstance(chii.level, MSD)
            and chii.level != MSD.MAEGASHIRA
        )
        return Conversion(
            policy=policy,
            index=Index(
                level_code=level_code,
                level=level,
                number=chii.number if numbered else None,
                side=None,
                annotation=None,
            ),
        )

    raise ValueError(f"Unsupported binning policy: {policy}")


def probe_indices(history: History, start_date: Date) -> ProbeResult:
    """Count actual-fight chii endpoints under BP1 through BP4."""
    raw_frequencies: Counter[Chii] = Counter()
    raw_form_frequencies: Counter[str] = Counter()
    index_frequencies = {policy: Counter() for policy in POLICIES}
    exceptions: dict[
        tuple[BinningPolicy, int | None, str],
        ExceptionAggregate,
    ] = {}
    missing_banzuke_occurrences: list[MissingBanzukeOccurrence] = []
    eligible_fight_count = 0
    endpoint_occurrence_count = 0

    dates = sorted(
        (
            item
            for item in history
            if _date_key(item) >= _date_key(start_date)
        ),
        key=_date_key,
    )
    for date in dates:
        basho = history[date]
        for day, daily_results in basho.summary.items():
            for pair, bout in daily_results.results_lookup.items():
                if bout.decision == "fusen":
                    continue
                eligible_fight_count += 1
                endpoints = (
                    (bout.rikishi1, bout.rikishi2, bout.outcome1),
                    (bout.rikishi2, bout.rikishi1, bout.outcome2),
                )
                for rikid, opponent_rikid, outcome in endpoints:
                    endpoint_occurrence_count += 1
                    chii = basho.banzuke.rikchii.get(rikid)
                    if chii is not None:
                        raw_frequencies[chii] += 1
                        raw_form_frequencies[_chii_form(chii)] += 1
                    else:
                        raw_form_frequencies["missing_chii"] += 1
                        missing_banzuke_occurrences.append(
                            MissingBanzukeOccurrence(
                                date=date,
                                day=int(day),
                                rikid=rikid,
                                opponent_rikid=opponent_rikid,
                                opponent_chii=basho.banzuke.rikchii.get(
                                    opponent_rikid
                                ),
                                outcome=outcome.name,
                                decision=_decision_text(bout.decision),
                                pair=str(pair),
                            )
                        )
                    for policy in POLICIES:
                        if chii is None:
                            continue
                        conversion = convert_chii(chii, policy)
                        if not conversion.valid:
                            _add_exception(
                                exceptions,
                                policy=policy,
                                chii=chii,
                                reason=str(conversion.failure_reason),
                                date=date,
                                day=int(day),
                                rikid=rikid,
                            )
                            continue
                        index_frequencies[policy][conversion.index] += 1

    return ProbeResult(
        start_date=start_date,
        first_processed_date=None if not dates else dates[0],
        last_processed_date=None if not dates else dates[-1],
        eligible_fight_count=eligible_fight_count,
        endpoint_occurrence_count=endpoint_occurrence_count,
        raw_chii_frequencies=raw_frequencies,
        raw_chii_form_frequencies=raw_form_frequencies,
        index_frequencies=index_frequencies,
        exceptions=tuple(
            sorted(
                exceptions.values(),
                key=lambda item: (
                    item.policy.value,
                    -1 if item.chii is None else item.chii.ordinal(),
                    item.reason,
                ),
            )
        ),
        missing_banzuke_occurrences=tuple(missing_banzuke_occurrences),
    )


def write_probe_outputs(
    result: ProbeResult,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> ProbeOutputPaths:
    """Write one timestamped, auditable probe result."""
    generated_at, run_directory = _create_run_directory(Path(output_root))
    manifest = run_directory / "manifest.json"
    policy_summary = run_directory / "policy_summary.csv"
    index_frequencies = run_directory / "index_frequencies.csv"
    frequency_bands = run_directory / "frequency_bands.csv"
    chii_forms = run_directory / "chii_forms.csv"
    chii_index_map = run_directory / "chii_index_map.csv"
    conversion_exceptions = run_directory / "conversion_exceptions.csv"
    missing_banzuke_occurrences = (
        run_directory / "missing_banzuke_occurrences.csv"
    )

    _write_policy_summary(policy_summary, result)
    _write_index_frequencies(index_frequencies, result)
    _write_frequency_bands(frequency_bands, result)
    _write_chii_forms(chii_forms, result)
    _write_chii_index_map(chii_index_map, result)
    _write_conversion_exceptions(conversion_exceptions, result)
    _write_missing_banzuke_occurrences(
        missing_banzuke_occurrences,
        result,
    )
    _write_manifest(
        manifest,
        result=result,
        generated_at=generated_at,
        base_output_root=Path(output_root),
        run_directory=run_directory,
        output_paths={
            "policy_summary_csv": policy_summary,
            "index_frequencies_csv": index_frequencies,
            "frequency_bands_csv": frequency_bands,
            "chii_forms_csv": chii_forms,
            "chii_index_map_csv": chii_index_map,
            "conversion_exceptions_csv": conversion_exceptions,
            "missing_banzuke_occurrences_csv": missing_banzuke_occurrences,
        },
    )

    return ProbeOutputPaths(
        base_output_root=Path(output_root),
        run_directory=run_directory,
        manifest_json=manifest,
        policy_summary_csv=policy_summary,
        index_frequencies_csv=index_frequencies,
        frequency_bands_csv=frequency_bands,
        chii_forms_csv=chii_forms,
        chii_index_map_csv=chii_index_map,
        conversion_exceptions_csv=conversion_exceptions,
        missing_banzuke_occurrences_csv=missing_banzuke_occurrences,
    )


def run_index_probe(
    *,
    history: History,
    start_date: Date,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> tuple[ProbeResult, ProbeOutputPaths]:
    result = probe_indices(history, start_date)
    outputs = write_probe_outputs(result, output_root)
    return result, outputs


def _write_policy_summary(path: Path, result: ProbeResult) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "policy",
                "start_date",
                "eligible_fights",
                "endpoint_occurrences",
                "converted_occurrences",
                "conversion_exception_occurrences",
                "missing_banzuke_occurrences",
                "distinct_indices",
                "minimum_index_frequency",
                "median_index_frequency",
                "maximum_index_frequency",
            ],
        )
        writer.writeheader()
        for policy in POLICIES:
            frequencies = result.index_frequencies[policy]
            values = list(frequencies.values())
            exception_count = sum(
                item.occurrence_count
                for item in result.exceptions
                if item.policy == policy
            )
            writer.writerow(
                {
                    "policy": policy.value,
                    "start_date": str(result.start_date),
                    "eligible_fights": result.eligible_fight_count,
                    "endpoint_occurrences": result.endpoint_occurrence_count,
                    "converted_occurrences": sum(values),
                    "conversion_exception_occurrences": exception_count,
                    "missing_banzuke_occurrences": len(
                        result.missing_banzuke_occurrences
                    ),
                    "distinct_indices": len(frequencies),
                    "minimum_index_frequency": min(values, default=0),
                    "median_index_frequency": _format_median(values),
                    "maximum_index_frequency": max(values, default=0),
                }
            )


def _write_index_frequencies(path: Path, result: ProbeResult) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "policy",
                "index",
                "index_ordinal",
                "level_code",
                "level",
                "number",
                "side",
                "annotation",
                "occurrence_count",
                "occurrence_percentage",
            ],
        )
        writer.writeheader()
        for policy in POLICIES:
            frequencies = result.index_frequencies[policy]
            converted_total = sum(frequencies.values())
            for index in sorted(frequencies, key=Index.sort_key):
                count = frequencies[index]
                writer.writerow(
                    {
                        "policy": policy.value,
                        **_index_fields(index),
                        "occurrence_count": count,
                        "occurrence_percentage": _percentage(
                            count,
                            converted_total,
                        ),
                    }
                )


def _write_frequency_bands(path: Path, result: ProbeResult) -> None:
    bands = (
        ("1", 1, 1),
        ("2-4", 2, 4),
        ("5-9", 5, 9),
        ("10-19", 10, 19),
        ("20-49", 20, 49),
        ("50-99", 50, 99),
        ("100-199", 100, 199),
        ("200-399", 200, 399),
        ("400+", 400, None),
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "policy",
                "frequency_band",
                "index_count",
                "index_percentage",
            ],
        )
        writer.writeheader()
        for policy in POLICIES:
            frequencies = result.index_frequencies[policy]
            distinct_total = len(frequencies)
            for label, lower, upper in bands:
                count = sum(
                    1
                    for frequency in frequencies.values()
                    if frequency >= lower
                    and (upper is None or frequency <= upper)
                )
                writer.writerow(
                    {
                        "policy": policy.value,
                        "frequency_band": label,
                        "index_count": count,
                        "index_percentage": _percentage(
                            count,
                            distinct_total,
                        ),
                    }
                )


def _write_chii_forms(path: Path, result: ProbeResult) -> None:
    descriptions = {
        "lns": "level, number and east/west side; no annotation",
        "lnsa": "level, number, east/west side and annotation",
        "lna": "level, number and annotation; no side",
        "ln": "level and number; no side or annotation",
        "missing_chii": "bout endpoint has no modeled banzuke chii",
    }
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "form",
                "description",
                "occurrence_count",
                "occurrence_percentage",
            ],
        )
        writer.writeheader()
        for form in ("lns", "lnsa", "lna", "ln", "missing_chii"):
            count = result.raw_chii_form_frequencies.get(form, 0)
            writer.writerow(
                {
                    "form": form,
                    "description": descriptions[form],
                    "occurrence_count": count,
                    "occurrence_percentage": _percentage(
                        count,
                        result.endpoint_occurrence_count,
                    ),
                }
            )


def _write_chii_index_map(path: Path, result: ProbeResult) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "policy",
                "chii",
                "chii_ordinal",
                "chii_occurrence_count",
                "index",
                "index_ordinal",
                "index_level_code",
                "index_level",
                "index_number",
                "index_side",
                "index_annotation",
                "valid",
                "failure_reason",
            ],
        )
        writer.writeheader()
        for chii in sorted(
            result.raw_chii_frequencies,
            key=Chii.ordinal,
        ):
            for policy in POLICIES:
                conversion = convert_chii(chii, policy)
                index = conversion.index
                writer.writerow(
                    {
                        "policy": policy.value,
                        "chii": str(chii),
                        "chii_ordinal": chii.ordinal(),
                        "chii_occurrence_count": result.raw_chii_frequencies[chii],
                        "index": "" if index is None else index.display,
                        "index_ordinal": (
                            "" if index is None else index.ordinal
                        ),
                        "index_level_code": (
                            "" if index is None else index.level_code
                        ),
                        "index_level": "" if index is None else index.level,
                        "index_number": (
                            ""
                            if index is None or index.number is None
                            else index.number
                        ),
                        "index_side": (
                            "" if index is None or index.side is None else index.side
                        ),
                        "index_annotation": (
                            ""
                            if index is None or index.annotation is None
                            else index.annotation
                        ),
                        "valid": conversion.valid,
                        "failure_reason": conversion.failure_reason or "",
                    }
                )


def _write_conversion_exceptions(path: Path, result: ProbeResult) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "policy",
                "date",
                "day",
                "rikid",
                "chii",
                "chii_ordinal",
                "failure_reason",
                "aggregate_occurrence_count",
            ],
        )
        writer.writeheader()
        for item in result.exceptions:
            for detail in item.details:
                writer.writerow(
                    {
                        "policy": item.policy.value,
                        "date": str(detail.date),
                        "day": detail.day,
                        "rikid": detail.rikid,
                        "chii": "" if item.chii is None else str(item.chii),
                        "chii_ordinal": (
                            "" if item.chii is None else item.chii.ordinal()
                        ),
                        "failure_reason": item.reason,
                        "aggregate_occurrence_count": item.occurrence_count,
                    }
                )


def _write_missing_banzuke_occurrences(
    path: Path,
    result: ProbeResult,
) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "date",
                "day",
                "rikid",
                "opponent_rikid",
                "opponent_chii",
                "opponent_chii_ordinal",
                "outcome",
                "decision",
                "pair",
            ],
        )
        writer.writeheader()
        for item in result.missing_banzuke_occurrences:
            writer.writerow(
                {
                    "date": str(item.date),
                    "day": item.day,
                    "rikid": item.rikid,
                    "opponent_rikid": item.opponent_rikid,
                    "opponent_chii": (
                        ""
                        if item.opponent_chii is None
                        else str(item.opponent_chii)
                    ),
                    "opponent_chii_ordinal": (
                        ""
                        if item.opponent_chii is None
                        else item.opponent_chii.ordinal()
                    ),
                    "outcome": item.outcome,
                    "decision": item.decision,
                    "pair": item.pair,
                }
            )


def _write_manifest(
    path: Path,
    *,
    result: ProbeResult,
    generated_at: datetime,
    base_output_root: Path,
    run_directory: Path,
    output_paths: dict[str, Path],
) -> None:
    policy_summaries = {}
    for policy in POLICIES:
        frequencies = result.index_frequencies[policy]
        policy_summaries[policy.value] = {
            "distinct_indices": len(frequencies),
            "converted_occurrences": sum(frequencies.values()),
            "conversion_exception_occurrences": sum(
                item.occurrence_count
                for item in result.exceptions
                if item.policy == policy
            ),
        }

    payload = {
        "probe": "clean_elo_index_probe",
        "generated_at": generated_at.isoformat(),
        "base_output_root": str(base_output_root),
        "run_directory": str(run_directory),
        "requested_start_date": str(result.start_date),
        "first_processed_date": (
            None
            if result.first_processed_date is None
            else str(result.first_processed_date)
        ),
        "last_processed_date": (
            None
            if result.last_processed_date is None
            else str(result.last_processed_date)
        ),
        "observation_unit": "bout endpoint",
        "eligibility": {
            "ordinary_win_loss": "included",
            "draw": "included",
            "blank_decision": "included because W/L is present",
            "paired_fusen": "excluded because no fight occurred",
            "missing_banzuke_chii": (
                "itemised without classifying Mz versus data error"
            ),
        },
        "policies": {
            "BP1": "retain level, number, side and annotation",
            "BP2": (
                "remove annotation; require east or west side"
            ),
            "BP3": "remove annotation and side; retain level and number",
            "BP4": (
                "remove annotation and side; also remove number for Y/O/S/K"
            ),
        },
        "eligible_fight_count": result.eligible_fight_count,
        "endpoint_occurrence_count": result.endpoint_occurrence_count,
        "distinct_raw_chii": len(result.raw_chii_frequencies),
        "missing_banzuke_occurrence_count": len(
            result.missing_banzuke_occurrences
        ),
        "policy_summaries": policy_summaries,
        "outputs": {
            key: str(value)
            for key, value in output_paths.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _add_exception(
    exceptions: dict[
        tuple[BinningPolicy, int | None, str],
        ExceptionAggregate,
    ],
    *,
    policy: BinningPolicy,
    chii: Chii | None,
    reason: str,
    date: Date,
    day: int,
    rikid: RikId,
) -> None:
    ordinal = None if chii is None else chii.ordinal()
    key = policy, ordinal, reason
    aggregate = exceptions.get(key)
    if aggregate is None:
        aggregate = ExceptionAggregate(
            policy=policy,
            chii=chii,
            reason=reason,
        )
        exceptions[key] = aggregate
    aggregate.add(date, day, rikid)


def _side_component(side: Side) -> str:
    if side == Side.EAST:
        return "e"
    if side == Side.WEST:
        return "w"
    return "none"


def _annotation_component(annotation: Annotation) -> str | None:
    if annotation == Annotation.EMPTY:
        return None
    return annotation.name


def _chii_form(chii: Chii) -> str:
    has_side = chii.side != Side.NONE
    has_annotation = chii.ann != Annotation.EMPTY
    if has_side and not has_annotation:
        return "lns"
    if has_side and has_annotation:
        return "lnsa"
    if not has_side and has_annotation:
        return "lna"
    return "ln"


def _decision_text(decision) -> str:
    value = getattr(decision, "value", None)
    return str(decision) if value is None else str(value)


def _index_fields(index: Index) -> dict[str, object]:
    return {
        "index": index.display,
        "index_ordinal": index.ordinal,
        "level_code": index.level_code,
        "level": index.level,
        "number": "" if index.number is None else index.number,
        "side": "" if index.side is None else index.side,
        "annotation": (
            "" if index.annotation is None else index.annotation
        ),
    }


def _format_median(values: list[int]) -> str:
    if not values:
        return "0"
    value = median(values)
    return f"{value:.1f}" if isinstance(value, float) else str(value)


def _percentage(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.000000"
    return f"{100.0 * numerator / denominator:.6f}"


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)


def _create_run_directory(base_root: Path) -> tuple[datetime, Path]:
    base_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    while True:
        run_directory = base_root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory


def parse_date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/")
        return Date(Year(int(year_text)), Month(int(month_text)))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY/MM"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe chii frequencies under BP1 through BP4."
    )
    parser.add_argument(
        "--start",
        required=True,
        type=parse_date,
        help="First basho to inspect, in YYYY/MM format.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result, outputs = run_index_probe(
        history=get_history(),
        start_date=args.start,
        output_root=args.output_root,
    )
    print(f"Eligible fights: {result.eligible_fight_count}")
    print(f"Endpoint occurrences: {result.endpoint_occurrence_count}")
    for policy in POLICIES:
        converted = sum(result.index_frequencies[policy].values())
        exception_count = sum(
            item.occurrence_count
            for item in result.exceptions
            if item.policy == policy
        )
        print(
            f"{policy.value}: {len(result.index_frequencies[policy])} indices, "
            f"{converted} converted, "
            f"{exception_count} conversion exceptions"
        )
    print(
        "Missing-banzuke endpoints: "
        f"{len(result.missing_banzuke_occurrences)}"
    )
    print(f"Run directory: {outputs.run_directory}")
    print(f"Manifest: {outputs.manifest_json}")


if __name__ == "__main__":
    main()
