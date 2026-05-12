"""Standing Win Probability page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_standing_win_probability_page(page: Page, target_path: Path) -> None:
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            f"<title>{escape(page.title)}</title>",
            "<style>",
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-muted: #c9d4ee; --site-line: #7f95c0; --site-line-soft: rgba(127, 149, 192, 0.55); --control-bg: #d7e0ef; --control-text: #10264f; --accent: #8fb5ff; }",
            "* { box-sizing: border-box; }",
            "html, body { min-height: 100%; }",
            "body { min-width: 320px; min-height: 100vh; margin: 0; padding: 20px; overflow: hidden; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; line-height: 1.35; }",
            ".tool-shell { height: calc(100vh - 40px); display: flex; flex-direction: column; border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { flex: 0 0 auto; padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tool-layout { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 230px minmax(0, 1fr); }",
            ".tool-options { padding: 14px; border-right: 1px solid var(--site-line); overflow-y: auto; }",
            ".tool-options h2 { margin: 0 0 14px; font-size: 1rem; }",
            ".control-group { margin-bottom: 16px; }",
            ".control-label { display: block; margin-bottom: 6px; font-weight: 700; }",
            ".checkbox-control { display: flex; align-items: center; gap: 7px; cursor: pointer; }",
            ".checkbox-control input { margin: 0; accent-color: var(--accent); }",
            ".control-disabled { color: var(--site-muted); cursor: default; opacity: 0.65; }",
            "select { width: 100%; min-height: 28px; border: 1px solid #aebddb; border-radius: 4px; background: var(--control-bg); color: var(--control-text); font: inherit; padding: 2px 4px; }",
            "select:focus, input:focus { outline: 1px solid var(--site-muted); outline-offset: 1px; }",
            ".tool-content { min-width: 0; min-height: 0; padding: 12px; overflow: hidden; }",
            ".tool-content-inner { width: 100%; height: 100%; min-height: 0; display: flex; flex-direction: column; border: 1px solid var(--site-line-soft); background: rgba(255, 255, 255, 0.025); }",
            ".chart-header { flex: 0 0 auto; padding: 10px 12px 0; }",
            "#chart-title { margin: 0; font-size: 1.05rem; font-weight: 700; }",
            "#chart { flex: 1 1 auto; min-width: 0; min-height: 0; }",
            "</style>",
            '<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>',
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
            '<div class="tool-layout">',
            '<aside class="tool-options">',
            "<h2>Options</h2>",
            '<div class="control-group">',
            '<label class="control-label" for="source-select">Source</label>',
            '<select id="source-select"></select>',
            "</div>",
            '<div class="control-group">',
            '<label id="error-toggle-control" class="checkbox-control">',
            '<input id="error-toggle" type="checkbox" checked>',
            "<span>Error bars</span>",
            "</label>",
            "</div>",
            '<div class="control-group">',
            '<label class="control-label" for="division-select">Division</label>',
            '<select id="division-select"></select>',
            "</div>",
            "</aside>",
            '<main class="tool-content">',
            '<div class="tool-content-inner">',
            '<div class="chart-header"><h2 id="chart-title"></h2></div>',
            '<div id="chart"></div>',
            "</div>",
            "</main>",
            "</div>",
            "</div>",
            "<script>",
            STANDING_WIN_PROBABILITY_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


STANDING_WIN_PROBABILITY_JS = r"""
const chart = document.getElementById("chart");
const sourceSelect = document.getElementById("source-select");
const divisionSelect = document.getElementById("division-select");
const errorToggle = document.getElementById("error-toggle");
const errorToggleControl = document.getElementById("error-toggle-control");
const chartTitle = document.getElementById("chart-title");
let pageConfig;
let activeRows = [];

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",");
  return lines.slice(1).map(line => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index];
    });
    return row;
  });
}

function numeric(value) {
  return Number.parseFloat(value);
}

function divisionForChii(chii) {
  if (chii.startsWith("Ms")) return "Makushita";
  if (chii.startsWith("Sd")) return "Sandanme";
  if (chii.startsWith("Jd")) return "Jonidan";
  if (chii.startsWith("Jk")) return "Jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "Makuuchi";
  if (chii.startsWith("J")) return "Juryo";
  return "Other";
}

