import argparse
import datetime
import json
import math
from pathlib import Path
from statistics import fmean, pstdev
from typing import Iterable

try:
    from src.infra.config import EPOCH
    from src.infra.connect import connect
    from src.sumo_core.BasicEnums import Division, MSD
    from src.sumo_core.History import Date, History
except ImportError:  # pragma: no cover - fallback for package-style execution
    from ..infra.config import EPOCH
    from ..infra.connect import connect
    from ..sumo_core.BasicEnums import Division, MSD
    from ..sumo_core.History import Date, History


DIVISIONS: tuple[Division, ...] = (
    Division.MAKUUCHI,
    Division.JURYO,
    Division.MAKUSHITA,
    Division.SANDANME,
    Division.JONIDAN,
    Division.JONOKUCHI,
)

MAKUUCHI_LEVELS = {
    MSD.YOKOZUNA,
    MSD.OZEKI,
    MSD.SEKIWAKE,
    MSD.KOMUSUBI,
    MSD.MAEGASHIRA,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute basho-to-basho division retention and write a dark-themed "
            "Plotly HTML chart."
        )
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Optional output HTML path. If omitted, writes to "
            "files/output/division_churn.html relative to this program."
        ),
    )
    return parser


def _default_output_path() -> Path:
    # division_churn.py is expected at: Sumo-Tools/src/misc/division_churn.py
    # so parents[2] is the repository root: Sumo-Tools/
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "files" / "output" / "division_churn.html"


def _division_label(div: Division) -> str:
    labels = {
        Division.MAKUUCHI: "Makuuchi",
        Division.JURYO: "Juryo",
        Division.MAKUSHITA: "Makushita",
        Division.SANDANME: "Sandanme",
        Division.JONIDAN: "Jonidan",
        Division.JONOKUCHI: "Jonokuchi",
    }
    return labels[div]


def _division_of_level(level: object) -> Division:
    """
    Collapse the rank-level model to division-level buckets.

    In this codebase, makuuchi ranks are represented by MSD values, while the
    lower divisions are represented directly by Division values.
    """
    if level in MAKUUCHI_LEVELS:
        return Division.MAKUUCHI

    if isinstance(level, Division):
        return level

    raise TypeError(f"Cannot map level {level!r} to a Division")


def _members_by_division(history: History, date: Date) -> dict[Division, set]:
    """
    Return division -> set[RikId] for the given basho date.
    """
    banzuke = history[date].banzuke
    out: dict[Division, set] = {div: set() for div in DIVISIONS}

    for rid in banzuke.riks:
        chii = banzuke.rikchii[rid]
        div = _division_of_level(chii.level)
        out[div].add(rid)

    return out


def common_pop(history: History, date: Date, division: Division) -> int:
    """
    Number of rikishi in `division` on `date` who were also in `division`
    in the immediately previous basho.

    Undefined for the first date in the history ordering.
    """
    dates = sorted(history.keys())
    idx = dates.index(date)
    if idx == 0:
        raise ValueError("common_pop is undefined for the first date in history")

    prev_date = dates[idx - 1]
    prev_members = _members_by_division(history, prev_date)[division]
    curr_members = _members_by_division(history, date)[division]
    return len(prev_members & curr_members)


def _population(history: History, date: Date, division: Division) -> int:
    """
    Current population of a division at a basho date.
    """
    return len(_members_by_division(history, date)[division])


def retention_pct(history: History, date: Date, division: Division) -> float | None:
    """
    Percentage of the current division population that was in the same division
    in the previous basho.

    Returns None if the current population is empty.
    """
    pop = _population(history, date, division)
    if pop == 0:
        return None
    return 100.0 * common_pop(history, date, division) / pop


def _retention_series(history: History) -> dict[Division, list[dict[str, object]]]:
    dates = sorted(history.keys())
    series: dict[Division, list[dict[str, object]]] = {div: [] for div in DIVISIONS}

    for date in dates[1:]:
        for div in DIVISIONS:
            value = retention_pct(history, date, div)
            point = {
                "date": str(date),
                "retention_pct": value,
                "common_pop": common_pop(history, date, div),
                "population": _population(history, date, div),
            }
            series[div].append(point)

    return series


