"""Interactive charts for fixed v1 Equelo artefacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.sumo_core.Chii import Chii

from .api import load_entrant_initial_ratings
from .model import OUTPUT_ROOT


DEFAULT_CHART_DIR = OUTPUT_ROOT / "charts"
DEFAULT_ENTRANT_CHART_PATH = DEFAULT_CHART_DIR / "entrant_initial_ratings_v0.html"
DEFAULT_ENTRANT_CHART_V1_PATH = DEFAULT_CHART_DIR / "entrant_initial_ratings_v1.html"
DEFAULT_ENTRANT_CHART_V2_PATH = DEFAULT_CHART_DIR / "entrant_initial_ratings_v2.html"
DEFAULT_ENTRANT_CHART_V3_PATH = DEFAULT_CHART_DIR / "entrant_initial_ratings_v3.html"
DEFAULT_ENTRANT_CHART_V4_PATH = DEFAULT_CHART_DIR / "entrant_initial_ratings_v4.html"
DEFAULT_ENTRANT_CHART_V5_PATH = DEFAULT_CHART_DIR / "entrant_initial_ratings_v5.html"
V1_MAX_CHII = Chii.from_str("Jd100w").ordinal()
V2_DELETE_ORDINALS = {
    Chii.from_str(f"J{rank}{side}").ordinal()
    for rank in range(13, 25)
    for side in ("e", "w")
}
V4_DELETE_ORDINALS = V2_DELETE_ORDINALS | {
    Chii.from_str(f"M{rank}{side}").ordinal()
    for rank in range(18, 23)
    for side in ("e", "w")
}
V3_MASK_ORDINALS = {
    Chii.from_str("O3w").ordinal(),
    Chii.from_str("S2e").ordinal(),
    Chii.from_str("S2w").ordinal(),
    Chii.from_str("S3e").ordinal(),
    Chii.from_str("K2e").ordinal(),
    Chii.from_str("Sd101e").ordinal(),
}
V5_BRIDGE_MASK_START = Chii.from_str("M12e").ordinal()
V5_BRIDGE_MASK_END = Chii.from_str("Ms2e").ordinal()


def entrant_initial_rating_rows(output_root: Path = OUTPUT_ROOT) -> list[dict[str, object]]:
    """Return entrant initial ratings ordered by chii ordinal."""

    ratings = load_entrant_initial_ratings(output_root=output_root)
    rows: list[dict[str, object]] = []

    for ordinal_text, rating in sorted(ratings.items(), key=lambda item: int(item[0])):
        ordinal = int(ordinal_text)
        rows.append(
            {
                "ordinal": ordinal,
                "chii": str(Chii.from_ordinal(ordinal)),
                "rating": float(rating),
            }
        )

    return rows


def write_entrant_initial_rating_chart(
    *,
    output_root: Path = OUTPUT_ROOT,
    output_path: Path = DEFAULT_ENTRANT_CHART_PATH,
    max_ordinal: int | None = None,
    delete_ordinals: set[int] | None = None,
    mask_ordinals: set[int] | None = None,
    title: str = "Fixed v1 Entrant Initial Ratings v0 Raw",
    include_monotone_fit: bool = False,
    fit_mode: str = "cubic",
) -> Path:
    """Write an interactive Plotly chart of fixed v1 entrant initial ratings."""

    rows = entrant_initial_rating_rows(output_root=output_root)
    if max_ordinal is not None:
        rows = [row for row in rows if int(row["ordinal"]) <= max_ordinal]
    if delete_ordinals:
        rows = [row for row in rows if int(row["ordinal"]) not in delete_ordinals]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mask_ordinals = mask_ordinals or set()
    plot_rows = [
        row for row in rows
        if int(row["ordinal"]) not in mask_ordinals
    ]
    x = [row["chii"] for row in plot_rows]
    y = [row["rating"] for row in plot_rows]
    ordinals = [row["ordinal"] for row in plot_rows]
    category_order = [row["chii"] for row in rows]
    fit_y = (
        monotone_fit_values(rows=rows, support_rows=plot_rows, mode=fit_mode)
        if include_monotone_fit
        else None
    )

    html = _page(
        title=title,
        data={
            "x": x,
            "y": y,
            "ordinals": ordinals,
            "category_order": category_order,
            "fit_x": category_order,
            "fit_y": fit_y,
            "raw_mode": "markers" if include_monotone_fit else "lines+markers",
        },
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path


def write_all_entrant_initial_rating_charts(
    *,
    output_root: Path = OUTPUT_ROOT,
    output_dir: Path = DEFAULT_CHART_DIR,
) -> dict[str, Path]:
    """Write the auditable entrant initial rating chart sequence."""

    return {
        "v0_raw": write_entrant_initial_rating_chart(
            output_root=output_root,
            output_path=output_dir / DEFAULT_ENTRANT_CHART_PATH.name,
            title="Fixed v1 Entrant Initial Ratings v0 Raw",
        ),
        "v1_cut_jd101": write_entrant_initial_rating_chart(
            output_root=output_root,
            output_path=output_dir / DEFAULT_ENTRANT_CHART_V1_PATH.name,
            max_ordinal=V1_MAX_CHII,
            title="Fixed v1 Entrant Initial Ratings v1 Through Jd100w",
        ),
        "v2_delete_j13_j24": write_entrant_initial_rating_chart(
            output_root=output_root,
            output_path=output_dir / DEFAULT_ENTRANT_CHART_V2_PATH.name,
            max_ordinal=V1_MAX_CHII,
            delete_ordinals=V2_DELETE_ORDINALS,
            title="Fixed v1 Entrant Initial Ratings v2 Delete J13e-J24w",
        ),
        "v3_mask_sd101e": write_entrant_initial_rating_chart(
            output_root=output_root,
            output_path=output_dir / DEFAULT_ENTRANT_CHART_V3_PATH.name,
            max_ordinal=V1_MAX_CHII,
            delete_ordinals=V2_DELETE_ORDINALS,
            mask_ordinals=V3_MASK_ORDINALS,
            title="Fixed v1 Entrant Initial Ratings v3 Mask Selected Rare Ranks",
        ),
        "v4_delete_m18_m22": write_entrant_initial_rating_chart(
            output_root=output_root,
            output_path=output_dir / DEFAULT_ENTRANT_CHART_V4_PATH.name,
            max_ordinal=V1_MAX_CHII,
            delete_ordinals=V4_DELETE_ORDINALS,
            mask_ordinals=V3_MASK_ORDINALS,
            title="Fixed v1 Entrant Initial Ratings v4 Delete M18e-M22w",
        ),
        "v5_monotone_fit": write_entrant_initial_rating_chart(
            output_root=output_root,
            output_path=output_dir / DEFAULT_ENTRANT_CHART_V5_PATH.name,
            max_ordinal=V1_MAX_CHII,
            delete_ordinals=V4_DELETE_ORDINALS,
            mask_ordinals=v5_mask_ordinals(output_root=output_root),
            title="Fixed v1 Entrant Initial Ratings v5 Monotone Fit",
            include_monotone_fit=True,
        ),
    }


def v5_mask_ordinals(output_root: Path = OUTPUT_ROOT) -> set[int]:
    """Return v5 masks: v3 masks plus the M12w..Ms2e bridge region."""

    return V3_MASK_ORDINALS | {Chii.from_str("Ms3e").ordinal()} | {
        int(row["ordinal"])
        for row in entrant_initial_rating_rows(output_root=output_root)
        if V5_BRIDGE_MASK_START <= int(row["ordinal"]) <= V5_BRIDGE_MASK_END
    }


def monotone_fit_values(
    *,
    rows: list[dict[str, object]],
    support_rows: list[dict[str, object]],
    mode: str = "cubic",
) -> list[float]:
    """Return a strictly decreasing fit evaluated on every row."""

    index_by_ordinal = {
        int(row["ordinal"]): index
        for index, row in enumerate(rows)
    }
    xs = [index_by_ordinal[int(row["ordinal"])] for row in support_rows]
    ys = strictly_decreasing([float(row["rating"]) for row in support_rows])

    if mode != "cubic":
        raise ValueError(f"Unknown fit mode: {mode}")

    return [
        evaluate_monotone_cubic(xs, ys, x)
        for x in range(len(rows))
    ]


def strictly_decreasing(values: list[float], epsilon: float = 0.001) -> list[float]:
    """Clamp values to a strictly decreasing sequence with minimal downward edits."""

    if not values:
        return []

    out = [float(values[0])]
    for value in values[1:]:
        candidate = float(value)
        if candidate >= out[-1]:
            candidate = out[-1] - epsilon
        out.append(candidate)
    return out


def evaluate_monotone_cubic(xs: list[int], ys: list[float], x: int) -> float:
    """Evaluate a monotone cubic Hermite interpolant."""

    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")
    if len(xs) < 2:
        raise ValueError("At least two support points are required")

    slopes = [
        (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i])
        for i in range(len(xs) - 1)
    ]
    tangents = monotone_tangents(xs, slopes)

    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]

    interval = 0
    while interval < len(xs) - 2 and x > xs[interval + 1]:
        interval += 1

    x0 = xs[interval]
    x1 = xs[interval + 1]
    y0 = ys[interval]
    y1 = ys[interval + 1]
    m0 = tangents[interval]
    m1 = tangents[interval + 1]
    h = x1 - x0
    t = (x - x0) / h

    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return h00 * y0 + h10 * h * m0 + h01 * y1 + h11 * h * m1


def monotone_tangents(xs: list[int], slopes: list[float]) -> list[float]:
    """Return monotonicity-preserving cubic tangents for monotone data."""

    tangents = [0.0 for _ in xs]
    tangents[0] = slopes[0]
    tangents[-1] = slopes[-1]

    for i in range(1, len(xs) - 1):
        left = slopes[i - 1]
        right = slopes[i]
        if left == 0.0 or right == 0.0 or (left > 0.0) != (right > 0.0):
            tangents[i] = 0.0
            continue

        h_left = xs[i] - xs[i - 1]
        h_right = xs[i + 1] - xs[i]
        w1 = 2 * h_right + h_left
        w2 = h_right + 2 * h_left
        tangents[i] = (w1 + w2) / ((w1 / left) + (w2 / right))

    return tangents


def _page(*, title: str, data: dict[str, object]) -> str:
    payload = json.dumps(data)
    title_json = json.dumps(title)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="icon" type="image/x-icon" href="../Sumo/meep.png">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    html, body {{
      margin: 0;
      min-height: 100%;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f8fb;
      color: #172033;
    }}
    main {{
      padding: 24px;
    }}
    h1 {{
      margin: 0 0 16px;
      font-size: 22px;
      font-weight: 650;
    }}
    #chart {{
      width: 100%;
      height: calc(100vh - 96px);
      min-height: 520px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <div id="chart"></div>
  </main>
  <script>
    const chartData = {payload};
    const trace = {{
      type: "scatter",
      mode: chartData.raw_mode || "lines+markers",
      name: "raw retained",
      x: chartData.x,
      y: chartData.y,
      customdata: chartData.ordinals,
      line: {{
        color: "#2357a4",
        width: 2
      }},
      marker: {{
        color: "#2357a4",
        size: 5
      }},
      hovertemplate:
        "chii=%{{x}}<br>" +
        "ordinal=%{{customdata}}<br>" +
        "rating=%{{y:.3f}}" +
        "<extra></extra>"
    }};

    const traces = [trace];
    if (chartData.fit_y !== null) {{
      traces.push({{
        type: "scatter",
        mode: "lines",
        name: "strict monotone fit",
        x: chartData.fit_x,
        y: chartData.fit_y,
        line: {{
          color: "#c23b22",
          width: 3
        }},
        hovertemplate:
          "chii=%{{x}}<br>" +
          "fit=%{{y:.3f}}" +
          "<extra></extra>"
      }});
    }}

    const layout = {{
      title: {{ text: {title_json}, x: 0, xanchor: "left" }},
      margin: {{ l: 72, r: 24, t: 36, b: 120 }},
      paper_bgcolor: "#f7f8fb",
      plot_bgcolor: "#ffffff",
      xaxis: {{
        title: "Chii",
        type: "category",
        categoryorder: "array",
        categoryarray: chartData.category_order,
        tickangle: -60,
        automargin: true
      }},
      yaxis: {{
        title: "Entrant initial rating",
        zeroline: false,
        automargin: true
      }},
      hovermode: "closest"
    }};

    const config = {{
      responsive: true,
      displaylogo: false,
      scrollZoom: true
    }};

    Plotly.newPlot("chart", traces, layout, config);
  </script>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write fixed v1 Equelo interactive charts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory containing fixed v1 artefacts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="HTML file for v0/v1, or output directory when --version all.",
    )
    parser.add_argument(
        "--version",
        choices=("all", "v0", "v1", "v2", "v3", "v4", "v5"),
        default="all",
        help="Chart version to generate.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.version == "all":
        written = write_all_entrant_initial_rating_charts(
            output_root=args.output_root,
            output_dir=DEFAULT_CHART_DIR if args.output is None else args.output,
        )
        for name, path in written.items():
            print(f"{name}: {path}")
        return

    if args.version == "v0":
        output_path = args.output or DEFAULT_ENTRANT_CHART_PATH
        written = write_entrant_initial_rating_chart(
            output_root=args.output_root,
            output_path=output_path,
            title="Fixed v1 Entrant Initial Ratings v0 Raw",
        )
        print(f"v0_raw: {written}")
        return

    output_path = args.output or DEFAULT_ENTRANT_CHART_V1_PATH
    if args.version == "v1":
        written = write_entrant_initial_rating_chart(
            output_root=args.output_root,
            output_path=output_path,
            max_ordinal=V1_MAX_CHII,
            title="Fixed v1 Entrant Initial Ratings v1 Through Jd100w",
        )
        print(f"v1_cut_jd101: {written}")
        return

    output_path = args.output or (
        DEFAULT_ENTRANT_CHART_V5_PATH
        if args.version == "v5"
        else
        DEFAULT_ENTRANT_CHART_V4_PATH
        if args.version == "v4"
        else DEFAULT_ENTRANT_CHART_V3_PATH
        if args.version == "v3"
        else DEFAULT_ENTRANT_CHART_V2_PATH
    )
    delete_ordinals = V4_DELETE_ORDINALS if args.version in {"v4", "v5"} else V2_DELETE_ORDINALS
    mask_ordinals = (
        v5_mask_ordinals(output_root=args.output_root)
        if args.version == "v5"
        else V3_MASK_ORDINALS
        if args.version in {"v3", "v4"}
        else None
    )
    title = (
        "Fixed v1 Entrant Initial Ratings v5 Monotone Fit"
        if args.version == "v5"
        else
        "Fixed v1 Entrant Initial Ratings v4 Delete M18e-M22w"
        if args.version == "v4"
        else "Fixed v1 Entrant Initial Ratings v3 Mask Selected Rare Ranks"
        if args.version == "v3"
        else "Fixed v1 Entrant Initial Ratings v2 Delete J13e-J24w"
    )
    written = write_entrant_initial_rating_chart(
        output_root=args.output_root,
        output_path=output_path,
        max_ordinal=V1_MAX_CHII,
        delete_ordinals=delete_ordinals,
        mask_ordinals=mask_ordinals,
        title=title,
        include_monotone_fit=args.version == "v5",
    )
    print(
        f"{'v5_monotone_fit' if args.version == 'v5' else 'v4_delete_m18_m22' if args.version == 'v4' else 'v3_mask_selected' if args.version == 'v3' else 'v2_delete_j13_j24'}: {written}"
    )


if __name__ == "__main__":
    main()