function displayChii(chii) {
  const sanyaku = pageConfig.display.sanyaku;
  if (chii.startsWith("Y")) return sanyaku.includes(chii);
  if (chii.startsWith("O")) return sanyaku.includes(chii);
  if (chii.startsWith("S") && !chii.startsWith("Sd")) return sanyaku.includes(chii);
  if (chii.startsWith("K")) return sanyaku.includes(chii);
  return true;
}

function groupRows(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!displayChii(row.selected_chii) || !displayChii(row.opponent_chii)) continue;
    if (!groups.has(row.selected_chii)) groups.set(row.selected_chii, []);
    groups.get(row.selected_chii).push(row);
  }
  return Array.from(groups.entries())
    .sort((a, b) => numeric(a[1][0].selected_ordinal) - numeric(b[1][0].selected_ordinal))
    .map(([selected, selectedRows]) => [
      selected,
      selectedRows.sort((a, b) => numeric(a.opponent_ordinal) - numeric(b.opponent_ordinal))
    ]);
}

function sourceConfig() {
  return pageConfig.data_sources.find(source => source.id === sourceSelect.value);
}

function traceForRows(selected, rows, source) {
  const trace = {
    x: rows.map(row => row.opponent_chii),
    y: rows.map(row => numeric(row.p_selected_wins)),
    mode: "lines+markers",
    name: selected,
    type: "scatter",
    visible: selected === pageConfig.default_trace ? true : "legendonly",
    meta: { division: divisionForChii(selected) },
    customdata: rows.map(row => source.id === "observed"
      ? [
          row.selected_chii,
          row.opponent_chii,
          numeric(row.opponent_ordinal),
          numeric(row.n_obs),
          numeric(row.n_selected_wins),
          numeric(row.ci95_lower),
          numeric(row.ci95_upper)
        ]
      : [
          row.selected_chii,
          row.opponent_chii,
          numeric(row.opponent_ordinal),
          numeric(row.selected_rating),
          numeric(row.opponent_rating)
        ]
    )
  };

  if (source.id === "observed") {
    trace.error_y = {
      type: "data",
      symmetric: false,
      array: rows.map(row => numeric(row.ci95_upper) - numeric(row.p_selected_wins)),
      arrayminus: rows.map(row => numeric(row.p_selected_wins) - numeric(row.ci95_lower)),
      visible: errorToggle.checked,
      color: "rgba(68, 140, 240, 0.34)",
      thickness: 1,
      width: 4
    };
    trace.hovertemplate =
      "Selected=%{customdata[0]}<br>" +
      "Opponent=%{customdata[1]}<br>" +
      "P(selected wins)=%{y:.3f}<br>" +
      "CI95=[%{customdata[5]:.3f}, %{customdata[6]:.3f}]<br>" +
      "Wins=%{customdata[4]:,} / %{customdata[3]:,}" +
      "<extra></extra>";
  } else {
    trace.hovertemplate =
      "Selected=%{customdata[0]}<br>" +
      "Opponent=%{customdata[1]}<br>" +
      "P(selected wins)=%{y:.3f}<br>" +
      "Selected rating=%{customdata[3]:.1f}<br>" +
      "Opponent rating=%{customdata[4]:.1f}" +
      "<extra></extra>";
  }

  return trace;
}

function traceInDivision(trace, division) {
  return division === "All" || trace.meta.division === division;
}

function visibilityForDivision(division, traces) {
  let firstVisible = true;
  return traces.map(trace => {
    if (!traceInDivision(trace, division)) return false;
    if (trace.name === pageConfig.default_trace) {
      firstVisible = false;
      return true;
    }
    if (firstVisible) {
      firstVisible = false;
      return true;
    }
    return "legendonly";
  });
}

