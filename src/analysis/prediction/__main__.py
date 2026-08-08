"""Command-line application for the canonical Proposal 1 run."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .definition import Proposal1Definition
from .output import HistorySource, write_proposal_1_outputs
from .run import run_proposal_1


def main() -> None:
    arguments = _arguments()
    history_zip = arguments.history_zip.resolve()
    end_date = _date(arguments.end)
    history = load_history_with_annotations(str(history_zip.with_suffix("")))
    result = run_proposal_1(history, Proposal1Definition(end_date=end_date))
    output_directory = (
        arguments.output_root
        / f"proposal_1_{str(result.definition.start_date).replace('/', '_')}_to_{str(end_date).replace('/', '_')}"
    )
    write_proposal_1_outputs(
        result,
        output_directory,
        HistorySource(path=str(history_zip), sha256=_sha256(history_zip)),
    )
    print(f"Wrote Proposal 1 artifacts to {output_directory.resolve()}")


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--end", required=True, metavar="YYYY/MM")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("files/output/prediction/proposal_1"),
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


if __name__ == "__main__":
    main()
