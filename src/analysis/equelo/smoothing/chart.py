"""Responsive Plotly chart of the direct inputs to Equelo smoothing."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from src.sumo_core.Chii import Chii


PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"
DEFAULT_FILE_NAME = "supported_fixed_point_estimates.html"


@dataclass(frozen=True)
class SupportedEstimate:
    chii: str
    ordinal: int
    rating: float
    n_basho_start: int
    distinct_rikishi: int
    se_basho_start: float | None


@dataclass(frozen=True)
class ChiiSupport:
    chii: str
    ordinal: int
    appearances: int


def load_supported_estimates(path: Path) -> tuple[SupportedEstimate, ...]:
    """Load direct estimates from an Expt2 ``*_with_stats.csv`` artifact."""

    with path.open(newline="", encoding="utf-8") as stream:
        rows = tuple(csv.DictReader(stream))
    required = {
        "chii",
        "ordinal",
        "rating",
        "n_basho_start",
        "distinct_rikishi",
        "se_basho_start",
    }
    if rows:
        missing = required - set(rows[0])
        if missing:
            raise ValueError(
                f"Supported-estimate CSV is missing columns: {sorted(missing)}"
            )
    estimates = (
        SupportedEstimate(
            chii=row["chii"],
            ordinal=int(row["ordinal"]),
            rating=float(row["rating"]),
            n_basho_start=int(row["n_basho_start"]),
            distinct_rikishi=int(row["distinct_rikishi"]),
            se_basho_start=(
                None
                if not row["se_basho_start"]
                else float(row["se_basho_start"])
            ),
        )
        for row in rows
    )
    return tuple(sorted(estimates, key=lambda row: row.ordinal))


def load_chii_support(path: Path) -> tuple[ChiiSupport, ...]:
    """Load the complete pre-filter support domain from CSV."""

    with path.open(newline="", encoding="utf-8") as stream:
        rows = tuple(csv.DictReader(stream))
    support = (
        ChiiSupport(
            chii=row["chii"],
            ordinal=int(row.get("ordinal", "") or row["chii_ordinal"]),
            appearances=int(row["appearances"]),
        )
        for row in rows
    )
    return tuple(sorted(support, key=lambda row: row.ordinal))


def write_chii_support_csv(
    path: Path,
    appearances: Mapping[Chii, int],
) -> Path:
    """Persist the complete collapsed support domain used by the solver."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("chii", "chii_ordinal", "appearances"),
        )
        writer.writeheader()
        for chii, count in sorted(
            appearances.items(), key=lambda item: item[0].ordinal()
        ):
            writer.writerow({
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "appearances": int(count),
            })
    return path


def write_supported_fixed_point_chart(
    source_csv: Path,
    output_path: Path | None = None,
    *,
    support_csv: Path | None = None,
) -> Path:
    """Write a page-width chart of solver-native supported estimates."""

    estimates = load_supported_estimates(source_csv)
    if not estimates:
        raise ValueError(f"Supported-estimate CSV contains no rows: {source_csv}")
    destination = (
        source_csv.with_name(DEFAULT_FILE_NAME)
        if output_path is None
        else output_path
    )
    destination.parent.mkdir(parents=True, exist_ok=True)

    support = (
        tuple(
            ChiiSupport(row.chii, row.ordinal, row.n_basho_start)
            for row in estimates
        )
        if support_csv is None
        else load_chii_support(support_csv)
    )
    labels = [row.chii for row in support]
    estimates_by_chii = {row.chii: row for row in estimates}
    ratings = []
    customdata = []
    for label in labels:
        estimate = estimates_by_chii.get(label)
        ratings.append(None if estimate is None else estimate.rating)
        customdata.append(
            None
            if estimate is None
            else [
                estimate.n_basho_start,
                estimate.distinct_rikishi,
                estimate.ordinal,
                estimate.se_basho_start,
            ]
        )
    traces = [
        {
            "type": "scattergl",
            "mode": "markers",
            "name": "Supported fixed-point estimate",
            "x": labels,
            "y": ratings,
            "customdata": customdata,
            "marker": {"size": 5, "color": "#2457a7"},
            "hovertemplate": (
                "<b>%{x}</b><br>rating=%{y:.2f}"
                "<br>basho starts=%{customdata[0]}"
                "<br>distinct rikishi=%{customdata[1]}"
                "<br>ordinal=%{customdata[2]}"
                "<br>SE=%{customdata[3]:.2f}<extra></extra>"
            ),
        },
    ]
    layout = {
        "title": {
            "text": (
                "Supported fixed-point initial-rating estimates"
                f"<br><sup>{source_csv.name}; {len(estimates)} direct estimates "
                f"from {len(support)} pre-filter chii; stronger to weaker</sup>"
            ),
            "x": 0.01,
            "xanchor": "left",
        },
        "autosize": True,
        "xaxis": {
            "title": {"text": "Chii (stronger to weaker)"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
            "tickangle": -90,
            "automargin": True,
        },
        "yaxis": {
            "title": {"text": "Fixed-point initial rating"},
            "automargin": True,
        },
        "hovermode": "closest",
        "showlegend": False,
        "margin": {"l": 75, "r": 35, "t": 95, "b": 145},
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#f7f8fa",
    }
    config = {
        "responsive": True,
        "displaylogo": False,
        "scrollZoom": True,
    }
    markup = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Supported fixed-point initial-rating estimates</title>
<script src="{PLOTLY_CDN}"></script>
<style>
html, body {{ width: 100%; height: 100%; margin: 0; font-family: system-ui, sans-serif; }}
#chart {{ width: 100vw; height: 100vh; min-height: 620px; }}
</style>
</head>
<body>
<div id="chart" role="img" aria-label="Supported fixed-point initial-rating estimates"></div>
<script>
const traces = {json.dumps(traces, separators=(',', ':'))};
const layout = {json.dumps(layout, separators=(',', ':'))};
const config = {json.dumps(config, separators=(',', ':'))};
Plotly.newPlot('chart', traces, layout, config);
</script>
</body>
</html>
"""
    destination.write_text(markup, encoding="utf-8")
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Chart direct supported fixed-point estimates."
    )
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--support-csv",
        type=Path,
        default=None,
        help="Optional complete pre-filter chii-support CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output = write_supported_fixed_point_chart(
        args.source_csv,
        args.output,
        support_csv=args.support_csv,
    )
    print(f"Supported fixed-point chart: {output}")


if __name__ == "__main__":
    main()
