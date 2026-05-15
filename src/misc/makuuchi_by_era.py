import argparse
import datetime
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
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


OUTPUT_HTML_NAME = "rank_era_chart.html"
OUTPUT_CSV_NAME = "rank_era_chart.csv"
SITE_BUNDLE_DIR = "rank_era/site/makuuchi_rank_by_era"

# Each era is (start_year_inclusive, end_year_exclusive).
ERAS: list[tuple[int, int]] = [
    (1958, 1968),
    (1968, 1978),
    (1978, 1988),
    (1988, 1998),
    (1998, 2008),
    (2008, 2018),
    (2018, 2027),
]

_SANYAKU_LEVELS = {
    MSD.YOKOZUNA,
    MSD.OZEKI,
    MSD.SEKIWAKE,
    MSD.KOMUSUBI,
}


@dataclass(frozen=True)
class MakuuchiRankByEraOutputs:
    output_root: Path
    bundle_dir: Path
    diagnostic_csv: Path
    page_json: Path
    ranks_csv: Path
    metadata_json: Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a makuuchi rank-by-era chart and CSV from the new History model."
        )
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--output-html",
        type=Path,
        default=None,
        help=(
            "Optional output HTML path. If omitted, writes to "
            "files/output/rank_era_chart.html relative to this program."
        ),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help=(
            "Optional output CSV path. If omitted, writes to "
            "files/output/rank_era_chart.csv relative to this program."
        ),
    )
    return parser


def _repo_root() -> Path:
    # rank_era_chart.py is expected at: Sumo-Tools/src/misc/rank_era_chart.py
    return Path(__file__).resolve().parents[2]


def _default_output_html() -> Path:
    return _repo_root() / "files" / "output" / OUTPUT_HTML_NAME


def _default_output_csv() -> Path:
    return _repo_root() / "files" / "output" / OUTPUT_CSV_NAME


def _default_output_root() -> Path:
    return _repo_root() / "files" / "output"


def _rank_label(chii) -> Optional[str]:
    """
    Map a Chii to the rank bucket used in the chart.

    Only makuuchi ranks are included:
    - Yokozuna, Ozeki, Sekiwake, Komusubi as Y/O/S/K
    - Maegashira as M<number>

    Lower divisions are ignored.
    """
    level = chii.level

    if isinstance(level, Division):
        return None

    if level in _SANYAKU_LEVELS:
        return level.as_abbreviation()

    if level == MSD.MAEGASHIRA:
        return f"M{chii.number}"

    return None


def _format_era_label(start: int, end_exclusive: int) -> str:
    return f"{start}-{end_exclusive - 1}"


def _era_labels() -> list[str]:
    return [_format_era_label(start, end) for start, end in ERAS]


def _era_label(year: int) -> Optional[str]:
    for start, end in ERAS:
        if start <= year < end:
            return _format_era_label(start, end)
    return None


def _ordered_rank_labels(all_labels: set[str]) -> list[str]:
    sanyaku = [label for label in ["Y", "O", "S", "K"] if label in all_labels]
    maegashira_nums = sorted(
        int(label[1:]) for label in all_labels if label.startswith("M")
    )
    return sanyaku + [f"M{n}" for n in maegashira_nums]


def compute_era_counts(history: History) -> dict[str, dict[str, int]]:
    """
    Return:
        era_label -> { rank_label -> count }

    Counts are basho appearances of makuuchi rank slots, pooling side and
    annotation within each slot.
    """
    counts: dict[str, dict[str, int]] = {
        era_label: defaultdict(int) for era_label in _era_labels()
    }

    for date, basho in history.items():
        era = _era_label(int(date.year))
        if era is None:
            continue

        for rid in basho.banzuke.riks:
            chii = basho.banzuke.rikchii[rid]
            label = _rank_label(chii)
            if label is not None:
                counts[era][label] += 1

    return counts


