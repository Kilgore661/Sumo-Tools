"""Run the controlled retrospective post-1988 Elo model comparison."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .evaluation import evaluate
from .model import (
    ComparisonDefinition,
    DEFAULT_K_CONFIG,
    DEFAULT_PRIOR_CSV,
    load_adopted_prior,
    run_comparison,
)
from .output import HistorySource, write_outputs


def main() -> None:
    args = _parser().parse_args()
    history_zip = args.history_zip.resolve()
    history = load_history_with_annotations(str(history_zip.with_suffix("")))
    definition = ComparisonDefinition(
        start_date=Date(Year(1989), Month(1)),
        end_date=_date(args.end),
        bootstrap_resamples=args.bootstrap_resamples,
        calibration_bin_width=args.calibration_bin_width,
        calibration_min_bin_participants=args.calibration_min_bin_participants,
    )
    prior = load_adopted_prior(args.prior_csv)
    run = run_comparison(
        history, definition, prior=prior, k_config=args.k_config
    )
    evaluation = evaluate(run)
    output_directory = args.output_root / (
        f"retrospective_{str(definition.start_date).replace('/', '_')}_to_"
        f"{str(definition.end_date).replace('/', '_')}"
    )
    write_outputs(
        run,
        evaluation,
        output_directory,
        HistorySource(str(history_zip), _sha256(history_zip)),
    )
    print(f"Wrote Elo model-selection artifacts to {output_directory.resolve()}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--end", required=True, metavar="YYYY/MM")
    parser.add_argument("--prior-csv", type=Path, default=DEFAULT_PRIOR_CSV)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("files/output/analysis/elo_model_selection"),
    )
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--calibration-bin-width", type=float, default=0.05)
    parser.add_argument("--calibration-min-bin-participants", type=int, default=100)
    return parser


def _date(value: str) -> Date:
    year, month = (int(part) for part in value.split("/"))
    return Date(Year(year), Month(month))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
