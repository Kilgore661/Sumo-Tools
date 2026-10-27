"""Fit and score P1-WL priors at a descending sequence of epsilon values."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from time import perf_counter

from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    ModelSpec,
    _context,
    _run_model,
    rank_pair,
    score,
)
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.equelo_bkp1.params import (
    DEFAULT_K_CONFIG,
    MODEL_BASE,
    MODEL_Q,
    load_divisional_k,
)
from src.analysis.equelo_bkp1.simulate import BoutEligibility, count_eligibility
from src.analysis.equelo_bkp1.solve import initial_prior_state, iterate_once
from src.analysis.equelo_population_policy.predict_candidate import load_alpha_prior
from src.analysis.prediction.bouts import select_rated_bouts
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.validation.provenance import history_fingerprint


DEFAULT_EPSILONS = (
    1000.0,
    300.0,
    100.0,
    50.0,
    30.0,
    20.0,
    15.0,
    12.0,
    10.0,
    9.0,
    8.5,
    8.0,
    7.0,
    6.0,
    5.0,
    4.0,
    3.0,
    2.0,
    1.0,
    0.5,
    0.3,
    0.2,
    0.1,
)
DEFAULT_OUTPUT_PARENT = Path(
    "src/validation/elo89-expert-account/Matters Arising/"
    "P1 Epsilon Sweep/output"
)
DEFAULT_REFERENCE_PRIOR = Path("files/output/analysis/equelo_bkp1/prior.csv")
ELO89_START = Date.from_ints(1989, 1)
ITERATION_FIELDS = (
    "iteration",
    "max_prior_change",
    "max_change_chii",
    "max_change_observation_count",
    "mean_recentering_adjustment",
    "minimum_recentering_adjustment",
    "maximum_recentering_adjustment",
    "elapsed_seconds",
)
RESULT_FIELDS = (
    "epsilon",
    "iteration",
    "maximum_change",
    "mean_log_loss",
    "mean_brier_loss",
    "log_difference_from_reference_p1",
    "brier_difference_from_reference_p1",
    "minimum_rating",
    "maximum_rating",
    "elapsed_seconds",
    "prior_path",
    "prior_sha256",
)


def run_sweep(
    history: History,
    *,
    output_root: Path,
    epsilons: tuple[float, ...] = DEFAULT_EPSILONS,
    reference_prior_path: Path = DEFAULT_REFERENCE_PRIOR,
    k_config_path: Path = DEFAULT_K_CONFIG,
    eligibility: BoutEligibility = BoutEligibility.P1_WL,
    history_source: dict[str, object] | None = None,
) -> Path:
    """Iterate once, retaining and scoring the first state below each epsilon."""

    thresholds = _validate_epsilons(epsilons)
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite epsilon sweep: {output_root}")
    dates = sorted(history)
    if not dates or dates[0] != ELO89_START:
        first = None if not dates else str(dates[0])
        raise ValueError(
            "P1 epsilon sweep History must begin at 1989/01; "
            f"received {first!r}"
        )

    started = perf_counter()
    output_root.mkdir(parents=True)
    priors_root = output_root / "priors"
    priors_root.mkdir()
    iteration_path = output_root / "iterations.csv"
    result_path = output_root / "results.csv"
    _write_header(iteration_path, ITERATION_FIELDS)
    _write_header(result_path, RESULT_FIELDS)

    source = dict(history_source or {"kind": "provided History"})
    source["selected_history_sha256"] = history_fingerprint(history)
    k_path = k_config_path.resolve()
    reference_path = reference_prior_path.resolve()
    selection = select_rated_bouts(
        history, start_date=dates[0], end_date=dates[-1]
    )
    contexts = tuple(_context(history, bout) for bout in selection.bouts)
    definition = ComparisonDefinition(
        start_date=dates[0], end_date=dates[-1], q=MODEL_Q
    )
    forecast_k = load_divisional_k_fn(k_path)
    fit_k = load_divisional_k(k_path)

    reference_prior, reference_conversion = load_alpha_prior(reference_path)
    reference_spec = ModelSpec(  # type: ignore[arg-type]
        "B_kP1", divisional_k=True, informed_prior=True
    )
    print(
        f"Reference P1: scoring {selection.rated_bout_count:,} bouts",
        flush=True,
    )
    reference_run = _run_model(
        contexts, definition, reference_spec, reference_prior, forecast_k
    )
    reference_losses = tuple(score(row) for row in reference_run.forecasts)
    reference_log, reference_brier = _mean_losses(reference_losses)
    del reference_run

    manifest = {
        "schema_version": 1,
        "experiment": "P1-WL epsilon stopping-threshold sweep",
        "status": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "history": {
            **source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "basho_count": len(dates),
            "preprocessing": "oracle annotation_only",
        },
        "selection": {
            "raw_result_count": selection.raw_result_count,
            "rated_bout_count": selection.rated_bout_count,
            "excluded_fusen_count": selection.excluded_fusen_count,
            "excluded_draw_count": selection.excluded_draw_count,
        },
        "model": {
            "eligibility": eligibility.value,
            "eligibility_counts": asdict(count_eligibility(history, eligibility)),
            "q": MODEL_Q,
            "base": MODEL_BASE,
            "population_policy": "legacy_departure",
            "recentering": "support-proportional",
            "initial_map": f"every literal chii set to {MODEL_BASE}",
            "convergence_rule": "first iteration with maximum change < epsilon",
            "k_config": _file_identity(k_path),
        },
        "epsilons_descending": list(thresholds),
        "reference": {
            "name": "published P1",
            "prior": _file_identity(reference_path),
            "source_row_count": reference_conversion.source_row_count,
            "pair_count": reference_conversion.pair_count,
            "pairing_rule": "unweighted mean of available east/west literal-chii ratings",
            "mean_log_loss": reference_log,
            "mean_brier_loss": reference_brier,
        },
        "evaluation": {
            "kind": "retrospective initialisation forecast replay",
            "warning": "The fitted prior and scores use the same historical interval; this is model-selection evidence, not prospective validation.",
        },
        "outputs": {
            "iterations": iteration_path.name,
            "results": result_path.name,
            "priors": priors_root.name,
        },
    }
    _write_json(output_root / "manifest.json", manifest)

    priors, support = initial_prior_state(history)
    pending = list(thresholds)
    iteration = 0
    print(
        " epsilon  iteration  max-change  log-loss  brier-loss  "
        "log-v-P1   elapsed",
        flush=True,
    )
    while pending:
        iteration += 1
        priors, iteration_row = iterate_once(
            history,
            priors,
            support,
            fit_k,
            iteration=iteration,
            eligibility=eligibility,
        )
        elapsed = perf_counter() - started
        _append_csv(
            iteration_path,
            ITERATION_FIELDS,
            {**asdict(iteration_row), "elapsed_seconds": elapsed},
        )
        crossed: list[float] = []
        while pending and iteration_row.max_prior_change < pending[0]:
            crossed.append(pending.pop(0))
        if not crossed:
            continue

        prior_name = f"iteration-{iteration:06d}.csv"
        prior_path = priors_root / prior_name
        if not prior_path.exists():
            _write_prior(prior_path, priors, support)
        candidate = _adopted_prior(priors, prior_path)
        candidate_run = _run_model(
            contexts, definition, reference_spec, candidate, forecast_k
        )
        candidate_losses = tuple(score(row) for row in candidate_run.forecasts)
        mean_log, mean_brier = _mean_losses(candidate_losses)
        del candidate_run, candidate_losses
        elapsed = perf_counter() - started
        for epsilon in crossed:
            row = {
                "epsilon": epsilon,
                "iteration": iteration,
                "maximum_change": iteration_row.max_prior_change,
                "mean_log_loss": mean_log,
                "mean_brier_loss": mean_brier,
                "log_difference_from_reference_p1": mean_log - reference_log,
                "brier_difference_from_reference_p1": mean_brier - reference_brier,
                "minimum_rating": min(priors.values()),
                "maximum_rating": max(priors.values()),
                "elapsed_seconds": elapsed,
                "prior_path": f"priors/{prior_name}",
                "prior_sha256": _sha256(prior_path),
            }
            _append_csv(result_path, RESULT_FIELDS, row)
            print(
                f"{epsilon:8g}  {iteration:9d}  "
                f"{iteration_row.max_prior_change:10.4f}  "
                f"{mean_log:8.6f}  {mean_brier:10.6f}  "
                f"{mean_log - reference_log:+9.6f}  "
                f"{_elapsed(elapsed):>9}",
                flush=True,
            )

    rows = _read_results(result_path)
    best_log = min(rows, key=lambda row: float(row["mean_log_loss"]))
    best_brier = min(rows, key=lambda row: float(row["mean_brier_loss"]))
    manifest["status"] = "complete"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["runtime_seconds"] = perf_counter() - started
    manifest["best"] = {
        "mean_log_loss": _result_identity(best_log, "mean_log_loss"),
        "mean_brier_loss": _result_identity(best_brier, "mean_brier_loss"),
    }
    _write_json(output_root / "manifest.json", manifest)
    (output_root / "findings.md").write_text(
        _findings(rows, reference_log, reference_brier), encoding="utf-8"
    )
    print(f"Output: {output_root.resolve()}", flush=True)
    return output_root


def _validate_epsilons(values: tuple[float, ...]) -> tuple[float, ...]:
    if not values:
        raise ValueError("At least one epsilon is required")
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Epsilons must be positive finite numbers")
    if len(set(values)) != len(values):
        raise ValueError("Epsilons must be unique")
    return tuple(sorted(values, reverse=True))


def _adopted_prior(priors: dict[Chii, float], source: Path) -> AdoptedPrior:
    grouped: dict[str, list[float]] = defaultdict(list)
    for chii, rating in priors.items():
        grouped[rank_pair(chii)].append(rating)
    ratings = {
        pair: sum(values) / len(values) for pair, values in grouped.items()
    }
    return AdoptedPrior(
        source_path=str(source.resolve()),
        sha256=_sha256(source),
        rating_by_pair=ratings,
        fallback_rating=min(ratings.values()),
    )


def _mean_losses(losses: tuple[tuple[float, float], ...]) -> tuple[float, float]:
    if not losses:
        raise ValueError("Cannot score an empty forecast set")
    count = len(losses)
    return (
        sum(value[0] for value in losses) / count,
        sum(value[1] for value in losses) / count,
    )


def _write_prior(path: Path, priors: dict[Chii, float], support: dict[Chii, int]) -> None:
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


def _write_header(path: Path, fields: tuple[str, ...]) -> None:
    with path.open("x", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=fields).writeheader()


def _append_csv(path: Path, fields: tuple[str, ...], row: dict[str, object]) -> None:
    with path.open("a", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=fields).writerow(row)
        stream.flush()


def _read_results(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _result_identity(row: dict[str, str], metric: str) -> dict[str, object]:
    return {
        "epsilon": float(row["epsilon"]),
        "iteration": int(row["iteration"]),
        "maximum_change": float(row["maximum_change"]),
        "value": float(row[metric]),
    }


def _findings(
    rows: list[dict[str, str]], reference_log: float, reference_brier: float
) -> str:
    best_log = min(rows, key=lambda row: float(row["mean_log_loss"]))
    best_brier = min(rows, key=lambda row: float(row["mean_brier_loss"]))
    lines = [
        "# P1-WL epsilon sweep", "",
        "Lower loss is better. The prior and evaluation use the same historical interval, so these are retrospective model-selection results.", "",
        f"Published P1: log loss {reference_log:.9f}; Brier loss {reference_brier:.9f}.", "",
        "| Epsilon | Iteration | Maximum change | Log loss | Brier loss | Log difference from P1 |", "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {float(row['epsilon']):g} | {int(row['iteration'])} | "
            f"{float(row['maximum_change']):.6f} | "
            f"{float(row['mean_log_loss']):.9f} | "
            f"{float(row['mean_brier_loss']):.9f} | "
            f"{float(row['log_difference_from_reference_p1']):+.9f} |"
        )
    lines.extend([
        "", f"Best log loss: epsilon {float(best_log['epsilon']):g} at iteration {best_log['iteration']} ({float(best_log['mean_log_loss']):.9f}).",
        f"Best Brier loss: epsilon {float(best_brier['epsilon']):g} at iteration {best_brier['iteration']} ({float(best_brier['mean_brier_loss']):.9f}).", "",
    ])
    return "\n".join(lines)


def _selected_history(full: History, start: Date, end: Date | None) -> History:
    selected = History(
        {
            date: full[date]
            for date in sorted(full)
            if date >= start and (end is None or date <= end)
        }
    )
    if not selected:
        raise ValueError("Selected epsilon-sweep interval is empty")
    return make_oracle(selected, collapse_mode="annotation_only").history


def _load_history(path: Path) -> History:
    resolved = path.resolve()
    zip_path = resolved if resolved.suffix.lower() == ".zip" else resolved.with_suffix(".zip")
    if not zip_path.is_file():
        raise FileNotFoundError(f"History zip not found: {zip_path}")
    return load_history_with_annotations(str(zip_path.with_suffix("")))


def _parse_date(value: str) -> Date:
    try:
        year, month = value.split("-", maxsplit=1)
        if len(year) != 4 or len(month) != 2:
            raise ValueError
        return Date.from_ints(int(year), int(month))
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected YYYY-MM") from error


def _parse_epsilons(value: str) -> tuple[float, ...]:
    try:
        parsed = tuple(float(item.strip()) for item in value.split(",") if item.strip())
        return _validate_epsilons(parsed)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--start", type=_parse_date, default=ELO89_START)
    parser.add_argument("--end", type=_parse_date)
    parser.add_argument(
        "--epsilons",
        type=_parse_epsilons,
        default=DEFAULT_EPSILONS,
        help="comma-separated thresholds (default: %(default)s)",
    )
    parser.add_argument(
        "--eligibility",
        choices=tuple(item.value for item in BoutEligibility),
        default=BoutEligibility.P1_WL.value,
    )
    parser.add_argument("--reference-prior", type=Path, default=DEFAULT_REFERENCE_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    full = _load_history(args.history_zip)
    history = _selected_history(full, args.start, args.end)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = args.output or DEFAULT_OUTPUT_PARENT / f"epsilon-sweep-{stamp}"
    source_path = args.history_zip.resolve()
    if source_path.suffix.lower() != ".zip":
        source_path = source_path.with_suffix(".zip")
    run_sweep(
        history,
        output_root=output,
        epsilons=args.epsilons,
        reference_prior_path=args.reference_prior,
        k_config_path=args.k_config,
        eligibility=BoutEligibility(args.eligibility),
        history_source={"kind": "annotated History zip", **_file_identity(source_path)},
    )
    return 0


def _elapsed(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _file_identity(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    return {"path": str(resolved), "sha256": _sha256(resolved)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
