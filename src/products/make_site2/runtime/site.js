(function () {
  const PAGE_PARAM = "page";
  const contentPanel = document.getElementById("content-panel");
  let runtimeManifest = null;

  bootNavigationToggle();
  boot().catch(error => {
    contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  });

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
      contentPanel.replaceChildren();
      return;
    }
    selectPage(pageId, { replaceUrl: true });
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
    if (artifact.kind !== "indexed_table") throw new Error(`Unsupported artifact kind: ${artifact.kind}`);

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
    const filteredRows = rows.filter(row => row.division_id === state.division).slice(0, 20);

    contentPanel.innerHTML = [
      '<section class="content-panel" aria-labelledby="content-title">',
      '<header class="content-heading">',
      `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
      `<p>${escapeHtml(panel.heading.summary)}</p>`,
      '</header>',
      renderFilterSection(panel.contents.filter_section, state, index),
      renderIndexedTable(artifact, filteredRows, state),
      '</section>'
    ].join("");
    wireFilterSection(panel, state);
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
    return entries.find(entry => entry.basho === index.default_basho) || entries[entries.length - 1];
  }

  function renderFilterSection(filterSection, state, index) {
    return [
      '<form class="filter-section" aria-label="Filters">',
      ...filterSection.filters.map(filter => renderFilter(filter, state, index)),
      '</form>'
    ].join("");
  }

  function renderFilter(filter, state, index) {
    if (filter.control === "checkbox") {
      return [
        '<label class="checkbox-control">',
        `<input type="checkbox" name="${escapeHtml(filter.id)}"${state[filter.id] ? " checked" : ""}>`,
        `<span>${escapeHtml(filter.label)}</span>`,
        '</label>'
      ].join("");
    }
    const values = filter.control === "basho_date_selector"
      ? (index.entries || []).map(entry => ({ value: entry.basho, label: entry.label }))
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

  function renderIndexedTable(artifact, rows, state) {
    const groups = new Map(artifact.column_groups.map(group => [group.id, group]));
    const visibleColumns = artifact.columns.filter(column => isColumnVisible(column, groups, state));
    return [
      '<table class="brb-table">',
      '<thead><tr>',
      ...visibleColumns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
      '</tr></thead>',
      '<tbody>',
      ...rows.map((row, index) => [
        '<tr>',
        ...visibleColumns.map(column => `<td>${escapeHtml(cellValue(column, row, index))}</td>`),
        '</tr>'
      ].join("")),
      '</tbody>',
      '</table>'
    ].join("");
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
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Could not load ${path}`);
    return response.json();
  }

  async function fetchCsv(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Could not load ${path}`);
    return parseCsv(await response.text());
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
