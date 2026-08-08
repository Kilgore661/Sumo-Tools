"""Run Proposal 5's deterministic division-only initialization experiment."""

from __future__ import annotations

import argparse
import csv
from datetime import timedelta
import hashlib
from pathlib import Path
from time import perf_counter

from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .definition import Proposal1Definition
from .division_initialisation import run_division_initialisation
from .division_initialisation_output import write_division_initialisation_outputs
from .output import HistorySource
from .randomised_prior import PassProgress, load_prior_values


def main() -> None:
    started = perf_counter()
    arguments = _arguments()
    history_zip = arguments.history_zip.resolve()
    prior_csv = arguments.prior_csv.resolve()
    placebo_csv = arguments.placebo_envelope_csv.resolve()
    end_date = _date(arguments.end)
    output_directory = (
        arguments.output_root
        / f"division_initialisation_1989_01_to_{str(end_date).replace('/', '_')}"
    )
    history = load_history_with_annotations(str(history_zip.with_suffix("")))

    def show_progress(update: PassProgress) -> None:
        elapsed = perf_counter() - started
        remaining = (
            elapsed / update.completed_passes
            * (update.total_passes - update.completed_passes)
        )
        print(
            f"[{update.completed_passes}/{update.total_passes}] "
            f"{update.label}  elapsed {_duration(elapsed)}  "
            f"ETA {_duration(remaining)}",
            flush=True,
        )

    result = run_division_initialisation(
        history,
        Proposal1Definition(end_date=end_date),
        load_prior_values(prior_csv),
        progress=show_progress,
    )
    with placebo_csv.open(newline="", encoding="utf-8") as stream:
        placebo_envelope = tuple(csv.DictReader(stream))
    write_division_initialisation_outputs(
        result,
        placebo_envelope,
        output_directory,
        HistorySource(path=str(history_zip), sha256=_sha256(history_zip)),
        HistorySource(path=str(prior_csv), sha256=_sha256(prior_csv)),
        HistorySource(path=str(placebo_csv), sha256=_sha256(placebo_csv)),
    )
    total_seconds = perf_counter() - started
    (output_directory / "execution_time.txt").write_text(
        f"total_execution_seconds={total_seconds:.3f}\n"
        f"total_execution_time={_duration(total_seconds)}\n",
        encoding="utf-8",
    )
    print(f"Wrote division-initialization artifacts to {output_directory.resolve()}")
    print(f"Total execution time: {_duration(total_seconds)} ({total_seconds:.3f} seconds)")


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--prior-csv", required=True, type=Path)
    parser.add_argument(
        "--placebo-envelope-csv",
        required=True,
        type=Path,
    )
    parser.add_argument("--end", required=True, metavar="YYYY/MM")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("files/output/prediction/division_initialisation"),
    )
    return parser.parse_args()


def _date(value: str) -> Date:
    year, month = (int(part) for part in value.split("/"))
    return Date(Year(year), Month(month))


def _sha256(filename: Path) -> str:
    digest = hashlib.sha256()
    with filename.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _duration(seconds: float) -> str:
    return str(timedelta(seconds=round(seconds)))


if __name__ == "__main__":
    main()
