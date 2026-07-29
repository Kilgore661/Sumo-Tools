"""Describe start-of-basho Elo ratings associated with each binned index."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scipy.stats import t as student_t

from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History

from .index_probe import (
    BinningPolicy,
    Index,
    POLICIES,
    convert_chii,
)
from .simulate import SimulationResult, simulate


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/clean_elo/rating_probe"
)
CONFIDENCE_LEVEL = 0.95


@dataclass
class RunningStats:
    """Numerically stable running sample moments."""

    n: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def add(self, value: float) -> None:
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (value - self.mean)

    @property
    def sample_standard_deviation(self) -> float | None:
        if self.n < 2:
            return None
        return math.sqrt(self.m2 / (self.n - 1))

    @property
    def standard_error(self) -> float | None:
        standard_deviation = self.sample_standard_deviation
        if standard_deviation is None:
            return None
        return standard_deviation / math.sqrt(self.n)

    @property
    def naive_margin_of_error(self) -> float | None:
        standard_error = self.standard_error
        if standard_error is None:
            return None
        critical_value = float(
            student_t.ppf(
                0.5 + CONFIDENCE_LEVEL / 2.0,
                self.n - 1,
            )
        )
        return critical_value * standard_error

    @property
    def relative_margin_of_error(self) -> float | None:
        """Return the naive margin of error as a fraction of |mean|."""
        margin = self.naive_margin_of_error
        if margin is None or self.mean == 0.0:
            return None
        return margin / abs(self.mean)

    def naive_ci95(self) -> tuple[float, float] | None:
        margin = self.naive_margin_of_error
        if margin is None:
            return None
        return self.mean - margin, self.mean + margin


@dataclass(frozen=True)
class RatingProbeResult:
    start_date: Date
    simulation: SimulationResult
    index_stats: dict[BinningPolicy, dict[Index, RunningStats]]
    conversion_exception_counts: dict[BinningPolicy, int]
    missing_banzuke_occurrences: int


@dataclass(frozen=True)
class RatingProbeOutputPaths:
    run_directory: Path
    index_rating_statistics_csv: Path
    standard_error_relative_margin_html: Path
    bp4_mean_ci95_html: Path
    manifest_json: Path


def probe_index_ratings(
    history: History,
    start_date: Date,
    *,
    count_absences: bool = False,
) -> RatingProbeResult:
    """Associate each rikishi-basho with its start-of-basho rating and chii."""
    simulation = simulate(
        history=history,
        start_date=start_date,
        count_absences=count_absences,
    )
    stats: dict[BinningPolicy, dict[Index, RunningStats]] = {
        policy: {} for policy in POLICIES
    }
    exceptions = {policy: 0 for policy in POLICIES}
    missing_banzuke_occurrences = 0

    for date in sorted(simulation.basho_ratings, key=_date_key):
        basho = history[date]
        initial_ratings = simulation.basho_ratings[
            date
        ].initial_after_normalisation
        for rikid, rating in initial_ratings.items():
            chii = basho.banzuke.rikchii.get(rikid)
            if chii is None:
                missing_banzuke_occurrences += 1
                continue
            for policy in POLICIES:
                conversion = convert_chii(chii, policy)
                if not conversion.valid:
                    exceptions[policy] += 1
                    continue
                policy_stats = stats[policy]
                index = conversion.index
                policy_stats.setdefault(index, RunningStats()).add(rating)

    return RatingProbeResult(
        start_date=start_date,
        simulation=simulation,
        index_stats=stats,
        conversion_exception_counts=exceptions,
        missing_banzuke_occurrences=missing_banzuke_occurrences,
    )


def write_rating_probe_outputs(
    result: RatingProbeResult,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> RatingProbeOutputPaths:
    generated_at, run_directory = _create_run_directory(Path(output_root))
    statistics_csv = run_directory / "index_rating_statistics.csv"
    chart_html = (
        run_directory
        / "bp1_standard_error_by_relative_margin_of_error.html"
    )
    bp4_mean_ci95_html = run_directory / "bp4_mean_rating_with_ci95.html"
    manifest_json = run_directory / "manifest.json"

    with statistics_csv.open("w", newline="", encoding="utf-8") as stream:
        fieldnames = [
            "policy",
            "index",
            "index_ordinal",
            "level_code",
            "level",
            "number",
            "side",
            "annotation",
            "n",
            "mean_rating",
            "sample_standard_deviation",
            "standard_error",
            "naive_margin_of_error",
            "naive_relative_margin_of_error",
            "naive_relative_margin_of_error_percentage",
            "naive_ci95_lower",
            "naive_ci95_upper",
            "naive_ci95_width",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for policy in POLICIES:
            for index in sorted(
                result.index_stats[policy],
                key=Index.sort_key,
            ):
                summary = result.index_stats[policy][index]
                interval = summary.naive_ci95()
                lower = None if interval is None else interval[0]
                upper = None if interval is None else interval[1]
                writer.writerow(
                    {
                        "policy": policy.value,
                        **_index_fields(index),
                        "n": summary.n,
                        "mean_rating": _number(summary.mean),
                        "sample_standard_deviation": _number(
                            summary.sample_standard_deviation
                        ),
                        "standard_error": _number(summary.standard_error),
                        "naive_margin_of_error": _number(
                            summary.naive_margin_of_error
                        ),
                        "naive_relative_margin_of_error": _number(
                            summary.relative_margin_of_error
                        ),
                        "naive_relative_margin_of_error_percentage": _number(
                            None
                            if summary.relative_margin_of_error is None
                            else 100.0
                            * summary.relative_margin_of_error
                        ),
                        "naive_ci95_lower": _number(lower),
                        "naive_ci95_upper": _number(upper),
                        "naive_ci95_width": _number(
                            None
                            if interval is None
                            else upper - lower
                        ),
                    }
                )

    _write_standard_error_relative_margin_chart(chart_html, result)
    _write_bp4_mean_ci95_chart(bp4_mean_ci95_html, result)

    manifest = {
        "generated_at_utc": generated_at.isoformat(),
        "requested_start_date": str(result.start_date),
        "confidence_level": CONFIDENCE_LEVEL,
        "rating_observation": (
            "One rikishi-basho represented in the simulation, associated "
            "with current chii and initial-after-normalisation rating"
        ),
        "confidence_method": (
            "Naive two-sided Student-t interval for the arithmetic mean; "
            "observations are treated as independent"
        ),
        "relative_margin_of_error_definition": (
            "Student-t 95% margin of error / absolute mean rating"
        ),
        "rated_bout_count": result.simulation.rated_bout_count,
        "ignored_fusen_count": result.simulation.ignored_fusen_count,
        "missing_banzuke_occurrences": (
            result.missing_banzuke_occurrences
        ),
        "policies": {
            policy.value: {
                "distinct_indices": len(result.index_stats[policy]),
                "observations": sum(
                    item.n
                    for item in result.index_stats[policy].values()
                ),
                "conversion_exception_occurrences": (
                    result.conversion_exception_counts[policy]
                ),
            }
            for policy in POLICIES
        },
        "files": {
            "index_rating_statistics_csv": str(statistics_csv),
            "bp1_standard_error_by_relative_margin_of_error_html": (
                str(chart_html)
            ),
            "bp4_mean_rating_with_ci95_html": str(bp4_mean_ci95_html),
        },
    }
    manifest_json.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return RatingProbeOutputPaths(
        run_directory=run_directory,
        index_rating_statistics_csv=statistics_csv,
        standard_error_relative_margin_html=chart_html,
        bp4_mean_ci95_html=bp4_mean_ci95_html,
        manifest_json=manifest_json,
    )


def run_rating_probe(
    *,
    history: History,
    start_date: Date,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    count_absences: bool = False,
) -> tuple[RatingProbeResult, RatingProbeOutputPaths]:
    result = probe_index_ratings(
        history,
        start_date,
        count_absences=count_absences,
    )
    return result, write_rating_probe_outputs(result, output_root)


def _index_fields(index: Index) -> dict[str, object]:
    return {
        "index": index.display,
        "index_ordinal": index.ordinal,
        "level_code": index.level_code,
        "level": index.level,
        "number": "" if index.number is None else index.number,
        "side": "" if index.side is None else index.side,
        "annotation": (
            "" if index.annotation is None else index.annotation
        ),
    }


def _number(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _write_standard_error_relative_margin_chart(
    path: Path,
    result: RatingProbeResult,
) -> None:
    """Write a Plotly BP1 SE-versus-relative-margin scatter chart."""
    points = [
        (index, summary)
        for index, summary in sorted(
            result.index_stats[BinningPolicy.BP1].items(),
            key=lambda item: item[0].sort_key(),
        )
        if summary.standard_error not in (None, 0.0)
        and summary.relative_margin_of_error not in (None, 0.0)
    ]
    data = [
        {
            "type": "scattergl",
            "mode": "markers",
            "name": "BP1 indices",
            "x": [
                100.0 * summary.relative_margin_of_error
                for _, summary in points
            ],
            "y": [summary.standard_error for _, summary in points],
            "text": [
                (
                    f"{index.display}<br>n={summary.n}"
                    f"<br>SE={summary.standard_error:.3f}"
                    "<br>Relative margin="
                    f"{100.0 * summary.relative_margin_of_error:.3f}%"
                )
                for index, summary in points
            ],
            "hovertemplate": "%{text}<extra></extra>",
            "marker": {"size": 6, "opacity": 0.55},
        }
    ]
    layout = {
        "title": {"text": "BP1 standard error by relative margin of error"},
        "xaxis": {
            "title": {"text": "Naive relative margin of error (%)"},
            "type": "log",
        },
        "yaxis": {
            "title": {"text": "Standard error"},
            "type": "log",
        },
        "showlegend": False,
        "margin": {"l": 80, "r": 30, "t": 60, "b": 75},
        "height": 680,
    }
    _write_plotly_chart(
        path,
        chart_id="bp1-se-relative-margin",
        data=data,
        layout=layout,
        aria_label=(
            "BP1 scatter chart of standard error against naive relative "
            "margin of error, with logarithmic axes."
        ),
    )


def _write_bp4_mean_ci95_chart(
    path: Path,
    result: RatingProbeResult,
) -> None:
    """Write an evenly spaced Plotly BP4 mean chart with CI95 error bars."""
    policy_stats = result.index_stats[BinningPolicy.BP4]
    points = [
        (index, policy_stats[index])
        for index in sorted(policy_stats, key=Index.sort_key)
    ]
    indices = [index.display for index, _ in points]
    lower = []
    upper = []
    hover = []
    for index, summary in points:
        interval = summary.naive_ci95()
        lower.append(None if interval is None else interval[0])
        upper.append(None if interval is None else interval[1])
        interval_text = (
            "undefined"
            if interval is None
            else f"{interval[0]:.2f} to {interval[1]:.2f}"
        )
        hover.append(
            f"{index.display}<br>n={summary.n}"
            f"<br>mean={summary.mean:.2f}<br>CI95={interval_text}"
        )
    means = [summary.mean for _, summary in points]
    error_plus = [
        0.0 if high is None else high - mean
        for mean, high in zip(means, upper)
    ]
    error_minus = [
        0.0 if low is None else mean - low
        for mean, low in zip(means, lower)
    ]
    data = [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "x": indices,
            "y": means,
            "text": hover,
            "hovertemplate": "%{text}<extra></extra>",
            "name": "Mean rating with naive CI95",
            "line": {"width": 1.5},
            "marker": {"size": 3},
            "error_y": {
                "type": "data",
                "symmetric": False,
                "array": error_plus,
                "arrayminus": error_minus,
                "visible": True,
                "thickness": 0.8,
                "width": 0,
            },
        }
    ]
    layout = {
        "title": {"text": "BP4 mean start-of-basho rating with naive CI95"},
        "xaxis": {
            "title": {"text": "BP4 index"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": indices,
            "tickangle": -60,
            "automargin": True,
        },
        "yaxis": {
            "title": {"text": "Start-of-basho Elo rating"},
            "automargin": True,
            "range": [min(means), max(means)],
        },
        "showlegend": False,
        "hovermode": "closest",
        "margin": {"l": 80, "r": 30, "t": 85, "b": 120},
        "height": 720,
    }
    _write_plotly_chart(
        path,
        chart_id="bp4-mean-ci95",
        data=data,
        layout=layout,
        aria_label=(
            "BP4 chart of mean start-of-basho Elo ratings with a naive "
            "95 percent confidence band. Every chii is evenly spaced."
        ),
    )


def _write_plotly_chart(
    path: Path,
    *,
    chart_id: str,
    data: list[dict[str, object]],
    layout: dict[str, object],
    aria_label: str,
) -> None:
    """Write a self-contained chart fragment using pinned Plotly from CDN."""
    data_json = json.dumps(data, separators=(",", ":"))
    layout_json = json.dumps(layout, separators=(",", ":"))
    markup = f"""<div id="{chart_id}" role="img" aria-label="{aria_label}" style="width:100%;min-height:680px"></div>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<script>
