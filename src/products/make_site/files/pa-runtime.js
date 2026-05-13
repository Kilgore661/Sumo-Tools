const runtimeState = {
  taggedManifest: null,
  optionState: {},
  sort: null,
  rows: [],
  metadata: null,
  index: null,
  indexEntry: null
};

async function bootSiteRuntime() {
  const pageId = resolveInitialPageId();
  const manifestIndex = await loadManifestIndex();
  const taggedManifest = await loadTaggedManifest(pageId, manifestIndex);
  const urlState = readUrlState();
  const optionState = resolveOptionState(taggedManifest, urlState);
  runtimeState.taggedManifest = taggedManifest;
  runtimeState.optionState = optionState;
  runtimeState.sort = defaultSortForManifest(taggedManifest?.manifest, optionState);
  applyUrlSortState(taggedManifest?.manifest, urlState);
  normaliseUrlIfNeeded(pageId, taggedManifest, optionState);
  renderPageShell(taggedManifest);
  renderOptionsPanel(taggedManifest, optionState);
  await renderPublishedArtefact(taggedManifest, optionState);
  registerRuntimeListeners(taggedManifest, optionState);
}

function resolveInitialPageId() {
  return document.body.dataset.selectedPageId || "";
}

async function loadManifestIndex() {
  return fetch(rootRelativeUrl("manifest-index.json")).then(response => response.json());
}

async function loadTaggedManifest(pageId, manifestIndex) {
  if (!pageId) return null;
  const manifestPath = manifestIndex[pageId];
  if (!manifestPath) throw new Error(`No PA manifest registered for ${pageId}`);
  return fetch(rootRelativeUrl(manifestPath)).then(response => response.json());
}

function readUrlState() {
  return Object.fromEntries(new URLSearchParams(window.location.search).entries());
}

function applyUrlSortState(manifest, urlState) {
  if (!manifest || !urlState.sort) return;
  const column = columnById(manifest, urlState.sort);
  if (!column || !column.sortable) return;
  runtimeState.sort = {
    column: column.id,
    descending: urlState.desc === "true"
  };
}

function resolveOptionState(taggedManifest, urlState) {
  if (!taggedManifest) return {};
  const options = collectOptions(taggedManifest);
  return Object.fromEntries(options.map(option => [
    option.id,
    coerceOptionValue(option, urlState[option.url_key || option.id] ?? option.default)
  ]));
}

function normaliseUrlIfNeeded(pageId, taggedManifest, optionState) {
  if (!taggedManifest || !pageId) return;
  const url = new URL(window.location.href);
  const params = new URLSearchParams();
  for (const option of collectOptions(taggedManifest)) {
    params.set(option.url_key || option.id, String(optionState[option.id]));
  }
  if (runtimeState.sort) {
    params.set("sort", runtimeState.sort.column);
    params.set("desc", String(runtimeState.sort.descending));
  }
  const next = `${url.pathname}?${params.toString()}${url.hash}`;
  if (`${url.pathname}${url.search}${url.hash}` !== next) {
    history.replaceState(null, "", next);
  }
}

function renderPageShell(taggedManifest) {
  const heading = document.getElementById("page-heading");
  const summary = document.getElementById("page-summary");
  if (!taggedManifest) {
    heading.textContent = "Select a page";
    summary.textContent = "";
    return;
  }
  heading.textContent = taggedManifest.manifest.heading;
  summary.textContent = document.body.dataset.pageSummary || "";
}

function renderOptionsPanel(taggedManifest, optionState) {
  const panel = document.getElementById("options-panel");
  if (!taggedManifest) {
    panel.innerHTML = "";
    return;
  }
  const options = collectOptions(taggedManifest);
  const controls = options.length
    ? options.map(option => renderOptionControl(option, optionState, taggedManifest)).join("")
    : `<p class="runtime-note">No options.</p>`;
  panel.innerHTML = `<h2>Options</h2>${controls}`;
  wireOptionControls(panel, taggedManifest);
}