function visibleCategoryArray() {
  const ordinals = new Map();
  const visibleTraces = chart.data.filter(trace =>
    traceInDivision(trace, divisionSelect.value) &&
    (trace.visible === true || trace.visible === undefined)
  );
  const fallbackTraces = chart.data.filter(trace =>
    traceInDivision(trace, divisionSelect.value) && trace.visible !== false
  );
  const traces = visibleTraces.length ? visibleTraces : fallbackTraces;
  for (const trace of traces) {
    for (let i = 0; i < trace.x.length; i += 1) {
      ordinals.set(trace.x[i], trace.customdata[i][2]);
    }
  }
  return Array.from(ordinals.entries())
    .sort((a, b) => a[1] - b[1])
    .map(([label]) => label);
}

function updateVisibleDomain() {
  Plotly.relayout(chart, {
    "xaxis.categoryarray": visibleCategoryArray(),
    "xaxis.autorange": true
  });
}

function isolateTrace(curveNumber) {
  const target = chart.data[curveNumber];
  if (!target || !traceInDivision(target, divisionSelect.value)) return;
  const visibility = chart.data.map((trace, index) => {
    if (!traceInDivision(trace, divisionSelect.value)) return false;
    return index === curveNumber ? true : "legendonly";
  });
  Plotly.restyle(chart, { visible: visibility }).then(updateVisibleDomain);
}

async function loadSource() {
  const source = sourceConfig();
  chartTitle.textContent = source.label;
  errorToggle.disabled = !source.has_error_bars;
  errorToggle.checked = source.has_error_bars && errorToggle.checked;
  errorToggleControl.classList.toggle("control-disabled", !source.has_error_bars);
  const text = await fetch(`data/${source.data}`).then(response => response.text());
  activeRows = parseCsv(text);
  const traces = groupRows(activeRows).map(([selected, rows]) => traceForRows(selected, rows, source));
  const layout = {
    title: null,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: {
      title: "Opponent sideless chii",
      type: "category",
      categoryorder: "array",
      categoryarray: []
    },
    yaxis: {
      title: pageConfig.y_axis.label,
      range: [pageConfig.y_axis.min, pageConfig.y_axis.max],
      tickformat: pageConfig.y_axis.tickformat
    },
    hovermode: "closest",
    legend: {
      title: { text: "Selected chii" },
      itemclick: "toggle",
      itemdoubleclick: false
    },
    margin: { l: 70, r: 30, t: 70, b: 90 }
  };
  Plotly.newPlot(chart, traces, layout, { responsive: true, displaylogo: false })
    .then(() => {
      if (chart.removeAllListeners) {
        chart.removeAllListeners("plotly_restyle");
        chart.removeAllListeners("plotly_legenddoubleclick");
      }
      chart.on("plotly_restyle", updateVisibleDomain);
      chart.on("plotly_legenddoubleclick", event => {
        isolateTrace(event.curveNumber);
        return false;
      });
      Plotly.restyle(chart, { visible: visibilityForDivision(divisionSelect.value, traces) })
        .then(updateVisibleDomain);
    });
}

async function initialise() {
  pageConfig = await fetch("data/page.json").then(response => response.json());
  const sourceControl = pageConfig.controls.find(control => control.id === "source");
  const divisionControl = pageConfig.controls.find(control => control.id === "division");
  for (const value of sourceControl.values) {
    const option = document.createElement("option");
    option.value = value.value;
    option.textContent = value.label;
    sourceSelect.appendChild(option);
  }
  for (const value of divisionControl.values) {
    const option = document.createElement("option");
    option.value = value.value;
    option.textContent = value.label;
    divisionSelect.appendChild(option);
  }
  sourceSelect.value = sourceControl.default;
  divisionSelect.value = divisionControl.default;
  await loadSource();
}

sourceSelect.addEventListener("change", loadSource);
divisionSelect.addEventListener("change", () => {
  Plotly.restyle(chart, {
    visible: visibilityForDivision(divisionSelect.value, Array.from(chart.data))
  }).then(updateVisibleDomain);
});
errorToggle.addEventListener("change", event => {
  if (!sourceConfig().has_error_bars) return;
  Plotly.restyle(chart, { "error_y.visible": event.target.checked });
});
initialise();
"""


