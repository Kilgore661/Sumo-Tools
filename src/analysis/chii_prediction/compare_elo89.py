"""Run the frozen matched production Elo-89 versus higher-chii comparison."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.analysis.elo89.config import ACCEPTED_PRIOR_PATH
from src.analysis.elo89.prior_loader import load_paired_prior
from src.analysis.elo89.producer import DEFAULT_K_CONFIG
from src.analysis.elo89.replay import Q, replay_elo89
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.prediction.bouts import select_rated_bouts
from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from .__main__ import parse_date
from .comparison import (
    DEFAULT_BOOTSTRAP_REPLICATES,
    DEFAULT_BOOTSTRAP_SEED,
    compare_run,
)
from .comparison_output import write_comparison_outputs


REPLAY_ORIGIN = parse_date("1989/01")
DEFAULT_EVALUATION_END = parse_date("2026/11")
DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1989_01 to 2026_11.zip")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/chii_prediction")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--evaluation-start", type=parse_date, default=REPLAY_ORIGIN)
    parser.add_argument("--evaluation-end", type=parse_date, default=DEFAULT_EVALUATION_END)
    parser.add_argument("--prior", type=Path, default=ACCEPTED_PRIOR_PATH)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--bootstrap-replicates", type=int, default=DEFAULT_BOOTSTRAP_REPLICATES)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    source = args.history_zip.resolve()
    prior_path = args.prior.resolve()
    k_path = args.k_config.resolve()
    for label, path in (("History zip", source), ("prior", prior_path), ("K config", k_path)):
        if not path.is_file():
            parser.error(f"{label} not found: {path}")
    if source.suffix.lower() != ".zip":
        parser.error(f"History source must be a zip: {source}")
    if args.evaluation_start < REPLAY_ORIGIN:
        parser.error("Evaluation cannot begin before the frozen 1989/01 replay origin")
    if args.evaluation_end < args.evaluation_start:
        parser.error("Evaluation end must not precede evaluation start")

    history = load_history_with_annotations(str(source.with_suffix("")))
    dates = sorted(history)
    if not dates:
        parser.error("History is empty")
    if dates[0] != REPLAY_ORIGIN:
        parser.error(f"History must begin at 1989/01; represented start is {dates[0]}")
    if args.evaluation_end > dates[-1]:
        parser.error(
            f"Evaluation ends at {args.evaluation_end}, after represented History end {dates[-1]}"
        )
    if args.evaluation_start not in history or args.evaluation_end not in history:
        parser.error("Both evaluation boundaries must be represented basho")

    prior = load_paired_prior(prior_path)
    run = replay_elo89(
        history=history,
        start_date=REPLAY_ORIGIN,
        end_date=dates[-1],
        prior=prior,
        divisional_k=load_divisional_k_fn(k_path),
        q=Q,
    )
    selection = select_rated_bouts(
        history, start_date=args.evaluation_start, end_date=args.evaluation_end
    )
    result = compare_run(
        run,
        evaluation_start=args.evaluation_start,
        evaluation_end=args.evaluation_end,
        raw_result_count=selection.raw_result_count,
        rated_bout_count=selection.rated_bout_count,
        excluded_fusen_count=selection.excluded_fusen_count,
        excluded_draw_count=selection.excluded_draw_count,
        bootstrap_replicates=args.bootstrap_replicates,
        bootstrap_seed=args.bootstrap_seed,
    )
    paths = write_comparison_outputs(
        result=result,
        output_root=args.output_root,
        history_source=source,
        history_sha256=_sha256(source),
        represented_start=str(dates[0]),
        represented_end=str(dates[-1]),
        prior_source=prior.source_path,
        prior_sha256=prior.sha256,
        k_config_path=k_path,
        k_config_sha256=_sha256(k_path),
        q=Q,
    )
    print(paths.report.read_text(encoding="utf-8"))
    print(f"Outputs: {paths.root.resolve()}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
