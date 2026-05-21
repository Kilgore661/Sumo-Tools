(function () {
  const PAGE_PARAM = "page";
  const contentPanel = document.getElementById("content-panel");
  let runtimeManifest = null;

  bootSiteContext();
  bootNavigationToggle();
  boot().catch(error => {
    contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  });

  function bootSiteContext() {
    const context = siteContext();
    document.body.classList.add(`site-context-${context.id}`);
    if (context.titlePrefix) {
      document.title = `${context.titlePrefix} ${document.title}`;
    }
  }

  function siteContext() {
    const hostname = window.location.hostname.toLowerCase();
    if (hostname === "68.66.241.105" || hostname === "www.661.org.uk" || hostname === "661.org.uk") {
      return { id: "remote", label: "Remote Site", titlePrefix: "REMOTE" };
    }
    if (hostname.startsWith("192.168.")) {
      return { id: "local", label: "Local Site" };
    }
    return { id: "preview", label: "Preview Site", titlePrefix: "PREVIEW" };
  }

  async function boot() {
    runtimeManifest = await fetchJson("runtime/site-manifest.json");
    const navLinks = [...document.querySelectorAll(".nav-link[data-page-id]")];
    for (const link of navLinks) {
      link.addEventListener("click", event => {
        event.preventDefault();
        selectPage(link.dataset.pageId, { pushUrl: true });
      });
    }
    window.addEventListener("popstate", () => loadStateFromUrl());
    loadStateFromUrl();
  }

  function bootNavigationToggle() {
    const shell = document.querySelector("[data-nav-shell]");
    const panel = document.querySelector("[data-nav-panel]");
    const toggle = document.querySelector("[data-nav-toggle]");
    if (!shell || !panel || !toggle) return;

    const storageKey = toggle.dataset.storageKey || "gaspodeSumoLab.makeSite2.navCollapsed";
    const initialCollapsed = window.localStorage.getItem(storageKey) === "true";
    applyNavigationCollapsedState(shell, panel, toggle, initialCollapsed);

    toggle.addEventListener("click", () => {
      const collapsed = !shell.classList.contains("nav-collapsed");
      applyNavigationCollapsedState(shell, panel, toggle, collapsed);
      window.localStorage.setItem(storageKey, String(collapsed));
    });
  }

  function applyNavigationCollapsedState(shell, panel, toggle, collapsed) {
    shell.classList.toggle("nav-collapsed", collapsed);
    panel.hidden = collapsed;
    panel.setAttribute("aria-hidden", String(collapsed));
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.setAttribute("aria-label", collapsed ? "Show navigation" : "Hide navigation");
    toggle.title = collapsed ? "Show navigation" : "Hide navigation";
    toggle.textContent = collapsed ? ">" : "<";
  }

  function loadStateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const pageId = params.get(PAGE_PARAM) || "";
    if (!pageId) {
      markActivePage("");
      renderLandingPanel();
      return;
    }
    selectPage(pageId, { replaceUrl: true });
  }

  function renderLandingPanel() {
    const context = siteContext();
    contentPanel.innerHTML = [
      '<section class="landing-panel">',
      `<h2>${escapeHtml(context.label)}</h2>`,
      '</section>'
    ].join("");
  }

  function selectPage(pageId, { pushUrl = false, replaceUrl = false } = {}) {
    markActivePage(pageId);
    if (pushUrl || replaceUrl) {
      writePageUrl(pageId, { replace: replaceUrl });
    }
    const panel = runtimeManifest.ui.content_panels.find(candidate => candidate.page_id === pageId);
    if (!panel) {
      contentPanel.replaceChildren();
      return;
    }
    renderContentPanel(panel).catch(error => {
      contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
    });
  }

  function markActivePage(pageId) {
    for (const link of document.querySelectorAll(".nav-link[data-page-id]")) {
      link.classList.toggle("is-active", link.dataset.pageId === pageId);
    }
  }

  function writePageUrl(pageId, { replace }) {
    const params = new URLSearchParams(window.location.search);
    if (pageId) {
      params.set(PAGE_PARAM, pageId);
    } else {
      params.delete(PAGE_PARAM);
    }
    const search = params.toString();
    const next = `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
    if (next === `${window.location.pathname}${window.location.search}${window.location.hash}`) return;
    if (replace) {
      history.replaceState(null, "", next);
    } else {
      history.pushState(null, "", next);
    }
  }

  function writePanelUrl(pageId, filters, state, { replace }) {
    const params = new URLSearchParams(window.location.search);
    if (pageId) params.set(PAGE_PARAM, pageId);
    for (const filter of filters) {
      params.set(filter.url_key || filter.id, String(state[filter.id]));
    }
    const search = params.toString();
    const next = `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
    if (next === `${window.location.pathname}${window.location.search}${window.location.hash}`) return;
    if (replace) {
      history.replaceState(null, "", next);
    } else {
      history.pushState(null, "", next);
    }
  }

  async function renderContentPanel(panel, overrideState = null) {
    if (panel.grammar !== "G1") throw new Error(`Unsupported content grammar: ${panel.grammar}`);
    const artifact = runtimeManifest.artifacts[panel.contents.pa.artifact_id];
    if (!artifact) throw new Error(`Unknown artifact: ${panel.contents.pa.artifact_id}`);
    if (artifact.kind === "indexed_table") {
      await renderIndexedTableContentPanel(panel, artifact, overrideState);
      return;
    }
    if (artifact.kind === "banzuke_changes") {
      await renderBanzukeChangesContentPanel(panel, artifact, overrideState);
      return;
    }
    if (artifact.kind === "standings") {
      await renderStandingsContentPanel(panel, artifact, overrideState);
      return;
    }
    if (artifact.kind === "chart") {
      await renderChartContentPanel(panel, artifact, overrideState);
      return;
    }
    throw new Error(`Unsupported artifact kind: ${artifact.kind}`);
  }

  async function renderIndexedTableContentPanel(panel, artifact, overrideState = null) {
    const filters = panel.contents.filter_section.filters;
    const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
    const index = await fetchJson(artifact.indexed_source.index_path);
    const selectedEntry = selectedIndexEntry(index, state[artifact.selector_filter_id]);
    state[artifact.selector_filter_id] = selectedEntry.basho;
    const payloadPath = selectedEntry[artifact.indexed_source.payload_path_field];
    const dataRoot = artifact.indexed_source.index_path.replace(/[^/]+$/, "");
    const rows = await fetchCsv(`${dataRoot}${payloadPath.replace(/^data\//, "")}`);
    state.division = resolveSelectedDivision(rows, state.division);
    writePanelUrl(panel.page_id, filters, state, { replace: true });
    const filteredRows = rows.filter(row => row.division_id === state.division);

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body">',
      renderFilterSection(panel.contents.filter_section, state, index),
      '<div class="pa-slot">',
      renderArtifactTitleBlock(artifact, state, selectedEntry, filters),
      renderIndexedTable(artifact, filteredRows, state),
      '</div>',
      '</div>',
      renderNotes(artifact, state),
      '</section>'
    ].join("");
    wireFilterSection(panel, state);
  }

  async function renderBanzukeChangesContentPanel(panel, artifact, overrideState = null) {
    const filters = panel.contents.filter_section.filters;
    const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
    const config = await fetchJson(artifact.config_source.path);
    const rows = await fetchCsv(artifact.rows_source.path);
    state.division = resolveBanzukeChangesDivision(config, state.division);
    writePanelUrl(panel.page_id, filters, state, { replace: true });
    const filteredRows = rows.filter(row => row.division_id === state.division);

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body">',
      renderFilterSection(panel.contents.filter_section, state),
      '<div class="pa-slot">',
      renderBanzukeChangesTable(artifact, filteredRows, state, config),
      '</div>',
      '</div>',
      renderNotes(artifact, state),
      '</section>'
    ].join("");
    wireFilterSection(panel, state);
  }

  async function renderStandingsContentPanel(panel, artifact, overrideState = null) {
    const filters = panel.contents.filter_section.filters;
    const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
    const config = await fetchJson(artifact.config_source.path);
    state.current_num_basho = resolveStandingsWindow(config, state.current_num_basho);
    state.division = resolveStandingsDivision(config, state.division);
    const source = selectedStandingsSource(artifact, state);
    const rows = await fetchCsv(source.path);
    writePanelUrl(panel.page_id, filters, state, { replace: true });
    const filteredRows = standingsRowsForState(rows, state);
    const sortedRows = sortedStandingsRows(filteredRows, state);

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body">',
      renderFilterSection(panel.contents.filter_section, state),
      '<div class="pa-slot">',
      renderStandingsTable(artifact, sortedRows, filteredRows, state),
      '</div>',
      '</div>',
      renderNotes(artifact, state),
      '</section>'
    ].join("");
    wireFilterSection(panel, state);
  }

  async function renderChartContentPanel(panel, artifact, overrideState = null) {
    if (artifact.renderer !== "finish_by_chii_chart") {
      throw new Error(`Unsupported chart renderer: ${artifact.renderer}`);
    }
    const filters = panel.contents.filter_section.filters;
    const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    state.division = resolveSelectedDataValue(
      rowsBySource[artifact.data_binding.sources[0]] || [],
      "division",
      state.division,
      "division_id",
    );
    state.chii = resolveSelectedFilterValueFromSource(
      filters.find(filter => filter.id === "chii"),
      state,
      rowsBySource,
    );
    writePanelUrl(panel.page_id, filters, state, { replace: true });

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body">',
      renderFilterSection(panel.contents.filter_section, state, null, rowsBySource),
      '<div class="pa-slot">',
      renderFinishByChiiChart(artifact, state, filters, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, state),
      '</section>'
    ].join("");
    renderFinishByChiiPlot(artifact, state, rowsBySource);
    wireFilterSection(panel, state);
  }

  async function fetchArtifactCsvSet(artifact) {
    const entries = await Promise.all(
      artifact.data_sources.map(async source => [source.id, await fetchCsv(source.path)])
    );
    return Object.fromEntries(entries);
  }

  function renderArtifactTitleBlock(artifact, state, entry, filters) {
    const title = artifactTitle(artifact, state, entry, filters);
    if (!title) return "";
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(title)}</h4>`,
      '</div>'
    ].join("");
  }

  function artifactTitle(artifact, state, entry, filters) {
    if (artifact.id !== "basho_results_browser") return "";
    return bashoResultsTitle(state, entry, filters);
  }

  function bashoResultsTitle(state, entry, filters) {
    const division = filterValueLabel(filters, "division", state.division) || state.division || "";
    const label = entry.label || entry.basho || "";
    if (entry.latest_day && Number(entry.latest_day) < 15) {
      return `${division} Results (Day ${entry.latest_day}) for ${label}`;
    }
    return `${division} Results for ${label}`;
  }

  function filterValueLabel(filters, filterId, value) {
    const filter = filters.find(candidate => candidate.id === filterId);
    const option = (filter?.values || []).find(candidate => candidate.value === value);
    return option?.label || "";
  }

  function readFilterUrlState(filters) {
    const params = new URLSearchParams(window.location.search);
    return Object.fromEntries(filters.map(filter => [
      filter.id,
      params.get(filter.url_key || filter.id)
    ]));
  }

  function resolveFilterState(filters, urlState) {
    return Object.fromEntries(filters.map(filter => [
      filter.id,
      coerceFilterValue(filter, urlState[filter.id] ?? filter.default)
    ]));
  }

  function coerceFilterValue(filter, value) {
    if (filter.control === "checkbox") return value === true || value === "true";
    return value === null || value === undefined || value === "" ? filter.default : value;
  }

  function resolveSelectedDivision(rows, selectedDivision) {
    const divisions = [...new Set(rows.map(row => row.division_id).filter(Boolean))];
    return divisions.includes(selectedDivision) ? selectedDivision : divisions[0] || selectedDivision;
  }

  function resolveBanzukeChangesDivision(config, selectedDivision) {
    const divisions = (config.divisions || []).map(division => division.id);
    return divisions.includes(selectedDivision) ? selectedDivision : config.default_division;
  }

  function resolveStandingsWindow(config, selectedWindow) {
    const windows = (config.supported_num_basho || []).map(String);
    return windows.includes(String(selectedWindow)) ? String(selectedWindow) : String(config.default_num_basho);
  }

  function resolveStandingsDivision(config, selectedDivision) {
    const divisions = ["all", "makuuchi", "juryo", "makushita", "sandanme", "jonidan", "jonokuchi"];
    return divisions.includes(selectedDivision) ? selectedDivision : config.default_division;
  }

  function selectedStandingsSource(artifact, state) {
    return artifact.data_sources.find(source =>
      String(source.option_value) === String(state[artifact.selector_filter_id])
    );
  }

  function wireFilterSection(panel, state) {
    const form = contentPanel.querySelector(".filter-section");
    if (!form) return;
    form.addEventListener("change", event => {
      const control = event.target;
      if (!(control instanceof HTMLInputElement || control instanceof HTMLSelectElement)) return;
      const filters = panel.contents.filter_section.filters;
      const nextState = { ...state };
      for (const filter of filters) {
        const input = form.elements[filter.id];
        if (!input) continue;
        nextState[filter.id] = filter.control === "checkbox" ? input.checked : input.value;
      }
      writePanelUrl(panel.page_id, filters, nextState, { replace: false });
      renderContentPanel(panel, nextState).catch(error => {
        contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
      });
    });
  }

  function selectedIndexEntry(index, selected) {
    const entries = index.entries || [];
    if (selected && selected !== "latest") {
      const match = entries.find(entry => entry.basho === selected);
      if (match) return match;
    }
    return entries.find(entry => entry.basho === index.default_basho) || latestIndexEntry(entries);
  }

  function latestIndexEntry(entries) {
    return [...entries].sort((left, right) => String(right.basho).localeCompare(String(left.basho)))[0];
  }

  function bashoSelectorValues(index) {
    return [...(index.entries || [])]
      .sort((left, right) => String(right.basho).localeCompare(String(left.basho)))
      .map(entry => ({ value: entry.basho, label: entry.label || entry.basho }));
  }

  function renderFilterSection(filterSection, state, index, rowsBySource = {}) {
    return [
      '<form class="filter-section" aria-label="Filters">',
      '<h4>Options</h4>',
      '<ul class="filter-list">',
      ...filterSection.filters.map(filter => `<li>${renderFilter(filter, state, index, rowsBySource)}</li>`),
      '</ul>',
      '</form>'
    ].join("");
  }

  function renderFilter(filter, state, index, rowsBySource = {}) {
    if (filter.control === "checkbox") {
      return [
        '<label class="checkbox-control">',
        `<input type="checkbox" name="${escapeHtml(filter.id)}"${state[filter.id] ? " checked" : ""}>`,
        `<span>${escapeHtml(filter.label)}</span>`,
        '</label>'
      ].join("");
    }
    const values = filter.control === "basho_date_selector"
      ? bashoSelectorValues(index)
      : filter.values_source
      ? dataSelectorValues(filter, state, rowsBySource)
      : filter.values;
    const selected = filter.control === "basho_date_selector"
      ? selectedIndexEntry(index, state[filter.id]).basho
      : state[filter.id];
    return [
      '<label class="filter-control">',
      `<span>${escapeHtml(filter.label)}</span>`,
      `<select name="${escapeHtml(filter.id)}">`,
      ...values.map(value => {
        const selectedAttr = value.value === selected ? " selected" : "";
        return `<option value="${escapeHtml(value.value)}"${selectedAttr}>${escapeHtml(value.label)}</option>`;
      }),
      '</select>',
      '</label>'
    ].join("");
  }

  function dataSelectorValues(filter, state, rowsBySource) {
    const source = filter.values_source;
    const rows = rowsBySource[source.source] || [];
    const partitionValue = source.partition_filter ? state[source.partition_filter] : null;
    const entries = new Map();
    for (const row of rows) {
      if (source.partition_filter) {
        const actual = normalizedSourceValue(row[source.partition_field], source.partition_normalizer);
        if (actual !== partitionValue) continue;
      }
      entries.set(row[source.field], {
        value: row[source.field],
        label: row[source.label_field],
        order: Number(row[source.order_field]),
      });
    }
    return [...entries.values()]
      .sort((left, right) => left.order - right.order)
      .map(({ value, label }) => ({ value, label }));
  }

  function resolveSelectedFilterValueFromSource(filter, state, rowsBySource) {
    const values = filter ? dataSelectorValues(filter, state, rowsBySource) : [];
    return values.some(value => value.value === state[filter.id])
      ? state[filter.id]
      : values[0]?.value || state[filter.id];
  }

  function resolveSelectedDataValue(rows, field, selectedValue, normalizer = null) {
    const values = [...new Set(rows.map(row => normalizedSourceValue(row[field], normalizer)))].filter(Boolean);
    return values.includes(selectedValue) ? selectedValue : values[0] || selectedValue;
  }

  function normalizedSourceValue(value, normalizer) {
    if (normalizer === "division_id") return divisionId(value);
    return value;
  }

  function divisionId(value) {
    return String(value || "").toLowerCase().replace(/\s+/g, "_");
  }

  function renderFinishByChiiChart(artifact, state, filters, rowsBySource) {
    const rows = finishByChiiRows(artifact, state, rowsBySource);
    if (!rows.length) {
      return '<p>No Finish by Chii data matches the selected options.</p>';
    }
    const divisionLabel = filterValueLabel(filters, "division", state.division) || rows[0].division;
    const directionLabel = state.direction === "bottom" ? "Bottom" : "Top";
    const probabilityLabel = state.direction === "bottom"
      ? "No better than nth-worst"
      : "No worse than nth";
    const sampleSize = rows[0].n || "";
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(divisionLabel)} ${escapeHtml(state.chii)}: ${escapeHtml(directionLabel)} finish</h4>`,
      `<div>${escapeHtml(probabilityLabel)} by wins, sample size ${escapeHtml(sampleSize)}</div>`,
      '</div>',
      '<div id="finish-by-chii-chart" class="plotly-chart"></div>'
    ].join("");
  }

  function renderFinishByChiiPlot(artifact, state, rowsBySource) {
    const host = document.getElementById("finish-by-chii-chart");
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    const rows = finishByChiiRows(artifact, state, rowsBySource);
    const probabilityField = state.direction === "bottom"
      ? "p_no_better_than_mth_worst"
      : "p_no_worse_than_n";
    const trace = {
      type: "bar",
      x: rows.map(row => Number(row.threshold)),
      y: rows.map(row => 100 * (Number(row[probabilityField]) || 0)),
      marker: {
        color: "rgba(143, 181, 255, 0.88)",
        line: {
          color: "rgba(220, 232, 255, 0.95)",
          width: 1,
        },
      },
      hovertemplate: "Threshold %{x}<br>Probability %{y:.1f}%<extra></extra>",
    };
    const layout = {
      autosize: true,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 64, r: 26, t: 18, b: 58 },
      xaxis: {
        title: state.direction === "top" ? "No worse than n" : "No better than nth-worst",
        tickmode: "linear",
        dtick: 1,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: "Probability",
        range: [0, 100],
        ticksuffix: "%",
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
    Plotly.react(host, [trace], layout, { responsive: true, displaylogo: false });
  }

  function finishByChiiRows(artifact, state, rowsBySource) {
    const sourceId = state.direction === "bottom" ? "bottom_thresholds" : "top_thresholds";
    return [...(rowsBySource[sourceId] || [])]
      .filter(row => divisionId(row.division) === state.division && row.chii === state.chii)
      .sort((left, right) => Number(left.threshold) - Number(right.threshold));
  }

  function renderIndexedTable(artifact, rows, state) {
    const groups = new Map(artifact.column_groups.map(group => [group.id, group]));
    const visibleColumns = artifact.columns.filter(column => isColumnVisible(column, groups, state));
    return [
      '<table class="artifact-table brb-table">',
      '<thead><tr>',
      ...visibleColumns.map(column => `<th ${tableCellAttributes(column)}>${escapeHtml(column.heading)}</th>`),
      '</tr></thead>',
      '<tbody>',
      ...rows.map((row, index) => [
        '<tr>',
        ...visibleColumns.map(column => `<td ${tableCellAttributes(column)}>${escapeHtml(cellValue(column, row, index))}</td>`),
        '</tr>'
      ].join("")),
      '</tbody>',
      '</table>'
    ].join("");
  }

  function renderBanzukeChangesTable(artifact, rows, state, config) {
    const title = config.title || artifact.heading;
    const table = state.banzuke_style
      ? renderBanzukeStyleTable(rows, state)
      : renderBanzukeScanTable(rows, state);
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(title)}</h4>`,
      '</div>',
      table,
    ].join("");
  }

  function renderBanzukeStyleTable(rows, state) {
    const eastColumns = banzukeSideColumns("east", state);
    const westColumns = banzukeSideColumns("west", state);
    return [
      '<table class="artifact-table banzuke-changes-table">',
      '<thead>',
      '<tr>',
      `<th colspan="${eastColumns.length}">East</th>`,
      '<th rowspan="2">Rank</th>',
      `<th colspan="${westColumns.length}">West</th>`,
      '</tr>',
      '<tr>',
      ...eastColumns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
      ...westColumns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
      '</tr>',
      '</thead>',
      '<tbody>',
      ...rows.map(row => [
        '<tr>',
        ...eastColumns.map(column => renderBanzukeSideCell(row, column)),
        `<th scope="row">${escapeHtml(row.bz_chii)}</th>`,
        ...westColumns.map(column => renderBanzukeSideCell(row, column)),
        '</tr>',
      ].join("")),
      '</tbody>',
      '</table>',
    ].join("");
  }

  function renderBanzukeScanTable(rows, state) {
    const columns = banzukeScanColumns(state);
    const sideRows = rows.flatMap(row => ["east", "west"].map(side => ({ row, side })))
      .filter(item => item.row[`${item.side}_rikishi_id`]);
    return [
      '<table class="artifact-table banzuke-changes-table">',
      '<thead>',
      '<tr>',
      ...columns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
      '</tr>',
      '</thead>',
      '<tbody>',
      ...sideRows.map(({ row, side }) => [
        '<tr>',
        ...columns.map(column => renderBanzukeScanCell(row, side, column)),
        '</tr>',
      ].join("")),
      '</tbody>',
      '</table>',
    ].join("");
  }

  function banzukeSideColumns(side, state) {
    const identity = { id: "shikona", heading: "Shikona", side };
    const columns = [];
    if (state.equelo) columns.push({ id: "equelo", heading: "Equelo", side });
    if (state.context) {
      columns.push({ id: "old_chii", heading: "Previous Chii", side });
      columns.push({ id: "result", heading: "Result", side });
    }
    if (state.delta) columns.push({ id: "delta", heading: "Delta", side });
    if (side === "east") return [...columns, identity];
    return [identity, ...columns.reverse()];
  }

  function banzukeScanColumns(state) {
    const columns = [
      { id: "chii", heading: "Chii" },
      { id: "shikona", heading: "Shikona" },
    ];
    if (state.context) {
      columns.push({ id: "old_chii", heading: "Previous Chii" });
      columns.push({ id: "result", heading: "Result" });
    }
    if (state.delta) columns.push({ id: "delta", heading: "Delta" });
    if (state.equelo) columns.push({ id: "equelo", heading: "Equelo" });
    return columns;
  }

  function renderBanzukeSideCell(row, column) {
    const rikishiId = row[`${column.side}_rikishi_id`];
    const attributes = banzukeCellAttributes(column.id);
    if (!rikishiId) return `<td${attributes}></td>`;
    return `<td${attributes}>${banzukeSideValue(row, column.side, column.id)}</td>`;
  }

  function renderBanzukeScanCell(row, side, column) {
    return `<td${banzukeCellAttributes(column.id)}>${banzukeSideValue(row, side, column.id)}</td>`;
  }

  function banzukeCellAttributes(columnId) {
    return columnId === "shikona" ? ' data-column-id="shikona"' : "";
  }

  function banzukeSideValue(row, side, columnId) {
    if (columnId === "chii") return escapeHtml(row[`${side}_chii`]);
    if (columnId === "shikona") {
      return renderRikishiLink(
        row[`${side}_shikona`],
        row[`${side}_rikishi_id`],
      );
    }
    if (columnId === "result") {
      const result = row[`${side}_result`];
      const movement = row[`${side}_result_movement`];
      return escapeHtml([result, movement].filter(Boolean).join(" "));
    }
    return escapeHtml(row[`${side}_${columnId}`]);
  }

  function renderRikishiLink(shikona, rikishiId) {
    if (!rikishiId) return "";
    return [
      `<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}"`,
      ' target="_blank" rel="noopener">',
      escapeHtml(shikona),
      '</a>',
    ].join("");
  }

  function renderStandingsTable(artifact, rows, filteredRows, state) {
    const visibleColumns = standingsVisibleColumns(artifact, state);
    const meanPositions = competitionPositions(filteredRows, "selected_average_credited_wins");
    const percentPositions = competitionPositions(filteredRows, "win_percent");
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      '</div>',
      '<table class="artifact-table standings-table">',
      renderStandingsTableHead(artifact, visibleColumns),
      '<tbody>',
      ...rows.map((row, index) => [
        '<tr>',
        ...visibleColumns.map(column =>
          `<td ${tableCellAttributes(column)}>${standingsCellValue(column, row, index, meanPositions, percentPositions)}</td>`
        ),
        '</tr>',
      ].join("")),
      '</tbody>',
      '</table>',
    ].join("");
  }

  function standingsVisibleColumns(artifact, state) {
    const visibleGroups = standingsVisibleGroups(state);
    return artifact.columns.filter(column =>
      column.always_visible || visibleGroups.includes(column.group)
    );
  }

  function standingsVisibleGroups(state) {
    if (state.metric_group_preset === "percentages") return ["identity", "wins_per_bout"];
    if (state.metric_group_preset === "combined") return ["identity", "wins_per_basho", "wins_per_bout"];
    return ["identity", "wins_per_basho"];
  }

  function renderStandingsTableHead(artifact, visibleColumns) {
    const groups = artifact.column_groups.filter(group =>
      visibleColumns.some(column => column.group === group.id)
    );
    return [
      '<thead>',
      '<tr>',
      ...groups.map(group => {
        const count = visibleColumns.filter(column => column.group === group.id).length;
        return `<th colspan="${count}">${escapeHtml(group.heading)}</th>`;
      }),
      '</tr>',
      '<tr>',
      ...visibleColumns.map(column => `<th ${tableCellAttributes(column)}>${escapeHtml(column.heading)}</th>`),
      '</tr>',
      '</thead>',
    ].join("");
  }

  function standingsCellValue(column, row, index, meanPositions, percentPositions) {
    if (column.id === "row_number") return String(index + 1);
    if (column.id === "shikona") return renderRikishiLink(row.shikona, row.rikishi_id);
    if (column.id === "selected_average_credited_wins") return decimal(row.selected_average_credited_wins, 2);
    if (column.id === "selected_average_rank") return String(meanPositions.get(String(row.rikishi_id)));
    if (column.id === "win_percent") return decimal(row.win_percent, 1);
    if (column.id === "win_percent_rank") return String(percentPositions.get(String(row.rikishi_id)));
    return escapeHtml(cellValue(column, row, index));
  }

  function standingsRowsForState(rows, state) {
    return rows.filter(row =>
      (state.division === "all" || standingsDivisionMatches(row.chii_ordinal, state.division)) &&
      (!state.current_only || row.is_current === "1")
    );
  }

  function standingsDivisionMatches(chiiOrdinal, division) {
    const level = Math.floor(Number(chiiOrdinal) / 100000);
    if (division === "makuuchi") return level >= 0 && level <= 4;
    if (division === "juryo") return level === 5;
    if (division === "makushita") return level === 6;
    if (division === "sandanme") return level === 7;
    if (division === "jonidan") return level === 8;
    if (division === "jonokuchi") return level === 9;
    return true;
  }

  function sortedStandingsRows(rows, state) {
    const sortField = state.metric_group_preset === "standard"
      ? "selected_average_credited_wins"
      : "win_percent";
    return [...rows].sort((left, right) => compareValues(right[sortField], left[sortField]));
  }

  function competitionPositions(rows, field) {
    const ordered = [...rows].sort((left, right) => compareValues(right[field], left[field]));
    const positions = new Map();
    let previousValue = null;
    let previousPosition = 0;
    for (const [index, row] of ordered.entries()) {
      const value = row[field];
      const position = index > 0 && compareValues(value, previousValue) === 0
        ? previousPosition
        : index + 1;
      previousValue = value;
      previousPosition = position;
      positions.set(String(row.rikishi_id), position);
    }
    return positions;
  }

  function decimal(value, places) {
    return Number(value).toFixed(places);
  }

  function compareValues(left, right) {
    const leftNumber = Number(left);
    const rightNumber = Number(right);
    if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
      return leftNumber - rightNumber;
    }
    return String(left).localeCompare(String(right));
  }

  function tableCellAttributes(column) {
    return `data-column-id="${escapeHtml(column.id)}"`;
  }

  function renderNotes(artifact, state) {
    const notes = (artifact.notes || []).filter(note => noteApplies(note, state));
    if (!notes.length) return "";
    return [
      '<aside class="notes-panel">',
      '<h4>Notes</h4>',
      '<ol>',
      ...notes.map(note => `<li>${escapeHtml(note.text)}</li>`),
      '</ol>',
      '</aside>'
    ].join("");
  }

  function noteApplies(note, state) {
    const applies = note.applies_to || ["all"];
    if (applies.includes("all")) return true;
    if (applies.includes("previous_basho")) return Boolean(state.previous_context);
    if (applies.includes("rating_context")) return Boolean(state.rating_context);
    if (applies.includes("nu_chii")) return Boolean(state.nu_chii);
    if (applies.includes("context")) return Boolean(state.context);
    if (applies.includes("delta")) return Boolean(state.delta);
    if (applies.includes("equelo")) return Boolean(state.equelo);
    if (applies.includes(state.metric_group_preset)) return true;
    return false;
  }

  function isColumnVisible(column, groups, state) {
    if (column.always_visible) return true;
    const group = groups.get(column.group);
    if (!group) return false;
    if (group.always_visible) {
      if (column.id === "equelo" || column.id === "delta_equelo") return Boolean(state.rating_context);
      if (column.id === "nu_chii") return Boolean(state.nu_chii);
      return true;
    }
    if (group.controlling_filter_id) return Boolean(state[group.controlling_filter_id]);
    return false;
  }

  function cellValue(column, row, index) {
    if (column.id === "row_number") return String(index + 1);
    return row[column.source_field || column.id] || "";
  }

  async function fetchJson(path) {
    const response = await fetch(cacheBustedUrl(path));
    if (!response.ok) throw new Error(`Could not load ${path}`);
    return response.json();
  }

  async function fetchCsv(path) {
    const response = await fetch(cacheBustedUrl(path));
    if (!response.ok) throw new Error(`Could not load ${path}`);
    return parseCsv(await response.text());
  }

  function cacheBustedUrl(path) {
    if (document.body.dataset.cacheMode !== "dev" || !document.body.dataset.cacheBust) {
      return path;
    }
    const url = new URL(path, window.location.href);
    url.searchParams.set(document.body.dataset.cacheBustParam || "cb", document.body.dataset.cacheBust);
    return url.toString();
  }

  function parseCsv(text) {
    const rows = csvRows(text.trim());
    const headers = rows.shift() || [];
    return rows.map(row => Object.fromEntries(headers.map((header, index) => [header, row[index] || ""])));
  }

  function csvRows(text) {
    const rows = [];
    let row = [];
    let field = "";
    let quoted = false;
    for (let index = 0; index < text.length; index += 1) {
      const char = text[index];
      const next = text[index + 1];
      if (quoted && char === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = !quoted;
      } else if (!quoted && char === ",") {
        row.push(field);
        field = "";
      } else if (!quoted && (char === "\n" || char === "\r")) {
        if (char === "\r" && next === "\n") index += 1;
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
      } else {
        field += char;
      }
    }
    row.push(field);
    rows.push(row);
    return rows;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
}());
