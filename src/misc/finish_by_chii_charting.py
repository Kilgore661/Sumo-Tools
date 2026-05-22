import json
from pathlib import Path


AVERAGE_MIN_SAMPLE_SIZE_BY_DIVISION = {
    "makuuchi": 76,
    "juryo": 406,
}


def write_finish_chart(
    top_rows: list[dict[str, object]],
    bottom_rows: list[dict[str, object]],
    output_path: Path,
    start: int,
    end: int,
) -> Path:
    payload = _build_payload(top_rows, bottom_rows, start, end)
    payload_json = json.dumps(payload, ensure_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_html(payload_json), encoding="utf-8")
    return output_path


def write_average_finish_chart(
    summary_rows: list[dict[str, object]],
    output_path: Path,
    start: int,
    end: int,
    min_sample_size_by_division: dict[str, int] | None = None,
) -> Path:
    thresholds = min_sample_size_by_division or AVERAGE_MIN_SAMPLE_SIZE_BY_DIVISION
    payload = _build_average_payload(summary_rows, start, end, thresholds)
    payload_json = json.dumps(payload, ensure_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_average_html(payload_json), encoding="utf-8")
    return output_path


def _build_payload(
    top_rows: list[dict[str, object]],
    bottom_rows: list[dict[str, object]],
    start: int,
    end: int,
) -> dict[str, object]:
    divisions: dict[str, dict[str, object]] = {}

    for source, direction in ((top_rows, "top"), (bottom_rows, "bottom")):
        for row in source:
            division_id = str(row["division"]).lower()
            division = divisions.setdefault(
                division_id,
                {
                    "id": division_id,
                    "label": row["division"],
                    "chii": {},
                },
            )
            chii = str(row["chii"])
            chii_entry = division["chii"].setdefault(
                chii,
                {
                    "label": chii,
                    "ordinal": int(row["chii_ordinal"]),
                    "sampleSize": int(row["n"]),
                    "top": {},
                    "bottom": {},
                },
            )
            probability_key = (
                "p_no_worse_than_n"
                if direction == "top"
                else "p_no_better_than_mth_worst"
            )
            chii_entry[direction][int(row["threshold"])] = float(row[probability_key])

    for division in divisions.values():
        chii_values = sorted(
            division["chii"].values(),
            key=lambda item: (item["ordinal"], item["label"]),
        )
        division["chii"] = chii_values

    return {
        "title": "Finish by Chii",
        "start": start,
        "end": end,
        "defaultDivision": "makuuchi",
        "defaultDirection": "top",
        "divisions": divisions,
    }


def _build_average_payload(
    summary_rows: list[dict[str, object]],
    start: int,
    end: int,
    min_sample_size_by_division: dict[str, int],
) -> dict[str, object]:
    divisions: dict[str, dict[str, object]] = {}

    for row in summary_rows:
        sample_size = int(row["n"])
        division_id = str(row["division"]).lower()
        min_sample_size = min_sample_size_by_division.get(division_id, 0)
        if sample_size < min_sample_size:
            continue

        division = divisions.setdefault(
            division_id,
            {
                "id": division_id,
                "label": row["division"],
                "minSampleSize": min_sample_size,
                "rows": [],
            },
        )
        division["rows"].append(
            {
                "chii": str(row["chii"]),
                "ordinal": int(row["chii_ordinal"]),
                "sampleSize": sample_size,
                "meanPositionPct": float(row["mean_position_pct"]),
            }
        )

    for division in divisions.values():
        division["rows"].sort(key=lambda item: (item["ordinal"], item["chii"]))

    return {
        "title": "Average Finish by Chii",
        "start": start,
        "end": end,
        "minSampleSizeByDivision": min_sample_size_by_division,
        "defaultDivision": "makuuchi",
        "defaultSort": "value",
        "divisions": divisions,
    }


