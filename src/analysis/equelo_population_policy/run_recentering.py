"""Isolated sweep of post-iteration chii-map recentering policies."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import json
import math
from pathlib import Path

from ...infra.connect import connect
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from ..equelo.config_main import INITIAL_ELO
from ..equelo.expt1.Oracle import make_oracle
from ..equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from .model import PopulationPolicy
from .solve import solve


DEFAULT_OUTPUT = Path("files/output/analysis/equelo_population_policy/recentering")
ALPHAS = (0.0, 0.25, 0.5, 1.0)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history = make_oracle(
        connect(args.start, args.end, use_zip=args.zip),
        collapse_mode="annotation_only",
    ).history
    params = build_elo_params(
        k_policy="divisional",
        b=args.base,
        q=args.q,
        config_path=args.k_config,
    )
    results = {}
    for alpha in ALPHAS:
        name = _variant_name(alpha)
        results[name] = solve(
            history,
            params,
            PopulationPolicy.LEGACY_DEPARTURE,
            base=args.base,
            epsilon=args.epsilon,
            max_iterations=args.max_iterations,
            progress=_print_progress,
            variant=name,
            recentering_alpha=alpha,
        )

    support = _chii_support(history)
    summary = _summary(results, support)
    args.output.mkdir(parents=True, exist_ok=True)
    _write_outputs(args.output, args, results, support, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if all(result.converged for result in results.values()) else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hold legacy Elo replay fixed and vary only chii-map recentering"
    )
    parser.add_argument("--start", type=int, default=1989)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--base", type=float, default=INITIAL_ELO)
    parser.add_argument("--q", type=float, default=900.0)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG_PATH)
    parser.add_argument("--epsilon", type=float, default=10.0)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _print_progress(row) -> None:
    if row.iteration == 1 or row.iteration % 10 == 0 or row.max_prior_change < 10.0:
        print(
            f"[{row.policy}] iteration={row.iteration} delta={row.max_prior_change:.6f} "
            f"rms-difference-change={row.rms_pairwise_difference_change:.6f} "
            f"max={row.max_change_chii} n={row.max_change_observation_count}",
            flush=True,
        )


def _summary(results, support: dict[Chii, int]) -> dict[str, object]:
    baseline = results["uniform"]
    variants = {}
    for name, result in results.items():
        last = result.iteration_rows[-1]
        map_delta = {
            chii: result.priors[chii] - baseline.priors[chii]
            for chii in baseline.priors
        }
        final_difference_metrics = _difference_metrics(tuple(map_delta.values()))
        low_support = [
            (rating, chii)
            for chii, rating in result.priors.items()
            if support[chii] <= 10
        ]
        highest_low_rating, highest_low_chii = max(low_support)
        variants[name] = {
            "alpha": result.recentering_alpha,
            "converged": result.converged,
            "iterations": result.iterations,
            "final_delta": result.final_delta,
            "final_iteration_mean_adjustment": last.map_recentering_shift,
            "final_iteration_minimum_adjustment": last.minimum_recentering_adjustment,
            "final_iteration_maximum_adjustment": last.maximum_recentering_adjustment,
            "final_iteration_rms_pairwise_difference_change": last.rms_pairwise_difference_change,
            "final_iteration_maximum_pairwise_difference_change": last.maximum_pairwise_difference_change,
            "maximum_iteration_rms_pairwise_difference_change": max(
                row.rms_pairwise_difference_change for row in result.iteration_rows
            ),
            "maximum_iteration_pairwise_difference_change": max(
                row.maximum_pairwise_difference_change for row in result.iteration_rows
            ),
            "final_map_mean_absolute_change_from_uniform": sum(
                abs(value) for value in map_delta.values()
            ) / len(map_delta),
            "final_map_rms_pairwise_difference_change_from_uniform": final_difference_metrics[0],
            "final_map_maximum_pairwise_difference_change_from_uniform": final_difference_metrics[1],
            "minimum_prior": min(result.priors.values()),
            "maximum_prior": max(result.priors.values()),
            "highest_low_support_chii": str(highest_low_chii),
            "highest_low_support_rating": highest_low_rating,
        }
    return {"variants": variants}


def _difference_metrics(values: tuple[float, ...]) -> tuple[float, float]:
    if len(values) < 2:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    rms = math.sqrt(2.0 * len(values) / (len(values) - 1) * variance)
    return rms, max(values) - min(values)


def _write_outputs(output, args, results, support, summary) -> None:
    manifest = {
        "start": args.start,
        "end": args.end,
        "base": args.base,
        "q": args.q,
        "k_config": str(args.k_config),
        "epsilon": args.epsilon,
        "max_iterations": args.max_iterations,
        "population_policy": PopulationPolicy.LEGACY_DEPARTURE.value,
        "recentering_alphas": list(ALPHAS),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    _write_csv(
        output / "iterations.csv",
        [asdict(row) for result in results.values() for row in result.iteration_rows],
    )
    rows = []
    baseline = results["uniform"]
    for name, result in results.items():
        for chii in sorted(result.priors, key=lambda item: item.ordinal()):
            rows.append(
                {
                    "variant": name,
                    "alpha": result.recentering_alpha,
                    "chii": str(chii),
                    "ordinal": chii.ordinal(),
                    "observations": support[chii],
                    "rating": result.priors[chii],
                    "change_from_uniform": result.priors[chii] - baseline.priors[chii],
                }
            )
    _write_csv(output / "prior_comparison.csv", rows)
    (output / "findings.md").write_text(_findings(summary), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _findings(summary: dict[str, object]) -> str:
    rows = summary["variants"]
    lines = [
        "# Chii-map recentering sweep",
        "",
        "The Elo replay uses the legacy departure policy in every variant. Only",
        "the allocation of the post-iteration chii-map correction changes.",
        "",
        "| Variant | Alpha | Iterations | Max prior | Highest low-support prior | Final per-step RMS difference change | Final-map RMS difference change |",
        "|---|---:|---:|---:|---|---:|---:|",
    ]
    for name in ("uniform", "support_0_25", "support_0_5", "support_1"):
        row = rows[name]
        lines.append(
            f"| {name} | {row['alpha']} | {row['iterations']} | "
            f"{row['maximum_prior']:.3f} | `{row['highest_low_support_chii']}` "
            f"{row['highest_low_support_rating']:.3f} | "
            f"{row['final_iteration_rms_pairwise_difference_change']:.6f} | "
            f"{row['final_map_rms_pairwise_difference_change_from_uniform']:.6f} |"
        )
    lines.extend(
        [
            "",
            "`alpha=0` is the old common shift and changes no differences in the",
            "recentering step. `alpha=1` allocates correction directly in",
            "proportion to support. Intermediate values show the trade-off.",
            "",
        ]
    )
    return "\n".join(lines)


def _variant_name(alpha: float) -> str:
    labels = {0.0: "uniform", 0.25: "support_0_25", 0.5: "support_0_5", 1.0: "support_1"}
    return labels[alpha]


def _chii_support(history: History) -> dict[Chii, int]:
    counts: dict[Chii, int] = {}
    for basho in history.values():
        for chii in basho.banzuke.rikchii.values():
            counts[chii] = counts.get(chii, 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
