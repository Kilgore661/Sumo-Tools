import argparse
import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Optional

try:
    from src.infra.config import EPOCH
    from src.infra.connect import connect
    from src.sumo_core.BasicEnums import MSD, Division
    from src.sumo_core.History import History
except ImportError:  # pragma: no cover - fallback for package-style execution
    from ..infra.config import EPOCH
    from ..infra.connect import connect
    from ..sumo_core.BasicEnums import MSD, Division
    from ..sumo_core.History import History


OUTPUT_HTML_NAME = "banzuke_division_era_chart.html"
OUTPUT_CSV_NAME = "banzuke_division_era_chart.csv"
SITE_BUNDLE_DIR = "banzuke_division_era/site/banzuke_division_by_era"

# Display order: top-to-bottom in legend / CSV / console
DIVISION_LABELS: list[str] = [
    "Makuuchi",
    "Juryo",
    "Makushita",
    "Sandanme",
    "Jonidan",
    "Jonokuchi",
]

# Harmonious, saturated, not-too-bright palette
DIVISION_COLOURS: dict[str, str] = {
    "Makuuchi": "#6D597A",
    "Juryo": "#355C7D",
    "Makushita": "#457B9D",
    "Sandanme": "#2A9D8F",
    "Jonidan": "#8D6A9F",
    "Jonokuchi": "#BC6C25",
}

MAKUUCHI_LEVELS = {
    MSD.YOKOZUNA,
    MSD.OZEKI,
    MSD.SEKIWAKE,
    MSD.KOMUSUBI,
    MSD.MAEGASHIRA,
}


@dataclass(frozen=True)
class BanzukeDivisionByEraOutputs:
    output_root: Path
    bundle_dir: Path
    diagnostic_csv: Path
    page_json: Path
    divisions_csv: Path
    metadata_json: Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a stacked era chart of average banzuke composition by division "
            "from the new History model."
        )
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--num-years-per-era",
        type=int,
        default=1,
        help=(
            "Width of each era bucket in years. Any leftover years at the end "
            "form their own shorter era. Default: 1."
        ),
    )
    parser.add_argument(
        "--output-html",
        type=Path,
        default=None,
        help=(
            "Optional output HTML path. If omitted, writes to "
            "files/output/banzuke_division_era_chart.html relative to this program."
        ),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help=(
            "Optional output CSV path. If omitted, writes to "
            "files/output/banzuke_division_era_chart.csv relative to this program."
        ),
    )
    return parser


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_output_html() -> Path:
    return _repo_root() / "files" / "output" / OUTPUT_HTML_NAME


def _default_output_csv() -> Path:
    return _repo_root() / "files" / "output" / OUTPUT_CSV_NAME


def _default_output_root() -> Path:
    return _repo_root() / "files" / "output"


def _build_eras(start_year: int, end_year: int, num_years_per_era: int) -> list[tuple[int, int, str]]:
    if num_years_per_era <= 0:
        raise ValueError("--num-years-per-era must be positive")

    if end_year < start_year:
        raise ValueError("--end must be >= --start")

    eras: list[tuple[int, int, str]] = []
    era_start = start_year

    while era_start <= end_year:
        era_end_exclusive = min(era_start + num_years_per_era, end_year + 1)
        eras.append(
            (
                era_start,
                era_end_exclusive,
                f"{era_start}-{era_end_exclusive - 1}",
            )
        )
        era_start = era_end_exclusive

    return eras


def _era_label(year: int, eras: list[tuple[int, int, str]]) -> Optional[str]:
    for start, end, label in eras:
        if start <= year < end:
            return label
    return None


def _division_label(chii) -> str:
    level = chii.level

    if level in MAKUUCHI_LEVELS:
        return "Makuuchi"

    if level == Division.JURYO:
        return "Juryo"
    if level == Division.MAKUSHITA:
        return "Makushita"
    if level == Division.SANDANME:
        return "Sandanme"
    if level == Division.JONIDAN:
        return "Jonidan"
    if level == Division.JONOKUCHI:
        return "Jonokuchi"

    raise TypeError(f"Cannot map level {level!r} to a division label")