async function renderPublishedArtefact(taggedManifest, optionState) {
  const panel = document.getElementById("pa-panel");
  if (!taggedManifest) {
    panel.innerHTML = `<p class="runtime-note">Choose a navigation item.</p>`;
    return;
  }
  switch (taggedManifest.manifest_class) {
    case "TablePA":
      return renderTablePA(taggedManifest.manifest, optionState, panel);
    case "IndexedTablePA":
      return renderIndexedTablePA(taggedManifest.manifest, optionState, panel);
    case "ChartPA":
      return renderChartPA(taggedManifest.manifest, optionState, panel);
    case "MultiViewPA":
      return renderMultiViewPA(taggedManifest.manifest, optionState, panel);
    case "EssayPA":
      return renderEssayPA(taggedManifest.manifest, optionState, panel);
    case "ExcludedPA":
      return renderExcludedPA(taggedManifest.manifest, optionState, panel);
    default:
      throw new Error(`Unsupported PA manifest class ${taggedManifest.manifest_class}`);
  }
}

function collectOptions(taggedManifest) {
  const manifest = taggedManifest.manifest;
  if (taggedManifest.manifest_class === "MultiViewPA") {
    return [manifest.view_option];
  }
  return manifest.options || [];
}

async function renderTablePA(manifest, optionState, panel) {
  if (manifest.renderer === "standings_table") {
    return renderStandingsTable(manifest, optionState, panel);
  }
  if (manifest.renderer === "sectioned_table") {
    return renderSectionedTable(manifest, optionState, panel);
  }
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "TablePA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderIndexedTablePA(manifest, optionState, panel) {
  const index = await loadJsonFile(manifest.indexed_source.index_path);
  runtimeState.index = index;
  const entries = index.entries || [];
  if (!entries.length) {
    panel.innerHTML = `<p class="runtime-note">No indexed table data is configured.</p>`;
    return;
  }
  const selector = manifest.selector_option;
  const selected = optionState[selector] && optionState[selector] !== "latest"
    ? optionState[selector]
    : index.default_basho;
  const entry = entries.find(item => String(item.basho) === String(selected)) || entries.at(-1);
  runtimeState.indexEntry = entry;
  if (entry?.basho && optionState[selector] !== entry.basho) {
    runtimeState.optionState = { ...runtimeState.optionState, [selector]: entry.basho };
    optionState = runtimeState.optionState;
    normaliseUrlIfNeeded(runtimeState.taggedManifest.tag, runtimeState.taggedManifest, optionState);
  }
  const rows = await loadCsvRows(entry[manifest.indexed_source.payload_path_field]);
  runtimeState.rows = rows;
  runtimeState.metadata = entry;

  const divisions = [...new Map(rows.map(row => [
    row.division_id,
    row.division_label || row.division_id
  ])).entries()];
  const selectedDivision = divisions.some(([id]) => id === optionState.division)
    ? optionState.division
    : divisions[0]?.[0];
  if (selectedDivision && selectedDivision !== optionState.division) {
    runtimeState.optionState = { ...optionState, division: selectedDivision };
  }
  const effectiveState = runtimeState.optionState;
  const filteredRows = rows.filter(row => !effectiveState.division || row.division_id === effectiveState.division);
  const visibleColumns = visibleColumnsForIndexedTable(manifest, effectiveState);
  const sortedRows = sortRows(filteredRows, manifest);
  panel.innerHTML = `
    <div class="table-panel">
      <h2 class="table-title">${escapeHtml(indexedTableTitle(manifest, effectiveState, entry))}</h2>
      <p class="runtime-note">Generated ${escapeHtml(index.generated_at || "")}. Payload state: ${escapeHtml(entry.status || "")}${entry.latest_day ? `, Day ${escapeHtml(entry.latest_day)}` : ""}.</p>
      <div class="table-wrap">
        <table>
          ${renderTableHead(manifest, visibleColumns)}
          <tbody>
            ${sortedRows.map((row, index) => renderTableRow(row, index, visibleColumns)).join("")}
          </tbody>
        </table>
      </div>
      ${renderNotes(manifest, effectiveState)}
    </div>
  `;
  renderOptionsPanel(runtimeState.taggedManifest, effectiveState);
  wireTableHeaders(panel, manifest, effectiveState);
}

async function renderChartPA(manifest, optionState, panel) {
  if (manifest.renderer === "standing_win_probability_chart") {
    return renderStandingWinProbabilityChart(manifest, optionState, panel);
  }
  const trace = (manifest.traces || [])[0];
  if (trace?.kind === "bar") {
    return renderSimpleBarChart(manifest, optionState, panel);
  }
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "ChartPA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderMultiViewPA(manifest, optionState, panel) {
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "MultiViewPA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderEssayPA(manifest, optionState, panel) {
  panel.innerHTML = manifest.body_html || `<p class="runtime-note">${escapeHtml(manifest.heading)}</p>`;
}

