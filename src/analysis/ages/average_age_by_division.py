"""Calculate banzuke age statistics by basho and formal division."""

from __future__ import annotations

import argparse
import calendar
import csv
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Mapping

from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.parser.basho_calendar import basho_date_coverage
from src.infra.parser.parser2_utils import RESULTS_DIR
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import Date, History


DEFAULT_OUTPUT = Path("files/output/analysis/ages/average_age_by_division.csv")
DIVISION_ORDER = (
    "Makuuchi",
    "Juryo",
    "Makushita",
    "Sandanme",
    "Jonidan",
    "Jonokuchi",
)


@dataclass(frozen=True)
class AverageAgeByDivisionRow:
    basho: str
    start_date: str
    division: str
    banzuke_rikishi: int
    exact_birth_date: int
    missing_exact_birth_date: int
    missing_bio: int
    bio_without_exact_birth_date: int
    mean_age_years: float | None
    min_age_years: float | None
    max_age_years: float | None


def exact_age_years(birth_date: date, as_of: date) -> float:
    """Return continuous civil age, treating 1 March as a leap-day anniversary."""

    if as_of < birth_date:
        raise ValueError(f"Date {as_of} precedes birth date {birth_date}")
    anniversary = _anniversary(birth_date, as_of.year)
    if as_of >= anniversary:
        completed = as_of.year - birth_date.year
        previous = anniversary
        following = _anniversary(birth_date, as_of.year + 1)
    else:
        completed = as_of.year - birth_date.year - 1
        previous = _anniversary(birth_date, as_of.year - 1)
        following = anniversary
    return completed + (as_of - previous).days / (following - previous).days


def exact_basho_start_dates(
    history: History,
    *,
    results_root: Path = Path(RESULTS_DIR),
) -> dict[Date, date]:
    """Resolve and validate exact Day 1 dates for every represented basho."""

    result: dict[Date, date] = {}
    for basho in sorted(history):
        coverage = basho_date_coverage(basho, results_root=results_root)
        if not coverage.consistent or coverage.start_date is None:
            detail = coverage.warning or "no unique exact Day 1"
            raise ValueError(f"Cannot resolve exact Day 1 for {basho}: {detail}")
        result[basho] = coverage.start_date
    return result


def average_age_by_division(
    history: History,
    bios: BioStore,
    start_dates: Mapping[Date, date],
) -> tuple[AverageAgeByDivisionRow, ...]:
    """Return age and birth-date coverage statistics for represented divisions."""

    history_dates = frozenset(history)
    supplied_dates = frozenset(start_dates)
    if supplied_dates != history_dates:
        missing = ", ".join(str(value) for value in sorted(history_dates - supplied_dates))
        extra = ", ".join(str(value) for value in sorted(supplied_dates - history_dates))
        raise ValueError(f"Exact Day 1 coverage does not match History (missing={missing or '-'}; extra={extra or '-'})")

    bio_ids = frozenset(bios.bios)
    rows: list[AverageAgeByDivisionRow] = []
    for basho in sorted(history):
        start_date = start_dates[basho]
        if (start_date.year, start_date.month) != (int(basho.year), int(basho.month)):
            raise ValueError(f"Exact Day 1 {start_date} is inconsistent with basho label {basho}")
        groups: dict[str, list[object]] = {division: [] for division in DIVISION_ORDER}
        for rikishi_id in history[basho].banzuke.riks:
            chii = history[basho].banzuke.get_chii(rikishi_id)
            groups[_division_name(chii.level)].append(rikishi_id)

        for division in DIVISION_ORDER:
            rikishi_ids = groups[division]
            if not rikishi_ids:
                continue
            missing_bio = sum(rikishi_id not in bio_ids for rikishi_id in rikishi_ids)
            bio_without_exact = sum(
                rikishi_id in bio_ids and bios[rikishi_id].birth_date is None
                for rikishi_id in rikishi_ids
            )
            ages = [
                exact_age_years(bios[rikishi_id].birth_date.value, start_date)
                for rikishi_id in rikishi_ids
                if rikishi_id in bio_ids and bios[rikishi_id].birth_date is not None
            ]
            row = AverageAgeByDivisionRow(
                basho=str(basho),
                start_date=start_date.isoformat(),
                division=division,
                banzuke_rikishi=len(rikishi_ids),
                exact_birth_date=len(ages),
                missing_exact_birth_date=missing_bio + bio_without_exact,
                missing_bio=missing_bio,
                bio_without_exact_birth_date=bio_without_exact,
                mean_age_years=sum(ages) / len(ages) if ages else None,
                min_age_years=min(ages) if ages else None,
                max_age_years=max(ages) if ages else None,
            )
            _validate_row(row)
            rows.append(row)
    return tuple(rows)