def write_matrix_csv(
    era_counts: dict[str, dict[str, int]],
    output_path: Path,
) -> Path:
    """
    Write a wide CSV of the form:

        rank,1958-1965,1966-1975,...,2016-2025,total
    """
    import csv

    all_labels: set[str] = set()
    for counts in era_counts.values():
        all_labels.update(counts.keys())

    rank_labels = _ordered_rank_labels(all_labels)
    era_labels = _era_labels()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", *era_labels, "total"])

        for rank in rank_labels:
            row_counts = [era_counts[era].get(rank, 0) for era in era_labels]
            total = sum(row_counts)
            writer.writerow([rank, *row_counts, total])

    return output_path


def write_makuuchi_rank_by_era_bundle(
    era_counts: dict[str, dict[str, int]],
    bundle_dir: Path,
    *,
    start: int,
    end: int,
    source_csv: Path,
) -> MakuuchiRankByEraOutputs:
    output_root = bundle_dir.parents[2]
    bundle_dir.mkdir(parents=True, exist_ok=True)
    outputs = MakuuchiRankByEraOutputs(
        output_root=output_root,
        bundle_dir=bundle_dir,
        diagnostic_csv=source_csv,
        page_json=bundle_dir / "page.json",
        ranks_csv=bundle_dir / "ranks.csv",
        metadata_json=bundle_dir / "metadata.json",
    )
    write_makuuchi_rank_by_era_csv(era_counts, outputs.ranks_csv)
    _write_page_json(outputs.page_json, start=start, end=end)
    _write_metadata_json(
        outputs.metadata_json,
        era_counts=era_counts,
        start=start,
        end=end,
        source_csv=source_csv,
    )
    return outputs


def write_makuuchi_rank_by_era_csv(
    era_counts: dict[str, dict[str, int]],
    output_path: Path,
) -> Path:
    import csv

    all_labels: set[str] = set()
    for counts in era_counts.values():
        all_labels.update(counts.keys())

    rank_labels = _ordered_rank_labels(all_labels)
    era_labels = _era_labels()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "era", "count", "total"])

        for rank in rank_labels:
            total = sum(era_counts[era].get(rank, 0) for era in era_labels)
            for era in era_labels:
                writer.writerow([rank, era, era_counts[era].get(rank, 0), total])

    return output_path


def build_makuuchi_rank_by_era_outputs(
    history: History,
    *,
    output_root: Path | None = None,
    start: int,
    end: int,
    print_summary: bool = True,
) -> MakuuchiRankByEraOutputs:
    if output_root is None:
        output_root = _default_output_root()
    era_counts = compute_era_counts(history)
    diagnostic_csv = output_root / OUTPUT_CSV_NAME
    write_matrix_csv(era_counts, diagnostic_csv)
    outputs = write_makuuchi_rank_by_era_bundle(
        era_counts=era_counts,
        bundle_dir=output_root / SITE_BUNDLE_DIR,
        start=start,
        end=end,
        source_csv=diagnostic_csv,
    )
    if print_summary:
        _print_summary(era_counts)
        print(f"Wrote CSV to {diagnostic_csv}")
        print(f"Wrote bundle to {outputs.bundle_dir}")
    return outputs


def _write_page_json(output_path: Path, *, start: int, end: int) -> None:
    era_labels = _era_labels()
    page = {
        "title": "Makuuchi Rank by Era",
        "summary": "Historical Makuuchi rank structure by era.",
        "subtitle": (
            f"Makuuchi rank-slot appearances by era ({start}-{end}). "
            "Side and annotation are pooled within each rank bucket."
        ),
        "data_sources": [
            {
                "id": "ranks",
                "label": "Rank appearances by era",
                "data": "ranks.csv",
                "media_type": "text/csv",
            }
        ],
        "chart": {
            "x_field": "rank",
            "y_field": "count",
            "group_field": "era",
            "group_order": era_labels,
            "x_label": "Rank",
            "x_type": "category",
            "x_tickangle": -45,
            "y_label": "Appearances",
            "legend_title": "Era",
            "barmode": "stack",
        },
        "rank_policy": {
            "scope": "makuuchi",
            "side": "pooled",
            "annotation": "pooled_into_base_rank_bucket",
            "buckets": ["Y", "O", "S", "K", "M<number>"],
        },
    }
    output_path.write_text(json.dumps(page, indent=2) + "\n", encoding="utf-8")


