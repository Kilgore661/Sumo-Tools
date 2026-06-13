"""Inspect History and BioStore shikona facts for selected rikishi."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class HistoryShikonaRun:
    shikona: Shikona
    start: Date
    end: Date
    count: int


def load_history(history_zip: Path | None) -> History:
    """Load History from a zip-backed path or the live store."""
    if history_zip is None:
        return get_history()
    return load_history_with_annotations(str(history_zip.with_suffix("")))


def history_shikona_by_date(history: History, rikid: RikId) -> list[tuple[Date, Shikona]]:
    """Return all History banzuke shikona observations for one rikishi."""
    observations: list[tuple[Date, Shikona]] = []

    for date in sorted(history.keys()):
        basho = history(date)
        if rikid in basho.banzuke.riks:
            observations.append((date, basho.banzuke.rikshik[rikid]))

    return observations


def history_shikona_runs(
    observations: list[tuple[Date, Shikona]]
) -> list[HistoryShikonaRun]:
    """Collapse dated History shikona observations into contiguous runs."""
    if not observations:
        return []

    runs: list[HistoryShikonaRun] = []
    run_shikona = observations[0][1]
    run_start = observations[0][0]
    run_end = observations[0][0]
    run_count = 1

    for date, shikona in observations[1:]:
        if shikona == run_shikona:
            run_end = date
            run_count += 1
            continue

        runs.append(
            HistoryShikonaRun(
                shikona=run_shikona,
                start=run_start,
                end=run_end,
                count=run_count,
            )
        )
        run_shikona = shikona
        run_start = date
        run_end = date
        run_count = 1

    runs.append(
        HistoryShikonaRun(
            shikona=run_shikona,
            start=run_start,
            end=run_end,
            count=run_count,
        )
    )
    return runs


def print_bio_section(rikid: RikId, bios: BioStore) -> None:
    """Print BioStore shikona facts for one rikishi."""
    bio = bios[rikid]
    print("BioStore")
    print(f"  latest_shikona: {bio.latest_shikona()}")
    print(f"  hatsu_dohyo: {bio.hatsu_dohyo}")
    print(f"  intai: {bio.intai}")
    print("  shikona_history:")
    for use in bio.shikona_history:
        print(f"    {use.first_basho}: {use.shikona}")


def print_history_section(history: History, rikid: RikId) -> None:
    """Print History shikona facts for one rikishi."""
    observations = history_shikona_by_date(history, rikid)
    print("History")
    print(f"  banzuke appearances: {len(observations)}")

    if not observations:
        return

    print(f"  first: {observations[0][0]} {observations[0][1]}")
    print(f"  last: {observations[-1][0]} {observations[-1][1]}")
    print("  distinct shikona:")
    for shikona in sorted({shikona for _, shikona in observations}, key=str):
        print(f"    {shikona}")

    print("  runs:")
    for run in history_shikona_runs(observations):
        print(f"    {run.start} to {run.end}: {run.shikona} ({run.count})")


def inspect_rikid(rikid: RikId, history: History, bios: BioStore) -> None:
    """Print History and BioStore facts for one rikishi."""
    print(f"rikid {rikid}")
    print("=" * (6 + len(str(rikid))))
    print_bio_section(rikid, bios)
    print_history_section(history, rikid)
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect BioStore and History shikona facts for rikishi ids."
    )
    parser.add_argument("rikids", nargs="+", type=int)
    parser.add_argument(
        "--history-zip",
        type=Path,
        default=None,
        help="Optional History zip path. Defaults to the live store.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = load_history(args.history_zip)
    bios = load_bio_store()

    for raw_rikid in args.rikids:
        inspect_rikid(RikId(raw_rikid), history, bios)


if __name__ == "__main__":
    main()