def _html(payload_json: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Finish by Chii</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      color-scheme: dark;
      --site-bg: #07142d;
      --site-panel: #0d1f47;
      --site-panel-strong: #132b5c;
      --site-text: #ffffff;
      --site-muted: #c9d4ee;
      --site-line: #7f95c0;
      --site-line-soft: rgba(127, 149, 192, 0.55);
      --control-bg: #d7e0ef;
      --control-text: #10264f;
      --accent: #8fb5ff;
      --bar: #8fb5ff;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      min-width: 320px;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      overflow: hidden;
      background: var(--site-bg);
      color: var(--site-text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.35;
    }}

    .tool-shell {{
      height: calc(100vh - 40px);
      display: flex;
      flex-direction: column;
      border: 1px solid var(--site-line);
      background: var(--site-panel);
    }}

    .tool-title-bar {{
      flex: 0 0 auto;
      padding: 12px 16px;
      border-bottom: 1px solid var(--site-line);
      background: var(--site-panel-strong);
      font-size: 1.25rem;
      font-weight: 700;
    }}

    .tool-layout {{
      flex: 1 1 auto;
      min-height: 0;
      display: grid;
      grid-template-columns: 230px minmax(0, 1fr);
    }}

    .tool-options {{
      padding: 14px;
      border-right: 1px solid var(--site-line);
      overflow-y: auto;
    }}

    .tool-options h2 {{
      margin: 0 0 14px;
      font-size: 1rem;
    }}

    .control-group {{
      margin-bottom: 16px;
    }}

    .control-label {{
      display: block;
      margin-bottom: 6px;
      font-weight: 700;
    }}

    .radio-option {{
      display: flex;
      align-items: center;
      gap: 7px;
      margin-bottom: 7px;
      cursor: pointer;
    }}

    .radio-option input {{
      margin: 0;
      accent-color: var(--accent);
    }}

    .chii-stepper {{
      display: grid;
      grid-template-columns: 34px minmax(0, 1fr) 34px;
      gap: 6px;
      align-items: center;
    }}

    select,
    button {{
      min-height: 28px;
      border: 1px solid #aebddb;
      border-radius: 4px;
      background: var(--control-bg);
      color: var(--control-text);
      font: inherit;
    }}

    select {{
      width: 100%;
      padding: 2px 4px;
    }}

    button {{
      padding: 0;
      cursor: pointer;
      font-size: 18px;
      line-height: 1;
    }}

    button:focus,
    select:focus,
    input:focus {{
      outline: 1px solid var(--site-muted);
      outline-offset: 1px;
    }}

    .tool-content {{
      min-width: 0;
      min-height: 0;
      padding: 12px;
      overflow: hidden;
    }}

    .tool-content-inner {{
      width: 100%;
      height: 100%;
      min-height: 0;
      display: flex;
      flex-direction: column;
      border: 1px solid var(--site-line-soft);
      background: rgba(255, 255, 255, 0.025);
    }}

    .chart-header {{
      flex: 0 0 auto;
      padding: 10px 12px 0;
    }}

    #chart-title {{
      margin: 0;
      font-size: 1.05rem;
      font-weight: 700;
    }}

    #chart-subtitle {{
      margin-top: 3px;
      color: var(--site-muted);
      font-size: 0.9rem;
    }}

    #chart {{
      flex: 1 1 auto;
      min-height: 0;
      width: 100%;
    }}

    @media (max-width: 760px) {{
      body {{
        overflow: auto;
      }}

      .tool-shell {{
        height: auto;
        min-height: calc(100vh - 40px);
      }}

      .tool-layout {{
        grid-template-columns: 1fr;
      }}

      .tool-options {{
        border-right: 0;
        border-bottom: 1px solid var(--site-line);
      }}

      .tool-content {{
        height: 520px;
      }}
    }}
  </style>
