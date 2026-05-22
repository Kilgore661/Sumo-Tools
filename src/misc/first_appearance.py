import argparse
import csv
import datetime
import json
from dataclasses import dataclass
from pathlib import Path

try:
    from src.infra.config import EPOCH
    from src.infra.connect import connect
    from src.sumo_core.BasicPrimitives import Day
    from src.sumo_core.Chii import Chii
    from src.sumo_core.History import Date, History
except ImportError:  # pragma: no cover - fallback for package-style execution
    from ..infra.config import EPOCH
    from ..infra.connect import connect
    from ..sumo_core.BasicPrimitives import Day
    from ..sumo_core.Chii import Chii
    from ..sumo_core.History import Date, History


OUTPUT_CSV_NAME = "first_app.csv"
OUTPUT_HTML_NAME = "first_app.html"
SITE_BUNDLE_DIR = "first_app/site/first_chii_appearance"

BASE_YEAR = 1958
BASE_MONTH = 1
DTICK_912_DAYS_MS = 912 * 24 * 60 * 60 * 1000


@dataclass(frozen=True, order=True)
class FirstAppearance:
    date: Date
    day: Day


@dataclass(frozen=True)
class FirstChiiAppearanceOutputs:
    output_root: Path
    bundle_dir: Path
    diagnostic_csv: Path
    page_json: Path
    appearances_csv: Path
    metadata_json: Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute first observed bout appearance for each Chii, "
            "write a CSV, and render a Plotly HTML chart."
        )
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help=(
            "Optional output CSV path. If omitted, writes to "
            "files/output/first_app.csv relative to this program."
        ),
    )
    parser.add_argument(
        "--output-html",
        type=Path,
        default=None,
        help=(
            "Optional output HTML path. If omitted, writes to "
            "files/output/first_app.html relative to this program."
        ),
    )
    return parser


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_output_csv() -> Path:
    return _repo_root() / "files" / "output" / OUTPUT_CSV_NAME


def _default_output_html() -> Path:
    return _repo_root() / "files" / "output" / OUTPUT_HTML_NAME


def _default_output_root() -> Path:
    return _repo_root() / "files" / "output"


def first_app(history: History) -> dict[Chii, FirstAppearance]:
    out: dict[Chii, FirstAppearance] = {}

    for date in sorted(history.keys()):
        basho = history[date]
        banzuke = basho.banzuke
        summary = basho.summary

        for day in sorted(summary.keys()):
            daily_results = summary[day]

            for bout in daily_results.results_lookup.values():
                r1 = bout.rikishi1
                r2 = bout.rikishi2

                if r1 in banzuke.rikchii:
                    c1 = banzuke.rikchii[r1]
                    if c1 not in out:
                        out[c1] = FirstAppearance(date=date, day=day)

                if r2 in banzuke.rikchii:
                    c2 = banzuke.rikchii[r2]
                    if c2 not in out:
                        out[c2] = FirstAppearance(date=date, day=day)

    return out


def _rows_by_first_seen(first_seen: dict[Chii, FirstAppearance]) -> list[tuple[Chii, FirstAppearance]]:
    return sorted(
        first_seen.items(),
        key=lambda item: (
            item[1].date.year,
            item[1].date.month,
            item[1].day,
            item[0].ordinal(),
            str(item[0]),
        ),
    )


def _rows_by_ordinal(first_seen: dict[Chii, FirstAppearance]) -> list[tuple[Chii, FirstAppearance]]:
    return sorted(
        first_seen.items(),
        key=lambda item: (item[0].ordinal(), str(item[0])),
    )


def _date_to_yyyymm(date: Date) -> str:
    return f"{int(date.year):04d}/{int(date.month):02d}"


def _month_index(date: Date) -> int:
    """
    Number of months since 1958/01, with 1958/01 -> 0.
    """
    return (int(date.year) - BASE_YEAR) * 12 + (int(date.month) - BASE_MONTH)


def write_first_app_csv(
    first_seen: dict[Chii, FirstAppearance],
    output_path: Path,
) -> Path:
    rows = _rows_by_first_seen(first_seen)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chii", "ordinal", "year", "month"])

        for chii, first in rows:
            writer.writerow(
                [
                    str(chii),
                    chii.ordinal(),
                    int(first.date.year),
                    int(first.date.month),
                ]
            )

    return output_path