async function renderExcludedPA(manifest, optionState, panel) {
  panel.innerHTML = `
    <h2>${escapeHtml(manifest.heading)}</h2>
    <p class="runtime-note">${escapeHtml(manifest.reason)}</p>
  `;
}

async function renderSimpleBarChart(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  const trace = (manifest.traces || [])[0];
  if (!source || !trace) {
    panel.innerHTML = `<p class="runtime-note">No chart data is configured.</p>`;
    return;
  }
  const rows = await loadCsvRows(source.path);
  const orderedRows = orderRowsForAxis(rows, manifest.x_axis, trace.x);
  const maxValue = Math.max(...orderedRows.map(row => Number(row[trace.y]) || 0), 0);
  panel.innerHTML = `
    <div class="chart-panel">
      <h2 class="chart-title">${escapeHtml(source.label || manifest.heading)}</h2>
      <div class="bar-chart">
        <div class="bar-y-label">${escapeHtml(manifest.y_axis?.label || trace.y)}</div>
        <div class="bar-plot" role="img" aria-label="${escapeHtml(manifest.heading)}">
          ${orderedRows.map(row => renderBar(row, trace, maxValue)).join("")}
        </div>
        <div></div>
        <div class="bar-x-label">${escapeHtml(manifest.x_axis?.label || trace.x)}</div>
      </div>
      ${renderNotes(manifest, optionState)}
    </div>
  `;
}

function orderRowsForAxis(rows, axis, fallbackField) {
  const order = axis?.order_values || [];
  if (!order.length) return rows;
  const rowByValue = new Map(rows.map(row => [row[axis.source_field || fallbackField], row]));
  return order.map(value => rowByValue.get(value)).filter(Boolean);
}

function renderBar(row, trace, maxValue) {
  const rawValue = Number(row[trace.y]) || 0;
  const height = maxValue > 0 ? Math.max(1, (rawValue / maxValue) * 100) : 0;
  return `
    <div class="bar-item">
      <div class="bar-value">${escapeHtml(rawValue)}</div>
      <div class="bar" style="height: ${height}%"></div>
      <div class="bar-label">${escapeHtml(row[trace.x])}</div>
    </div>
  `;
}

async function renderStandingWinProbabilityChart(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  const trace = (manifest.traces || [])[0];
  if (!source || !trace) {
    panel.innerHTML = `<p class="runtime-note">No chart data is configured.</p>`;
    return;
  }
  const rows = await loadCsvRows(source.path);
  const visibleRows = rows
    .filter(row => displayStandingChii(row.selected_chii, manifest))
    .filter(row => displayStandingChii(row.opponent_chii, manifest))
    .filter(row => optionState.division === "All" || divisionLabelForChii(row.selected_chii) === optionState.division);
  const grouped = groupRowsBy(visibleRows, trace.group_by);
  const chart = buildLineChartModel(grouped, trace, manifest, optionState);
  panel.innerHTML = `
    <div class="chart-panel">
      <h2 class="chart-title">${escapeHtml(source.label || manifest.heading)}: ${escapeHtml(optionState.division)}</h2>
      <div class="line-chart-wrap">
        ${renderLineChartSvg(chart)}
      </div>
      ${renderLineLegend(chart)}
      ${renderNotes(manifest, optionState)}
    </div>
  `;
}

function groupRowsBy(rows, field) {
  const groups = new Map();
  for (const row of rows) {
    const key = row[field];
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.entries()]
    .sort((a, b) => Number(a[1][0].selected_ordinal) - Number(b[1][0].selected_ordinal))
    .map(([key, groupRows]) => [
      key,
      groupRows.sort((a, b) => Number(a.opponent_ordinal) - Number(b.opponent_ordinal))
    ]);
}