(() => {{
  const root = document.getElementById("{chart_id}");
  const styles = getComputedStyle(document.documentElement);
  const token = (name, fallback) => styles.getPropertyValue(name).trim() || fallback;
  const data = {data_json};
  const layout = {layout_json};
  const series1 = token("--viz-series-1", "#2563eb");
  const foreground = token("--foreground", "#111827");
  const mutedForeground = token("--muted-foreground", "#6b7280");
  const border = token("--border", "#d1d5db");
  data.forEach((trace, index) => {{
    if (index === 1) {{
      trace.fillcolor = series1;
      trace.opacity = 0.24;
    }}
    if (index === 2 || data.length === 1) {{
      trace.marker = Object.assign({{}}, trace.marker, {{color: series1}});
      trace.line = Object.assign({{}}, trace.line, {{color: series1}});
    }}
    if (trace.error_y) trace.error_y.color = mutedForeground;
  }});
  Object.assign(layout, {{
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: {{color: foreground}},
  }});
  layout.xaxis = Object.assign({{}}, layout.xaxis, {{gridcolor: border, zerolinecolor: border}});
  layout.yaxis = Object.assign({{}}, layout.yaxis, {{gridcolor: border, zerolinecolor: border}});
  Plotly.newPlot(root, data, layout, {{responsive: true, displaylogo: false}});
}})();
</script>
"""
    path.write_text(markup, encoding="utf-8")


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)


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


def parse_date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/")
        return Date(Year(int(year_text)), Month(int(month_text)))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY/MM"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Probe naïve confidence intervals for Elo ratings by binned index."
        )
    )
    parser.add_argument(
        "--start",
        required=True,
        type=parse_date,
        help="First basho to simulate, in YYYY/MM format.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    parser.add_argument(
        "--count-absences",
        action="store_true",
        help="Include paired fusen and inferred kyujo in the Elo simulation.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result, outputs = run_rating_probe(
        history=get_history(),
        start_date=args.start,
        output_root=args.output_root,
        count_absences=args.count_absences,
    )
    for policy in POLICIES:
        policy_stats = result.index_stats[policy]
        print(
            f"{policy.value}: {len(policy_stats)} indices, "
            f"{sum(item.n for item in policy_stats.values())} observations"
        )
    print(f"Run directory: {outputs.run_directory}")
    print(f"Statistics: {outputs.index_rating_statistics_csv}")
    print(f"Chart: {outputs.standard_error_relative_margin_html}")
    print(f"BP4 mean CI95 chart: {outputs.bp4_mean_ci95_html}")


if __name__ == "__main__":
    main()