def write_average_age_by_division_csv(
    rows: tuple[AverageAgeByDivisionRow, ...],
    output_path: Path = DEFAULT_OUTPUT,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(AverageAgeByDivisionRow.__dataclass_fields__))
        writer.writeheader()
        for row in rows:
            values = asdict(row)
            for field in ("mean_age_years", "min_age_years", "max_age_years"):
                value = values[field]
                values[field] = "" if value is None else f"{value:.10f}"
            writer.writerow(values)
    return output_path


def produce_average_age_by_division(
    *,
    history: History,
    bios: BioStore,
    output_root: Path,
    start_dates: Mapping[Date, date] | None = None,
    results_root: Path = Path(RESULTS_DIR),
) -> Path:
    dates = start_dates if start_dates is not None else exact_basho_start_dates(history, results_root=results_root)
    rows = average_age_by_division(history, bios, dates)
    return write_average_age_by_division_csv(rows, output_root / "average_age_by_division.csv")


def _anniversary(birth_date: date, year: int) -> date:
    if birth_date.month == 2 and birth_date.day == 29 and not calendar.isleap(year):
        return date(year, 3, 1)
    return date(year, birth_date.month, birth_date.day)


def _division_name(level: MSD | Division) -> str:
    if isinstance(level, MSD):
        return "Makuuchi"
    names = {
        Division.JURYO: "Juryo",
        Division.MAKUSHITA: "Makushita",
        Division.SANDANME: "Sandanme",
        Division.JONIDAN: "Jonidan",
        Division.JONOKUCHI: "Jonokuchi",
    }
    try:
        return names[level]
    except KeyError as error:
        raise ValueError(f"Unsupported formal division level: {level}") from error


def _validate_row(row: AverageAgeByDivisionRow) -> None:
    if row.banzuke_rikishi != row.exact_birth_date + row.missing_exact_birth_date:
        raise ValueError(f"Birth-date coverage does not reconcile for {row.basho} {row.division}")
    if row.missing_exact_birth_date != row.missing_bio + row.bio_without_exact_birth_date:
        raise ValueError(f"Missing-date causes do not reconcile for {row.basho} {row.division}")
    values = (row.mean_age_years, row.min_age_years, row.max_age_years)
    if row.exact_birth_date == 0 and any(value is not None for value in values):
        raise ValueError(f"Age statistics exist without contributors for {row.basho} {row.division}")
    if row.exact_birth_date and not (
        row.min_age_years <= row.mean_age_years <= row.max_age_years  # type: ignore[operator]
    ):
        raise ValueError(f"Invalid age range for {row.basho} {row.division}")


def _load_history(path: Path | None) -> History:
    if path is None:
        return get_history()
    archive = path if path.suffix.lower() == ".zip" else path.with_suffix(".zip")
    return load_history_with_annotations(str(archive.with_suffix("")))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--bios-json", type=Path, default=DEFAULT_BIOS_JSON)
    parser.add_argument("--results-root", type=Path, default=Path(RESULTS_DIR))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    history = _load_history(args.history_zip)
    rows = average_age_by_division(
        history,
        load_bio_store(args.bios_json),
        exact_basho_start_dates(history, results_root=args.results_root),
    )
    write_average_age_by_division_csv(rows, args.output)
    print(f"Rows: {len(rows)}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