def _division_counts_for_basho(basho) -> dict[str, int]:
    counts = {label: 0 for label in DIVISION_LABELS}

    for rid in basho.banzuke.riks:
        chii = basho.banzuke.rikchii[rid]
        label = _division_label(chii)
        counts[label] += 1

    return counts


def compute_era_average_counts(
    history: History,
    eras: list[tuple[int, int, str]],
) -> dict[str, dict[str, float]]:
    per_era_samples: dict[str, dict[str, list[int]]] = {
        era_label: {division: [] for division in DIVISION_LABELS}
        for _, _, era_label in eras
    }

    for date, basho in history.items():
        era = _era_label(int(date.year), eras)
        if era is None:
            continue

        basho_counts = _division_counts_for_basho(basho)
        for division in DIVISION_LABELS:
            per_era_samples[era][division].append(basho_counts[division])

    averages: dict[str, dict[str, float]] = {
        era_label: {}
        for _, _, era_label in eras
    }

    for _, _, era_label in eras:
        for division in DIVISION_LABELS:
            samples = per_era_samples[era_label][division]
            averages[era_label][division] = fmean(samples) if samples else 0.0

    return averages


def write_matrix_csv(
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
    output_path: Path,
) -> Path:
    import csv

    era_labels = [label for _, _, label in eras]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["era", *DIVISION_LABELS, "total_avg"])

        for era_label in era_labels:
            raw_values = [era_averages[era_label].get(div, 0.0) for div in DIVISION_LABELS]
            rounded_values = [round(value, 3) for value in raw_values]
            total_avg = round(sum(raw_values), 3)
            writer.writerow([era_label, *rounded_values, total_avg])

    return output_path


def write_banzuke_division_by_era_csv(
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
    output_path: Path,
) -> Path:
    import csv

    era_labels = [label for _, _, label in eras]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["era", "division", "average_rikishi", "total_average"])

        for era_label in era_labels:
            raw_values = [era_averages[era_label].get(div, 0.0) for div in DIVISION_LABELS]
            total_average = round(sum(raw_values), 3)
            for division in DIVISION_LABELS:
                writer.writerow(
                    [
                        era_label,
                        division,
                        round(era_averages[era_label].get(division, 0.0), 3),
                        total_average,
                    ]
                )

    return output_path


def write_banzuke_division_by_era_bundle(
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
    bundle_dir: Path,
    *,
    start: int,
    end: int,
    num_years_per_era: int,
    source_csv: Path,
) -> BanzukeDivisionByEraOutputs:
    output_root = bundle_dir.parents[2]
    bundle_dir.mkdir(parents=True, exist_ok=True)
    outputs = BanzukeDivisionByEraOutputs(
        output_root=output_root,
        bundle_dir=bundle_dir,
        diagnostic_csv=source_csv,
        page_json=bundle_dir / "page.json",
        divisions_csv=bundle_dir / "divisions.csv",
        metadata_json=bundle_dir / "metadata.json",
    )
    write_banzuke_division_by_era_csv(
        era_averages,
        eras,
        outputs.divisions_csv,
    )
    _write_page_json(
        outputs.page_json,
        eras=eras,
        start=start,
        end=end,
        num_years_per_era=num_years_per_era,
    )
    _write_metadata_json(
        outputs.metadata_json,
        era_averages=era_averages,
        eras=eras,
        start=start,
        end=end,
        num_years_per_era=num_years_per_era,
        source_csv=source_csv,
    )
    return outputs


def build_banzuke_division_by_era_outputs(
    history: History,
    *,
    output_root: Path | None = None,
    start: int,
    end: int,
    num_years_per_era: int = 10,
    print_summary: bool = True,
) -> BanzukeDivisionByEraOutputs:
    if output_root is None:
        output_root = _default_output_root()
    eras = _build_eras(start, end, num_years_per_era)
    era_averages = compute_era_average_counts(history, eras)
    diagnostic_csv = output_root / OUTPUT_CSV_NAME
    write_matrix_csv(era_averages, eras, diagnostic_csv)
    outputs = write_banzuke_division_by_era_bundle(
        era_averages=era_averages,
        eras=eras,
        bundle_dir=output_root / SITE_BUNDLE_DIR,
        start=start,
        end=end,
        num_years_per_era=num_years_per_era,
        source_csv=diagnostic_csv,
    )
    if print_summary:
        _print_summary(era_averages, eras)
        print(f"Wrote CSV to {diagnostic_csv}")
        print(f"Wrote bundle to {outputs.bundle_dir}")
    return outputs