function buildLineChartModel(groupedRows, trace, manifest, optionState) {
  const width = 920;
  const height = 520;
  const margin = { top: 24, right: 24, bottom: 88, left: 72 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const allRows = groupedRows.flatMap(([, rows]) => rows);
  const xValues = [...new Set(allRows.map(row => Number(row.opponent_ordinal)))]
    .filter(Number.isFinite)
    .sort((a, b) => a - b);
  const xMin = xValues[0] ?? 0;
  const xMax = xValues.at(-1) ?? 1;
  const yMin = manifest.y_axis?.minimum ?? 0;
  const yMax = manifest.y_axis?.maximum ?? 1;
  const scaleX = value => margin.left + ((value - xMin) / Math.max(1, xMax - xMin)) * plotWidth;
  const scaleY = value => margin.top + (1 - ((value - yMin) / Math.max(1, yMax - yMin))) * plotHeight;
  const colors = ["#8fb5ff", "#f2c14e", "#6ed6a0", "#f28c8c", "#b38cff", "#7bdff2", "#f7a072", "#d4e157", "#ff9bd2", "#a0c4ff"];
  return {
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    trace,
    manifest,
    optionState,
    xValues,
    scaleX,
    scaleY,
    series: groupedRows.map(([key, rows], index) => ({
      key,
      color: colors[index % colors.length],
      rows
    }))
  };
}

function renderLineChartSvg(chart) {
  const { width, height, margin, plotWidth, plotHeight, scaleX, scaleY } = chart;
  const yTicks = [0, 0.25, 0.5, 0.75, 1];
  const xTickRows = representativeXTicks(chart);
  return `
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(chart.manifest.heading)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${scaleY(value)}" y2="${scaleY(value)}"></line>
        <text class="tick-label" x="${margin.left - 10}" y="${scaleY(value) + 4}" text-anchor="end">${Math.round(value * 100)}%</text>
      `).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${margin.top + plotHeight}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${margin.top + plotHeight}" y2="${margin.top + plotHeight}"></line>
      ${xTickRows.map(row => `
        <text class="tick-label" x="${scaleX(Number(row.opponent_ordinal))}" y="${margin.top + plotHeight + 22}" text-anchor="middle">${escapeHtml(row.opponent_chii)}</text>
      `).join("")}
      <text class="axis-label" x="${margin.left + plotWidth / 2}" y="${height - 20}" text-anchor="middle">${escapeHtml(chart.manifest.x_axis?.label || "Opponent standing")}</text>
      <text class="axis-label" transform="translate(20 ${margin.top + plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.manifest.y_axis?.label || chart.trace.y)}</text>
      ${chart.series.map(series => renderSeries(series, chart)).join("")}
    </svg>
  `;
}

function representativeXTicks(chart) {
  const firstSeries = chart.series[0]?.rows || [];
  const maxTicks = 12;
  const step = Math.max(1, Math.ceil(firstSeries.length / maxTicks));
  return firstSeries.filter((_, index) => index % step === 0 || index === firstSeries.length - 1);
}

function renderSeries(series, chart) {
  const points = series.rows.map(row => {
    const x = chart.scaleX(Number(row[chart.manifest.x_axis?.order_field || "opponent_ordinal"]));
    const y = chart.scaleY(Number(row[chart.trace.y]));
    return { row, x, y };
  }).filter(point => Number.isFinite(point.x) && Number.isFinite(point.y));
  const polyline = points.map(point => `${point.x},${point.y}`).join(" ");
  const errorBars = chart.optionState.error_bars ? points.map(point => renderErrorBar(point, chart)).join("") : "";
  return `
    <g>
      ${errorBars}
      <polyline class="trace-line" points="${polyline}" style="stroke:${series.color}"></polyline>
      ${points.map(point => `<circle class="trace-point" cx="${point.x}" cy="${point.y}" r="3" style="fill:${series.color}"><title>${escapeHtml(series.key)} vs ${escapeHtml(point.row.opponent_chii)}: ${formatPercent(point.row[chart.trace.y])}</title></circle>`).join("")}
    </g>
  `;
}

function renderErrorBar(point, chart) {
  const low = Number(point.row.ci95_lower);
  const high = Number(point.row.ci95_upper);
  if (!Number.isFinite(low) || !Number.isFinite(high)) return "";
  const y1 = chart.scaleY(high);
  const y2 = chart.scaleY(low);
  return `<line class="error-bar" x1="${point.x}" x2="${point.x}" y1="${y1}" y2="${y2}"></line>`;
}

function renderLineLegend(chart) {
  return `
    <div class="chart-legend">
      ${chart.series.map(series => `<span><span class="legend-swatch" style="background:${series.color}"></span>${escapeHtml(series.key)}</span>`).join("")}
    </div>
  `;
}

function displayStandingChii(chii, manifest) {
  const sanyaku = manifest.provenance?.sanyaku_display || [];
  if (!chii) return false;
  if (chii.startsWith("Y")) return sanyaku.includes(chii);
  if (chii.startsWith("O")) return sanyaku.includes(chii);
  if (chii.startsWith("S") && !chii.startsWith("Sd")) return sanyaku.includes(chii);
  if (chii.startsWith("K")) return sanyaku.includes(chii);
  return true;
}

function divisionLabelForChii(chii) {
  if (!chii) return "Other";
  if (chii.startsWith("Ms")) return "Makushita";
  if (chii.startsWith("Sd")) return "Sandanme";
  if (chii.startsWith("Jd")) return "Jonidan";
  if (chii.startsWith("Jk")) return "Jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "Makuuchi";
  if (chii.startsWith("J")) return "Juryo";
  return "Other";
}

function formatPercent(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${(number * 100).toFixed(1)}%` : value;
}

