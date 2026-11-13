"""Analyse age at first san'yaku for complete-record rikishi."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from src.analysis.site89.rikishi_bio_data import completed_years
from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .eligible_rikishi import parse_date, select_complete_record_population


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/greatness/sanyaku_age")
SANYAKU_LEVELS = frozenset(
    {MSD.KOMUSUBI, MSD.SEKIWAKE, MSD.OZEKI, MSD.YOKOZUNA}
)


@dataclass(frozen=True)
class SanyakuAgeRecord:
    rikishi_id: int
    shikona: str
    birth_date: str
    first_sanyaku_basho: str
    first_sanyaku_chii: str
    age: int


@dataclass(frozen=True)
class AgeDistributionRow:
    age: int
    rikishi: int
    share_percent: float


@dataclass(frozen=True)
class ProbabilityAfterAgeRow:
    age_threshold: int
    rikishi_becoming_sanyaku_after_age: int
    sanyaku_rikishi_with_birth_date: int
    probability: float


@dataclass(frozen=True)
class SanyakuAgeAnalysis:
    complete_record_rikishi: int
    reached_sanyaku: int
    sanyaku_missing_birth_date: int
    records: tuple[SanyakuAgeRecord, ...]
    distribution: tuple[AgeDistributionRow, ...]
    probability_after_age: tuple[ProbabilityAfterAgeRow, ...]


def analyse_sanyaku_ages(
    history: History,
    bios: BioStore,
    *,
    epoch: Date | None = None,
) -> SanyakuAgeAnalysis:
    """Calculate age at first san'yaku and its empirical tail distribution."""

    population = select_complete_record_population(history, epoch=epoch)
    first_sanyaku: dict[RikId, tuple[Date, Chii]] = {}
    for basho in population.dates:
        for rikishi_id, chii in history[basho].banzuke.rikchii.items():
            if (
                rikishi_id in population.complete_ids
                and chii.level in SANYAKU_LEVELS
            ):
                first_sanyaku.setdefault(rikishi_id, (basho, chii))

    records: list[SanyakuAgeRecord] = []
    missing_birth_date = 0
    for rikishi_id, (basho, chii) in first_sanyaku.items():
        bio = bios.bios.get(rikishi_id)
        if bio is None or bio.birth_date is None:
            missing_birth_date += 1
            continue
        as_of = date(int(basho.year), int(basho.month), 1)
        records.append(
            SanyakuAgeRecord(
                rikishi_id=int(rikishi_id),
                shikona=str(bio.latest_shikona()),
                birth_date=str(bio.birth_date),
                first_sanyaku_basho=str(basho),
                first_sanyaku_chii=str(chii),
                age=completed_years(bio.birth_date.value, as_of),
            )
        )
    records.sort(key=lambda row: (row.age, row.first_sanyaku_basho, row.rikishi_id))

    age_counts = Counter(row.age for row in records)
    denominator = len(records)
    distribution = tuple(
        AgeDistributionRow(
            age=age,
            rikishi=count,
            share_percent=round(100 * count / denominator, 2),
        )
        for age, count in sorted(age_counts.items())
    )
    probability_after_age = _probability_after_age(records)

    return SanyakuAgeAnalysis(
        complete_record_rikishi=len(population.complete_ids),
        reached_sanyaku=len(first_sanyaku),
        sanyaku_missing_birth_date=missing_birth_date,
        records=tuple(records),
        distribution=distribution,
        probability_after_age=probability_after_age,
    )


def _probability_after_age(
    records: list[SanyakuAgeRecord],
) -> tuple[ProbabilityAfterAgeRow, ...]:
    if not records:
        return ()
    ages = [row.age for row in records]
    denominator = len(ages)
    return tuple(
        ProbabilityAfterAgeRow(
            age_threshold=threshold,
            rikishi_becoming_sanyaku_after_age=sum(age > threshold for age in ages),
            sanyaku_rikishi_with_birth_date=denominator,
            probability=sum(age > threshold for age in ages) / denominator,
        )
        for threshold in range(min(ages) - 1, max(ages) + 1)
    )


def write_outputs(
    analysis: SanyakuAgeAnalysis,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    _write_csv(output_root / "rikishi.csv", analysis.records, SanyakuAgeRecord)
    _write_csv(
        output_root / "age_distribution.csv",
        analysis.distribution,
        AgeDistributionRow,
    )
    _write_csv(
        output_root / "probability_after_age.csv",
        analysis.probability_after_age,
        ProbabilityAfterAgeRow,
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
    parser.add_argument(
        "--epoch",
        type=parse_date,
        help="Supporting boundary basho (YYYY/MM); defaults to History's first basho.",
    )
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--bios-json", type=Path, default=DEFAULT_BIOS_JSON)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    analysis = analyse_sanyaku_ages(
        _load_history(args.history_zip),
        load_bio_store(args.bios_json),
        epoch=args.epoch,
    )
    write_outputs(analysis, args.output_root)
    print(f"Complete represented records: {analysis.complete_record_rikishi}")
    print(f"Reached san'yaku: {analysis.reached_sanyaku}")
    print(f"San'yaku rikishi with birth date: {len(analysis.records)}")
    print(f"San'yaku rikishi missing birth date: {analysis.sanyaku_missing_birth_date}")
    print(f"Output: {args.output_root}")


if __name__ == "__main__":
    main()
