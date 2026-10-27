"""Record an open-ended P1 fixed-point trajectory at durable checkpoints."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from time import perf_counter

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo_bkp1.params import (
    DEFAULT_K_CONFIG,
    MODEL_BASE,
    MODEL_Q,
    load_divisional_k,
)
from src.analysis.equelo_bkp1.simulate import BoutEligibility, count_eligibility
from src.analysis.equelo_bkp1.solve import initial_prior_state, iterate_once
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.validation.provenance import history_fingerprint


DEFAULT_OUTPUT_PARENT = Path(
    "src/validation/elo89-expert-account/Matters Arising/"
    "P1 Fixed-Point Trajectory/output"
)
ELO89_START = Date.from_ints(1989, 1)
ITERATION_FIELDS = (
    "iteration",
    "max_prior_change",
    "max_change_chii",
    "max_change_observation_count",
    "mean_recentering_adjustment",
    "minimum_recentering_adjustment",
    "maximum_recentering_adjustment",
    "gradient_10",
    "elapsed_seconds",
    "checkpoint_due",
)


def run_trajectory(
    history: History,
    *,
    output_root: Path,
    k_config_path: Path = DEFAULT_K_CONFIG,
    eligibility: BoutEligibility = BoutEligibility.P1_WL,
    report_every: int = 10,
    checkpoint_every: int = 100,
    history_source: dict[str, object] | None = None,
    _iteration_limit: int | None = None,
) -> Path:
    """Run until process termination, writing each completed iteration."""

    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite trajectory: {output_root}")
    if report_every < 1 or checkpoint_every < 1:
        raise ValueError("Report and checkpoint intervals must be positive")
    if _iteration_limit is not None and _iteration_limit < 1:
        raise ValueError("Internal iteration limit must be positive")
    dates = sorted(history)
    if not dates or dates[0] != ELO89_START:
        first = None if not dates else str(dates[0])
        raise ValueError(
            "P1 trajectory History must begin at 1989/01; "
            f"received {first!r}"
        )

    k_path = k_config_path.resolve()
    source = dict(history_source or {"kind": "provided History"})
    source["selected_history_sha256"] = history_fingerprint(history)
    priors, support = initial_prior_state(history)
    eligibility_counts = asdict(count_eligibility(history, eligibility))
    started_at = datetime.now(timezone.utc).isoformat()

    output_root.mkdir(parents=True)
    checkpoints_root = output_root / "checkpoints"
    checkpoints_root.mkdir()
    ledger = output_root / "iterations.csv"
    with ledger.open("x", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=ITERATION_FIELDS).writeheader()

    manifest = {
        "schema_version": 1,
        "experiment": "open-ended P1 fixed-point trajectory",
        "mode": "iteration-controlled; no epsilon or iteration ceiling",
        "started_at_utc": started_at,
        "history": {
            **source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "basho_count": len(dates),
            "preprocessing": "oracle annotation_only",
        },
        "model": {
            "eligibility": eligibility.value,
            "eligibility_counts": eligibility_counts,
            "q": MODEL_Q,
            "base": MODEL_BASE,
            "population_policy": "legacy_departure",
            "recentering": "support-proportional",
            "initial_map": f"every literal chii set to {MODEL_BASE}",
            "k_config": _file_identity(k_path),
        },
        "recording": {
            "report_every": report_every,
            "checkpoint_every": checkpoint_every,
            "gradient_window": 10,
            "ledger": ledger.name,
            "checkpoints": checkpoints_root.name,
        },
        "prior_count": len(priors),
    }
    _write_json(output_root / "manifest.json", manifest)

    divisional_k = load_divisional_k(k_path)
    deltas: list[float] = []
    started = perf_counter()
    print(
        f"P1 trajectory: eligibility={eligibility.value}; "
        f"chii={len(priors):,}; checkpoint every {checkpoint_every} iterations",
        flush=True,
    )
    print(f"Output: {output_root.resolve()}", flush=True)
    print(
        "iteration  max-change  chii       support  gradient-10  "
        "elapsed    checkpoint",
        flush=True,
    )

    iteration = 0
    while True:
        iteration += 1
        priors, row = iterate_once(
            history,
            priors,
            support,
            divisional_k,
            iteration=iteration,
            eligibility=eligibility,
        )
        deltas.append(row.max_prior_change)
        gradient = None
        if len(deltas) >= 11:
            gradient = (deltas[-1] - deltas[-11]) / 10.0
        elapsed = perf_counter() - started
        checkpoint_due = iteration % checkpoint_every == 0
        _append_iteration(
            ledger,
            {
                **asdict(row),
                "gradient_10": "" if gradient is None else gradient,
                "elapsed_seconds": elapsed,
                "checkpoint_due": checkpoint_due,
            },
        )

        checkpoint_saved = False
        if checkpoint_due:
            _write_checkpoint(
                checkpoints_root,
                iteration=iteration,
                priors=priors,
                support=support,
                row=row,
                gradient=gradient,
                elapsed=elapsed,
                root_manifest=manifest,
            )
            checkpoint_saved = True

        if iteration == 1 or iteration % report_every == 0 or checkpoint_saved:
            _print_progress(row, gradient, elapsed, checkpoint_saved)

        if _iteration_limit is not None and iteration >= _iteration_limit:
            return output_root


def _write_checkpoint(
    checkpoints_root: Path,
    *,
    iteration: int,
    priors: dict[Chii, float],
    support: dict[Chii, int],
    row,
    gradient: float | None,
    elapsed: float,
    root_manifest: dict[str, object],
) -> Path:
    name = f"iteration-{iteration:06d}"
    final = checkpoints_root / name
    temporary = checkpoints_root / f".{name}.tmp"
    if final.exists() or temporary.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {final}")
    temporary.mkdir()
    prior_path = temporary / "prior.csv"
    _write_prior(prior_path, priors, support)
    checkpoint_manifest = {
        "schema_version": 1,
        "kind": "P1 fixed-point trajectory checkpoint",
        "iteration": iteration,
        "current_maximum_change": row.max_prior_change,
        "maximum_change_chii": row.max_change_chii,
        "maximum_change_support": row.max_change_observation_count,
        "gradient_10": gradient,
        "elapsed_seconds": elapsed,
        "eligibility": root_manifest["model"]["eligibility"],  # type: ignore[index]
        "history_selected_sha256": root_manifest["history"][  # type: ignore[index]
            "selected_history_sha256"
        ],
        "q": MODEL_Q,
        "base": MODEL_BASE,
        "trajectory_manifest": {
            "path": "../../manifest.json",
            "sha256": _sha256(checkpoints_root.parent / "manifest.json"),
        },
        "prior": {"path": "prior.csv", "sha256": _sha256(prior_path)},
    }
    _write_json(temporary / "manifest.json", checkpoint_manifest)
    temporary.rename(final)
    return final


def _write_prior(
    path: Path,
    priors: dict[Chii, float],
    support: dict[Chii, int],
) -> None:
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=("chii", "ordinal", "support", "rating")
        )
        writer.writeheader()
        for chii in sorted(priors, key=Chii.ordinal):
            writer.writerow(
                {
                    "chii": str(chii),
                    "ordinal": chii.ordinal(),
                    "support": support[chii],
                    "rating": priors[chii],
                }
            )


def _append_iteration(path: Path, row: dict[str, object]) -> None:
    with path.open("a", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=ITERATION_FIELDS).writerow(row)
        stream.flush()


def _print_progress(row, gradient, elapsed, checkpoint_saved) -> None:
    gradient_text = "-" if gradient is None else f"{gradient:+.6f}"
    print(
        f"{row.iteration:9d}  {row.max_prior_change:10.4f}  "
        f"{row.max_change_chii:<9}  {row.max_change_observation_count:7d}  "
        f"{gradient_text:>11}  {_elapsed(elapsed):>9}  "
        f"{'saved' if checkpoint_saved else ''}",
        flush=True,
    )


def _elapsed(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _selected_history(full: History, start: Date, end: Date | None) -> History:
    selected = History(
        {
            date: full[date]
            for date in sorted(full)
            if date >= start and (end is None or date <= end)
        }
    )
    if not selected:
        raise ValueError("Selected trajectory interval is empty")
    return make_oracle(selected, collapse_mode="annotation_only").history


def _load_history(path: Path) -> History:
    resolved = path.resolve()
    zip_path = (
        resolved
        if resolved.suffix.lower() == ".zip"
        else resolved.with_suffix(".zip")
    )
    if not zip_path.is_file():
        raise FileNotFoundError(f"History zip not found: {zip_path}")
    return load_history_with_annotations(str(zip_path.with_suffix("")))


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM")
    return Date.from_ints(int(match.group(1)), int(match.group(2)))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--start", type=_parse_date, default=ELO89_START)
    parser.add_argument("--end", type=_parse_date)
    parser.add_argument(
        "--eligibility",
        choices=tuple(item.value for item in BoutEligibility),
        required=True,
    )
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--report-every", type=int, default=10)
    parser.add_argument("--checkpoint-every", type=int, default=100)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    full = _load_history(args.history_zip)
    history = _selected_history(full, args.start, args.end)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = args.output or DEFAULT_OUTPUT_PARENT / (
        f"{args.eligibility}-trajectory-{stamp}"
    )
    source_path = args.history_zip.resolve()
    if source_path.suffix.lower() != ".zip":
        source_path = source_path.with_suffix(".zip")
    run_trajectory(
        history,
        output_root=output,
        k_config_path=args.k_config,
        eligibility=BoutEligibility(args.eligibility),
        report_every=args.report_every,
        checkpoint_every=args.checkpoint_every,
        history_source={
            "kind": "annotated History zip",
            **_file_identity(source_path),
        },
    )
    return 0


def _file_identity(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "sha256": _sha256(resolved),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