function registerRuntimeListeners(taggedManifest, optionState) {
}

function renderOptionControl(option, optionState, taggedManifest) {
  const value = optionState[option.id];
  const values = dynamicOptionValues(option, taggedManifest) || option.values || [];
  if (option.control === "radio_group") {
    return `
      <div class="control-group">
        <div class="control-label">${escapeHtml(option.label)}</div>
        <div class="radio-group">
          ${values.map(item => `
            <label class="radio-option">
              <input type="radio" name="${escapeHtml(option.id)}" data-option-id="${escapeHtml(option.id)}" value="${escapeHtml(item.value)}" ${String(value) === String(item.value) ? "checked" : ""}>
              <span>${escapeHtml(item.label)}</span>
            </label>
          `).join("")}
        </div>
      </div>
    `;
  }
  if (option.kind === "boolean") {
    return `
      <div class="control-group">
        <label class="checkbox-option">
          <input type="checkbox" data-option-id="${escapeHtml(option.id)}" ${value === true || value === "true" ? "checked" : ""}>
          <span>${escapeHtml(option.label)}</span>
        </label>
      </div>
    `;
  }
  return `
    <div class="control-group">
      <label class="control-label" for="option-${escapeHtml(option.id)}">${escapeHtml(option.label)}</label>
      <select id="option-${escapeHtml(option.id)}" data-option-id="${escapeHtml(option.id)}">
        ${values.map(item => `
          <option value="${escapeHtml(item.value)}" ${String(value) === String(item.value) ? "selected" : ""}>${escapeHtml(item.label)}</option>
        `).join("")}
      </select>
    </div>
  `;
}

function dynamicOptionValues(option, taggedManifest) {
  if (!taggedManifest || taggedManifest.manifest_class !== "IndexedTablePA") return null;
  if (option.id === taggedManifest.manifest.selector_option && runtimeState.index?.entries) {
    return [...runtimeState.index.entries]
      .reverse()
      .map(entry => ({ value: entry.basho, label: entry.label || entry.basho }));
  }
  if (option.id === "division" && runtimeState.rows?.length) {
    return [...new Map(runtimeState.rows.map(row => [
      row.division_id,
      row.division_label || row.division_id
    ])).entries()].map(([value, label]) => ({ value, label }));
  }
  return null;
}

function wireOptionControls(panel, taggedManifest) {
  const optionById = new Map(collectOptions(taggedManifest).map(option => [option.id, option]));
  panel.querySelectorAll("[data-option-id]").forEach(control => {
    control.addEventListener("change", async () => {
      try {
        const option = optionById.get(control.dataset.optionId);
        const value = option.kind === "boolean" ? control.checked : control.value;
        runtimeState.optionState[option.id] = coerceOptionValue(option, value);
        runtimeState.sort = defaultSortForManifest(taggedManifest.manifest, runtimeState.optionState);
        normaliseUrlIfNeeded(resolveInitialPageId(), taggedManifest, runtimeState.optionState);
        renderOptionsPanel(taggedManifest, runtimeState.optionState);
        await renderPublishedArtefact(taggedManifest, runtimeState.optionState);
      } catch (error) {
        alert(`No data is available for the selected options.\n\n${error.message || error}`);
      }
    });
  });
}

