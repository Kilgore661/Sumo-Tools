"""Write self-contained interactive HTML pairwise matrices."""

from __future__ import annotations

import html
from pathlib import Path

from .model import PairwiseSnapshot, SortOrder, win_probability


CELL_SIZE = 10
LEFT_MARGIN = 154
TOP_MARGIN = 154
RIGHT_MARGIN = 18
BOTTOM_MARGIN = 18


def write_pairwise_html(
    *, snapshot: PairwiseSnapshot, order: SortOrder, output_path: Path
) -> Path:
    """Write one matrix whose cells are ten screen pixels at natural size."""

    rows = snapshot.ordered(order)
    grid_size = CELL_SIZE * len(rows)
    width = LEFT_MARGIN + grid_size + RIGHT_MARGIN
    height = TOP_MARGIN + grid_size + BOTTOM_MARGIN
    labels = _labels(rows)
    cells = _cells(rows, snapshot.q)
    title = f"{snapshot.division.title()} Elo89 pairwise win probabilities"
    subtitle = (
        f"{snapshot.basho} after Day {snapshot.latest_day} · ordered by {order} · "
        "each square is P(row beats column)"
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {html.escape(order)} order</title>
<style>
:root {{
  color-scheme: light dark;
  --page: light-dark(#fafafa, #18181b);
  --text: light-dark(#202124, #f4f4f5);
  --muted-text: light-dark(#646970, #a1a1aa);
  --tooltip: light-dark(#ffffff, #27272a);
  --tooltip-border: light-dark(#d4d4d8, #52525b);
  --loss: light-dark(#c93f45, #ff6b72);
  --even: light-dark(#e5e7eb, #3f3f46);
  --win: light-dark(#23865b, #4ac58c);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 24px;
  background: var(--page);
  color: var(--text);
  font: 14px/1.4 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
main {{ max-width: {width + 20}px; margin: 0 auto; }}
h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
.subtitle {{ margin: 4px 0 14px; color: var(--muted-text); }}
.matrix-wrap {{ width: 100%; overflow-x: auto; }}
svg {{ display: block; width: {width}px; height: {height}px; }}
.axis-label {{ fill: var(--text); font-size: 11px; }}
.cell {{ shape-rendering: crispEdges; }}
.cell.loss {{ fill: color-mix(in srgb, var(--loss) var(--strength), var(--even)); }}
.cell.win {{ fill: color-mix(in srgb, var(--win) var(--strength), var(--even)); }}
.cell.even {{ fill: var(--even); }}
.cell:hover {{ stroke: var(--text); stroke-width: 1.5px; vector-effect: non-scaling-stroke; }}
.legend {{
  display: grid;
  grid-template-columns: auto minmax(120px, 1fr) auto;
  align-items: center;
  gap: 8px;
  max-width: 420px;
  margin: 12px auto 0;
  color: var(--muted-text);
  font-size: 12px;
}}
.legend-bar {{
  height: 10px;
  background: linear-gradient(to right, var(--loss), var(--even) 50%, var(--win));
}}
#tooltip {{
  position: fixed;
  z-index: 10;
  max-width: 320px;
  padding: 8px 10px;
  border: 1px solid var(--tooltip-border);
  border-radius: 6px;
  background: var(--tooltip);
  color: var(--text);
  box-shadow: 0 4px 18px rgb(0 0 0 / 18%);
  pointer-events: none;
  white-space: pre-line;
  font-variant-numeric: tabular-nums;
}}
#tooltip[hidden] {{ display: none; }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(title)}</h1>
  <p class="subtitle">{html.escape(subtitle)}</p>
  <div class="matrix-wrap">
    <svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="matrix-title matrix-desc">
      <title id="matrix-title">{html.escape(title)} in {html.escape(order)} order</title>
      <desc id="matrix-desc">Rows are prospective winners and columns are opponents. Red is below fifty percent, neutral is fifty percent, and green is above fifty percent.</desc>
      {labels}
      {cells}
    </svg>
  </div>
  <div class="legend" aria-label="Probability colour scale">
    <span>0.00</span><div class="legend-bar"></div><span>1.00</span>
  </div>
</main>
<div id="tooltip" role="tooltip" hidden></div>
<script>
const tooltip = document.getElementById("tooltip");
const placeTooltip = event => {{
  const pad = 14;
  tooltip.style.left = `${{Math.min(event.clientX + pad, window.innerWidth - tooltip.offsetWidth - pad)}}px`;
  tooltip.style.top = `${{Math.min(event.clientY + pad, window.innerHeight - tooltip.offsetHeight - pad)}}px`;
}};
document.querySelectorAll(".cell").forEach(cell => {{
  cell.addEventListener("pointerenter", event => {{
    const d = cell.dataset;
    tooltip.textContent = `${{d.row}} (${{d.rowChii}}) · Elo89 ${{d.rowRating}}\nvs ${{d.column}} (${{d.columnChii}}) · Elo89 ${{d.columnRating}}\nP(${{d.row}} wins) = ${{d.probability}}\nRating difference = ${{d.difference}}`;
    tooltip.hidden = false;
    placeTooltip(event);
  }});
  cell.addEventListener("pointermove", placeTooltip);
  cell.addEventListener("pointerleave", () => {{ tooltip.hidden = true; }});
}});
</script>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return output_path


def _labels(rows) -> str:
    parts = []
    for index, row in enumerate(rows):
        coordinate = index * CELL_SIZE
        label = html.escape(f"{row.chii} {row.shikona}")
        row_y = TOP_MARGIN + coordinate + 8
        column_x = LEFT_MARGIN + coordinate + 8
        column_y = TOP_MARGIN - 6
        parts.append(
            f'<text class="axis-label" x="{LEFT_MARGIN - 6}" y="{row_y}" '
            f'text-anchor="end">{label}</text>'
        )
        parts.append(
            f'<text class="axis-label" x="{column_x}" y="{column_y}" '
            f'transform="rotate(-55 {column_x} {column_y})">{label}</text>'
        )
    return "\n      ".join(parts)


def _cells(rows, q: float) -> str:
    parts = []
    for row_index, row in enumerate(rows):
        for column_index, column in enumerate(rows):
            probability = win_probability(row.rating, column.rating, q=q)
            strength = min(1.0, abs(probability - 0.5) * 2.0) * 90.0
            kind = "loss" if probability < 0.5 else "win" if probability > 0.5 else "even"
            difference = row.rating - column.rating
            aria = html.escape(
                f"{row.shikona} against {column.shikona}: {probability:.3f}",
                quote=True,
            )
            attributes = {
                "row": row.shikona,
                "row-chii": row.chii,
                "row-rating": f"{row.rating:.2f}",
                "column": column.shikona,
                "column-chii": column.chii,
                "column-rating": f"{column.rating:.2f}",
                "probability": f"{probability:.3f}",
                "difference": f"{difference:+.2f}",
            }
            data = " ".join(
                f'data-{key}="{html.escape(value, quote=True)}"'
                for key, value in attributes.items()
            )
            parts.append(
                f'<rect class="cell {kind}" '
                f'x="{LEFT_MARGIN + column_index * CELL_SIZE}" '
                f'y="{TOP_MARGIN + row_index * CELL_SIZE}" '
                f'width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'style="--strength:{strength:.2f}%" {data} aria-label="{aria}" />'
            )
    return "\n      ".join(parts)