def write_first_chii_appearance_csv(
    first_seen: dict[Chii, FirstAppearance],
    output_path: Path,
) -> Path:
    rows = _rows_by_ordinal(first_seen)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "chii",
                "ordinal",
                "year",
                "month",
                "first_appearance_month_index",
            ]
        )

        for chii, first in rows:
            writer.writerow(
                [
                    str(chii),
                    chii.ordinal(),
                    int(first.date.year),
                    int(first.date.month),
                    _month_index(first.date),
                ]
            )

    return output_path


def write_first_chii_appearance_bundle(
    first_seen: dict[Chii, FirstAppearance],
    bundle_dir: Path,
    *,
    start: int,
    end: int,
    source_csv: Path,
) -> FirstChiiAppearanceOutputs:
    output_root = bundle_dir.parents[2]
    bundle_dir.mkdir(parents=True, exist_ok=True)
    outputs = FirstChiiAppearanceOutputs(
        output_root=output_root,
        bundle_dir=bundle_dir,
        diagnostic_csv=source_csv,
        page_json=bundle_dir / "page.json",
        appearances_csv=bundle_dir / "appearances.csv",
        metadata_json=bundle_dir / "metadata.json",
    )
    write_first_chii_appearance_csv(first_seen, outputs.appearances_csv)
    _write_page_json(
        output_path=outputs.page_json,
        start=start,
        end=end,
    )
    _write_metadata_json(
        output_path=outputs.metadata_json,
        first_seen=first_seen,
        start=start,
        end=end,
        source_csv=source_csv,
    )
    return outputs


def build_first_chii_appearance_outputs(
    history: History,
    *,
    output_root: Path | None = None,
    start: int,
    end: int,
    print_summary: bool = True,
) -> FirstChiiAppearanceOutputs:
    if output_root is None:
        output_root = _default_output_root()
    first_seen = first_app(history)
    diagnostic_csv = output_root / OUTPUT_CSV_NAME
    write_first_app_csv(first_seen, diagnostic_csv)
    outputs = write_first_chii_appearance_bundle(
        first_seen=first_seen,
        bundle_dir=output_root / SITE_BUNDLE_DIR,
        start=start,
        end=end,
        source_csv=diagnostic_csv,
    )
    if print_summary:
        _print_summary(first_seen)
        print(f"Wrote CSV to {diagnostic_csv}")
        print(f"Wrote bundle to {outputs.bundle_dir}")
    return outputs


def _write_page_json(
    output_path: Path,
    *,
    start: int,
    end: int,
) -> None:
    page = {
        "title": "First Chii Appearance",
        "summary": "Earliest observed bout appearance for each chii.",
        "subtitle": f"First observed bout appearance by chii in sumodb bout records ({start}-{end}).",
        "data_sources": [
            {
                "id": "appearances",
                "label": "First observed appearance",
                "data": "appearances.csv",
                "media_type": "text/csv",
            }
        ],
        "chart": {
            "x_field": "chii",
            "x_order_field": "ordinal",
            "y_field": "first_appearance_month_index",
            "x_label": "Chii",
            "x_type": "category",
            "x_tickangle": -45,
            "y_label": "First appearance",
            "base_year": BASE_YEAR,
            "base_month": BASE_MONTH,
            "max_x_tick_labels": 40,
        },
    }
    output_path.write_text(json.dumps(page, indent=2) + "\n", encoding="utf-8")


