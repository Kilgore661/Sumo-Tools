"""Run the retrospective trailing-10 Chii initialization experiment."""

from __future__ import annotations

import argparse
import gc
import hashlib
from pathlib import Path

from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .chii_initialisation import run_chii_initialised_elo
from .chii_initialisation_output import write_chii_initialisation_outputs
from .chii_prior import build_chii_prior
from .definition import Proposal1Definition
from .output import HistorySource
from .run import run_proposal_1
from .scope_summary import summarize_rolling_signs, summarize_scopes
from .sekitori import evaluate_sekitori_bouts, evaluate_sub_sekitori_bouts


def main() -> None:
    arguments = _arguments()
    history_zip = arguments.history_zip.resolve()
    end_date = _date(arguments.end)
    history = load_history_with_annotations(str(history_zip.with_suffix("")))
    definition = Proposal1Definition(end_date=end_date)

    baseline = run_proposal_1(history, definition)
    prior = build_chii_prior(
        history,
        baseline,
        trailing_observations=10,
        common_mean=definition.initial_rating,
    )
    baseline_summaries = summarize_scopes(history, baseline)
    baseline_signs = summarize_rolling_signs(
        history,
        baseline,
        definition.rolling_windows,
    )
    del baseline
    gc.collect()

    result = run_chii_initialised_elo(history, definition, prior)
    chii_summaries = summarize_scopes(history, result)
    chii_signs = summarize_rolling_signs(
        history,
        result,
        definition.rolling_windows,
    )
    sekitori = evaluate_sekitori_bouts(history, result)
    sub_sekitori = evaluate_sub_sekitori_bouts(history, result)
    output_directory = (
        arguments.output_root
        / f"chii_initialisation_{str(definition.start_date).replace('/', '_')}_to_{str(end_date).replace('/', '_')}"
    )
    write_chii_initialisation_outputs(
        result,
        sekitori,
        sub_sekitori,
        baseline_summaries,
        chii_summaries,
        baseline_signs,
        chii_signs,
        output_directory,
        HistorySource(path=str(history_zip), sha256=_sha256(history_zip)),
    )
    print(f"Wrote Chii-initialization artifacts to {output_directory.resolve()}")


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--end", required=True, metavar="YYYY/MM")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("files/output/prediction/chii_initialisation"),
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
