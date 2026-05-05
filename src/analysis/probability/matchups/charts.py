from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from src.analysis.probability.matchups.traces import EqueloTracePoint, ObservedTracePoint


def write_observed_trace_chart(
    points: tuple[ObservedTracePoint, ...],
    output_path: Path,
    *,
    initially_visible: str = "Y1",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    traces = []
    points = _filter_display_points(points)

    for selected_chii, rows in _group_points(points):
        visible = True if selected_chii == initially_visible else "legendonly"
        xs = [row.opponent_chii for row in rows]
        ys = [row.p_selected_wins for row in rows]
        error_plus = [row.ci95_upper - row.p_selected_wins for row in rows]
        error_minus = [row.p_selected_wins - row.ci95_lower for row in rows]
        customdata = [
            (
                row.selected_chii,
                row.opponent_chii,
                row.opponent_ordinal,
                row.n_obs,
                row.n_selected_wins,
                row.ci95_lower,
                row.ci95_upper,
            )
            for row in rows
        ]
        traces.append(
            {
                "x": xs,
                "y": ys,
                "mode": "lines+markers",
                "name": selected_chii,
                "visible": visible,
                "type": "scatter",
                "meta": {"division": _division_for_chii(selected_chii)},
                "error_y": {
                    "type": "data",
                    "symmetric": False,
                    "array": error_plus,
                    "arrayminus": error_minus,
                    "visible": True,
                    "color": "rgba(30, 86, 160, 0.34)",
                    "thickness": 1,
                    "width": 4,
                },
                "customdata": customdata,
                "hovertemplate": (
                    "Selected=%{customdata[0]}<br>"
                    "Opponent=%{customdata[1]}<br>"
                    "P(selected wins)=%{y:.3f}<br>"
                    "CI95=[%{customdata[5]:.3f}, %{customdata[6]:.3f}]<br>"
                    "Wins=%{customdata[4]:,} / %{customdata[3]:,}"
                    "<extra></extra>"
                ),
            }
        )

    _write_plotly_html(
        output_path=output_path,
        traces=traces,
        title="Observed Sideless Chii Matchup Traces",
        yaxis_title="Observed P(selected chii wins)",
        categoryarray=_opponent_categoryarray(points),
        include_error_toggle=True,
    )
    return output_path


def write_equelo_trace_chart(
    points: tuple[EqueloTracePoint, ...],
    output_path: Path,
    *,
    initially_visible: str = "Y1",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    traces = []
    points = _filter_display_points(points)

    for selected_chii, rows in _group_points(points):
        visible = True if selected_chii == initially_visible else "legendonly"
        xs = [row.opponent_chii for row in rows]
        ys = [row.p_selected_wins for row in rows]
        customdata = [
            (
                row.selected_chii,
                row.opponent_chii,
                row.opponent_ordinal,
                row.selected_rating,
                row.opponent_rating,
            )
            for row in rows
        ]
        traces.append(
            {
                "x": xs,
                "y": ys,
                "mode": "lines+markers",
                "name": selected_chii,
                "visible": visible,
                "type": "scatter",
                "meta": {"division": _division_for_chii(selected_chii)},
                "customdata": customdata,
                "hovertemplate": (
                    "Selected=%{customdata[0]}<br>"
                    "Opponent=%{customdata[1]}<br>"
                    "P(selected wins)=%{y:.3f}<br>"
                    "Selected rating=%{customdata[3]:.1f}<br>"
                    "Opponent rating=%{customdata[4]:.1f}"
                    "<extra></extra>"
                ),
            }
        )

    _write_plotly_html(
        output_path=output_path,
        traces=traces,
        title="Equelo Sideless Chii Matchup Traces",
        yaxis_title="Equelo-implied P(selected chii wins)",
        categoryarray=_opponent_categoryarray(points),
        include_error_toggle=False,
    )
    return output_path


def _group_points(points: Iterable) -> list[tuple[str, list]]:
    grouped: dict[str, list] = {}
    ordinals: dict[str, int] = {}
    for point in points:
        grouped.setdefault(point.selected_chii, []).append(point)
        ordinals[point.selected_chii] = point.selected_ordinal

    result: list[tuple[str, list]] = []
    for selected_chii in sorted(grouped, key=lambda chii: ordinals[chii]):
        result.append(
            (
                selected_chii,
                sorted(grouped[selected_chii], key=lambda point: point.opponent_ordinal),
            )
        )
    return result


def _write_plotly_html(
    *,
    output_path: Path,
    traces: list[dict],
    title: str,
    yaxis_title: str,
    categoryarray: list[str],
    include_error_toggle: bool,
) -> None:
    layout = {
        "title": title,
        "xaxis": {
            "title": "Opponent sideless chii",
            "type": "category",
            "categoryorder": "array",
            "categoryarray": categoryarray,
        },
        "yaxis": {"title": yaxis_title, "range": [0, 1], "tickformat": ".0%"},
        "hovermode": "closest",
        "legend": {
            "title": {"text": "Selected chii"},
            "itemclick": "toggle",
            "itemdoubleclick": False,
        },
        "margin": {"l": 70, "r": 30, "t": 70, "b": 90},
    }
    divisions = _division_options(traces)
    initial_division = next(
        (
            trace["meta"]["division"]
            for trace in traces
            if trace.get("visible") is True
        ),
        divisions[0] if divisions else "All",
    )
    error_toggle_html = (
        """
    <label class="checkbox-control">
      <input id="error-toggle" type="checkbox" checked>
      Error bars
    </label>"""
        if include_error_toggle
        else ""
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    html, body {{
      margin: 0;
      height: 100%;
      font-family: Arial, sans-serif;
      color: #172033;
    }}
    body {{
      display: flex;
      flex-direction: column;
    }}
    .toolbar {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px 0;
      font-size: 13px;
    }}
    .toolbar select {{
      font: inherit;
      padding: 4px 26px 4px 8px;
    }}
    .checkbox-control {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      margin-left: 8px;
    }}
    #chart {{
      width: 100vw;
      flex: 1;
      min-height: 0;
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <label for="division-select">Division</label>
    <select id="division-select"></select>
    {error_toggle_html}
  </div>
  <div id="chart"></div>
  <script>
    const traces = {json.dumps(traces)};
    const layout = {json.dumps(layout)};
    const divisions = {json.dumps(divisions)};
    const initialDivision = {json.dumps(initial_division)};
    const includeErrorToggle = {json.dumps(include_error_toggle)};
    const chart = document.getElementById("chart");
    const divisionSelect = document.getElementById("division-select");
    const errorToggle = document.getElementById("error-toggle");
    let activeDivision = initialDivision;

    function traceDivision(trace) {{
      return trace.meta && trace.meta.division ? trace.meta.division : "Other";
    }}

    function traceInActiveDivision(trace) {{
      return activeDivision === "All" || traceDivision(trace) === activeDivision;
    }}

    function initialiseDivisionSelect() {{
      for (const division of divisions) {{
        const option = document.createElement("option");
        option.value = division;
        option.textContent = division;
        divisionSelect.appendChild(option);
      }}
      divisionSelect.value = activeDivision;
    }}

    function visibilityForDivision(division) {{
      let firstVisible = true;
      return chart.data.map(trace => {{
        const inDivision = division === "All" || traceDivision(trace) === division;
        if (!inDivision) {{
          return false;
        }}
        if (firstVisible) {{
          firstVisible = false;
          return true;
        }}
        return "legendonly";
      }});
    }}

    function applyDivision(division) {{
      activeDivision = division;
      Plotly.restyle(chart, {{ visible: visibilityForDivision(division) }})
        .then(updateVisibleDomain);
    }}

    function isolateTrace(curveNumber) {{
      const target = chart.data[curveNumber];
      if (!target || !traceInActiveDivision(target)) {{
        return;
      }}
      const visibility = chart.data.map((trace, index) => {{
        if (!traceInActiveDivision(trace)) {{
          return false;
        }}
        return index === curveNumber ? true : "legendonly";
      }});
      Plotly.restyle(chart, {{ visible: visibility }}).then(updateVisibleDomain);
    }}

    function visibleCategoryArray() {{
      const ordinals = new Map();
      const visibleTraces = chart.data.filter(
        trace => traceInActiveDivision(trace) &&
          (trace.visible === true || trace.visible === undefined)
      );
      const fallbackTraces = chart.data.filter(
        trace => traceInActiveDivision(trace) && trace.visible !== false
      );
      const sourceTraces = visibleTraces.length ? visibleTraces : fallbackTraces;

      for (const trace of sourceTraces) {{
        for (let i = 0; i < trace.x.length; i += 1) {{
          const label = trace.x[i];
          const ordinal = trace.customdata[i][2];
          ordinals.set(label, ordinal);
        }}
      }}

      return Array.from(ordinals.entries())
        .sort((a, b) => a[1] - b[1])
        .map(([label]) => label);
    }}

    function updateVisibleDomain() {{
      const categoryarray = visibleCategoryArray();
      Plotly.relayout(chart, {{
        "xaxis.categoryarray": categoryarray,
        "xaxis.autorange": true
      }});
    }}

    initialiseDivisionSelect();
    Plotly.newPlot(chart, traces, layout, {{responsive: true}})
      .then(() => applyDivision(activeDivision));
    chart.on("plotly_restyle", updateVisibleDomain);
    chart.on("plotly_legenddoubleclick", event => {{
      isolateTrace(event.curveNumber);
      return false;
    }});
    if (includeErrorToggle && errorToggle) {{
      errorToggle.addEventListener("change", event => {{
        Plotly.restyle(chart, {{ "error_y.visible": event.target.checked }});
      }});
    }}
    divisionSelect.addEventListener("change", event => applyDivision(event.target.value));
  </script>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


def _opponent_categoryarray(points: Iterable) -> list[str]:
    ordinals: dict[str, int] = {}
    for point in points:
        ordinals[point.opponent_chii] = point.opponent_ordinal
    return [
        chii
        for chii, _ in sorted(ordinals.items(), key=lambda item: item[1])
    ]


def _filter_display_points(points: tuple) -> tuple:
    return tuple(
        point for point in points
        if _display_chii(point.selected_chii) and _display_chii(point.opponent_chii)
    )


def _display_chii(chii: str) -> bool:
    if chii.startswith("Y"):
        return chii == "Y1"
    if chii.startswith("O"):
        return chii == "O1"
    if chii.startswith("S") and not chii.startswith("Sd"):
        return chii == "S1"
    if chii.startswith("K"):
        return chii == "K1"
    return True


def _division_for_chii(chii: str) -> str:
    if chii.startswith("Ms"):
        return "Makushita"
    if chii.startswith("Sd"):
        return "Sandanme"
    if chii.startswith("Jd"):
        return "Jonidan"
    if chii.startswith("Jk"):
        return "Jonokuchi"
    if chii.startswith(("Y", "O", "S", "K", "M")):
        return "Makuuchi"
    if chii.startswith("J"):
        return "Juryo"
    return "Other"


def _division_options(traces: list[dict]) -> list[str]:
    preferred = [
        "Makuuchi",
        "Juryo",
        "Makushita",
        "Sandanme",
        "Jonidan",
        "Jonokuchi",
        "Other",
    ]
    present = {trace["meta"]["division"] for trace in traces}
    options = [division for division in preferred if division in present]
    options.extend(sorted(present - set(preferred)))
    return options + ["All"]
