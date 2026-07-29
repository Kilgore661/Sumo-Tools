"""Test whether BP4 mean Elo ratings are non-increasing with chii ordinal."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Sequence


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/clean_elo/monotonicity_probe"
)
DEFAULT_BOOTSTRAP_SAMPLES = 10_000
DEFAULT_RANDOM_SEED = 20260729


@dataclass(frozen=True)
class IndexEstimate:
    index: str
    ordinal: int
    level: str
    number: int | None
    n: int
    mean: float
    standard_error: float | None


@dataclass(frozen=True)
class Scope:
    name: str
    description: str
    includes: Callable[[IndexEstimate], bool]


@dataclass(frozen=True)
class MonotonicityResult:
    scope: Scope
    estimates: tuple[IndexEstimate, ...]
    excluded_count: int
    fitted_means: tuple[float, ...]
    statistic: float
    bootstrap_samples: int
    exceedances: int
    p_value: float
    monte_carlo_standard_error: float
    random_seed: int


@dataclass(frozen=True)
class OutputPaths:
    run_directory: Path
    summary_csv: Path
    fitted_values_csv: Path
    manifest_json: Path


SCOPES = (
    Scope(
        name="M1_to_M18",
        description="BP4 makuuchi maegashira indices M1 through M18",
        includes=lambda item: (
            item.level == "M"
            and item.number is not None
            and 1 <= item.number <= 18
        ),
    ),
    Scope(
        name="Y_to_Jd100",
        description="BP4 indices from Y through Jd100",
        includes=lambda item: (
            item.ordinal <= 810000
        ),
    ),
)


def read_bp4_estimates(statistics_csv: Path) -> list[IndexEstimate]:
    """Read BP4 group means and any available standard errors."""
    estimates: list[IndexEstimate] = []
    with Path(statistics_csv).open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["policy"] != "BP4":
                continue
            standard_error = row["standard_error"]
            parsed_standard_error = (
                None if not standard_error else float(standard_error)
            )
            if (
                parsed_standard_error is not None
                and parsed_standard_error <= 0.0
            ):
                parsed_standard_error = None
            estimates.append(
                IndexEstimate(
                    index=row["index"],
                    ordinal=int(row["index_ordinal"]),
                    level=row["level"],
                    number=(
                        None if not row["number"] else int(row["number"])
                    ),
                    n=int(row["n"]),
                    mean=float(row["mean_rating"]),
                    standard_error=parsed_standard_error,
                )
            )
    return sorted(estimates, key=lambda item: item.ordinal)


def fit_non_increasing(
    values: Sequence[float],
    weights: Sequence[float],
) -> tuple[float, ...]:
    """Return the weighted least-squares non-increasing isotonic fit."""
    if len(values) != len(weights):
        raise ValueError("values and weights must have equal lengths")
    if not values:
        return ()
    blocks: list[list[float | int]] = []
    for position, (value, weight) in enumerate(zip(values, weights)):
        if weight <= 0.0:
            raise ValueError("weights must be positive")
        blocks.append([position, position, weight, weight * value])
        while len(blocks) >= 2:
            previous = blocks[-2]
            current = blocks[-1]
            previous_mean = float(previous[3]) / float(previous[2])
            current_mean = float(current[3]) / float(current[2])
            if previous_mean >= current_mean:
                break
            merged = [
                int(previous[0]),
                int(current[1]),
                float(previous[2]) + float(current[2]),
                float(previous[3]) + float(current[3]),
            ]
            blocks[-2:] = [merged]

    fitted = [0.0] * len(values)
    for start, end, weight, weighted_sum in blocks:
        block_mean = float(weighted_sum) / float(weight)
        for position in range(int(start), int(end) + 1):
            fitted[position] = block_mean
    return tuple(fitted)


def test_monotonicity(
    all_estimates: Sequence[IndexEstimate],
    scope: Scope,
    *,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> MonotonicityResult:
    """Run a plug-in parametric-bootstrap goodness-of-fit test."""
    if bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be positive")
    in_scope = [item for item in all_estimates if scope.includes(item)]
    estimates = tuple(
        item
        for item in in_scope
        if item.standard_error is not None
        and item.standard_error > 0.0
    )
    if len(estimates) < 2:
        raise ValueError(f"{scope.name} needs at least two usable indices")

    means = [item.mean for item in estimates]
    standard_errors = [
        float(item.standard_error) for item in estimates
    ]
    weights = [1.0 / (value * value) for value in standard_errors]
    fitted = fit_non_increasing(means, weights)
    statistic = _lack_of_fit_statistic(means, fitted, standard_errors)

    generator = random.Random(random_seed)
    exceedances = 0
    for _ in range(bootstrap_samples):
        simulated = [
            generator.gauss(mean, standard_error)
            for mean, standard_error in zip(fitted, standard_errors)
        ]
        simulated_fit = fit_non_increasing(simulated, weights)
        simulated_statistic = _lack_of_fit_statistic(
            simulated,
            simulated_fit,
            standard_errors,
        )
        if simulated_statistic >= statistic:
            exceedances += 1

    p_value = (exceedances + 1.0) / (bootstrap_samples + 1.0)
    monte_carlo_standard_error = math.sqrt(
        p_value * (1.0 - p_value) / (bootstrap_samples + 1.0)
    )
    return MonotonicityResult(
        scope=scope,
        estimates=estimates,
        excluded_count=len(in_scope) - len(estimates),
        fitted_means=fitted,
        statistic=statistic,
        bootstrap_samples=bootstrap_samples,
        exceedances=exceedances,
        p_value=p_value,
        monte_carlo_standard_error=monte_carlo_standard_error,
        random_seed=random_seed,
    )


def run_probe(
    statistics_csv: Path,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[tuple[MonotonicityResult, ...], OutputPaths]:
    estimates = read_bp4_estimates(statistics_csv)
    results = tuple(
        test_monotonicity(
            estimates,
            scope,
            bootstrap_samples=bootstrap_samples,
            random_seed=random_seed + position,
        )
        for position, scope in enumerate(SCOPES)
    )
    paths = write_outputs(
        results,
        source_statistics_csv=Path(statistics_csv),
        output_root=output_root,
    )
    return results, paths


def write_outputs(
    results: Sequence[MonotonicityResult],
    *,
    source_statistics_csv: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> OutputPaths:
    generated_at, run_directory = _create_run_directory(Path(output_root))
    summary_csv = run_directory / "monotonicity_test_summary.csv"
    fitted_values_csv = run_directory / "monotonicity_fitted_values.csv"
    manifest_json = run_directory / "manifest.json"

    with summary_csv.open("w", newline="", encoding="utf-8") as stream:
        fields = [
            "scope",
            "description",
            "first_index",
            "last_index",
            "index_count",
            "excluded_index_count",
            "observation_count",
            "lack_of_fit_statistic",
            "bootstrap_samples",
            "bootstrap_exceedances",
            "p_value",
            "monte_carlo_standard_error",
            "random_seed",
            "reject_at_0_05",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "scope": result.scope.name,
                    "description": result.scope.description,
                    "first_index": result.estimates[0].index,
                    "last_index": result.estimates[-1].index,
                    "index_count": len(result.estimates),
                    "excluded_index_count": result.excluded_count,
                    "observation_count": sum(
                        item.n for item in result.estimates
                    ),
                    "lack_of_fit_statistic": _number(result.statistic),
                    "bootstrap_samples": result.bootstrap_samples,
                    "bootstrap_exceedances": result.exceedances,
                    "p_value": _number(result.p_value),
                    "monte_carlo_standard_error": _number(
                        result.monte_carlo_standard_error
                    ),
                    "random_seed": result.random_seed,
                    "reject_at_0_05": result.p_value < 0.05,
                }
            )

    with fitted_values_csv.open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        fields = [
            "scope",
            "index",
            "index_ordinal",
            "n",
            "mean_rating",
            "standard_error",
            "fitted_monotonic_mean",
            "residual",
            "standardized_residual",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for result in results:
            for estimate, fitted in zip(
                result.estimates,
                result.fitted_means,
            ):
                residual = estimate.mean - fitted
                writer.writerow(
                    {
                        "scope": result.scope.name,
                        "index": estimate.index,
                        "index_ordinal": estimate.ordinal,
                        "n": estimate.n,
                        "mean_rating": _number(estimate.mean),
                        "standard_error": _number(
                            float(estimate.standard_error)
                        ),
                        "fitted_monotonic_mean": _number(fitted),
                        "residual": _number(residual),
                        "standardized_residual": _number(
                            residual / float(estimate.standard_error)
                        ),
                    }
                )

    manifest = {
        "generated_at_utc": generated_at.isoformat(),
        "source_statistics_csv": str(source_statistics_csv),
        "null_hypothesis": (
            "Expected BP4 mean start-of-basho Elo rating is "
            "non-increasing as index ordinal increases."
        ),
        "fit": (
            "Weighted non-increasing isotonic regression of group means; "
            "weight = 1 / standard_error^2."
        ),
        "test_statistic": (
            "Sum over indices of ((observed mean - fitted mean) / "
            "standard error)^2."
        ),
        "bootstrap": (
            "Plug-in parametric bootstrap. Independent normal group means "
            "are generated around the fitted null means using the observed "
            "standard errors, then the isotonic model is refitted."
        ),
        "limitations": [
            "Rikishi-basho observations are treated as independent.",
            "Observed standard errors are treated as fixed and known.",
            "The test concerns conditional mean Elo by BP4 index, not every "
            "individual rikishi or every interpretation of chii.",
        ],
        "files": {
            "summary_csv": str(summary_csv),
            "fitted_values_csv": str(fitted_values_csv),
        },
    }
    manifest_json.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return OutputPaths(
        run_directory=run_directory,
        summary_csv=summary_csv,
        fitted_values_csv=fitted_values_csv,
        manifest_json=manifest_json,
    )


def _lack_of_fit_statistic(
    observed: Sequence[float],
    fitted: Sequence[float],
    standard_errors: Sequence[float],
) -> float:
    statistic = 0.0
    for value, expected, standard_error in zip(
        observed,
        fitted,
        standard_errors,
    ):
        residual = value - expected
        if math.isclose(
            value,
            expected,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            residual = 0.0
        statistic += (residual / standard_error) ** 2
    return statistic


def _number(value: float) -> str:
    return f"{value:.9f}"


def _create_run_directory(base_root: Path) -> tuple[datetime, Path]:
    base_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    while True:
        run_directory = base_root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Test whether BP4 mean start-of-basho Elo ratings are "
            "non-increasing with chii ordinal."
        )
    )
    parser.add_argument(
        "statistics_csv",
        type=Path,
        help="index_rating_statistics.csv produced by rating_probe",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=DEFAULT_BOOTSTRAP_SAMPLES,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results, paths = run_probe(
        args.statistics_csv,
        output_root=args.output_root,
        bootstrap_samples=args.bootstrap_samples,
        random_seed=args.seed,
    )
    for result in results:
        print(
            f"{result.scope.name}: statistic={result.statistic:.6f}, "
            f"p={result.p_value:.9f} "
            f"({result.exceedances}/{result.bootstrap_samples} "
            "bootstrap statistics at least as large)"
        )
    print(f"Run directory: {paths.run_directory}")
    print(f"Summary: {paths.summary_csv}")
    print(f"Fitted values: {paths.fitted_values_csv}")


if __name__ == "__main__":
    main()
