"""Count san'yaku rikishi with complete represented records and birth dates."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class EligibilityCount:
    epoch: Date
    last_basho: Date
    observed_rikishi: int
    boundary_incumbents: int
    complete_record_rikishi: int
    reached_sanyaku: int
    sanyaku_missing_bio: int
    sanyaku_missing_birth_date: int
    sanyaku_with_birth_date: int


@dataclass(frozen=True)
class CompleteRecordPopulation:
    epoch: Date
    last_basho: Date
    dates: tuple[Date, ...]
    observed_ids: frozenset[RikId]
    boundary_ids: frozenset[RikId]
    complete_ids: frozenset[RikId]


def select_complete_record_population(
    history: History,
    *,
    epoch: Date | None = None,
) -> CompleteRecordPopulation:
    """Select rikishi first observed after a represented boundary banzuke."""

    dates = sorted(history)
    if not dates:
        raise ValueError("Eligible-rikishi analysis requires a non-empty History")

    selected_epoch = dates[0] if epoch is None else epoch
    try:
        epoch_index = dates.index(selected_epoch)
    except ValueError as exc:
        raise ValueError(
            f"Epoch must be a represented banzuke; received {selected_epoch}"
        ) from exc

    selected_dates = tuple(dates[epoch_index:])
    boundary_ids = frozenset(history[selected_epoch].banzuke.riks)
    observed_ids = frozenset(
        rikishi_id
        for date in selected_dates
        for rikishi_id in history[date].banzuke.riks
    )
    return CompleteRecordPopulation(
        epoch=selected_epoch,
        last_basho=selected_dates[-1],
        dates=selected_dates,
        observed_ids=observed_ids,
        boundary_ids=boundary_ids,
        complete_ids=observed_ids - boundary_ids,
    )


def count_eligible_rikishi(
    history: History,
    bios: BioStore,
    *,
    epoch: Date | None = None,
) -> EligibilityCount:
    """Count complete-record rikishi reaching san'yaku and birth-date coverage.

    The epoch banzuke is supporting boundary data. Every rikishi on it is
    conservatively treated as a left-boundary incumbent and excluded. A rikishi
    first appearing on a later represented banzuke has a complete represented
    record, even if that rikishi remains active at the end of History. San'yaku
    comprises Komusubi, Sekiwake, Ozeki, and Yokozuna.
    """

    population = select_complete_record_population(history, epoch=epoch)
    complete_ids = population.complete_ids
    sanyaku_levels = frozenset(
        {MSD.KOMUSUBI, MSD.SEKIWAKE, MSD.OZEKI, MSD.YOKOZUNA}
    )
    sanyaku_ids = frozenset(
        rikishi_id
        for date in population.dates
        for rikishi_id, chii in history[date].banzuke.rikchii.items()
        if rikishi_id in complete_ids and chii.level in sanyaku_levels
    )
    sanyaku_missing_bio_ids = sanyaku_ids - frozenset(bios.bios)
    sanyaku_missing_birth_date_ids = frozenset(
        rikishi_id
        for rikishi_id in sanyaku_ids & frozenset(bios.bios)
        if bios[rikishi_id].birth_date is None
    )
    sanyaku_with_birth_date_ids = (
        sanyaku_ids - sanyaku_missing_bio_ids - sanyaku_missing_birth_date_ids
    )

    return EligibilityCount(
        epoch=population.epoch,
        last_basho=population.last_basho,
        observed_rikishi=len(population.observed_ids),
        boundary_incumbents=len(population.boundary_ids),
        complete_record_rikishi=len(complete_ids),
        reached_sanyaku=len(sanyaku_ids),
        sanyaku_missing_bio=len(sanyaku_missing_bio_ids),
        sanyaku_missing_birth_date=len(sanyaku_missing_birth_date_ids),
        sanyaku_with_birth_date=len(sanyaku_with_birth_date_ids),
    )


def parse_date(value: str) -> Date:
    try:
        year, month = value.replace("-", "/").split("/")
        return Date.from_ints(int(year), int(month))
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            f"Expected a basho date in YYYY/MM format, received {value!r}"
        ) from exc


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
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load a History zip instead of the live store.",
    )
    parser.add_argument(
        "--bios-json",
        type=Path,
        default=DEFAULT_BIOS_JSON,
        help=f"Parsed rikishi bio JSON. Default: {DEFAULT_BIOS_JSON}",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = count_eligible_rikishi(
        _load_history(args.history_zip),
        load_bio_store(args.bios_json),
        epoch=args.epoch,
    )
    print(f"Epoch: {result.epoch}")
    print(f"Last represented basho: {result.last_basho}")
    print(f"Observed rikishi: {result.observed_rikishi}")
    print(f"Boundary incumbents excluded: {result.boundary_incumbents}")
    print(f"Complete represented records: {result.complete_record_rikishi}")
    print(f"Complete-record rikishi reaching san'yaku: {result.reached_sanyaku}")
    print(f"San'yaku rikishi missing bio: {result.sanyaku_missing_bio}")
    print(
        "San'yaku rikishi missing birth date: "
        f"{result.sanyaku_missing_birth_date}"
    )
    print(
        "San'yaku rikishi with birth date: "
        f"{result.sanyaku_with_birth_date}"
    )


if __name__ == "__main__":
    main()
