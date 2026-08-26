"""Compare population policies under the canonical q=400, alpha=1 BKP1 prior."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path

from ...infra.connect import connect
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from ..equelo.expt1.Oracle import make_oracle
from ..equelo.expt1.params import build_elo_params
from ..equelo_bkp1.params import DEFAULT_K_CONFIG, MODEL_BASE, MODEL_Q
from .model import FixedPointResult, PopulationPolicy, ReplayResult
from .simulate import replay
from .solve import solve


DEFAULT_PRIOR = Path("files/output/analysis/equelo_bkp1/prior.csv")
DEFAULT_OUTPUT = Path(
    "files/output/analysis/equelo_population_policy/bkp1_q400"
)
VARIANTS = (
    ("legacy_departure", PopulationPolicy.LEGACY_DEPARTURE),
    ("legacy_plus_dual_k", PopulationPolicy.LEGACY_DEPARTURE_BOUT_MASS),
    ("whole_population_start_only", PopulationPolicy.POST_BASHO_MEAN_START_ONLY),
    ("whole_population_mean", PopulationPolicy.POST_BASHO_MEAN),
)
LANDMARKS = (
    "M12e", "M15e", "M18e", "J1e", "J14e", "Ms1e",
    "Ms59e", "Ms60e", "Sd1e", "Sd100e", "Sd101e",
    "Jd100e", "Jd150e", "Jk1e",
)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history = make_oracle(
        connect(args.start, args.end, use_zip=args.zip),
        collapse_mode="annotation_only",
    ).history
    canonical_prior = _load_prior(args.prior)
    support = _chii_support(history)
    _assert_coverage(canonical_prior, support)
    params = build_elo_params(
        k_policy="divisional",
        b=MODEL_BASE,
        q=MODEL_Q,
        config_path=args.k_config,
    )

    print("[one-shot] replaying canonical prior under all policies", flush=True)
    one_shot = {
        name: replay(
            history,
            params,
            canonical_prior,
            policy,
            variant=name,
        )
        for name, policy in VARIANTS
    }

    fixed_points: dict[str, FixedPointResult] = {}
    for name, policy in VARIANTS:
        print(f"[{name}] solving q=400 alpha=1 fixed point", flush=True)
        fixed_points[name] = solve(
            history,
            params,
            policy,
            base=MODEL_BASE,
            epsilon=args.epsilon,
            max_iterations=args.max_iterations,
            progress=_progress,
            variant=name,
            normalisation_alpha=0.0,
            recentering_alpha=1.0,
        )

    summary = _summary(one_shot, fixed_points, canonical_prior, support)
    args.output.mkdir(parents=True, exist_ok=True)
    _write_outputs(
        args.output,
        args,
        summary,
        one_shot,
        fixed_points,
        canonical_prior,
        support,
    )
    findings = _findings(summary)
    (args.output / "findings.md").write_text(findings, encoding="utf-8")
    print(findings, flush=True)
    return 0 if all(result.converged for result in fixed_points.values()) else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1989)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--prior", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--epsilon", type=float, default=10.0)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _load_prior(path: Path) -> dict[Chii, float]:
    with path.open(newline="", encoding="utf-8") as stream:
        result = {Chii.from_str(row["chii"]): float(row["rating"]) for row in csv.DictReader(stream)}
    if not result:
        raise ValueError(f"Empty canonical prior: {path}")
    return result


def _assert_coverage(prior: dict[Chii, float], support: dict[Chii, int]) -> None:
    missing = set(support) - set(prior)
    extra = set(prior) - set(support)
    if missing or extra:
        raise ValueError(
            f"Canonical prior/history mismatch: {len(missing)} missing, {len(extra)} extra"
        )


def _summary(
    one_shot: dict[str, ReplayResult],
    fixed_points: dict[str, FixedPointResult],
    canonical_prior: dict[Chii, float],
    support: dict[Chii, int],
) -> dict[str, object]:
    legacy_one_shot = one_shot["legacy_departure"]
    direct = {}
    for name, result in one_shot.items():
        starts = [abs(row.start_adjustment_per_rikishi) for row in result.adjustments]
        ends = [abs(row.end_adjustment_per_rikishi) for row in result.adjustments]
        start_errors = [abs(row.adjusted_start_mean - row.target_mean) for row in result.adjustments]
        end_errors = [abs(row.adjusted_end_mean - row.target_mean) for row in result.adjustments]
        direct[name] = {
            "mean_log_loss": result.mean_log_loss,
            "mean_brier_score": result.mean_brier_score,
            "log_loss_difference_from_legacy": result.mean_log_loss - legacy_one_shot.mean_log_loss,
            "brier_difference_from_legacy": result.mean_brier_score - legacy_one_shot.mean_brier_score,
            "mean_absolute_start_adjustment": sum(starts) / len(starts),
            "maximum_absolute_start_adjustment": max(starts),
            "mean_absolute_end_adjustment": sum(ends) / len(ends),
            "maximum_absolute_end_adjustment": max(ends),
            "mean_absolute_start_mean_error": sum(start_errors) / len(start_errors),
            "maximum_absolute_start_mean_error": max(start_errors),
            "mean_absolute_end_mean_error": sum(end_errors) / len(end_errors),
            "maximum_absolute_end_mean_error": max(end_errors),
        }
    direct["rating_distance"] = _rating_distance(one_shot)

    fixed = {}
    legacy_fixed = fixed_points["legacy_departure"]
    for name, result in fixed_points.items():
        differences = [result.priors[chii] - legacy_fixed.priors[chii] for chii in support]
        canonical_differences = [result.priors[chii] - canonical_prior[chii] for chii in support]
        low_support = [
            (rating, chii) for chii, rating in result.priors.items() if support[chii] <= 10
        ]
        highest_low_rating, highest_low_chii = max(low_support)
        fixed[name] = {
            "converged": result.converged,
            "iterations": result.iterations,
            "final_delta": result.final_delta,
            "mean_log_loss": result.replay.mean_log_loss,
            "mean_brier_score": result.replay.mean_brier_score,
            "minimum_prior": min(result.priors.values()),
            "maximum_prior": max(result.priors.values()),
            "mean_absolute_prior_difference_from_legacy": _mean_abs(differences),
            "rms_prior_difference_from_legacy": _rms(differences),
            "maximum_absolute_prior_difference_from_legacy": max(abs(value) for value in differences),
            "mean_absolute_prior_difference_from_canonical": _mean_abs(canonical_differences),
            "maximum_absolute_prior_difference_from_canonical": max(abs(value) for value in canonical_differences),
            "highest_low_support_chii": str(highest_low_chii),
            "highest_low_support_rating": highest_low_rating,
            "landmarks": {
                label: result.priors[Chii.from_str(label)]
                for label in LANDMARKS
                if Chii.from_str(label) in result.priors
            },
        }
    return {"one_shot": direct, "fixed_point": fixed}


def _rating_distance(results: dict[str, ReplayResult]) -> dict[str, float]:
    legacy = results["legacy_departure"].basho_start_ratings
    whole = results["whole_population_mean"].basho_start_ratings
    values = []
    final_values = []
    final_date = max(legacy)
    for date in sorted(legacy):
        for rikid in legacy[date]:
            difference = whole[date][rikid] - legacy[date][rikid]
            values.append(difference)
            if date == final_date:
                final_values.append(difference)
    return {
        "observation_count": len(values),
        "mean_absolute_basho_start_difference": _mean_abs(values),
        "rms_basho_start_difference": _rms(values),
        "maximum_absolute_basho_start_difference": max(abs(value) for value in values),
        "final_active_count": len(final_values),
        "final_mean_absolute_difference": _mean_abs(final_values),
        "final_rms_difference": _rms(final_values),
        "final_maximum_absolute_difference": max(abs(value) for value in final_values),
    }


def _mean_abs(values: list[float]) -> float:
    return sum(abs(value) for value in values) / len(values)


def _rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def _write_outputs(
    output: Path,
    args,
    summary,
    one_shot,
    fixed_points,
    canonical_prior,
    support,
) -> None:
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    prior_path = args.prior.resolve()
    k_path = args.k_config.resolve()
    manifest = {
        "experiment": "BKP1 q=400 population-policy comparison",
        "start": args.start,
        "end": args.end,
        "q": MODEL_Q,
        "base": MODEL_BASE,
        "recentering_alpha": 1.0,
        "fixed_population_adjustment_alpha": 0.0,
        "canonical_prior": str(prior_path),
        "canonical_prior_sha256": _sha256(prior_path),
        "k_config": str(k_path),
        "k_config_sha256": _sha256(k_path),
        "epsilon": args.epsilon,
        "max_iterations": args.max_iterations,
        "variants": [name for name, _ in VARIANTS],
        "one_shot_rule": "all variants consume the same canonical BKP1 prior",
        "fixed_point_rule": "each variant is independently solved with q=400 alpha=1 map recentering",
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_csv(
        output / "one_shot_basho_adjustments.csv",
        [asdict(row) for result in one_shot.values() for row in result.adjustments],
    )
    _write_csv(
        output / "iterations.csv",
        [asdict(row) for result in fixed_points.values() for row in result.iteration_rows],
    )
    legacy = fixed_points["legacy_departure"]
    rows = []
    for name, result in fixed_points.items():
        for chii in sorted(canonical_prior, key=lambda item: item.ordinal()):
            rows.append({
                "variant": name,
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "observations": support[chii],
                "canonical_rating": canonical_prior[chii],
                "rating": result.priors[chii],
                "difference_from_canonical": result.priors[chii] - canonical_prior[chii],
                "difference_from_legacy_fixed_point": result.priors[chii] - legacy.priors[chii],
            })
    _write_csv(output / "fixed_point_prior_comparison.csv", rows)


def _findings(summary: dict[str, object]) -> str:
    one = summary["one_shot"]
    fixed = summary["fixed_point"]
    lines = [
        "# BKP1 q=400 population-policy comparison",
        "",
        "The one-shot comparison holds the canonical BKP1 prior fixed. The",
        "fixed-point comparison then allows each population policy to feed back",
        "through the same alpha=1 map-recentering rule.",
        "",
        "## One-shot isolation",
        "",
        "| Policy | Log loss | Difference | Brier | Difference | Mean start adjustment | Mean end adjustment |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, _ in VARIANTS:
        row = one[name]
        lines.append(
            f"| {name} | {row['mean_log_loss']:.6f} | {row['log_loss_difference_from_legacy']:+.6f} | "
            f"{row['mean_brier_score']:.6f} | {row['brier_difference_from_legacy']:+.6f} | "
            f"{row['mean_absolute_start_adjustment']:.3f} | {row['mean_absolute_end_adjustment']:.3f} |"
        )
    distance = one["rating_distance"]
    lines.extend([
        "",
        f"Across {distance['observation_count']:,} basho-start rating observations,",
        f"the policies differ by {distance['mean_absolute_basho_start_difference']:.3f}",
        f"points MAE and {distance['rms_basho_start_difference']:.3f} RMS.",
        f"At the final basho the MAE is {distance['final_mean_absolute_difference']:.3f}",
        f"and the maximum individual difference is {distance['final_maximum_absolute_difference']:.3f}.",
        "",
        "## Independently solved fixed points",
        "",
        "| Policy | Iterations | Log loss | Brier | Min prior | Max prior | MAE from legacy map | Max from legacy map |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for name, _ in VARIANTS:
        row = fixed[name]
        lines.append(
            f"| {name} | {row['iterations']} | {row['mean_log_loss']:.6f} | "
            f"{row['mean_brier_score']:.6f} | {row['minimum_prior']:.1f} | "
            f"{row['maximum_prior']:.1f} | {row['mean_absolute_prior_difference_from_legacy']:.3f} | "
            f"{row['maximum_absolute_prior_difference_from_legacy']:.3f} |"
        )
    lines.extend([
        "",
        "## Selected curve landmarks",
        "",
        "| Chii | Legacy fixed point | Whole-population fixed point | Difference |",
        "|---|---:|---:|---:|",
    ])
    for label in LANDMARKS:
        if label not in fixed["legacy_departure"]["landmarks"]:
            continue
        legacy_rating = fixed["legacy_departure"]["landmarks"][label]
        whole_rating = fixed["whole_population_mean"]["landmarks"][label]
        lines.append(
            f"| {label} | {legacy_rating:.1f} | {whole_rating:.1f} | "
            f"{whole_rating - legacy_rating:+.1f} |"
        )
    lines.extend([
        "",
        "The loss values use the fixed-point replay's legacy bout eligibility and",
        "are descriptive diagnostics, not the separate B-family predictive gate.",
        "",
    ])
    return "\n".join(lines)


def _progress(row) -> None:
    if row.iteration == 1 or row.iteration % 10 == 0 or row.max_prior_change < 10.0:
        print(
            f"[{row.policy}] iteration={row.iteration} delta={row.max_prior_change:.6f} "
            f"max={row.max_change_chii} n={row.max_change_observation_count}",
            flush=True,
        )


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _chii_support(history: History) -> dict[Chii, int]:
    counts: dict[Chii, int] = {}
    for basho in history.values():
        for chii in basho.banzuke.rikchii.values():
            counts[chii] = counts.get(chii, 0) + 1
    return counts


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
