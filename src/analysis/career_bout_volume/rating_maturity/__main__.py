"""Run the declared historical rating-maturity investigation."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis.elo_model_selection.model import (
    DEFAULT_K_CONFIG,
    DEFAULT_PRIOR_CSV,
    load_adopted_prior,
)
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .analysis import run_probe
from .model import ProbeDefinition
from .reports import DEFAULT_OUTPUT_ROOT, SourceIdentity, file_sha256, write_outputs


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1989_01 to 2026_11.zip")
DEFAULT_START = "1989/01"
DEFAULT_END = "2026/07"


def main() -> None:
    args = _parser().parse_args()
    history_zip = args.history_zip.resolve()
    prior_path = args.prior_csv.resolve()
    k_path = args.k_config.resolve()
    start = _date(DEFAULT_START)
    end = _date(args.end)
    print(f"Loading History: {history_zip}")
    history = load_history_with_annotations(str(history_zip.with_suffix("")))
    prior = load_adopted_prior(prior_path)
    divisional_k = load_divisional_k_fn(k_path)
    definition = ProbeDefinition(start_basho=str(start), end_basho=str(end))
    print(f"Running rating-maturity replay: {start} to {end}")
    result = run_probe(
        history,
        start_date=start,
        end_date=end,
        prior=prior,
        divisional_k=divisional_k,
        definition=definition,
    )
    print("Writing CSV, HTML, manifest and findings artifacts")
    outputs = write_outputs(
        result,
        SourceIdentity(
            history_path=str(history_zip), history_sha256=file_sha256(history_zip),
            prior_path=str(prior_path), prior_sha256=prior.sha256,
            k_config_path=str(k_path), k_config_sha256=file_sha256(k_path),
        ),
        output_root=args.output_root,
    )
    print(f"Basho: {result.history_basho_count}")
    print(f"Rikishi-basho observations: {len(result.maturity_rows)}")
    print(f"Eligible bouts: {result.rated_bout_count}")
    print(f"Model-state exclusions: {result.model_state_exclusion_count}")
    print(f"Run directory: {outputs.run_directory}")
    print(f"Findings: {outputs.findings}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--end", default=DEFAULT_END, metavar="YYYY/MM")
    parser.add_argument("--prior-csv", type=Path, default=DEFAULT_PRIOR_CSV)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def _date(value: str) -> Date:
    year, month = (int(part) for part in value.split("/"))
    return Date(Year(year), Month(month))


if __name__ == "__main__":
    main()