def _write_metadata_json(
    output_path: Path,
    *,
    era_counts: dict[str, dict[str, int]],
    start: int,
    end: int,
    source_csv: Path,
) -> None:
    all_labels: set[str] = set()
    for counts in era_counts.values():
        all_labels.update(counts.keys())
    metadata = {
        "analysis": "makuuchi_rank_by_era",
        "bundle": "makuuchi_rank_by_era",
        "start": start,
        "end": end,
        "row_count": len(all_labels),
        "source_csv": source_csv.as_posix(),
        "value_policy": (
            "Rows are pooled makuuchi rank buckets. Side and annotation are "
            "counted under the corresponding base rank bucket."
        ),
    }
    output_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def _plotly_traces(
    era_counts: dict[str, dict[str, int]],
    rank_labels: list[str],
) -> list[dict[str, object]]:
    traces: list[dict[str, object]] = []

    for era_label in _era_labels():
        traces.append(
            {
                "type": "bar",
                "name": era_label,
                "x": rank_labels,
                "y": [era_counts[era_label].get(rank, 0) for rank in rank_labels],
                "hovertemplate": (
                    "Era: %{fullData.name}<br>"
                    "Rank: %{x}<br>"
                    "Appearances: %{y}<extra></extra>"
                ),
            }
        )

    return traces


def write_chart_html(
    era_counts: dict[str, dict[str, int]],
    output_path: Path,
) -> Path:
    all_labels: set[str] = set()
    for counts in era_counts.values():
        all_labels.update(counts.keys())

    rank_labels = _ordered_rank_labels(all_labels)
    traces = _plotly_traces(era_counts, rank_labels)
    traces_json = json.dumps(traces, ensure_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sumo Rank Appearances by Era</title>
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
    <h1>Banzuke Rank Appearances by Era</h1>
    <p class="subtitle">
      Stacked by era. Side and annotation pooled within each makuuchi rank slot.
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
        title: "Rank",
        tickangle: -45,
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      yaxis: {{
        title: "Appearances",
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      legend: {{
        orientation: "v",
        yanchor: "top",
        y: 1,
        xanchor: "left",
        x: 1.02
      }},
      margin: {{
        l: 70,
        r: 170,
        t: 30,
        b: 90
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


def _print_summary(era_counts: dict[str, dict[str, int]]) -> None:
    all_labels: set[str] = set()
    for counts in era_counts.values():
        all_labels.update(counts.keys())

    rank_labels = _ordered_rank_labels(all_labels)

    print("Rank appearances by era")
    print("=" * 80)
    print(f"{'Rank':<8}", end="")
    for era_label in _era_labels():
        print(f"{era_label:>12}", end="")
    print(f"{'Total':>12}")
    print("-" * 80)

    for rank in rank_labels:
        values = [era_counts[era_label].get(rank, 0) for era_label in _era_labels()]
        total = sum(values)

        print(f"{rank:<8}", end="")
        for value in values:
            print(f"{value:>12}", end="")
        print(f"{total:>12}")

    print("-" * 80)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    history = connect(args.start, args.end, use_zip=args.zip)
    if not history:
        raise ValueError("No history returned by connect()")

    era_counts = compute_era_counts(history)

    output_csv = args.output_csv if args.output_csv is not None else _default_output_csv()
    output_html = (
        args.output_html if args.output_html is not None else _default_output_html()
    )

    written_csv = write_matrix_csv(era_counts, output_csv)
    written_html = write_chart_html(era_counts, output_html)
    written_bundle = write_makuuchi_rank_by_era_bundle(
        era_counts=era_counts,
        bundle_dir=_default_output_root() / SITE_BUNDLE_DIR,
        start=args.start,
        end=args.end,
        source_csv=output_csv,
    )

    _print_summary(era_counts)
    print()
    print(f"Wrote CSV to {written_csv}")
    print(f"Wrote chart to {written_html}")
    print(f"Wrote bundle to {written_bundle.bundle_dir}")


if __name__ == "__main__":
    main()