</head>
<body>
  <main class="tool-shell">
    <header class="tool-title-bar">
      <div id="page-title">Finish by Chii</div>
    </header>

    <div class="tool-layout">
      <aside class="tool-options">
        <h2>Options</h2>

        <div class="control-group">
          <span class="control-label">Division</span>
          <label class="radio-option">
            <input type="radio" name="division" value="makuuchi" checked>
            Makuuchi
          </label>
          <label class="radio-option">
            <input type="radio" name="division" value="juryo">
            Juryo
          </label>
        </div>

        <div class="control-group">
          <span class="control-label">Direction</span>
          <label class="radio-option">
            <input type="radio" name="direction" value="top" checked>
            Top
          </label>
          <label class="radio-option">
            <input type="radio" name="direction" value="bottom">
            Bottom
          </label>
        </div>

        <div class="control-group">
          <label class="control-label" for="chii-select">Chii</label>
          <div class="chii-stepper">
            <button type="button" id="chii-prev" aria-label="Previous chii">&lt;</button>
            <select id="chii-select"></select>
            <button type="button" id="chii-next" aria-label="Next chii">&gt;</button>
          </div>
        </div>
      </aside>

      <section class="tool-content">
        <div class="tool-content-inner" id="chart-panel">
          <div class="chart-header">
            <h1 id="chart-title">Finish by Chii</h1>
            <div id="chart-subtitle"></div>
          </div>
          <div id="chart"></div>
        </div>
      </section>
    </div>
  </main>

  <script>
    const payload = {payload_json};
    const state = {{
      division: payload.defaultDivision,
      direction: payload.defaultDirection,
      chii: null,
    }};

    const el = {{
      pageTitle: document.getElementById("page-title"),
      chartTitle: document.getElementById("chart-title"),
      chartSubtitle: document.getElementById("chart-subtitle"),
      chart: document.getElementById("chart"),
      panel: document.getElementById("chart-panel"),
      chii: document.getElementById("chii-select"),
      prev: document.getElementById("chii-prev"),
      next: document.getElementById("chii-next"),
      divisionInputs: Array.from(document.querySelectorAll("input[name='division']")),
      directionInputs: Array.from(document.querySelectorAll("input[name='direction']")),
    }};

    const plotConfig = {{
      responsive: true,
      displaylogo: false,
    }};

    document.addEventListener("DOMContentLoaded", init);

    function init() {{
      el.pageTitle.textContent = `${{payload.title}} (${{payload.start}}-${{payload.end}})`;
      state.chii = firstChiiForDivision(state.division);
      populateChiiSelect();
      wireEvents();
      render();
      observePanelResize();
    }}

    function wireEvents() {{
      el.divisionInputs.forEach((input) => {{
        input.addEventListener("change", () => {{
          if (!input.checked) {{
            return;
          }}
          state.division = input.value;
          state.chii = firstChiiForDivision(state.division);
          populateChiiSelect();
          render();
        }});
      }});

      el.directionInputs.forEach((input) => {{
        input.addEventListener("change", () => {{
          if (!input.checked) {{
            return;
          }}
          state.direction = input.value;
          render();
        }});
      }});

      el.chii.addEventListener("change", () => {{
        state.chii = el.chii.value;
        render();
      }});

      el.prev.addEventListener("click", () => {{
        stepChii(-1);
      }});

      el.next.addEventListener("click", () => {{
        stepChii(1);
      }});
    }}

    function populateChiiSelect() {{
      const entries = chiiEntries();
      el.chii.innerHTML = "";

      entries.forEach((entry) => {{
        const option = document.createElement("option");
        option.value = entry.label;
        option.textContent = entry.label;
        el.chii.appendChild(option);
      }});

      el.chii.value = state.chii;
    }}

    function stepChii(delta) {{
      const entries = chiiEntries();
      const index = entries.findIndex((entry) => entry.label === state.chii);
      const nextIndex = (index + delta + entries.length) % entries.length;
      state.chii = entries[nextIndex].label;
      el.chii.value = state.chii;
      render();
    }}

    function chiiEntries() {{
      return payload.divisions[state.division].chii;
    }}

    function firstChiiForDivision(division) {{
      return payload.divisions[division].chii[0].label;
    }}

    function selectedEntry() {{
      return chiiEntries().find((entry) => entry.label === state.chii);
    }}

    function render() {{
      const entry = selectedEntry();
      const divisionLabel = payload.divisions[state.division].label;
      const directionLabel = state.direction === "top" ? "Top" : "Bottom";
      const probabilityLabel = state.direction === "top"
        ? "No worse than nth"
        : "No better than nth-worst";
      const source = entry[state.direction];
      const x = Array.from({{ length: 10 }}, (_, i) => i + 1);
      const y = x.map((threshold) => 100 * (source[threshold] || 0));

      el.chartTitle.textContent = `${{divisionLabel}} ${{entry.label}}: ${{directionLabel}} finish`;
      el.chartSubtitle.textContent = `${{probabilityLabel}} by wins, sample size ${{entry.sampleSize}}`;

      const traces = [{{
        type: "bar",
        x,
        y,
        marker: {{
          color: "rgba(143, 181, 255, 0.88)",
          line: {{
            color: "rgba(220, 232, 255, 0.95)",
            width: 1,
          }},
        }},
        hovertemplate: "Threshold %{{x}}<br>Probability %{{y:.1f}}%<extra></extra>",
      }}];

      const layout = {{
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: {{ l: 64, r: 26, t: 18, b: 58 }},
        xaxis: {{
          title: state.direction === "top" ? "No worse than n" : "No better than nth-worst",
          tickmode: "linear",
          dtick: 1,
          gridcolor: "rgba(127,149,192,0.22)",
          zerolinecolor: "rgba(127,149,192,0.35)",
          color: "#c9d4ee",
        }},
        yaxis: {{
          title: "Probability",
          range: [0, 100],
          ticksuffix: "%",
          gridcolor: "rgba(127,149,192,0.22)",
          zerolinecolor: "rgba(127,149,192,0.35)",
          color: "#c9d4ee",
        }},
        font: {{
          family: "Arial, Helvetica, sans-serif",
          color: "#ffffff",
        }},
      }};

      Plotly.react(el.chart, traces, layout, plotConfig);
    }}

    function observePanelResize() {{
      if (!("ResizeObserver" in window)) {{
        window.addEventListener("resize", () => Plotly.Plots.resize(el.chart));
        return;
      }}

      const observer = new ResizeObserver(() => {{
        Plotly.Plots.resize(el.chart);
      }});
      observer.observe(el.panel);
    }}
  </script>