def _format_pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def _print_stats(series: dict[Division, list[dict[str, object]]]) -> None:
    print("Division churn statistics")
    print("=" * 80)
    print(
        f"{'Division':<12} {'N':>5} {'Mean %':>10} {'Stdev %':>10} "
        f"{'Min %':>10} {'Max %':>10}"
    )
    print("-" * 80)

    for div in DIVISIONS:
        values = [
            point["retention_pct"]
            for point in series[div]
            if point["retention_pct"] is not None
        ]
        if not values:
            print(
                f"{_division_label(div):<12} {0:>5} {'NA':>10} {'NA':>10} {'NA':>10} {'NA':>10}"
            )
            continue

        mean_val = fmean(values)
        stdev_val = pstdev(values)
        min_val = min(values)
        max_val = max(values)

        print(
            f"{_division_label(div):<12} "
            f"{len(values):>5} "
            f"{mean_val:>10.2f} "
            f"{stdev_val:>10.2f} "
            f"{min_val:>10.2f} "
            f"{max_val:>10.2f}"
        )

    print("-" * 80)
    print("Note: stdev is population standard deviation over the plotted series.")


def _build_plot_payload(series: dict[Division, list[dict[str, object]]]) -> list[dict[str, object]]:
    traces: list[dict[str, object]] = []

    for div in DIVISIONS:
        points = series[div]
        traces.append(
            {
                "name": _division_label(div),
                "x": [point["date"] for point in points],
                "y": [point["retention_pct"] for point in points],
                "mode": "lines",
                "type": "scatter",
                "hovertemplate": (
                    "Division: %{fullData.name}<br>"
                    "Basho: %{x}<br>"
                    "Retention: %{y:.2f}%<extra></extra>"
                ),
            }
        )

    return traces


def _write_html(output_path: Path, traces: list[dict[str, object]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload_json = json.dumps(traces, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Division Churn</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      color-scheme: dark;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      background: #111827;
      color: #e5e7eb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      width: 100%;
      height: 100%;
    }}

    .page {{
      box-sizing: border-box;
      min-height: 100vh;
      width: 100%;
      padding: 20px;
    }}

    h1 {{
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 700;
    }}

    .subtitle {{
      margin: 0 0 16px 0;
      color: #9ca3af;
      font-size: 14px;
      line-height: 1.5;
    }}

    .chart-wrap {{
      width: 100%;
      height: calc(100vh - 120px);
      min-height: 540px;
      background: #111827;
      border: 1px solid #374151;
      border-radius: 12px;
      overflow: hidden;
    }}

    #chart {{
      width: 100%;
      height: 100%;
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Division Churn</h1>
    <p class="subtitle">
      Percentage of each division's current population that was in the same division
      in the immediately previous basho.
    </p>
    <div class="chart-wrap">
      <div id="chart"></div>
    </div>
  </div>

  <script>
    const traces = {payload_json};

    const layout = {{
      paper_bgcolor: "#111827",
      plot_bgcolor: "#111827",
      font: {{
        color: "#e5e7eb"
      }},
      xaxis: {{
        type: "category",
        title: "Basho",
        tickangle: -45,
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      yaxis: {{
        title: "Retention (%)",
        range: [0, 100],
        gridcolor: "#374151",
        linecolor: "#4b5563",
        ticksuffix: "%",
        automargin: true
      }},
      legend: {{
        orientation: "h",
        yanchor: "bottom",
        y: 1.02,
        xanchor: "left",
        x: 0
      }},
      margin: {{
        l: 70,
        r: 30,
        t: 30,
        b: 90
      }},
      hovermode: "x unified"
    }};

    const config = {{
      responsive: true,
      displaylogo: false
    }};

    Plotly.newPlot("chart", traces, layout, config);
  </script>
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
    return output_path


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    history = connect(args.start, args.end, use_zip=args.zip)
    if not history:
        raise ValueError("No history returned by connect()")

    dates = sorted(history.keys())
    if len(dates) < 2:
        raise ValueError("Need at least two basho in history to compute division churn")

    series = _retention_series(history)
    _print_stats(series)

    output_path = args.output if args.output is not None else _default_output_path()
    written = _write_html(output_path, _build_plot_payload(series))

    print()
    print(f"Basho range: {dates[0]} -> {dates[-1]}")
    print(f"Output HTML: {written}")


if __name__ == "__main__":
    main()
