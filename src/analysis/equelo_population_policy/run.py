"""CLI and artifact writer for the Tranche 1 comparison."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path

from ...infra.connect import connect
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from ..equelo.config_main import INITIAL_ELO
from ..equelo.expt1.Oracle import make_oracle
from ..equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from .model import FixedPointResult, PopulationPolicy
from .simulate import replay
from .solve import solve


DEFAULT_OUTPUT = Path("files/output/analysis/equelo_population_policy")
VARIANTS: tuple[tuple[str, PopulationPolicy, float | None], ...] = (
    ("legacy_departure", PopulationPolicy.LEGACY_DEPARTURE, None),
    ("equal_share", PopulationPolicy.POST_BASHO_MEAN, 0.0),
    ("support_0_25", PopulationPolicy.POST_BASHO_MEAN, 0.25),
    ("support_0_5", PopulationPolicy.POST_BASHO_MEAN, 0.5),
    ("support_1", PopulationPolicy.POST_BASHO_MEAN, 1.0),
)


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
    results = {
        name: solve(
            history,
            params,
            policy,
            base=args.base,
            epsilon=args.epsilon,
            max_iterations=args.max_iterations,
            progress=_print_progress,
            variant=name,
            normalisation_alpha=alpha,
        )
        for name, policy, alpha in VARIANTS
    }
    common_priors = results["legacy_departure"].priors
    support = _chii_support(history)
    one_shot = {
        name: replay(
            history,
            params,
            common_priors,
            policy,
            variant=name,
            normalisation_support=support,
            normalisation_alpha=alpha or 0.0,
        )
        for name, policy, alpha in VARIANTS
    }
    args.output.mkdir(parents=True, exist_ok=True)
    summary = _summary(results, one_shot)
    _write_artifacts(args.output, args, results, one_shot, summary, support)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if all(result.converged for result in results.values()) else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare legacy, equal-share and support-weighted Equelo population policies"
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
            f"[{row.policy}] iteration={row.iteration} "
            f"delta={row.max_prior_change:.6f} shift={row.map_recentering_shift:+.6f} "
            f"max={row.max_change_chii} n={row.max_change_observation_count}",
            flush=True,
        )


def _summary(results, one_shot) -> dict[str, object]:
    legacy = results["legacy_departure"]
    fixed = {}
    differences = {}
    bottlenecks = {}
    one_shot_rows = {}
    for name, result in results.items():
        last = result.iteration_rows[-1]
        fixed[name] = {
            "normalisation_alpha": result.normalisation_alpha,
            "converged": result.converged,
            "iterations": result.iterations,
            "final_delta": result.final_delta,
            "mean_log_loss": result.replay.mean_log_loss,
            "mean_brier_score": result.replay.mean_brier_score,
            "target_mean": result.replay.target_mean,
            "minimum_prior": min(result.priors.values()),
            "maximum_prior": max(result.priors.values()),
        }
        diffs = [result.priors[chii] - legacy.priors[chii] for chii in legacy.priors]
        differences[name] = {
            "mean_signed": sum(diffs) / len(diffs),
            "mean_absolute": sum(abs(value) for value in diffs) / len(diffs),
            "max_absolute": max(abs(value) for value in diffs),
        }
        bottlenecks[name] = {
            "chii": last.max_change_chii,
            "observation_count": last.max_change_observation_count,
            "max_change": last.max_prior_change,
            "recentering_shift": last.map_recentering_shift,
        }

        replay_result = one_shot[name]
        start_abs = [abs(row.start_adjustment_per_rikishi) for row in replay_result.adjustments]
        end_abs = [abs(row.end_adjustment_per_rikishi) for row in replay_result.adjustments]
        one_shot_rows[name] = {
            "mean_log_loss": replay_result.mean_log_loss,
            "mean_brier_score": replay_result.mean_brier_score,
            "log_loss_difference_from_legacy": replay_result.mean_log_loss - one_shot["legacy_departure"].mean_log_loss,
            "brier_difference_from_legacy": replay_result.mean_brier_score - one_shot["legacy_departure"].mean_brier_score,
            "mean_absolute_population_boundary_adjustment": sum(start_abs) / len(start_abs),
            "max_absolute_population_boundary_adjustment": max(start_abs),
            "mean_absolute_post_bout_adjustment": sum(end_abs) / len(end_abs),
            "max_absolute_post_bout_adjustment": max(end_abs),
        }
    return {
        "fixed_point": fixed,
        "fixed_point_prior_difference_from_legacy": differences,
        "convergence_bottleneck": bottlenecks,
        "one_shot_from_legacy_priors": one_shot_rows,
    }


def _write_artifacts(
    output: Path,
    args: argparse.Namespace,
    results: dict[str, FixedPointResult],
    one_shot,
    summary: dict[str, object],
    support: dict[Chii, int],
) -> None:
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    manifest = {
        "start": args.start,
        "end": args.end,
        "base": args.base,
        "q": args.q,
        "k_config": str(args.k_config),
        "epsilon": args.epsilon,
        "max_iterations": args.max_iterations,
        "common_one_shot_prior": "legacy_departure",
        "variants": [name for name, _, _ in VARIANTS],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    _write_csv(
        output / "iterations.csv",
        [asdict(row) for result in results.values() for row in result.iteration_rows],
    )
    _write_csv(
        output / "basho_adjustments.csv",
        [asdict(row) for result in results.values() for row in result.replay.adjustments],
    )
    legacy = results["legacy_departure"]
    prior_rows = []
    for name, result in results.items():
        for chii in sorted(legacy.priors, key=lambda item: item.ordinal()):
            prior_rows.append(
                {
                    "variant": name,
                    "normalisation_alpha": result.normalisation_alpha,
                    "chii": str(chii),
                    "ordinal": chii.ordinal(),
                    "observations": support[chii],
                    "rating": result.priors[chii],
                    "difference_from_legacy": result.priors[chii] - legacy.priors[chii],
                }
            )
    _write_csv(output / "prior_comparison.csv", prior_rows)
    _write_csv(
        output / "one_shot_basho_adjustments.csv",
        [asdict(row) for result in one_shot.values() for row in result.adjustments],
    )
    (output / "findings.md").write_text(_findings(summary), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _findings(summary: dict[str, object]) -> str:
    fixed = summary["fixed_point"]
    bottlenecks = summary["convergence_bottleneck"]
    one_shot = summary["one_shot_from_legacy_priors"]
    lines = [
        "# Tranche 1 generated findings",
        "",
        "This is a controlled sweep of the legacy departure rule, equal-share",
        "whole-population mean preservation, and three support-weighted versions",
        "of that mean-preservation operator. All variants retain the same",
        "post-iteration unweighted chii-map recentering.",
        "",
        "## Fixed-point sweep",
        "",
        "| Variant | Alpha | Converged | Iterations | Delta | Min prior | Max prior |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, _, _ in VARIANTS:
        row = fixed[name]
        lines.append(
            f"| {name} | {row['normalisation_alpha']} | {row['converged']} | "
            f"{row['iterations']} | {row['final_delta']:.6f} | "
            f"{row['minimum_prior']:.3f} | {row['maximum_prior']:.3f} |"
        )
    lines.extend(["", "## Low-support diagnostic", ""])
    for name, _, _ in VARIANTS:
        row = bottlenecks[name]
        lines.append(
            f"- `{name}`: max step {row['max_change']:.6f} at "
            f"`{row['chii']}` (n={row['observation_count']}), map shift "
            f"{row['recentering_shift']:+.6f}."
        )
    lines.extend(
        [
            "",
            "## Controlled one-shot diagnostics",
            "",
            "All variants below use the same legacy fixed-point priors.",
            "",
            "| Variant | Log-loss difference | Brier difference | Mean boundary adjustment | Mean post-bout adjustment |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name, _, _ in VARIANTS:
        row = one_shot[name]
        lines.append(
            f"| {name} | {row['log_loss_difference_from_legacy']:+.9f} | "
            f"{row['brier_difference_from_legacy']:+.9f} | "
            f"{row['mean_absolute_population_boundary_adjustment']:.6f} | "
            f"{row['mean_absolute_post_bout_adjustment']:.6f} |"
        )
    lines.extend(
        [
            "",
            "These loss values are descriptive in-sample diagnostics, not a",
            "prospective model-selection result. Curve plausibility and the",
            "location of low-support extremes must be read from",
            "`prior_comparison.csv` before choosing a policy.",
            "",
        ]
    )
    return "\n".join(lines)


def _chii_support(history: History) -> dict[Chii, int]:
    counts: dict[Chii, int] = {}
    for basho in history.values():
        for chii in basho.banzuke.rikchii.values():
            counts[chii] = counts.get(chii, 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
