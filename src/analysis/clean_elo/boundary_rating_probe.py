"""Describe historical Elo ratings by division-boundary distance."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.analysis.boundary_positions import (
    boundary_positions,
    paired_boundary_group,
)
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History

from .config import DEFAULT_Q
from .monotonicity_probe import (
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_RANDOM_SEED,
    IndexEstimate,
    MonotonicityResult,
    Scope,
    test_monotonicity,
)
from .rating_probe import RunningStats
from .simulate import SimulationResult, simulate


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/clean_elo/boundary_rating_probe"
)
DEFAULT_TAIL_GROUPS = 7
TARGET_DIVISION = "M"


@dataclass(frozen=True)
class BoundaryRatingProbeResult:
    start_date: Date
    tail_groups: int
    simulation: SimulationResult
    slot_stats: dict[int, RunningStats]
    paired_group_stats: dict[int, RunningStats]
    missing_banzuke_occurrences: int


@dataclass(frozen=True)
class BoundaryCurveResult:
    ordered_distances: tuple[int, ...]
    endpoint_reversal: float
    endpoint_reversal_q_fraction: float
    monotonicity: MonotonicityResult


@dataclass(frozen=True)
class OutputPaths:
    run_directory: Path
    statistics_csv: Path
    curve_summary_csv: Path
    fitted_values_csv: Path
    chart_html: Path
    manifest_json: Path


def probe_boundary_ratings(
    history: History,
    start_date: Date,
    *,
    tail_groups: int = DEFAULT_TAIL_GROUPS,
    count_absences: bool = False,
) -> BoundaryRatingProbeResult:
    """Associate each Makuuchi rikishi-basho rating with boundary distance."""
    if tail_groups <= 0:
        raise ValueError("tail_groups must be positive")
    simulation = simulate(
        history=history,
        start_date=start_date,
        count_absences=count_absences,
    )
    slot_stats: dict[int, RunningStats] = {}
    group_stats: dict[int, RunningStats] = {}
    missing_banzuke_occurrences = 0

    for date in sorted(simulation.basho_ratings, key=_date_key):
        basho = history[date]
        positions = boundary_positions(basho.banzuke.rikchii)
        ratings = simulation.basho_ratings[
            date
        ].initial_after_normalisation
        for rikid, rating in ratings.items():
            position = positions.get(rikid)
            if position is None:
                missing_banzuke_occurrences += 1
                continue
            division, _from_top, from_bottom = position
            if division != TARGET_DIVISION:
                continue
            slot_stats.setdefault(from_bottom, RunningStats()).add(rating)
            group = paired_boundary_group(from_bottom)
            group_stats.setdefault(group, RunningStats()).add(rating)

    return BoundaryRatingProbeResult(
        start_date=start_date,
        tail_groups=tail_groups,
        simulation=simulation,
        slot_stats=slot_stats,
        paired_group_stats=group_stats,
        missing_banzuke_occurrences=missing_banzuke_occurrences,
    )


def analyse_boundary_curve(
    result: BoundaryRatingProbeResult,
    *,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> BoundaryCurveResult:
    """Test the paired lower-boundary curve from better to worse."""
    ordered_distances = tuple(
        distance
        for distance in range(result.tail_groups, 0, -1)
        if distance in result.paired_group_stats
    )
    estimates = []
    for ordinal, distance in enumerate(ordered_distances):
        summary = result.paired_group_stats[distance]
        estimates.append(
            IndexEstimate(
                index=f"top_bottom_{distance}",
                ordinal=ordinal,
                level="M_boundary",
                number=distance,
                n=summary.n,
                mean=summary.mean,
                standard_error=summary.standard_error,
            )
        )
    scope = Scope(
        name=f"top_bottom_{result.tail_groups}_to_1",
        description=(
            f"Paired Makuuchi boundary groups {result.tail_groups} through 1"
        ),
        includes=lambda _item: True,
    )
    monotonicity = test_monotonicity(
        estimates,
        scope,
        bootstrap_samples=bootstrap_samples,
        random_seed=random_seed,
    )
    first = result.paired_group_stats[ordered_distances[0]].mean
    last = result.paired_group_stats[ordered_distances[-1]].mean
    endpoint_reversal = last - first
    return BoundaryCurveResult(
        ordered_distances=ordered_distances,
        endpoint_reversal=endpoint_reversal,
        endpoint_reversal_q_fraction=endpoint_reversal / DEFAULT_Q,
        monotonicity=monotonicity,
    )


def run_probe(
    *,
    history: History,
    start_date: Date,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    tail_groups: int = DEFAULT_TAIL_GROUPS,
    count_absences: bool = False,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[
    BoundaryRatingProbeResult,
    BoundaryCurveResult,
    OutputPaths,
]:
    result = probe_boundary_ratings(
        history,
        start_date,
        tail_groups=tail_groups,
        count_absences=count_absences,
    )
    curve = analyse_boundary_curve(
        result,
        bootstrap_samples=bootstrap_samples,
        random_seed=random_seed,
    )
    outputs = write_outputs(
        result=result,
        curve=curve,
        output_root=output_root,
        count_absences=count_absences,
    )
    return result, curve, outputs


def write_outputs(
    *,
    result: BoundaryRatingProbeResult,
    curve: BoundaryCurveResult,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    count_absences: bool = False,
) -> OutputPaths:
    generated_at, run_directory = _create_run_directory(output_root)
    statistics_path = run_directory / "boundary_rating_statistics.csv"
    summary_path = run_directory / "boundary_curve_summary.csv"
    fitted_path = run_directory / "boundary_curve_fitted_values.csv"
    chart_path = run_directory / "boundary_curve.html"
    manifest_path = run_directory / "manifest.json"

    _write_statistics(statistics_path, result)
    _write_curve_summary(summary_path, result, curve)
    _write_fitted_values(fitted_path, curve)
    _write_chart(chart_path, result, curve)

    manifest = {
        "generated_at_utc": generated_at.isoformat(),
        "requested_start_date": str(result.start_date),
        "target_division": TARGET_DIVISION,
        "boundary_anchor": "bottom",
        "tail_groups": result.tail_groups,
        "count_absences": count_absences,
        "rating_observation": (
            "One represented Makuuchi rikishi-basho, associated with the "
            "initial-after-normalisation rating and current banzuke "
            "distance from the lower division boundary."
        ),
        "coordinates": {
            "raw_slot": (
                "Individual position from the bottom of the competitive "
                "Makuuchi division; bottommost rikishi is 1."
            ),
            "paired_group": (
                "ceil(raw_slot / 2); bottom two rikishi form "
                "top_bottom_1."
            ),
        },
        "curve_order": [
            f"top_bottom_{distance}"
            for distance in curve.ordered_distances
        ],
        "endpoint_reversal": curve.endpoint_reversal,
        "endpoint_reversal_q_fraction": (
            curve.endpoint_reversal_q_fraction
        ),
        "monotonicity_method": (
            "The same naive inverse-SE weighted isotonic parametric-bootstrap "
            "test used by clean_elo.monotonicity_probe."
        ),
        "monotonicity": _monotonicity_fields(curve.monotonicity),
        "limitations": [
            "Rikishi-basho observations are treated as independent.",
            "Paired groups are formed by banzuke order from the bottom, not "
            "by literal rank number.",
            "A paired group can combine different literal chii when the "
            "historical banzuke structure is irregular.",
        ],
        "outputs": {
            "statistics_csv": str(statistics_path),
            "curve_summary_csv": str(summary_path),
            "fitted_values_csv": str(fitted_path),
            "chart_html": str(chart_path),
            "manifest_json": str(manifest_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return OutputPaths(
        run_directory=run_directory,
        statistics_csv=statistics_path,
        curve_summary_csv=summary_path,
        fitted_values_csv=fitted_path,
        chart_html=chart_path,
        manifest_json=manifest_path,
    )


def _write_statistics(
    path: Path,
    result: BoundaryRatingProbeResult,
) -> None:
    fields = [
        "coordinate_type",
        "boundary_distance",
        "label",
        "raw_slot_min",
        "raw_slot_max",
        "n",
        "mean_rating",
        "sample_standard_deviation",
        "standard_error",
        "naive_margin_of_error",
        "naive_ci95_lower",
        "naive_ci95_upper",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for distance, summary in sorted(result.slot_stats.items()):
            writer.writerow(
                _statistics_row(
                    coordinate_type="raw_slot",
                    distance=distance,
                    label=f"bottom_{distance}",
                    raw_slot_min=distance,
                    raw_slot_max=distance,
                    summary=summary,
                )
            )
        for distance, summary in sorted(
            result.paired_group_stats.items()
        ):
            writer.writerow(
                _statistics_row(
                    coordinate_type="paired_group",
                    distance=distance,
                    label=f"top_bottom_{distance}",
                    raw_slot_min=2 * distance - 1,
                    raw_slot_max=2 * distance,
                    summary=summary,
                )
            )


def _statistics_row(
    *,
    coordinate_type: str,
    distance: int,
    label: str,
    raw_slot_min: int,
    raw_slot_max: int,
    summary: RunningStats,
) -> dict[str, object]:
    interval = summary.naive_ci95()
    return {
        "coordinate_type": coordinate_type,
        "boundary_distance": distance,
        "label": label,
        "raw_slot_min": raw_slot_min,
        "raw_slot_max": raw_slot_max,
        "n": summary.n,
        "mean_rating": _number(summary.mean),
        "sample_standard_deviation": _number(
            summary.sample_standard_deviation
        ),
        "standard_error": _number(summary.standard_error),
        "naive_margin_of_error": _number(
            summary.naive_margin_of_error
        ),
        "naive_ci95_lower": _number(
            None if interval is None else interval[0]
        ),
        "naive_ci95_upper": _number(
            None if interval is None else interval[1]
        ),
    }


def _write_curve_summary(
    path: Path,
    result: BoundaryRatingProbeResult,
    curve: BoundaryCurveResult,
) -> None:
    fields = [
        "scope",
        "first_group",
        "last_group",
        "endpoint_reversal",
        "elo_q",
        "endpoint_reversal_q_fraction",
        "lack_of_fit_statistic",
        "bootstrap_samples",
        "bootstrap_exceedances",
        "p_value",
        "reject_at_0_05",
    ]
    monotonicity = curve.monotonicity
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "scope": monotonicity.scope.name,
                "first_group": (
                    f"top_bottom_{curve.ordered_distances[0]}"
                ),
                "last_group": (
                    f"top_bottom_{curve.ordered_distances[-1]}"
                ),
                "endpoint_reversal": _number(
                    curve.endpoint_reversal
                ),
                "elo_q": DEFAULT_Q,
                "endpoint_reversal_q_fraction": _number(
                    curve.endpoint_reversal_q_fraction
                ),
                "lack_of_fit_statistic": _number(
                    monotonicity.statistic
                ),
                "bootstrap_samples": monotonicity.bootstrap_samples,
                "bootstrap_exceedances": monotonicity.exceedances,
                "p_value": _number(monotonicity.p_value),
                "reject_at_0_05": monotonicity.p_value < 0.05,
            }
        )


def _write_fitted_values(
    path: Path,
    curve: BoundaryCurveResult,
) -> None:
    fields = [
        "label",
        "boundary_distance",
        "n",
        "mean_rating",
        "standard_error",
        "fitted_monotonic_mean",
        "residual",
        "standardized_residual",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for estimate, fitted in zip(
            curve.monotonicity.estimates,
            curve.monotonicity.fitted_means,
        ):
            residual = estimate.mean - fitted
            standard_error = float(estimate.standard_error)
            writer.writerow(
                {
                    "label": estimate.index,
                    "boundary_distance": estimate.number,
                    "n": estimate.n,
                    "mean_rating": _number(estimate.mean),
                    "standard_error": _number(standard_error),
                    "fitted_monotonic_mean": _number(fitted),
                    "residual": _number(residual),
                    "standardized_residual": _number(
                        residual / standard_error
                    ),
                }
            )


def _write_chart(
    path: Path,
    result: BoundaryRatingProbeResult,
    curve: BoundaryCurveResult,
) -> None:
    labels = [
        f"top_bottom_{distance}"
        for distance in curve.ordered_distances
    ]
    summaries = [
        result.paired_group_stats[distance]
        for distance in curve.ordered_distances
    ]
    means = [summary.mean for summary in summaries]
    margins = [
        0.0
        if summary.naive_margin_of_error is None
        else summary.naive_margin_of_error
        for summary in summaries
    ]
    hover = [
        (
            f"{label}<br>n={summary.n}<br>mean={summary.mean:.2f}"
            f"<br>CI95 margin={margin:.2f}"
        )
        for label, summary, margin in zip(labels, summaries, margins)
    ]
    data = [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "x": labels,
            "y": means,
            "text": hover,
            "hovertemplate": "%{text}<extra></extra>",
            "line": {"width": 2, "color": "#2563eb"},
            "marker": {"size": 6, "color": "#2563eb"},
            "error_y": {
                "type": "data",
                "symmetric": True,
                "array": margins,
                "visible": True,
                "thickness": 1,
                "width": 0,
                "color": "#6b7280",
            },
        }
    ]
    layout = {
        "title": {
            "text": (
                "Historical Makuuchi start-of-basho Elo by lower-boundary "
                "group"
            )
        },
        "xaxis": {
            "title": {"text": "Paired boundary group"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
        },
        "yaxis": {
            "title": {"text": "Mean start-of-basho Elo"},
            "range": [min(means), max(means)],
        },
        "showlegend": False,
        "height": 680,
        "margin": {"l": 80, "r": 30, "t": 80, "b": 80},
    }
    markup = f"""<div id="boundary-rating-curve" role="img" aria-label="Historical Makuuchi Elo rating by paired lower-boundary group" style="width:100%;min-height:680px"></div>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<script>