def _write_metadata_json(
    output_path: Path,
    *,
    first_seen: dict[Chii, FirstAppearance],
    start: int,
    end: int,
    source_csv: Path,
) -> None:
    metadata = {
        "analysis": "first_chii_appearance",
        "bundle": "first_chii_appearance",
        "start": start,
        "end": end,
        "row_count": len(first_seen),
        "source_csv": source_csv.as_posix(),
        "value_policy": "Each row is the first observed bout appearance for one chii.",
    }
    output_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def write_first_app_html(
    first_seen: dict[Chii, FirstAppearance],
    output_path: Path,
) -> Path:
    rows = _rows_by_ordinal(first_seen)

    x_labels = [str(chii) for chii, _ in rows]
    y_values = [_month_index(first.date) for _, first in rows]
    customdata = [_date_to_yyyymm(first.date) for _, first in rows]

    tooltip_text = [f"{chii}: {_date_to_yyyymm(first.date)}" for chii, first in rows]

    trace = {
        "type": "bar",
        "x": x_labels,
        "y": y_values,
        "text": tooltip_text,
        "hovertemplate": "%{text}<extra></extra>",
    }

    traces_json = json.dumps([trace], ensure_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>First Bout Appearance by Chii</title>
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
      text-align: center;
    }}

    .chart-wrap {{
      width: 100%;
      height: calc(100vh - 120px);
      min-height: 560px;
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
    <h1>First Bout Appearance by Chii</h1>
    <div class="chart-wrap">
      <div id="chart"></div>
    </div>
  </div>

  <script>
    const traces = {traces_json};

    const baseDate = new Date({BASE_YEAR}, {BASE_MONTH - 1}, 1).getTime();
    const dtickMs = {DTICK_912_DAYS_MS};

    function monthIndexToLabel(monthIndex) {{
      const totalMonths = {BASE_MONTH - 1} + monthIndex;
      const year = {BASE_YEAR} + Math.floor(totalMonths / 12);
      const month = (totalMonths % 12) + 1;
      return String(year).padStart(4, "0") + "/" + String(month).padStart(2, "0");
    }}

    function buildTickVals(maxMonthIndex) {{
      const vals = [];
      let t = baseDate;

      while (true) {{
        const d = new Date(t);
        const monthIndex =
          (d.getFullYear() - {BASE_YEAR}) * 12 + d.getMonth() - ({BASE_MONTH} - 1);

        if (monthIndex > maxMonthIndex) break;

        vals.push(monthIndex);
        t += dtickMs;
      }}

      return vals;
    }}

    // Reduce x-axis crowding
    function buildXTickLabels(labels) {{
      const n = labels.length;
      const step = Math.ceil(n / 40); // ~40 labels max

      return labels.map((label, i) => {{
        if (i % step === 0) return label;
        return "";
      }});
    }}

    const xLabels = traces[0].x;
    const xTickText = buildXTickLabels(xLabels);

    const maxY = Math.max(...traces[0].y, 0);
    const tickvals = buildTickVals(maxY);
    const ticktext = tickvals.map(monthIndexToLabel);

    const layout = {{
      paper_bgcolor: "#111827",
      plot_bgcolor: "#111827",
      font: {{
        color: "#e5e7eb"
      }},
      xaxis: {{
        type: "category",
        title: "Chii",
        tickangle: -45,
        tickvals: xLabels,
        ticktext: xTickText,
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      yaxis: {{
        title: "First appearance",
        range: [0, maxY],
        tickmode: "array",
        tickvals: tickvals,
        ticktext: ticktext,
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      margin: {{
        l: 90,
        r: 30,
        t: 30,
        b: 120
      }},
      hovermode: "closest"
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


def _print_summary(first_seen: dict[Chii, FirstAppearance]) -> None:
    rows = _rows_by_first_seen(first_seen)

    print(f"Observed Chii values: {len(rows)}")
    if not rows:
        return

    first_chii, first_when = rows[0]
    last_chii, last_when = rows[-1]

    print(
        "Earliest observed Chii appearance: "
        f"{first_chii} (ordinal {first_chii.ordinal()}) at "
        f"{first_when.date}/{int(first_when.day)}"
    )
    print(
        "Latest first-observed Chii appearance: "
        f"{last_chii} (ordinal {last_chii.ordinal()}) at "
        f"{last_when.date}/{int(last_when.day)}"
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    history = connect(args.start, args.end, use_zip=args.zip)
    if not history:
        raise ValueError("No history returned by connect()")

    first_seen = first_app(history)

    output_csv = args.output_csv if args.output_csv is not None else _default_output_csv()
    output_html = args.output_html if args.output_html is not None else _default_output_html()

    written_csv = write_first_app_csv(first_seen, output_csv)
    written_html = write_first_app_html(first_seen, output_html)
    written_bundle = write_first_chii_appearance_bundle(
        first_seen=first_seen,
        bundle_dir=_default_output_root() / SITE_BUNDLE_DIR,
        start=args.start,
        end=args.end,
        source_csv=output_csv,
    )

    _print_summary(first_seen)
    print(f"Wrote CSV to {written_csv}")
    print(f"Wrote chart to {written_html}")
    print(f"Wrote bundle to {written_bundle.bundle_dir}")


if __name__ == "__main__":
    main()