def _write_page_json(
    output_path: Path,
    *,
    eras: list[tuple[int, int, str]],
    start: int,
    end: int,
    num_years_per_era: int,
) -> None:
    page = {
        "title": "Banzuke Division by Era",
        "summary": "Historical banzuke division structure by era.",
        "subtitle": (
            f"Average banzuke composition by division ({start}-{end}), "
            f"{num_years_per_era}-year era buckets except the final bucket."
        ),
        "data_sources": [
            {
                "id": "divisions",
                "label": "Average banzuke composition by era",
                "data": "divisions.csv",
                "media_type": "text/csv",
            }
        ],
        "chart": {
            "x_field": "era",
            "y_field": "average_rikishi",
            "group_field": "division",
            "x_label": "Era",
            "x_type": "category",
            "x_tickangle": -45,
            "x_order": [label for _, _, label in eras],
            "y_label": "Average rikishi per basho",
            "legend_title": "Division",
            "division_order": DIVISION_LABELS,
            "stack_order": list(reversed(DIVISION_LABELS)),
            "division_colours": DIVISION_COLOURS,
            "barmode": "stack",
        },
    }
    output_path.write_text(json.dumps(page, indent=2) + "\n", encoding="utf-8")


def _write_metadata_json(
    output_path: Path,
    *,
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
    start: int,
    end: int,
    num_years_per_era: int,
    source_csv: Path,
) -> None:
    metadata = {
        "analysis": "banzuke_division_by_era",
        "bundle": "banzuke_division_by_era",
        "start": start,
        "end": end,
        "num_years_per_era": num_years_per_era,
        "era_count": len(eras),
        "row_count": len(eras) * len(DIVISION_LABELS),
        "source_csv": source_csv.as_posix(),
        "value_policy": (
            "Each row is one era/division average count of rikishi per basho. "
            "The diagnostic CSV is retained as a wide matrix."
        ),
    }
    output_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def _plotly_traces(
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
) -> list[dict[str, object]]:
    era_labels = [label for _, _, label in eras]
    traces: list[dict[str, object]] = []

    # Plotly stacks from first trace at the bottom to last trace at the top.
    # So reverse the division order here to place:
    # Jonokuchi at bottom ... Makuuchi at top.
    for division in reversed(DIVISION_LABELS):
        traces.append(
            {
                "type": "bar",
                "name": division,
                "x": era_labels,
                "y": [era_averages[era_label].get(division, 0.0) for era_label in era_labels],
                "marker": {"color": DIVISION_COLOURS[division]},
                "hovertemplate": (
                    "Division: %{fullData.name}<br>"
                    "Era: %{x}<br>"
                    "Average rikishi per basho: %{y:.2f}<extra></extra>"
                ),
            }
        )

    return traces