(() => {{
  const root = document.getElementById("boundary-rating-curve");
  const data = {json.dumps(data, separators=(",", ":"))};
  const layout = {json.dumps(layout, separators=(",", ":"))};
  Plotly.newPlot(root, data, layout, {{responsive: true, displaylogo: false}});
}})();
</script>
"""
    path.write_text(markup, encoding="utf-8")


def _monotonicity_fields(
    result: MonotonicityResult,
) -> dict[str, object]:
    return {
        "scope": result.scope.name,
        "lack_of_fit_statistic": result.statistic,
        "bootstrap_samples": result.bootstrap_samples,
        "bootstrap_exceedances": result.exceedances,
        "p_value": result.p_value,
        "random_seed": result.random_seed,
        "reject_at_0_05": result.p_value < 0.05,
    }


def _number(value: float | None) -> str:
    return "" if value is None else f"{value:.9f}"


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)


def _create_run_directory(root: Path) -> tuple[datetime, Path]:
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    while True:
        run_directory = root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory


def parse_date(value: str) -> Date:
    try:
        year, month = value.split("/")
        return Date(Year(int(year)), Month(int(month)))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY/MM"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Probe historical Makuuchi Elo ratings by distance from the "
            "lower division boundary."
        )
    )
    parser.add_argument("--start", required=True, type=parse_date)
    parser.add_argument(
        "--tail-groups",
        type=int,
        default=DEFAULT_TAIL_GROUPS,
    )
    parser.add_argument(
        "--count-absences",
        action="store_true",
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
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    _result, curve, outputs = run_probe(
        history=get_history(),
        start_date=args.start,
        output_root=args.output_root,
        tail_groups=args.tail_groups,
        count_absences=args.count_absences,
        bootstrap_samples=args.bootstrap_samples,
        random_seed=args.seed,
    )
    print(f"Run directory: {outputs.run_directory}")
    print(
        f"Endpoint reversal: {curve.endpoint_reversal:.6f} "
        f"({curve.endpoint_reversal_q_fraction:.6f} q)"
    )
    print(
        f"Monotonicity: statistic={curve.monotonicity.statistic:.6f}, "
        f"p={curve.monotonicity.p_value:.9f}"
    )
    print(f"Statistics: {outputs.statistics_csv}")
    print(f"Curve summary: {outputs.curve_summary_csv}")
    print(f"Chart: {outputs.chart_html}")


if __name__ == "__main__":
    main()