async function renderStandingsTable(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  if (!source) {
    panel.innerHTML = `<p class="runtime-note">No data source matches the selected options.</p>`;
    return;
  }
  const [rows, metadata] = await Promise.all([
    loadCsvRows(source.path),
    source.metadata_path ? loadJsonFile(source.metadata_path) : Promise.resolve(null)
  ]);
  runtimeState.rows = rows;
  runtimeState.metadata = metadata;
  const visibleColumns = visibleColumnsForTable(manifest, optionState);
  const filteredRows = rows
    .filter(row => includeStandingsRow(row, optionState))
    .sort((a, b) => compareRows(a, b, columnById(manifest, runtimeState.sort.column), runtimeState.sort.descending));
  panel.innerHTML = `
    <div class="table-panel">
      <h2 class="table-title">${escapeHtml(standingsTitle(optionState, metadata, runtimeState.sort.column))}</h2>
      <div class="table-wrap">
        <table>
          ${renderTableHead(manifest, visibleColumns)}
          <tbody>
            ${filteredRows.map((row, index) => renderTableRow(row, index, visibleColumns)).join("")}
          </tbody>
        </table>
      </div>
      ${renderNotes(manifest, optionState)}
    </div>
  `;
  wireTableHeaders(panel, manifest, optionState);
}

async function renderSectionedTable(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  if (!source) {
    panel.innerHTML = `<p class="runtime-note">No data source is configured.</p>`;
    return;
  }
  const rows = await loadCsvRows(source.path);
  panel.innerHTML = `
    <div class="table-panel">
      <div class="sectioned-table-grid">
        ${(manifest.sections || []).map(section => renderTableSection(section, rows, manifest.columns || [])).join("")}
      </div>
      ${renderNotes(manifest, optionState)}
    </div>
  `;
}

