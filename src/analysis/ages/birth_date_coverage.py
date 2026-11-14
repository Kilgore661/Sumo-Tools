"""Count exact birth-date coverage on every represented banzuke."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


DEFAULT_OUTPUT = Path(
    "files/output/analysis/ages/birth_date_coverage_by_basho.csv"
)


@dataclass(frozen=True)
class BirthDateCoverageRow:
    basho: str
    banzuke_rikishi: int
    exact_birth_date: int
    missing_exact_birth_date: int
    missing_bio: int
    bio_without_exact_birth_date: int


def birth_date_coverage_by_basho(
    history: History,
    bios: BioStore,
) -> tuple[BirthDateCoverageRow, ...]:
    """Return exact birth-date coverage for every banzuke in ``history``.

    ``missing_exact_birth_date`` includes both rikishi absent from ``bios`` and
    rikishi whose bio exists but has no usable full calendar birth date.
    """

    bio_ids = frozenset(bios.bios)
    rows = []
    for basho in sorted(history):
        banzuke_ids = frozenset(history[basho].banzuke.riks)
        missing_bio_ids = banzuke_ids - bio_ids
        bio_without_exact_ids = frozenset(
            rikishi_id
            for rikishi_id in banzuke_ids & bio_ids
            if bios[rikishi_id].birth_date is None
        )
        missing_exact = len(missing_bio_ids) + len(bio_without_exact_ids)
        exact = len(banzuke_ids) - missing_exact
        row = BirthDateCoverageRow(
            basho=str(basho),
            banzuke_rikishi=len(banzuke_ids),
            exact_birth_date=exact,
            missing_exact_birth_date=missing_exact,
            missing_bio=len(missing_bio_ids),
            bio_without_exact_birth_date=len(bio_without_exact_ids),
        )
        _validate_row(row)
        rows.append(row)
    return tuple(rows)


def write_birth_date_coverage_csv(
    rows: tuple[BirthDateCoverageRow, ...],
    output_path: Path = DEFAULT_OUTPUT,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=tuple(BirthDateCoverageRow.__dataclass_fields__),
        )
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _validate_row(row: BirthDateCoverageRow) -> None:
    if row.banzuke_rikishi != row.exact_birth_date + row.missing_exact_birth_date:
        raise ValueError(f"Birth-date coverage does not reconcile for {row.basho}")
    if row.missing_exact_birth_date != (
        row.missing_bio + row.bio_without_exact_birth_date
    ):
        raise ValueError(f"Missing-birth-date causes do not reconcile for {row.basho}")


def _load_history(path: Path | None) -> History:
    if path is None:
        return get_history()
    archive = path if path.suffix.lower() == ".zip" else path.with_suffix(".zip")
    return load_history_with_annotations(str(archive.with_suffix("")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = birth_date_coverage_by_basho(
        _load_history(args.history_zip),
        load_bio_store(args.bios_json),
    )
    write_birth_date_coverage_csv(rows, args.output)
    print(f"Basho: {len(rows)}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
