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
    selectPage(pageId);
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
    const panel = runtimeManifest.ui.content_panels.find(candidate => candidate.page_id === pageId);
    if (!panel) {
      window.alert(
        `The requested page "${pageId}" is not available in this site build. Showing the home page instead.`
      );
      markActivePage("");
      writePageUrl("", { replace: true });
      renderLandingPanel();
      return;
    }
    markActivePage(pageId);
    if (pushUrl || replaceUrl) {
      writePageUrl(pageId, { replace: replaceUrl });
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
    const params = new URLSearchParams();
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
    const params = new URLSearchParams();
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
    if (artifact.kind === "sectioned_table") {
      await renderSectionedTableContentPanel(panel, artifact);
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

  async function renderSectionedTableContentPanel(panel, artifact) {
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    const rows = rowsBySource[artifact.primary_source] || [];

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body content-body-no-filters">',
      '<div class="pa-slot">',
      renderSectionedTable(artifact, rows),
      '</div>',
      '</div>',
      renderNotes(artifact, {}),
      '</section>'
    ].join("");
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
    if (artifact.renderer === "stacked_bar_chart") {
      await renderStackedBarChartContentPanel(panel, artifact);
      return;
    }
    if (artifact.renderer === "grouped_line_chart") {
      await renderGroupedLineChartContentPanel(panel, artifact);
      return;
    }
    if (artifact.renderer === "ordered_bar_chart") {
      await renderOrderedBarChartContentPanel(panel, artifact);
      return;
    }
    if (artifact.renderer === "category_bar_chart") {
      await renderCategoryBarChartContentPanel(panel, artifact);
      return;
    }
    if (artifact.renderer === "finish_by_chii_chart") {
      await renderFinishByChiiContentPanel(panel, artifact, overrideState);
      return;
    }
    if (artifact.renderer === "standing_win_probability_chart") {
      await renderStandingWinProbabilityContentPanel(panel, artifact, overrideState);
      return;
    }
    if (artifact.renderer === "career_length") {
      await renderCareerLengthContentPanel(panel, artifact, overrideState);
      return;
    }
    throw new Error(`Unsupported chart renderer: ${artifact.renderer}`);
  }

  async function renderStandingWinProbabilityContentPanel(panel, artifact, overrideState = null) {
    const filters = panel.contents.filter_section.filters;
    const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
    state.source = resolveSelectedDataSourceId(artifact, state.source);
    state.division = resolveFilterValue(filters, "division", state.division);
    writePanelUrl(panel.page_id, filters, state, { replace: true });
    const rowsBySource = await fetchArtifactCsvSet(artifact);

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body">',
      renderFilterSection(panel.contents.filter_section, state),
      '<div class="pa-slot">',
      renderStandingWinProbabilityChart(artifact, state, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, state),
      '</section>'
    ].join("");
    renderStandingWinProbabilityPlot(artifact, state, rowsBySource);
    wireFilterSection(panel, state);
  }

  async function renderCareerLengthContentPanel(panel, artifact, overrideState = null) {
    const filters = panel.contents.filter_section.filters;
    const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    state.view = resolveCareerLengthView(artifact, state.view);
    writePanelUrl(panel.page_id, filters, state, { replace: true });

    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body">',
      renderFilterSection(panel.contents.filter_section, state),
      '<div class="pa-slot">',
      renderCareerLengthArtifact(artifact, state, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, state),
      '</section>'
    ].join("");
    renderCareerLengthPlot(artifact, state, rowsBySource);
    wireFilterSection(panel, state);
  }

  async function renderFinishByChiiContentPanel(panel, artifact, overrideState = null) {
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

  async function renderStackedBarChartContentPanel(panel, artifact) {
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body content-body-no-filters">',
      '<div class="pa-slot">',
      renderStackedBarChart(artifact, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, {}),
      '</section>'
    ].join("");
    renderStackedBarPlot(artifact, rowsBySource);
  }

  async function renderGroupedLineChartContentPanel(panel, artifact) {
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body content-body-no-filters">',
      '<div class="pa-slot">',
      renderGroupedLineChart(artifact, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, {}),
      '</section>'
    ].join("");
    renderGroupedLinePlot(artifact, rowsBySource);
  }

  async function renderOrderedBarChartContentPanel(panel, artifact) {
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body content-body-no-filters">',
      '<div class="pa-slot">',
      renderOrderedBarChart(artifact, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, {}),
      '</section>'
    ].join("");
    renderOrderedBarPlot(artifact, rowsBySource);
  }

  async function renderCategoryBarChartContentPanel(panel, artifact) {
    const rowsBySource = await fetchArtifactCsvSet(artifact);
    contentPanel.innerHTML = [
      '<section class="content-panel">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
      '<div class="content-body content-body-no-filters">',
      '<div class="pa-slot">',
      renderCategoryBarChart(artifact, rowsBySource),
      '</div>',
      '</div>',
      renderNotes(artifact, {}),
      '</section>'
    ].join("");
    renderCategoryBarPlot(artifact, rowsBySource);
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
    if (value === null || value === undefined || value === "") return filter.default;
    if (
      filter.values &&
      filter.values.length &&
      !filter.values.some(candidate => String(candidate.value) === String(value))
    ) {
      return filter.default;
    }
    return value;
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
      String(source.filter_value) === String(state[artifact.selector_filter_id])
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
    if (!filterSection.filters.length) return "";
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
    const values = filterValues(filter, state, index, rowsBySource);
    const selected = selectedFilterValue(filter, state, index);
    if (values.length <= 7) {
      return renderRadioChoice(filter, values, selected);
    }
    return renderDropdownChoice(filter, values, selected);
  }

  function filterValues(filter, state, index, rowsBySource) {
    if (filter.id === "basho_date" && index) return bashoSelectorValues(index);
    if (filter.values_source) return dataSelectorValues(filter, state, rowsBySource);
    return filter.values;
  }

  function selectedFilterValue(filter, state, index) {
    if (filter.id === "basho_date" && index) {
      return selectedIndexEntry(index, state[filter.id]).basho;
    }
    return state[filter.id];
  }

  function renderRadioChoice(filter, values, selected) {
    return [
      `<div class="choice-control" role="group" aria-label="${escapeHtml(filter.label)}">`,
      `<span class="choice-label">${escapeHtml(filter.label)}</span>`,
      '<ul class="choice-list">',
      ...values.map(value => [
        '<li>',
        '<label class="radio-control">',
        `<input type="radio" name="${escapeHtml(filter.id)}" value="${escapeHtml(value.value)}"${value.value === selected ? " checked" : ""}>`,
        `<span>${escapeHtml(value.label)}</span>`,
        '</label>',
        '</li>',
      ].join("")),
      '</ul>',
      '</div>'
    ].join("");
  }

  function renderDropdownChoice(filter, values, selected) {
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

  function renderStackedBarChart(artifact, rowsBySource) {
    const rows = stackedBarRows(artifact, rowsBySource);
    if (!rows.length) {
      return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
    }
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      '</div>',
      `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
    ].join("");
  }

  function renderGroupedLineChart(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    if (!rows.length) {
      return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
    }
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      '</div>',
      `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
    ].join("");
  }

  function renderOrderedBarChart(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    if (!rows.length) {
      return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
    }
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      '</div>',
      `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
    ].join("");
  }

  function renderCategoryBarChart(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    if (!rows.length) {
      return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
    }
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      '</div>',
      `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
    ].join("");
  }

  function renderCareerLengthArtifact(artifact, state, rowsBySource) {
    const view = careerLengthView(artifact, state.view);
    if (view.kind === "table") {
      return renderCareerLengthTable(view, rowsBySource[state.view] || []);
    }
    const rows = rowsBySource[state.view] || [];
    if (!rows.length) {
      return `<p>No ${escapeHtml(view.label)} data is available.</p>`;
    }
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(view.label)}</h4>`,
      '</div>',
      '<div id="career-length-chart" class="plotly-chart"></div>',
    ].join("");
  }

  function renderStandingWinProbabilityChart(artifact, state, rowsBySource) {
    const source = selectedStandingSource(artifact, state);
    const rows = rowsBySource[source.id] || [];
    if (!rows.length) {
      return `<p>No ${escapeHtml(source.label)} data is available.</p>`;
    }
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      `<div>${escapeHtml(source.label)} source</div>`,
      '</div>',
      '<div id="standing-win-probability-chart" class="plotly-chart"></div>',
    ].join("");
  }

  function renderStandingWinProbabilityPlot(artifact, state, rowsBySource) {
    const host = document.getElementById("standing-win-probability-chart");
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    const source = selectedStandingSource(artifact, state);
    const rows = rowsBySource[source.id] || [];
    const traces = standingWinProbabilityTraces(artifact, state, source, rows);
    Plotly.react(
      host,
      traces,
      standingWinProbabilityLayout(artifact, traces),
      { responsive: true, displaylogo: false }
    ).then(() => {
      if (!host.on) return;
      host.on("plotly_legenddoubleclick", event => {
        const target = host.data[event.curveNumber];
        if (!target) return false;
        const visibility = host.data.map((trace, index) => {
          if (trace.meta?.division !== target.meta?.division) return false;
          return index === event.curveNumber ? true : "legendonly";
        });
        Plotly.restyle(host, { visible: visibility });
        return false;
      });
    });
  }

  function standingWinProbabilityTraces(artifact, state, source, rows) {
    const trace = artifact.traces[0];
    return standingWinProbabilityGroups(artifact, state, rows, trace)
      .map(group => standingWinProbabilityTrace(artifact, state, source, group, trace));
  }

  function standingWinProbabilityGroups(artifact, state, rows, trace) {
    const groups = new Map();
    for (const row of rows) {
      if (!displayStandingChii(artifact, row.selected_chii)) continue;
      if (!displayStandingChii(artifact, row.opponent_chii)) continue;
      const division = divisionForStandingChii(row.selected_chii);
      if (state.division !== "All" && division !== state.division) continue;
      if (!groups.has(row[trace.group_by])) groups.set(row[trace.group_by], []);
      groups.get(row[trace.group_by]).push(row);
    }
    const selectedOrderField = artifact.provenance.selected_order_field;
    const xOrderField = artifact.provenance.x_order_field;
    return [...groups.entries()]
      .map(([key, groupRows]) => ({
        key,
        division: divisionForStandingChii(key),
        order: Number(groupRows[0]?.[selectedOrderField]) || 0,
        rows: groupRows.sort((left, right) =>
          compareValues(Number(left[xOrderField]) || 0, Number(right[xOrderField]) || 0)
        ),
      }))
      .sort((left, right) => left.order - right.order);
  }

  function standingWinProbabilityTrace(artifact, state, source, group, trace) {
    const errorFields = trace.error_y || [];
    const showErrorBars = Boolean(state.error_bars) && errorFields.length === 2;
    const plotlyTrace = {
      type: "scatter",
      mode: "lines+markers",
      name: group.key,
      x: group.rows.map(row => row[trace.x]),
      y: group.rows.map(row => Number(row[trace.y])),
      visible: standingTraceVisible(artifact, group),
      meta: { division: group.division },
      customdata: group.rows.map(row => standingWinProbabilityCustomData(source, row)),
      hovertemplate: standingWinProbabilityHoverTemplate(source),
    };
    if (showErrorBars) {
      const lower = errorFields[0];
      const upper = errorFields[1];
      const array = group.rows.map(row => {
        const high = Number(row[upper]);
        const value = Number(row[trace.y]);
        return Number.isFinite(high) && Number.isFinite(value) ? high - value : 0;
      });
      const arrayminus = group.rows.map(row => {
        const low = Number(row[lower]);
        const value = Number(row[trace.y]);
        return Number.isFinite(low) && Number.isFinite(value) ? value - low : 0;
      });
      if (array.some(value => value > 0) || arrayminus.some(value => value > 0)) {
        plotlyTrace.error_y = {
          type: "data",
          symmetric: false,
          array,
          arrayminus,
          visible: true,
          color: "#d7e0ef",
          thickness: 2,
          width: 4,
        };
      }
    }
    return plotlyTrace;
  }

  function standingWinProbabilityCustomData(source, row) {
    if (source.id === "observed") {
      return [
        row.selected_chii,
        row.opponent_chii,
        Number(row.opponent_ordinal),
        Number(row.n_obs),
        Number(row.n_selected_wins),
        Number(row.ci95_lower),
        Number(row.ci95_upper),
      ];
    }
    return [
      row.selected_chii,
      row.opponent_chii,
      Number(row.opponent_ordinal),
      Number(row.selected_rating),
      Number(row.opponent_rating),
    ];
  }

  function standingWinProbabilityHoverTemplate(source) {
    if (source.id === "observed") {
      return [
        "Selected=%{customdata[0]}",
        "Opponent=%{customdata[1]}",
        "P(selected wins)=%{y:.3f}",
        "CI95=[%{customdata[5]:.3f}, %{customdata[6]:.3f}]",
        "Wins=%{customdata[4]:,} / %{customdata[3]:,}",
        "<extra></extra>",
      ].join("<br>");
    }
    return [
      "Selected=%{customdata[0]}",
      "Opponent=%{customdata[1]}",
      "P(selected wins)=%{y:.3f}",
      "Selected rating=%{customdata[3]:.1f}",
      "Opponent rating=%{customdata[4]:.1f}",
      "<extra></extra>",
    ].join("<br>");
  }

  function standingTraceVisible(artifact, group) {
    const preferred = artifact.provenance.default_display_trace || "";
    if (group.key === preferred) return true;
    return "legendonly";
  }

  function renderCareerLengthTable(view, rows) {
    const columns = view.columns || [];
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(view.label)}</h4>`,
      '</div>',
      '<table class="artifact-table">',
      '<thead><tr>',
      ...columns.map(column => `<th data-column-id="${escapeHtml(column.id)}">${escapeHtml(column.heading)}</th>`),
      '</tr></thead>',
      '<tbody>',
      ...rows.map((row, index) => [
        '<tr>',
        ...columns.map(column =>
          `<td data-column-id="${escapeHtml(column.id)}">${careerLengthCellValue(column, row, index)}</td>`
        ),
        '</tr>'
      ].join("")),
      '</tbody>',
      '</table>',
    ].join("");
  }

  function renderSectionedTable(artifact, rows) {
    return [
      '<div class="artifact-title-block">',
      `<h4>${escapeHtml(artifact.heading)}</h4>`,
      '</div>',
      '<div class="sectioned-table-grid">',
      ...artifact.sections.map(section =>
        renderTableSection(section, rows, artifact.columns || [])
      ),
      '</div>',
    ].join("");
  }

  function renderTableSection(section, rows, columns) {
    const sectionRows = [...rows]
      .filter(row => String(row[section.source_field]) === String(section.source_value))
      .sort((left, right) =>
        compareValues(Number(left[section.order_by]) || 0, Number(right[section.order_by]) || 0)
      );
    return [
      '<section class="table-section">',
      `<h5>${escapeHtml(section.heading)}</h5>`,
      '<table class="artifact-table sectioned-table">',
      '<thead><tr>',
      ...columns.map(column => `<th ${tableCellAttributes(column)}>${escapeHtml(column.heading)}</th>`),
      '</tr></thead>',
      '<tbody>',
      ...sectionRows.map((row, index) => [
        '<tr>',
        ...columns.map(column =>
          `<td ${tableCellAttributes(column)}>${escapeHtml(cellValue(column, row, index))}</td>`
        ),
        '</tr>'
      ].join("")),
      '</tbody>',
      '</table>',
      '</section>',
    ].join("");
  }

  function renderCareerLengthPlot(artifact, state, rowsBySource) {
    const view = careerLengthView(artifact, state.view);
    if (view.kind === "table") return;
    const host = document.getElementById("career-length-chart");
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    Plotly.react(
      host,
      careerLengthTraces(view, rowsBySource[state.view] || []),
      careerLengthLayout(view),
      { responsive: true, displaylogo: false }
    );
  }

  function careerLengthTraces(view, rows) {
    if (view.kind === "stacked_bar") {
      return view.y.map((field, index) => ({
        type: "bar",
        name: view.series_labels[index] || field,
        x: rows.map(row => row[view.x]),
        y: rows.map(row => Number(row[field]) || 0),
        hovertemplate: `${escapeHtml(view.x)}=%{x}<br>${escapeHtml(field)}=%{y}<extra></extra>`,
      }));
    }
    return [{
      type: "scatter",
      mode: "lines+markers",
      name: view.label,
      x: rows.map(row => row[view.x]),
      y: rows.map(row => Number(row[view.y]) || 0),
      hovertemplate: `${escapeHtml(view.x)}=%{x}<br>${escapeHtml(view.y)}=%{y}<extra></extra>`,
    }];
  }

  function renderCategoryBarPlot(artifact, rowsBySource) {
    const host = document.getElementById(chartElementId(artifact));
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    const trace = categoryBarTrace(artifact, rowsBySource);
    Plotly.react(
      host,
      [trace],
      categoryBarLayout(artifact, trace),
      { responsive: true, displaylogo: false }
    );
  }

  function renderOrderedBarPlot(artifact, rowsBySource) {
    const host = document.getElementById(chartElementId(artifact));
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    const trace = orderedBarTrace(artifact, rowsBySource);
    Plotly.react(
      host,
      [trace],
      orderedBarLayout(artifact, trace),
      { responsive: true, displaylogo: false }
    );
  }

  function renderGroupedLinePlot(artifact, rowsBySource) {
    const host = document.getElementById(chartElementId(artifact));
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    Plotly.react(
      host,
      groupedLineTraces(artifact, rowsBySource),
      groupedChartLayout(artifact, rowsBySource),
      { responsive: true, displaylogo: false }
    );
  }

  function renderStackedBarPlot(artifact, rowsBySource) {
    const host = document.getElementById(chartElementId(artifact));
    if (!host) return;
    if (!window.Plotly) {
      host.innerHTML = "<p>Plotly is not available.</p>";
      return;
    }
    Plotly.react(
      host,
      stackedBarTraces(artifact, rowsBySource),
      stackedBarLayout(artifact, rowsBySource),
      { responsive: true, displaylogo: false }
    );
  }

  function stackedBarRows(artifact, rowsBySource) {
    return chartRows(artifact, rowsBySource);
  }

  function chartRows(artifact, rowsBySource) {
    const sourceId = artifact.data_binding.sources[0];
    return rowsBySource[sourceId] || [];
  }

  function stackedBarTraceSpec(artifact) {
    const trace = artifact.traces.find(candidate => candidate.kind === "stacked_bar");
    if (!trace) throw new Error(`No stacked_bar trace for ${artifact.id}`);
    return trace;
  }

  function groupedLineTraceSpec(artifact) {
    const trace = artifact.traces.find(candidate => candidate.kind === "scatter");
    if (!trace) throw new Error(`No scatter trace for ${artifact.id}`);
    return trace;
  }

  function orderedBarTraceSpec(artifact) {
    const trace = artifact.traces.find(candidate => candidate.kind === "bar");
    if (!trace) throw new Error(`No bar trace for ${artifact.id}`);
    return trace;
  }

  function stackedBarTraces(artifact, rowsBySource) {
    const rows = stackedBarRows(artifact, rowsBySource);
    const trace = stackedBarTraceSpec(artifact);
    const groups = stackedBarGroupOrder(artifact, rows, trace);
    const colours = artifact.provenance.group_colours || {};
    return groups.map(group => {
      const groupRows = rows.filter(row => row[trace.group_by] === group);
      const plotlyTrace = {
        type: "bar",
        name: group,
        x: groupRows.map(row => row[trace.x]),
        y: groupRows.map(row => Number(row[trace.y])),
        hovertemplate: `${escapeHtml(trace.group_by)}=%{fullData.name}<br>${escapeHtml(trace.x)}=%{x}<br>${escapeHtml(trace.y)}=%{y}<extra></extra>`,
      };
      if (colours[group]) {
        plotlyTrace.marker = { color: colours[group] };
      }
      return plotlyTrace;
    });
  }

  function groupedLineTraces(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    const trace = groupedLineTraceSpec(artifact);
    const groups = chartGroupOrder(artifact, rows, trace);
    const defaultVisible = artifact.provenance.default_visible || [];
    return groups.map(group => {
      const groupRows = rows.filter(row => row[trace.group_by] === group);
      return {
        type: "scatter",
        mode: "lines",
        name: group,
        x: groupRows.map(row => row[trace.x]),
        y: groupRows.map(row => Number(row[trace.y])),
        visible: defaultVisible.length && !defaultVisible.includes(group) ? "legendonly" : true,
        hovertemplate: groupedLineHoverTemplate(trace, artifact.provenance.hover_fields || []),
        customdata: groupRows.map(row =>
          (artifact.provenance.hover_fields || []).map(field => row[field])
        ),
      };
    });
  }

  function orderedBarTrace(artifact, rowsBySource) {
    const rows = orderedRows(artifact, rowsBySource);
    const trace = orderedBarTraceSpec(artifact);
    const dateFields = artifact.provenance.date_fields || [];
    return {
      type: "bar",
      x: rows.map(row => row[trace.x]),
      y: rows.map(row => Number(row[trace.y])),
      customdata: rows.map(row => [
        row[artifact.provenance.order_field],
        ...dateFields.map(field => row[field]),
      ]),
      hovertemplate: orderedBarHoverTemplate(trace, artifact),
    };
  }

  function categoryBarTrace(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    const trace = orderedBarTraceSpec(artifact);
    const rowByCategory = new Map(rows.map(row => [row[trace.x], row]));
    const categories = artifact.x_axis.order_values.length
      ? artifact.x_axis.order_values
      : rows.map(row => row[trace.x]);
    return {
      type: "bar",
      name: trace.label,
      x: categories,
      y: categories.map(category => Number(rowByCategory.get(category)?.[trace.y] || 0)),
      hovertemplate: `${escapeHtml(trace.x)}=%{x}<br>${escapeHtml(trace.y)}=%{y}<extra></extra>`,
    };
  }

  function orderedRows(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    const orderField = artifact.provenance.order_field;
    if (!orderField) return rows;
    return [...rows].sort((left, right) => Number(left[orderField]) - Number(right[orderField]));
  }

  function orderedBarHoverTemplate(trace, artifact) {
    const orderField = artifact.provenance.order_field;
    const dateFields = artifact.provenance.date_fields || [];
    const lines = [
      `${escapeHtml(trace.x)}=%{x}`,
    ];
    if (orderField) {
      lines.push(`${escapeHtml(orderField)}=%{customdata[0]}`);
    }
    if (dateFields.length === 2) {
      lines.push(`${escapeHtml(trace.y)}=%{customdata[1]}/%{customdata[2]}`);
    } else {
      lines.push(`${escapeHtml(trace.y)}=%{y}`);
    }
    lines.push("<extra></extra>");
    return lines.join("<br>");
  }

  function groupedLineHoverTemplate(trace, hoverFields) {
    return [
      `${escapeHtml(trace.group_by)}=%{fullData.name}`,
      `${escapeHtml(trace.x)}=%{x}`,
      `${escapeHtml(trace.y)}=%{y:.3f}`,
      ...hoverFields.map((field, index) => `${escapeHtml(field)}=%{customdata[${index}]}`),
      "<extra></extra>",
    ].join("<br>");
  }

  function stackedBarGroupOrder(artifact, rows, trace) {
    const order = artifact.provenance.stack_order || artifact.provenance.group_order || [];
    if (order.length) return order;
    return [...new Set(rows.map(row => row[trace.group_by]))];
  }

  function chartGroupOrder(artifact, rows, trace) {
    const order = artifact.provenance.group_order || [];
    if (order.length) return order;
    return [...new Set(rows.map(row => row[trace.group_by]))];
  }

  function stackedBarLayout(artifact, rowsBySource) {
    const rows = stackedBarRows(artifact, rowsBySource);
    const trace = stackedBarTraceSpec(artifact);
    const xValues = artifact.x_axis.order_values.length
      ? artifact.x_axis.order_values
      : [...new Set(rows.map(row => row[trace.x]))];
    return {
      autosize: true,
      barmode: "stack",
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 76, r: 150, t: 18, b: 90 },
      xaxis: {
        title: artifact.x_axis.label,
        type: "category",
        categoryorder: "array",
        categoryarray: xValues,
        tickangle: artifact.provenance.x_tickangle || 0,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.18)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: artifact.y_axis.label,
        rangemode: artifact.y_axis.minimum === 0 ? "tozero" : "normal",
        range: axisRange(artifact.y_axis),
        tickformat: artifact.y_axis.tickformat || undefined,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      hovermode: "closest",
      legend: {
        title: { text: artifact.provenance.legend_title || "" },
        orientation: "v",
        yanchor: "top",
        y: 1,
        xanchor: "left",
        x: 1.02,
      },
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
  }

  function groupedChartLayout(artifact, rowsBySource) {
    const rows = chartRows(artifact, rowsBySource);
    const trace = groupedLineTraceSpec(artifact);
    const xValues = artifact.x_axis.order_values.length
      ? artifact.x_axis.order_values
      : [...new Set(rows.map(row => row[trace.x]))];
    return {
      autosize: true,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 76, r: 150, t: 18, b: 90 },
      xaxis: {
        title: artifact.x_axis.label,
        type: "category",
        categoryorder: "array",
        categoryarray: xValues,
        tickangle: artifact.provenance.x_tickangle || 0,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.18)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: artifact.y_axis.label,
        rangemode: artifact.y_axis.minimum === 0 ? "tozero" : "normal",
        range: axisRange(artifact.y_axis),
        tickformat: artifact.y_axis.tickformat || undefined,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      hovermode: "closest",
      legend: {
        title: { text: artifact.provenance.legend_title || "" },
        orientation: "v",
        yanchor: "top",
        y: 1,
        xanchor: "left",
        x: 1.02,
      },
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
  }

  function orderedBarLayout(artifact, trace) {
    const maxY = Math.max(...trace.y, 0);
    const yTicks = monthIndexTicks(maxY, artifact);
    return {
      autosize: true,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 90, r: 30, t: 18, b: 120 },
      xaxis: {
        title: artifact.x_axis.label,
        type: "category",
        categoryorder: "array",
        categoryarray: trace.x,
        tickvals: trace.x,
        ticktext: sparseTickText(trace.x, artifact.provenance.max_x_tick_labels || trace.x.length),
        tickangle: artifact.provenance.x_tickangle || 0,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.18)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: artifact.y_axis.label,
        range: [0, maxY],
        tickmode: "array",
        tickvals: yTicks.values,
        ticktext: yTicks.labels,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      hovermode: "closest",
      showlegend: false,
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
  }

  function categoryBarLayout(artifact, trace) {
    return {
      autosize: true,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 80, r: 30, t: 18, b: 70 },
      xaxis: {
        title: artifact.x_axis.label,
        type: "category",
        categoryorder: "array",
        categoryarray: trace.x,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.18)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: artifact.y_axis.label,
        rangemode: artifact.y_axis.minimum === 0 ? "tozero" : "normal",
        automargin: true,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      hovermode: "closest",
      showlegend: false,
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
  }

  function careerLengthLayout(view) {
    return {
      autosize: true,
      barmode: view.kind === "stacked_bar" ? "stack" : undefined,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 76, r: 40, t: 18, b: 70 },
      xaxis: {
        title: view.x_label,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.18)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: view.y_label,
        rangemode: "tozero",
        tickformat: view.tickformat || undefined,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      hovermode: "closest",
      legend: {
        orientation: "v",
        yanchor: "top",
        y: 1,
        xanchor: "left",
        x: 1.02,
      },
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
  }

  function standingWinProbabilityLayout(artifact, traces) {
    return {
      autosize: true,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 76, r: 36, t: 18, b: 92 },
      xaxis: {
        title: artifact.x_axis.label,
        type: "category",
        categoryorder: "array",
        categoryarray: visibleStandingCategories(traces),
        automargin: true,
        gridcolor: "rgba(127,149,192,0.18)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      yaxis: {
        title: artifact.y_axis.label,
        range: axisRange(artifact.y_axis),
        tickformat: artifact.y_axis.tickformat || undefined,
        automargin: true,
        gridcolor: "rgba(127,149,192,0.22)",
        zerolinecolor: "rgba(127,149,192,0.35)",
        color: "#c9d4ee",
      },
      hovermode: "closest",
      legend: {
        title: { text: artifact.provenance.legend_title || "" },
        itemclick: "toggle",
        itemdoubleclick: false,
      },
      font: {
        family: "Arial, Helvetica, sans-serif",
        color: "#ffffff",
      },
    };
  }

  function sparseTickText(labels, maxLabels) {
    const step = Math.max(1, Math.ceil(labels.length / maxLabels));
    return labels.map((label, index) => index % step === 0 ? label : "");
  }

  function monthIndexTicks(maxMonthIndex, artifact) {
    const tickVals = [];
    const step = 24;
    for (let value = 0; value <= maxMonthIndex; value += step) {
      tickVals.push(value);
    }
    if (!tickVals.includes(maxMonthIndex)) {
      tickVals.push(maxMonthIndex);
    }
    return {
      values: tickVals,
      labels: tickVals.map(value => monthIndexLabel(value, artifact)),
    };
  }

  function monthIndexLabel(monthIndex, artifact) {
    const totalMonths = artifact.provenance.base_month - 1 + monthIndex;
    const year = artifact.provenance.base_year + Math.floor(totalMonths / 12);
    const month = (totalMonths % 12) + 1;
    return `${String(year).padStart(4, "0")}/${String(month).padStart(2, "0")}`;
  }

  function axisRange(axis) {
    if (axis.minimum === null || axis.maximum === null) return undefined;
    return [axis.minimum, axis.maximum];
  }

  function chartElementId(artifact) {
    return `${artifact.id}-chart`;
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
    const direction = { id: "direction", heading: "⇅", side };
    const columns = [];
  
    if (state.equelo) columns.push({ id: "equelo", heading: "Equelo", side });
    if (state.context) {
      columns.push({ id: "old_chii", heading: "Previous Chii", side });
      columns.push({ id: "result", heading: "Result", side });
    }
    columns.push(direction);
    if (state.delta) columns.push({ id: "delta", heading: "Delta", side });
  
    if (side === "east") return [...columns, identity];
    return [identity, ...columns.reverse()];
  }

  function banzukeScanColumns(state) {
    const columns = [
      { id: "chii", heading: "Chii" },
      { id: "shikona", heading: "Shikona" },
      { id: "direction", heading: "⇅" },
    ];
    if (state.delta) columns.push({ id: "delta", heading: "Delta" });
    if (state.context) {
      columns.push({ id: "result", heading: "Result" });
      columns.push({ id: "old_chii", heading: "Previous Chii" });
    }
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

  function movementDirection(value) {
    if (String(value).startsWith("+")) return "↑";
    if (String(value).startsWith("-")) return "↓";
    return "";
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
    if (columnId === "direction") {
      return movementDirection(row[`${side}_delta`]);
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
    if (applies.includes(state.view)) return true;
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

  function resolveCareerLengthView(artifact, selectedView) {
    const views = artifact.provenance.views || {};
    return Object.prototype.hasOwnProperty.call(views, selectedView)
      ? selectedView
      : "distribution";
  }

  function careerLengthView(artifact, selectedView) {
    return artifact.provenance.views[resolveCareerLengthView(artifact, selectedView)];
  }

  function careerLengthCellValue(column, row, index) {
    if (column.id === "rank") return String(index + 1);
    const value = row[column.source_field || column.id] || "";
    if (column.id === "shikona") return renderRikishiLink(value, row.rikishi_id);
    if (column.formatter === "decimal_2") return decimal(value, 2);
    if (column.id === "active") return value === "True" || value === "true" || value === "1" ? "Yes" : "No";
    return escapeHtml(value);
  }

  function selectedStandingSource(artifact, state) {
    return artifact.data_sources.find(source => source.id === state.source)
      || artifact.data_sources[0];
  }

  function resolveSelectedDataSourceId(artifact, selectedSource) {
    return artifact.data_sources.some(source => source.id === selectedSource)
      ? selectedSource
      : artifact.data_sources[0].id;
  }

  function resolveFilterValue(filters, filterId, selectedValue) {
    const filter = filters.find(candidate => candidate.id === filterId);
    if (!filter) return selectedValue;
    return filter.values.some(value => value.value === selectedValue)
      ? selectedValue
      : filter.default;
  }

  function displayStandingChii(artifact, chii) {
    const sanyaku = artifact.provenance.sanyaku_display || [];
    if (String(chii).startsWith("Y")) return sanyaku.includes(chii);
    if (String(chii).startsWith("O")) return sanyaku.includes(chii);
    if (String(chii).startsWith("S") && !String(chii).startsWith("Sd")) {
      return sanyaku.includes(chii);
    }
    if (String(chii).startsWith("K")) return sanyaku.includes(chii);
    return true;
  }

  function divisionForStandingChii(chii) {
    const value = String(chii || "");
    if (value.startsWith("Ms")) return "Makushita";
    if (value.startsWith("Sd")) return "Sandanme";
    if (value.startsWith("Jd")) return "Jonidan";
    if (value.startsWith("Jk")) return "Jonokuchi";
    if (["Y", "O", "S", "K", "M"].some(prefix => value.startsWith(prefix))) return "Makuuchi";
    if (value.startsWith("J")) return "Juryo";
    return "Other";
  }

  function visibleStandingCategories(traces) {
    const entries = new Map();
    const visibleTraces = traces.filter(trace =>
      trace.visible === true || trace.visible === undefined
    );
    const selectedTraces = visibleTraces.length ? visibleTraces : traces;
    for (const trace of selectedTraces) {
      trace.x.forEach((label, index) => {
        entries.set(label, trace.customdata[index][2]);
      });
    }
    return [...entries.entries()]
      .sort((left, right) => Number(left[1]) - Number(right[1]))
      .map(([label]) => label);
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