function renderTableSection(section, rows, columns) {
  const sectionRows = rows
    .filter(row => row[section.source_field] === section.source_value)
    .sort((a, b) => comparePrimitive(Number(a[section.order_by] || 0), Number(b[section.order_by] || 0)));
  return `
    <section class="table-section">
      <h2>${escapeHtml(section.heading)}</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>${columns.map(column => renderPlainHeaderCell(column)).join("")}</tr>
          </thead>
          <tbody>
            ${sectionRows.map((row, index) => renderTableRow(row, index, columns)).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderPlainHeaderCell(column) {
  const classes = [column.align || ""].filter(Boolean).join(" ");
  return `<th class="${escapeHtml(classes)}">${escapeHtml(column.heading)}</th>`;
}

function dataSourceForOptions(manifest, optionState) {
  return (manifest.data_sources || []).find(source => {
    if (!source.option_id) return source.id === manifest.primary_source || manifest.data_sources.length === 1;
    return String(optionState[source.option_id]) === String(source.option_value);
  });
}

async function loadCsvRows(path) {
  const text = await fetch(path).then(response => {
    if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
    return response.text();
  });
  return parseCsv(text);
}

async function loadJsonFile(path) {
  return fetch(path).then(response => {
    if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
    return response.json();
  });
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = splitCsvLine(lines[0]);
  return lines.slice(1).filter(Boolean).map(line => {
    const values = splitCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function splitCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"' && line[i + 1] === '"') {
      current += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

function visibleColumnsForTable(manifest, optionState) {
  const presetId = optionState.metric_group_preset;
  const preset = (manifest.group_visibility_presets || []).find(item => item.id === presetId);
  const visibleGroups = new Set(preset ? preset.visible_groups : (manifest.column_groups || []).map(group => group.id));
  return (manifest.columns || []).filter(column => column.always_visible || visibleGroups.has(column.group));
}

function visibleColumnsForIndexedTable(manifest, optionState) {
  const visibleGroups = new Set((manifest.column_groups || [])
    .filter(group => group.always_visible)
    .map(group => group.id));
  if (optionState.previous_context === true || optionState.previous_context === "true") {
    visibleGroups.add("previous_basho");
  }
  if (optionState.rating_context === true || optionState.rating_context === "true") {
    visibleGroups.add("rating_state");
  }
  if (optionState.nu_chii === true || optionState.nu_chii === "true") {
    visibleGroups.add("rating_state");
  }
  return (manifest.columns || []).filter(column => {
    if (column.id === "nu_chii" && !(optionState.nu_chii === true || optionState.nu_chii === "true")) {
      return false;
    }
    if (["equelo", "delta_equelo"].includes(column.id) && !(optionState.rating_context === true || optionState.rating_context === "true")) {
      return false;
    }
    return column.always_visible || visibleGroups.has(column.group);
  });
}

function includeStandingsRow(row, optionState) {
  if ((optionState.current_only === true || optionState.current_only === "true") && String(row.is_current) !== "1") {
    return false;
  }
  if (optionState.division && optionState.division !== "all") {
    return divisionForChii(row.chii) === optionState.division;
  }
  return true;
}

function divisionForChii(chii) {
  if (!chii) return "other";
  if (chii.startsWith("Ms")) return "makushita";
  if (chii.startsWith("Sd")) return "sandanme";
  if (chii.startsWith("Jd")) return "jonidan";
  if (chii.startsWith("Jk")) return "jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "makuuchi";
  if (chii.startsWith("J")) return "juryo";
  return "other";
}

function renderTableHead(manifest, visibleColumns) {
  const groups = manifest.column_groups || [];
  const groupForColumn = new Map(visibleColumns.map(column => [column.id, groups.find(group => group.id === column.group)]));
  const groupCells = [];
  let index = 0;
  while (index < visibleColumns.length) {
    const group = groupForColumn.get(visibleColumns[index].id);
    const groupColumns = [];
    while (index < visibleColumns.length && groupForColumn.get(visibleColumns[index].id)?.id === group?.id) {
      groupColumns.push(visibleColumns[index]);
      index += 1;
    }
    groupCells.push(`<th colspan="${groupColumns.length}" class="center">${escapeHtml(group?.heading || "")}</th>`);
  }
  return `
    <thead>
      <tr>${groupCells.join("")}</tr>
      <tr>${visibleColumns.map(column => renderHeaderCell(column)).join("")}</tr>
    </thead>
  `;
}

function sortRows(rows, manifest) {
  if (!runtimeState.sort) return rows;
  const column = columnById(manifest, runtimeState.sort.column);
  if (!column) return rows;
  return [...rows].sort((a, b) => compareRows(a, b, column, runtimeState.sort.descending));
}

function indexedTableTitle(manifest, optionState, entry) {
  const division = labelForOption(manifest, "division", optionState.division) || optionState.division || "";
  const label = entry.label || entry.basho || "";
  if (entry.latest_day && Number(entry.latest_day) < 15) {
    return `${division} Results (Day ${entry.latest_day}) for ${label}`;
  }
  return `${division} Results for ${label}`;
}

function renderHeaderCell(column) {
  const active = runtimeState.sort?.column === column.id;
  const marker = active ? (runtimeState.sort.descending ? " ▼" : " ▲") : "";
  const classes = [column.align || "", column.sortable ? "sortable" : ""].filter(Boolean).join(" ");
  return `<th class="${escapeHtml(classes)}" data-column-id="${escapeHtml(column.id)}">${escapeHtml(column.heading)}${marker}</th>`;
}

function renderTableRow(row, index, visibleColumns) {
  return `<tr>${visibleColumns.map(column => renderTableCell(row, index, column)).join("")}</tr>`;
}

function renderTableCell(row, index, column) {
  const classes = [column.align || ""].filter(Boolean).join(" ");
  return `<td class="${escapeHtml(classes)}">${formatCell(row, index, column)}</td>`;
}

function formatCell(row, index, column) {
  if (column.formatter === "row_number") return String(index + 1);
  if (column.formatter === "competition_rank") return competitionRank(row, column);
  const raw = column.source_field ? row[column.source_field] : "";
  if (column.formatter === "decimal_2") return formatNumber(raw, 2);
  if (column.formatter === "percent_1") return `${formatNumber(raw, 1)}%`;
  if (column.link === "rikishi" && row.rikishi_id) {
    return `<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(row.rikishi_id)}">${escapeHtml(raw)}</a>`;
  }
  return escapeHtml(raw);
}

function competitionRank(row, column) {
  const source = column.source_field || column.sort_key;
  const sorted = [...runtimeState.rows]
    .filter(candidate => includeStandingsRow(candidate, runtimeState.optionState))
    .sort((a, b) => comparePrimitive(valueForSort(b, { sort_key: source, source_field: source, sort_kind: "numeric" }), valueForSort(a, { sort_key: source, source_field: source, sort_kind: "numeric" })));
  const target = Number(row[source]);
  const found = sorted.findIndex(candidate => Number(candidate[source]) === target);
  return found >= 0 ? String(found + 1) : "";
}

function formatNumber(value, digits) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : escapeHtml(value);
}

function wireTableHeaders(panel, manifest, optionState) {
  panel.querySelectorAll("th[data-column-id]").forEach(header => {
    const column = columnById(manifest, header.dataset.columnId);
    if (!column?.sortable) return;
    header.addEventListener("click", async () => {
      if (runtimeState.sort?.column === column.id) {
        runtimeState.sort.descending = !runtimeState.sort.descending;
      } else {
        runtimeState.sort = {
          column: column.id,
          descending: defaultSortDescending(column)
        };
      }
      normaliseUrlIfNeeded(resolveInitialPageId(), runtimeState.taggedManifest, runtimeState.optionState);
      await renderPublishedArtefact(runtimeState.taggedManifest, runtimeState.optionState);
    });
  });
}