def write_chart_html(
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
    output_path: Path,
) -> Path:
    traces = _plotly_traces(era_averages, eras)
    traces_json = json.dumps(traces, ensure_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Banzuke Composition by Era</title>
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
      text-align: center;
    }}

    .subtitle {{
      margin: 0 0 16px 0;
      color: #9ca3af;
      font-size: 14px;
      line-height: 1.5;
      text-align: center;
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
    <h1>Banzuke Composition by Era</h1>
    <p class="subtitle">
      Stacked bars show the average number of rikishi per basho in each division.
    </p>
    <div class="chart-wrap">
      <div id="chart"></div>
    </div>
  </div>

  <script>
    const traces = {traces_json};

    const layout = {{
      barmode: "stack",
      paper_bgcolor: "#111827",
      plot_bgcolor: "#111827",
      font: {{
        color: "#e5e7eb"
      }},
      xaxis: {{
        type: "category",
        title: "Era",
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      yaxis: {{
        title: "Average rikishi per basho",
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      legend: {{
        orientation: "v",
        yanchor: "top",
        y: 1,
        xanchor: "left",
        x: 1.02,
        traceorder: "reversed",
        itemclick: false,
        itemdoubleclick: false
      }},
      margin: {{
        l: 80,
        r: 190,
        t: 30,
        b: 70
      }},
      hovermode: "closest"
    }};

    const config = {{
      responsive: true,
      displaylogo: false
    }};

    const chart = document.getElementById("chart");
    let legendClickTimer = null;
    let legendClickCurve = null;

    function isolateTrace(curveNumber) {{
      const target = chart.data[curveNumber];
      if (!target) return;
      const visibility = chart.data.map((trace, index) =>
        index === curveNumber ? true : "legendonly"
      );
      Plotly.restyle(chart, {{ visible: visibility }});
    }}

    function toggleTrace(curveNumber) {{
      const target = chart.data[curveNumber];
      if (!target) return;
      const nextVisibility = target.visible === true || target.visible === undefined
        ? "legendonly"
        : true;
      Plotly.restyle(chart, {{ visible: nextVisibility }}, [curveNumber]);
    }}

    function handleLegendClick(event) {{
      const curveNumber = event.curveNumber;
      if (legendClickTimer && legendClickCurve === curveNumber) {{
        window.clearTimeout(legendClickTimer);
        legendClickTimer = null;
        legendClickCurve = null;
        isolateTrace(curveNumber);
        return false;
      }}

      if (legendClickTimer) {{
        window.clearTimeout(legendClickTimer);
        toggleTrace(legendClickCurve);
      }}

      legendClickCurve = curveNumber;
      legendClickTimer = window.setTimeout(() => {{
        toggleTrace(curveNumber);
        legendClickTimer = null;
        legendClickCurve = null;
      }}, 275);
      return false;
    }}

    Plotly.newPlot(chart, traces, layout, config).then(() => {{
      if (chart.removeAllListeners) {{
        chart.removeAllListeners("plotly_legendclick");
        chart.removeAllListeners("plotly_legenddoubleclick");
      }}
      chart.on("plotly_legendclick", handleLegendClick);
      chart.on("plotly_legenddoubleclick", event => {{
        isolateTrace(event.curveNumber);
        return false;
      }});
    }});
  </script>
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
    return output_path


def _print_summary(
    era_averages: dict[str, dict[str, float]],
    eras: list[tuple[int, int, str]],
) -> None:
    print("Average banzuke composition by era")
    print("=" * 108)
    print(f"{'Era':<12}", end="")
    for division in DIVISION_LABELS:
        print(f"{division:>14}", end="")
    print(f"{'Total avg':>14}")
    print("-" * 108)

    for _, _, era_label in eras:
        values = [era_averages[era_label].get(division, 0.0) for division in DIVISION_LABELS]
        total_avg = sum(values)

        print(f"{era_label:<12}", end="")
        for value in values:
            print(f"{value:>14.2f}", end="")
        print(f"{total_avg:>14.2f}")

    print("-" * 108)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    history = connect(args.start, args.end, use_zip=args.zip)
    if not history:
        raise ValueError("No history returned by connect()")

    eras = _build_eras(args.start, args.end, args.num_years_per_era)
    if not eras:
        raise ValueError("No era buckets were created")

    era_averages = compute_era_average_counts(history, eras)

    output_csv = args.output_csv if args.output_csv is not None else _default_output_csv()
    output_html = (
        args.output_html if args.output_html is not None else _default_output_html()
    )

    written_csv = write_matrix_csv(era_averages, eras, output_csv)
    written_html = write_chart_html(era_averages, eras, output_html)
    written_bundle = write_banzuke_division_by_era_bundle(
        era_averages=era_averages,
        eras=eras,
        bundle_dir=_default_output_root() / SITE_BUNDLE_DIR,
        start=args.start,
        end=args.end,
        num_years_per_era=args.num_years_per_era,
        source_csv=output_csv,
    )

    _print_summary(era_averages, eras)
    print()
    print(f"Years per era: {args.num_years_per_era}")
    print(f"Wrote CSV to {written_csv}")
    print(f"Wrote chart to {written_html}")
    print(f"Wrote bundle to {written_bundle.bundle_dir}")


if __name__ == "__main__":
    main()
