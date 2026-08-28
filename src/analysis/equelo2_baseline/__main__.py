"""Run the first full-history Equelo2 baseline on frozen Elo-89 priors."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from src.analysis.bout_data_completeness.__main__ import load_history
from src.analysis.elo_model_selection.model import DEFAULT_K_CONFIG
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .analysis import ExperimentDefinition, run_experiment


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/equelo2_baseline")
DEFAULT_ELO89_PRIOR = Path("files/output/analysis/equelo_bkp1/prior.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        default=None,
        help="Use an annotated History zip instead of the live store.",
    )
    parser.add_argument("--start", type=_date, default=_date("1958/01"))
    parser.add_argument("--end", type=_date, default=_date("2026/07"))
    parser.add_argument(
        "--reference-start", type=_date, default=_date("1989/01")
    )
    parser.add_argument("--boundary", type=_date, default=_date("1988/11"))
    parser.add_argument("--prior-csv", type=Path, default=DEFAULT_ELO89_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    started = perf_counter()
    args = build_parser().parse_args(argv)
    if args.start > args.end:
        raise ValueError(f"Start {args.start} is after end {args.end}")
    if args.boundary >= args.reference_start:
        raise ValueError("Boundary must precede the Elo-89 reference start")

    history, source = load_history(args.history_zip)
    output = args.output_root / (
        f"full_history_{str(args.start).replace('/', '_')}_to_"
        f"{str(args.end).replace('/', '_')}"
    )
    print(f"History source: {source.kind}", flush=True)
    print(f"Candidate interval: {args.start} to {args.end}", flush=True)
    print(f"Output: {output.resolve()}", flush=True)
    definition = ExperimentDefinition(
        start_date=args.start,
        end_date=args.end,
        reference_start_date=args.reference_start,
        boundary_date=args.boundary,
    )
    results = run_experiment(
        history,
        definition,
        prior_path=args.prior_csv,
        k_config_path=args.k_config,
        divisional_k=load_divisional_k_fn(args.k_config.resolve()),
        output_root=output,
        history_source=asdict(source),
        progress=lambda message: print(message, flush=True),
    )
    print(f"Findings: {results.findings.resolve()}", flush=True)
    print(f"Manifest: {results.manifest.resolve()}", flush=True)
    print(f"Total wall-clock time: {perf_counter() - started:.2f} seconds", flush=True)
    return 0


def _date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/", maxsplit=1)
        year = int(year_text)
        month = int(month_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"Expected YYYY/MM, got {value!r}") from error
    if month not in (1, 3, 5, 7, 9, 11):
        raise argparse.ArgumentTypeError(f"Not a basho month: {value}")
    return Date(Year(year), Month(month))


if __name__ == "__main__":
    raise SystemExit(main())