</body>
</html>
"""


def _average_html(payload_json: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Average Finish by Chii</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      color-scheme: dark;
      --site-bg: #07142d;
      --site-panel: #0d1f47;
      --site-panel-strong: #132b5c;
      --site-text: #ffffff;
      --site-muted: #c9d4ee;
      --site-line: #7f95c0;
      --site-line-soft: rgba(127, 149, 192, 0.55);
      --control-bg: #d7e0ef;
      --control-text: #10264f;
      --accent: #8fb5ff;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      min-width: 320px;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      overflow: hidden;
      background: var(--site-bg);
      color: var(--site-text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.35;
    }}

    .tool-shell {{
      height: calc(100vh - 40px);
      display: flex;
      flex-direction: column;
      border: 1px solid var(--site-line);
      background: var(--site-panel);
    }}

    .tool-title-bar {{
      flex: 0 0 auto;
      padding: 12px 16px;
      border-bottom: 1px solid var(--site-line);
      background: var(--site-panel-strong);
      font-size: 1.25rem;
      font-weight: 700;
    }}

    .tool-layout {{
      flex: 1 1 auto;
      min-height: 0;
      display: grid;
      grid-template-columns: 230px minmax(0, 1fr);
    }}

    .tool-options {{
      padding: 14px;
      border-right: 1px solid var(--site-line);
      overflow-y: auto;
    }}

    .tool-options h2 {{
      margin: 0 0 14px;
      font-size: 1rem;
    }}

    .control-group {{
      margin-bottom: 16px;
    }}

    .control-label {{
      display: block;
      margin-bottom: 6px;
      font-weight: 700;
    }}

    .radio-option {{
      display: flex;
      align-items: center;
      gap: 7px;
      margin-bottom: 7px;
      cursor: pointer;
    }}

    .radio-option input {{
      margin: 0;
      accent-color: var(--accent);
    }}

    button:focus,
    input:focus {{
      outline: 1px solid var(--site-muted);
      outline-offset: 1px;
    }}

    .tool-content {{
      min-width: 0;
      min-height: 0;
      padding: 12px;
      overflow: hidden;
    }}

    .tool-content-inner {{
      width: 100%;
      height: 100%;
      min-height: 0;
      display: flex;
      flex-direction: column;
      border: 1px solid var(--site-line-soft);
      background: rgba(255, 255, 255, 0.025);
    }}

    .chart-header {{
      flex: 0 0 auto;
      padding: 10px 12px 0;
    }}

    #chart-title {{
      margin: 0;
      font-size: 1.05rem;
      font-weight: 700;
    }}

    #chart-subtitle {{
      margin-top: 3px;
      color: var(--site-muted);
      font-size: 0.9rem;
    }}

    #chart {{
      flex: 1 1 auto;
      min-height: 0;
      width: 100%;
    }}

    @media (max-width: 760px) {{
      body {{
        overflow: auto;
      }}

      .tool-shell {{
        height: auto;
        min-height: calc(100vh - 40px);
      }}

      .tool-layout {{
        grid-template-columns: 1fr;
      }}

      .tool-options {{
        border-right: 0;
        border-bottom: 1px solid var(--site-line);
      }}

      .tool-content {{
        height: 560px;
      }}
    }}
  </style>
</head>
<body>
  <main class="tool-shell">
    <header class="tool-title-bar">
      <div id="page-title">Average Finish by Chii</div>
    </header>

    <div class="tool-layout">
      <aside class="tool-options">
        <h2>Options</h2>

        <div class="control-group">
          <span class="control-label">Division</span>
          <label class="radio-option">
            <input type="radio" name="division" value="makuuchi" checked>
            Makuuchi
          </label>
          <label class="radio-option">
            <input type="radio" name="division" value="juryo">
            Juryo
          </label>
        </div>

        <div class="control-group">
          <span class="control-label">Sort</span>
          <label class="radio-option">
            <input type="radio" name="sort" value="value" checked>
            By value
          </label>
          <label class="radio-option">
            <input type="radio" name="sort" value="chii">
            By chii
          </label>
        </div>
      </aside>

      <section class="tool-content">
        <div class="tool-content-inner" id="chart-panel">
          <div class="chart-header">
            <h1 id="chart-title">Average Finish by Chii</h1>
            <div id="chart-subtitle"></div>
          </div>
          <div id="chart"></div>
        </div>
      </section>
    </div>
  </main>

  <script>
    const payload = {payload_json};
    const state = {{
      division: payload.defaultDivision,
      sort: payload.defaultSort,
    }};

    const el = {{
      pageTitle: document.getElementById("page-title"),
      chartTitle: document.getElementById("chart-title"),
      chartSubtitle: document.getElementById("chart-subtitle"),
      chart: document.getElementById("chart"),
      panel: document.getElementById("chart-panel"),
      divisionInputs: Array.from(document.querySelectorAll("input[name='division']")),
      sortInputs: Array.from(document.querySelectorAll("input[name='sort']")),
    }};

    const plotConfig = {{
      responsive: true,
      displaylogo: false,
    }};

    document.addEventListener("DOMContentLoaded", init);

    function init() {{
      el.pageTitle.textContent = `${{payload.title}} (${{payload.start}}-${{payload.end}})`;
      wireEvents();
      render();
      observePanelResize();
    }}

    function wireEvents() {{
      el.divisionInputs.forEach((input) => {{
        input.addEventListener("change", () => {{
          if (!input.checked) {{
            return;
          }}
          state.division = input.value;
          render();
        }});
      }});

      el.sortInputs.forEach((input) => {{
        input.addEventListener("change", () => {{
          if (!input.checked) {{
            return;
          }}
          state.sort = input.value;
          render();
        }});
      }});
    }}

    function sortedRows() {{
      const rows = [...payload.divisions[state.division].rows];
      if (state.sort === "value") {{
        rows.sort((a, b) => (
          a.meanPositionPct - b.meanPositionPct
          || a.ordinal - b.ordinal
          || a.chii.localeCompare(b.chii)
        ));
      }} else {{
        rows.sort((a, b) => (
          a.ordinal - b.ordinal
          || a.chii.localeCompare(b.chii)
        ));
      }}
      return rows;
    }}

    function render() {{
      const division = payload.divisions[state.division];
      const rows = sortedRows();
      const x = rows.map((row) => row.chii);
      const y = rows.map((row) => 100 * row.meanPositionPct);
      const customdata = rows.map((row) => [row.sampleSize]);

      el.chartTitle.textContent = `${{division.label}} average finish by Chii`;
      el.chartSubtitle.textContent = `Mean normalized position, n >= ${{division.minSampleSize}}`;

      const traces = [{{
        type: "bar",
        x,
        y,
        customdata,
        marker: {{
          color: "rgba(143, 181, 255, 0.88)",
          line: {{
            color: "rgba(220, 232, 255, 0.95)",
            width: 1,
          }},
        }},
        hovertemplate: "%{{x}}<br>Mean position %{{y:.1f}}%<br>n %{{customdata[0]}}<extra></extra>",
      }}];

      const layout = {{
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: {{ l: 64, r: 26, t: 18, b: 92 }},
        xaxis: {{
          title: "Chii",
          tickangle: -45,
          automargin: true,
          gridcolor: "rgba(127,149,192,0.12)",
          zerolinecolor: "rgba(127,149,192,0.35)",
          color: "#c9d4ee",
        }},
        yaxis: {{
          title: "Mean normalized position",
          range: [0, 100],
          ticksuffix: "%",
          gridcolor: "rgba(127,149,192,0.22)",
          zerolinecolor: "rgba(127,149,192,0.35)",
          color: "#c9d4ee",
        }},
        font: {{
          family: "Arial, Helvetica, sans-serif",
          color: "#ffffff",
        }},
      }};

      Plotly.react(el.chart, traces, layout, plotConfig);
    }}

    function observePanelResize() {{
      if (!("ResizeObserver" in window)) {{
        window.addEventListener("resize", () => Plotly.Plots.resize(el.chart));
        return;
      }}

      const observer = new ResizeObserver(() => {{
        Plotly.Plots.resize(el.chart);
      }});
      observer.observe(el.panel);
    }}
  </script>
</body>
</html>
"""