function compareRows(a, b, column, descending) {
  const result = comparePrimitive(valueForSort(a, column), valueForSort(b, column));
  return descending ? -result : result;
}

function valueForSort(row, column) {
  const key = column.sort_key || column.source_field;
  const value = row[key] ?? "";
  if (column.sort_kind === "numeric" || column.sort_kind === "chii_ordinal") {
    const number = Number(value);
    return Number.isFinite(number) ? number : Number.POSITIVE_INFINITY;
  }
  return String(value).toLocaleLowerCase();
}

function comparePrimitive(a, b) {
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

function columnById(manifest, columnId) {
  return (manifest.columns || []).find(column => column.id === columnId);
}

function defaultSortForManifest(manifest, optionState) {
  if (!manifest) return null;
  const preset = (manifest.group_visibility_presets || []).find(item => item.id === optionState.metric_group_preset);
  const sort = preset?.default_sort || manifest.default_sort;
  if (!sort) return null;
  return { column: sort.column, descending: sort.descending };
}

function defaultSortDescending(column) {
  return !(column.sort_kind === "text" || column.sort_kind === "chii_ordinal");
}

function standingsTitle(optionState, metadata, sortColumn) {
  const division = labelForOption(runtimeState.taggedManifest.manifest, "division", optionState.division) || "All";
  const sortLabel = columnById(runtimeState.taggedManifest.manifest, sortColumn)?.heading || "Selected Column";
  const end = metadata?.effective_end_date || "";
  const monthYear = end ? bashoMonthYear(end) : "";
  return `${division} Standings by ${sortLabel} after ${monthYear} Basho`;
}

function bashoMonthYear(dateToken) {
  const [year, month] = dateToken.split("/");
  const monthName = new Date(Number(year), Number(month) - 1, 1).toLocaleString("en-GB", { month: "long" });
  return `${monthName} ${year}`;
}

function labelForOption(manifest, optionId, value) {
  const option = (manifest.options || []).find(item => item.id === optionId);
  return option?.values?.find(item => String(item.value) === String(value))?.label;
}

function renderNotes(manifest, optionState) {
  const notes = (manifest.notes || []).filter(note => noteApplies(note, optionState));
  if (!notes.length) return "";
  return `
    <div class="notes-panel">
      <h3>Notes</h3>
      <ol>
        ${notes.map(note => `<li>${formatNoteText(note)}</li>`).join("")}
      </ol>
    </div>
  `;
}

function formatNoteText(note) {
  return note.format === "html" ? note.text : escapeHtml(note.text);
}

function noteApplies(note, optionState) {
  const applies = note.applies_to || ["all"];
  if (applies.includes("all") || applies.includes(optionState.metric_group_preset)) {
    return true;
  }
  if (applies.includes("previous_basho")) {
    return optionState.previous_context === true || optionState.previous_context === "true";
  }
  if (applies.includes("rating_state")) {
    return (
      optionState.rating_context === true ||
      optionState.rating_context === "true" ||
      optionState.nu_chii === true ||
      optionState.nu_chii === "true"
    );
  }
  return false;
}

function coerceOptionValue(option, value) {
  if (option.kind === "boolean") {
    return value === true || value === "true";
  }
  const matching = (option.values || []).find(item => String(item.value) === String(value));
  return matching ? matching.value : value;
}

function rootRelativeUrl(path) {
  const configuredRoot = document.body.dataset.runtimeRoot;
  if (configuredRoot !== undefined) {
    return `${configuredRoot}${path}`;
  }
  const current = window.location.pathname;
  const marker = "/runtime-skeleton/";
  const index = current.indexOf(marker);
  if (index < 0) return path;
  const tail = current.slice(index + marker.length);
  const depth = Math.max(0, tail.split("/").filter(Boolean).length - 1);
  return "../".repeat(depth) + path;
}

function escapeHtml(value) {
  const span = document.createElement("span");
  span.textContent = value ?? "";
  return span.innerHTML;
}

document.addEventListener("DOMContentLoaded", () => {
  bootSiteRuntime().catch(error => {
    document.getElementById("pa-panel").innerHTML = `<pre>${escapeHtml(error.stack || error.message)}</pre>`;
  });
});
