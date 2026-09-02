"""Generate P2 by preserving P1's six divisional averages."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean
from time import perf_counter

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo_bkp1.params import DEFAULT_K_CONFIG, MODEL_Q, load_divisional_k
from src.infra.connect import connect
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .division import division_name
from .model import DIVISIONS, DivisionIterationRow, IterationRow
from .prior import divisional_targets, load_p1
from .solve import solve


DEFAULT_P1 = Path("files/output/analysis/equelo_bkp1/prior.csv")
DEFAULT_OUTPUT = Path("files/output/analysis/divisional_averages/p2")


def main(argv: list[str] | None = None) -> int:
    started = perf_counter()
    args = _parser().parse_args(argv)
    p1, _p1_support = load_p1(args.p1)
    targets = divisional_targets(p1)
    loaded_history = make_oracle(
        connect(args.start, args.end, use_zip=args.zip),
        collapse_mode="annotation_only",
    ).history
    history = _year_slice(loaded_history, args.start, args.end)

    print("P2 divisional-average fixed point", flush=True)
    print(f"History: {min(history)} to {max(history)}", flush=True)
    print(f"P1: {args.p1.resolve()}", flush=True)
    print("Fixed unweighted literal-chii targets:", flush=True)
    for division in DIVISIONS:
        print(f"  {division:<10} {targets[division]:.6f}", flush=True)

    result = solve(
        history,
        load_divisional_k(args.k_config.resolve()),
        p1=p1,
        targets=targets,
        epsilon=args.epsilon,
        max_iterations=args.max_iterations,
        support_threshold=args.support_threshold,
        progress=_progress,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    comparison = _comparison(result.priors, p1)
    _write_outputs(args, result, p1, comparison)

    elapsed = perf_counter() - started
    print(
        f"P2 {'converged' if result.converged else 'did not converge'} after "
        f"{result.iterations} iterations; final delta={result.final_delta:.6f}",
        flush=True,
    )
    print(f"Output: {args.output.resolve()}", flush=True)
    print(f"Total wall-clock time: {elapsed:.2f} seconds", flush=True)
    return 0 if result.converged else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1989)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--p1", type=Path, default=DEFAULT_P1)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--epsilon", type=float, default=10.0)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--support-threshold", type=int, default=60)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _year_slice(history: History, start: int, end: int) -> History:
    """Enforce the declared interval even when a source returns a wider History."""

    selected = History(
        {
            date: basho
            for date, basho in history.items()
            if start <= int(date.year) <= end
        }
    )
    if not selected:
        raise ValueError(f"History has no basho from {start} through {end}")
    return selected


def _progress(
    row: IterationRow,
    divisions: tuple[DivisionIterationRow, ...],
) -> None:
    print(
        f"[P2] iteration={row.iteration} delta={row.max_prior_change:.6f} "
        f"max={row.max_change_chii} n={row.max_change_observation_count} "
        f"log_loss={row.mean_log_loss:.6f} brier={row.mean_brier_loss:.6f}",
        flush=True,
    )
    for division in divisions:
        print(
            f"     {division.division:<10} raw={division.raw_map_mean:10.3f} "
            f"target={division.target_mean:10.3f} "
            f"P2-P1={division.mean_prior_difference_from_p1:+9.3f} "
            f"MAE={division.mean_absolute_prior_difference_from_p1:9.3f} "
            f"range={division.minimum_prior:9.3f}..{division.maximum_prior:9.3f}",
            flush=True,
        )


def _comparison(
    p2: dict[Chii, float], p1: dict[Chii, float]
) -> list[dict[str, object]]:
    rows = []
    for division in (*DIVISIONS, "All"):
        members = [
            chii
            for chii in p2
            if division == "All" or division_name(chii) == division
        ]
        differences = [p2[chii] - p1[chii] for chii in members]
        rows.append(
            {
                "division": division,
                "chii_count": len(members),
                "p1_mean": fmean(p1[chii] for chii in members),
                "p2_mean": fmean(p2[chii] for chii in members),
                "mean_difference": fmean(differences),
                "mean_absolute_difference": fmean(abs(value) for value in differences),
                "root_mean_square_difference": math.sqrt(
                    fmean(value * value for value in differences)
                ),
                "minimum_difference": min(differences),
                "maximum_difference": max(differences),
            }
        )
    return rows


def _write_outputs(args, result, p1, comparison) -> None:
    _write_csv(
        args.output / "prior.csv",
        [
            {
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "observations": result.support[chii],
                "supported": chii in result.supported_chii,
                "source_chii": str(result.completion_sources[chii]),
                "rating": result.priors[chii],
            }
            for chii in sorted(result.priors, key=lambda item: item.ordinal())
        ],
    )
    _write_csv(
        args.output / "p1_p2_literal.csv",
        [
            {
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "division": division_name(chii),
                "observations": result.support[chii],
                "supported": chii in result.supported_chii,
                "source_chii": str(result.completion_sources[chii]),
                "p1_rating": p1[chii],
                "rating": result.priors[chii],
                "difference_from_p1": result.priors[chii] - p1[chii],
            }
            for chii in sorted(result.priors, key=lambda item: item.ordinal())
        ],
    )
    _write_csv(
        args.output / "division_targets.csv",
        [
            {
                "division": division,
                "target_mean": result.targets[division],
                "chii_count": sum(
                    division_name(chii) == division for chii in result.priors
                ),
            }
            for division in DIVISIONS
        ],
    )
    _write_csv(
        args.output / "iterations.csv",
        [asdict(row) for row in result.iteration_rows],
    )
    _write_csv(
        args.output / "iteration_divisions.csv",
        [asdict(row) for row in result.division_iteration_rows],
    )
    _write_csv(
        args.output / "prior_iterations.csv",
        list(result.prior_iteration_rows),
    )
    final_changes = {
        Chii.from_str(str(row["chii"])): float(row["iteration_change"])
        for row in result.prior_iteration_rows
        if int(row["iteration"]) == result.iterations
    }
    _write_csv(
        args.output / "chii_identifiability_audit.csv",
        [
            {
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "division": division_name(chii),
                "observations": result.support[chii],
                "initialization_observations": result.initialization_support[chii],
                "carried_observations": (
                    result.support[chii] - result.initialization_support[chii]
                ),
                "initialization_fraction": (
                    result.initialization_support[chii] / result.support[chii]
                ),
                "support_threshold": result.support_threshold,
                "supported": chii in result.supported_chii,
                "completion_source_kind": (
                    "direct" if chii in result.supported_chii else "nearest_supported"
                ),
                "completion_source_chii": str(result.completion_sources[chii]),
                "completion_source_chii_ordinal": (
                    result.completion_sources[chii].ordinal()
                ),
                "final_iteration_change": final_changes[chii],
                "absolute_final_iteration_change": abs(final_changes[chii]),
            }
            for chii in sorted(result.priors, key=lambda item: item.ordinal())
        ],
    )
    _write_csv(
        args.output / "final_replay_basho_division_adjustments.csv",
        [asdict(row) for row in result.replay.adjustments],
    )
    _write_csv(args.output / "p1_p2_summary.csv", comparison)

    p1_path = args.p1.resolve()
    k_path = args.k_config.resolve()
    manifest = {
        "experiment": "P2 divisional-average fixed point",
        "baseline_commit": "244f476",
        "start": args.start,
        "end": args.end,
        "q": MODEL_Q,
        "map_recentering_alpha": 1.0,
        "support_threshold": result.support_threshold,
        "supported_chii": len(result.supported_chii),
        "unsupported_chii": len(result.priors) - len(result.supported_chii),
        "unsupported_completion": "nearest supported chii by ordinal; ties upward",
        "population_policy": "fixed_divisional_means_at_basho_start_and_end",
        "target_definition": "unweighted literal-chii division means from P1",
        "targets": result.targets,
        "p1": str(p1_path),
        "p1_sha256": _sha256(p1_path),
        "k_config": str(k_path),
        "k_config_sha256": _sha256(k_path),
        "epsilon": args.epsilon,
        "max_iterations": args.max_iterations,
        "converged": result.converged,
        "iterations": result.iterations,
        "final_delta": result.final_delta,
        "rated_bouts": result.replay.rated_bout_count,
        "mean_log_loss": result.replay.mean_log_loss,
        "mean_brier_loss": result.replay.mean_brier_loss,
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "findings.md").write_text(
        _findings(result, comparison), encoding="utf-8"
    )


def _findings(result, comparison) -> str:
    lines = [
        "# P2 divisional-average fixed point",
        "",
        f"Converged: `{result.converged}` after `{result.iterations}` iterations; "
        f"final maximum change `{result.final_delta:.6f}`.",
        "",
        "Each basho-start and basho-end active division is shifted by one common",
        "amount to its fixed P1-derived mean. After every fixed-point replay, the",
        "literal chii map is recentered independently within each division using",
        "P1's support-proportional alpha=1 allocation. Only chii with at least",
        f"{result.support_threshold} observations estimate themselves and participate",
        "in recentering; other chii inherit the nearest supported chii's value.",
        "",
        "| Division | Chii | P1 mean | P2 mean | Mean difference | MAE | RMS |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in comparison:
        lines.append(
            f"| {row['division']} | {row['chii_count']} | {row['p1_mean']:.3f} | "
            f"{row['p2_mean']:.3f} | {row['mean_difference']:+.3f} | "
            f"{row['mean_absolute_difference']:.3f} | "
            f"{row['root_mean_square_difference']:.3f} |"
        )
    lines.extend(
        [
            "",
            "These are diagnostic fixed-point replay scores, not the separate",
            "production predictive gate. Closeness to P1 is not by itself evidence",
            "that P2 is better supported.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
