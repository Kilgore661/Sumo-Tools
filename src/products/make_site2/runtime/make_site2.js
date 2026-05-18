const state = {
  envelope: null,
  filters: {},
  rows: [],
  sort: null,
  index: null,
  indexEntry: null,
  finishByChiiRows: []
};

const NAV_TOGGLE_STORAGE_KEY = "gaspodeSumoLab.makeSite2.navCollapsed";

document.addEventListener("DOMContentLoaded", () => {
  boot().catch(error => renderError(error));
});

async function boot() {
  bootNavigationToggle();
  wireNavigation();
  const pageId = selectedPageFromHash() || "basho_results_browser";
  await selectPage(pageId);
}

function bootNavigationToggle() {
  const shell = document.querySelector("[data-nav-shell]");
  const panel = document.querySelector("[data-nav-panel]");
  const toggle = document.querySelector("[data-nav-toggle]");
  if (!shell || !panel || !toggle) return;

  const initialCollapsed = window.localStorage.getItem(NAV_TOGGLE_STORAGE_KEY) === "true";
  applyNavigationCollapsedState(shell, panel, toggle, initialCollapsed);

  toggle.addEventListener("click", () => {
    const nextCollapsed = !shell.classList.contains("nav-collapsed");
    applyNavigationCollapsedState(shell, panel, toggle, nextCollapsed);
    window.localStorage.setItem(NAV_TOGGLE_STORAGE_KEY, String(nextCollapsed));
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

function wireNavigation() {
  document.querySelectorAll("[data-page-id]").forEach(link => {
    link.addEventListener("click", event => {
      event.preventDefault();
      window.location.hash = `page=${link.dataset.pageId}`;
      selectPage(link.dataset.pageId).catch(error => renderError(error));
    });
  });
  window.addEventListener("hashchange", () => {
    const pageId = selectedPageFromHash();
    if (pageId) selectPage(pageId).catch(error => renderError(error));
  });
}

function selectedPageFromHash() {
  const hash = window.location.hash.replace(/^#/, "");
  const params = new URLSearchParams(hash);
  return params.get("page");
}

async function selectPage(pageId) {
  const index = await fetchJson("manifest-index.json");
  const manifestPath = index[pageId];
  if (!manifestPath) throw new Error(`No make_site2 manifest registered for ${pageId}`);
  const envelope = await fetchJson(manifestPath);
  state.envelope = envelope;
  state.rows = [];
  state.metadata = null;
  state.index = null;
  state.indexEntry = null;
  state.finishByChiiRows = [];
  state.filters = resolveFilterState(envelope);
  state.sort = defaultSort(envelope);
  renderShell(envelope);
  await renderContent(envelope);
  document.querySelectorAll("[data-page-id]").forEach(link => {
    link.classList.toggle("active", link.dataset.pageId === pageId);
  });
}

function resolveFilterState(envelope) {
  const params = new URLSearchParams(window.location.search);
  const filters = collectFilters(envelope);
  return Object.fromEntries(filters.map(filter => [
    filter.id,
    coerceFilterValue(filter, params.get(filter.url_key || filter.id) ?? filter.default)
  ]));
}

function collectFilters(envelope) {
  const contents = envelope.contentPanel.contents || {};
  if (contents.grammar === "G2b") {
    return [
      contents.branchSelector,
      ...(contents.branches || []).flatMap(branch => branch.filters || [])
    ].filter(Boolean);
  }
  return [
    ...(contents.filters || []),
    ...(contents.pas || []).flatMap(pa => pa.filters || [])
  ];
}

function renderShell(envelope) {
  document.getElementById("page-title").textContent = envelope.contentPanel.heading.title;
  document.getElementById("page-summary").textContent = envelope.contentPanel.heading.summary || "";
  renderFilters(envelope);
}

function renderFilters(envelope) {
  const host = document.getElementById("filter-section");
  if (envelope.contentPanel.contents.grammar === "G2b") {
    renderG2bFilters(envelope, host);
    return;
  }
  const filters = collectFilters(envelope).filter(filterAppliesNow);
  host.innerHTML = filters.map(filter => renderFilterControl(filter)).join("");
  host.querySelectorAll("[data-filter-id]").forEach(control => {
    control.addEventListener("change", async () => {
      const filter = filters.find(item => item.id === control.dataset.filterId);
      state.filters[filter.id] = coerceFilterValue(
        filter,
        filter.kind === "boolean" ? control.checked : control.value
      );
      state.sort = defaultSort(envelope);
      writeUrlState(envelope);
      renderFilters(envelope);
      await renderContent(envelope);
    });
  });
}

function renderG2bFilters(envelope, host) {
  const contents = envelope.contentPanel.contents;
  const selectedBranch = selectedG2bBranch(contents);
  host.innerHTML = `
    <div class="branch-filter-panel">
      ${renderFilterControl(contents.branchSelector)}
    </div>
    ${(contents.branches || []).map(branch => `
      <div class="branch-filter-panel ${branch.id === selectedBranch.id ? "" : "inactive"}">
        <div class="filter-label">${escapeHtml(branch.tag)}</div>
        ${(branch.filters || []).map(filter => renderFilterControl(filter)).join("")}
      </div>
    `).join("")}
  `;
  host.querySelectorAll("[data-filter-id]").forEach(control => {
    const filter = collectFilters(envelope).find(item => item.id === control.dataset.filterId);
    const branchPanel = control.closest(".branch-filter-panel");
    if (branchPanel?.classList.contains("inactive")) {
      control.disabled = true;
      return;
    }
    control.addEventListener("change", async () => {
      state.filters[filter.id] = coerceFilterValue(
        filter,
        filter.kind === "boolean" ? control.checked : control.value
      );
      state.sort = defaultSort(envelope);
      writeUrlState(envelope);
      renderFilters(envelope);
      await renderContent(envelope);
    });
  });
}

function filterAppliesNow(filter) {
  if (!filter.appliesWhen) return true;
  const owner = filter.appliesWhen.filter;
  const values = filter.appliesWhen.values || [];
  return values.includes(String(state.filters[owner]));
}

function renderFilterControl(filter) {
  const value = state.filters[filter.id];
  const values = dynamicFilterValues(filter) || filter.values || [];
  if (filter.control === "radio_group") {
    return `
      <div class="filter-control filter-control-wide">
        <div class="filter-label">${escapeHtml(filter.label)}</div>
        <div class="radio-group">
          ${values.map(item => `
            <label class="radio-option">
              <input type="radio" name="${escapeHtml(filter.id)}" data-filter-id="${escapeHtml(filter.id)}" value="${escapeHtml(item.value)}" ${String(value) === String(item.value) ? "checked" : ""}>
              <span>${escapeHtml(item.label)}</span>
            </label>
          `).join("")}
        </div>
      </div>
    `;
  }
  if (filter.kind === "boolean") {
    return `
      <label class="checkbox-filter">
        <input type="checkbox" data-filter-id="${escapeHtml(filter.id)}" ${value ? "checked" : ""}>
        <span>${escapeHtml(filter.label)}</span>
      </label>
    `;
  }
  return `
    <div class="filter-control">
      <label for="filter-${escapeHtml(filter.id)}">${escapeHtml(filter.label)}</label>
      <select id="filter-${escapeHtml(filter.id)}" data-filter-id="${escapeHtml(filter.id)}">
        ${values.map(item => `
          <option value="${escapeHtml(item.value)}" ${String(value) === String(item.value) ? "selected" : ""}>${escapeHtml(item.label)}</option>
        `).join("")}
      </select>
    </div>
  `;
}

function dynamicFilterValues(filter) {
  if (filter.control === "basho_date_selector" && state.index?.entries?.length) {
    return [...state.index.entries]
      .reverse()
      .map(entry => ({ value: entry.basho, label: entry.label || entry.basho }));
  }
  if (filter.id === "division" && state.rows.length) {
    const entries = [...new Map(state.rows
      .filter(row => row.division_id)
      .map(row => [
        row.division_id,
        row.division_label || row.division_id
      ])).entries()];
    if (entries.length) {
      return entries.map(([value, label]) => ({ value, label }));
    }
  }
  if (filter.id === "chii" && state.finishByChiiRows.length) {
    const division = state.filters.division || "makuuchi";
    const entries = [...new Map(state.finishByChiiRows
      .filter(row => divisionId(row.division) === division)
      .sort((left, right) => Number(left.chii_ordinal) - Number(right.chii_ordinal))
      .map(row => [row.chii, row.chii])).entries()];
    if (entries.length) {
      return entries.map(([value, label]) => ({ value, label }));
    }
  }
  return null;
}

async function renderContent(envelope) {
  if (envelope.contentPanel.contents.grammar === "G2b") {
    await renderG2bContent(envelope);
    return;
  }
  if (envelope.contentPanel.contents.grammar === "G2") {
    await renderG2Content(envelope);
    return;
  }
  const pa = envelope.contentPanel.contents.pas[0];
  if (!pa) {
    throw new Error("No PA is configured for this page.");
  }
  if (pa.artifact.kind === "indexed_table") {
    await renderIndexedTable(envelope, pa);
    return;
  }
  if (pa.artifact.kind === "table") {
    await renderTable(envelope, pa);
    return;
  }
  if (pa.artifact.kind === "chart") {
    await renderChart(envelope, pa);
    return;
  }
  throw new Error(`Unsupported make_site2 artifact kind: ${pa.artifact.kind}`);
}

function selectedG2bBranch(contents) {
  const selector = contents.branchSelector;
  const selectedId = state.filters[selector.id] || selector.default;
  return (contents.branches || []).find(branch => branch.id === selectedId)
    || (contents.branches || [])[0];
}

async function renderG2bContent(envelope) {
  const contents = envelope.contentPanel.contents;
  const branch = selectedG2bBranch(contents);
  const pa = branch.pa;
  document.getElementById("notes-section").innerHTML = "";
  if (pa.artifact.kind === "career_length_chart") {
    await renderCareerLengthCharts(pa, document.getElementById("pa-section"));
  } else if (pa.artifact.renderer === "career_length_longest_table") {
    await renderCareerLengthLongest(envelope, branch, pa, document.getElementById("pa-section"));
  } else {
    throw new Error(`Unsupported G2b branch artifact: ${pa.artifact.kind}`);
  }
  renderNotes(envelope);
}

async function renderG2Content(envelope) {
  document.getElementById("notes-section").innerHTML = "";
  document.getElementById("pa-section").innerHTML = `
    <div class="g2-grid">
      ${(envelope.contentPanel.contents.pas || []).map(pa => `
        <section class="pa-card" data-pa-host="${escapeHtml(pa.id)}">
          <h3>${escapeHtml(pa.title)}</h3>
          <div class="pa-card-body"></div>
        </section>
      `).join("")}
    </div>
  `;
  for (const pa of envelope.contentPanel.contents.pas || []) {
    const host = document.querySelector(`[data-pa-host="${cssEscape(pa.id)}"] .pa-card-body`);
    if (pa.artifact.kind === "career_length_charts") {
      await renderCareerLengthCharts(pa, host);
    } else if (pa.artifact.renderer === "career_length_longest_table") {
      await renderCareerLengthLongest(envelope, null, pa, host);
    } else {
      host.innerHTML = `<p class="runtime-note">Unsupported G2 PA: ${escapeHtml(pa.id)}</p>`;
    }
  }
  renderNotes(envelope);
}

async function renderTable(envelope, pa) {
  const artifact = pa.artifact;
  const source = dataSourceForFilters(artifact);
  if (!source) {
    throw new Error(`No table data source matches the selected filters for ${pa.id}`);
  }
  const [rows, metadata] = await Promise.all([
    fetchCsvRows(source.path),
    source.metadata_path ? fetchJson(source.metadata_path) : Promise.resolve(null)
  ]);
  state.rows = rows;
  state.metadata = metadata;
  if (artifact.renderer === "standings_table") {
    renderStandingsTable(envelope, pa, rows, metadata);
    return;
  }
  if (artifact.renderer === "sectioned_table") {
    renderSectionedTable(envelope, pa, rows);
    return;
  }
  if (artifact.renderer === "banzuke_change_table") {
    renderBanzukeChangeTable(envelope, pa, rows, metadata);
    return;
  }
  throw new Error(`Unsupported table renderer: ${artifact.renderer}`);
}

function dataSourceForFilters(artifact) {
  return (artifact.dataSources || []).find(source => {
    if (!source.option_id) return source.id === artifact.primarySource || artifact.dataSources.length === 1;
    return String(state.filters[source.option_id]) === String(source.option_value);
  });
}

function renderStandingsTable(envelope, pa, rows, metadata) {
  const artifact = pa.artifact;
  const visibleColumns = visibleColumnsForTableArtifact(artifact);
  const visibleRows = rows
    .filter(includeStandingsRow)
    .sort((left, right) => {
      const column = (artifact.columns || []).find(item => item.id === state.sort?.column);
      if (!column) return 0;
      const result = comparePrimitive(valueForSort(left, column), valueForSort(right, column));
      return state.sort.descending ? -result : result;
    });
  document.getElementById("pa-section").innerHTML = `
    <div class="table-panel">
      <h3 class="table-title">${escapeHtml(standingsTitle(envelope, artifact, metadata))}</h3>
      <div class="table-wrap">
        <table>
          ${renderTableHead(artifact, visibleColumns)}
          <tbody>${visibleRows.map((row, index) => renderTableRow(row, index, visibleColumns)).join("")}</tbody>
        </table>
      </div>
    </div>
  `;
  renderNotes(envelope);
  wireTableHeaders(artifact);
}

function renderSectionedTable(envelope, pa, rows) {
  const artifact = pa.artifact;
  const columns = artifact.columns || [];
  document.getElementById("pa-section").innerHTML = `
    <div class="sectioned-table-panel">
      ${(artifact.sections || []).map(section => renderTableSection(section, rows, columns)).join("")}
    </div>
  `;
  renderNotes(envelope);
}

function renderTableSection(section, rows, columns) {
  const sectionRows = rows
    .filter(row => String(row[section.source_field]) === String(section.source_value))
    .sort((left, right) => comparePrimitive(Number(left[section.order_by]) || 0, Number(right[section.order_by]) || 0));
  return `
    <section class="table-panel sectioned-table">
      <h3 class="table-title">${escapeHtml(section.heading)}</h3>
      <div class="table-wrap table-wrap-compact">
        <table>
          <thead><tr>${columns.map(column => renderHeaderCell(column)).join("")}</tr></thead>
          <tbody>${sectionRows.map((row, index) => renderTableRow(row, index, columns)).join("")}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderBanzukeChangeTable(envelope, pa, rows, metadata) {
  const division = state.filters.division || metadata?.default_division || "makuuchi";
  const visibleRows = rows.filter(row => row.division_id === division);
  const title = banzukeChangesTitle(envelope, metadata, division);
  const table = state.filters.banzuke_style
    ? renderBanzukeTwoColumnTable(visibleRows)
    : renderBanzukeOneColumnTable(visibleRows);
  document.getElementById("pa-section").innerHTML = `
    <div class="table-panel banzuke-change-panel">
      <h3 class="table-title">${escapeHtml(title)}</h3>
      <div class="table-wrap banzuke-table-wrap">
        ${table}
      </div>
    </div>
  `;
  renderNotes(envelope);
}

function banzukeChangesTitle(envelope, metadata, division) {
  const divisionLabel = labelForFilter(envelope, "division", division) || division;
  const current = bashoMonthYear(metadata?.current_date || "");
  const previous = bashoMonthYear(metadata?.previous_date || "");
  if (current && previous) {
    return `${divisionLabel} Banzuke Changes: ${previous} to ${current}`;
  }
  return `${divisionLabel} Banzuke Changes`;
}

function renderBanzukeTwoColumnTable(rows) {
  const sideColumns = banzukeSideColumnCount();
  return `
    <table class="banzuke-change-table banzuke-change-table-two">
      <thead>
        <tr>
          <th scope="colgroup" colspan="${sideColumns}" class="center">East</th>
          <th scope="col" rowspan="2" class="center">Rank</th>
          <th scope="colgroup" colspan="${sideColumns}" class="center">West</th>
        </tr>
        <tr>
          ${banzukeTwoColumnSideHead("east")}
          ${banzukeTwoColumnSideHead("west")}
        </tr>
      </thead>
      <tbody>
        ${rows.map(row => `
          <tr>
            ${banzukeTwoColumnSideCells(row, "east")}
            <th scope="row" class="bcr-rank">${escapeHtml(row.bz_chii)}</th>
            ${banzukeTwoColumnSideCells(row, "west")}
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function banzukeTwoColumnSideHead(side) {
  const cells = [];
  if (side === "east") {
    if (state.filters.equelo) cells.push(`<th scope="col" class="right">Equelo</th>`);
    if (state.filters.context) cells.push(`<th scope="col">Chii</th>`, `<th scope="col">Result</th>`);
    cells.push(`<th scope="col" class="center">Move</th>`);
    if (state.filters.delta) cells.push(`<th scope="col" class="right">Delta</th>`);
    cells.push(`<th scope="col">Shikona</th>`);
    return cells.join("");
  }
  cells.push(`<th scope="col">Shikona</th>`);
  cells.push(`<th scope="col" class="center">Move</th>`);
  if (state.filters.delta) cells.push(`<th scope="col" class="right">Delta</th>`);
  if (state.filters.context) cells.push(`<th scope="col">Result</th>`, `<th scope="col">Chii</th>`);
  if (state.filters.equelo) cells.push(`<th scope="col" class="right">Equelo</th>`);
  return cells.join("");
}

function banzukeTwoColumnSideCells(row, side) {
  const cells = [];
  if (side === "east") {
    if (state.filters.equelo) cells.push(banzukeEqueloCell(row, side));
    if (state.filters.context) cells.push(banzukeTextCell(row[`${side}_old_chii`]), banzukeResultCell(row, side));
    cells.push(banzukeDirectionCell(row, side));
    if (state.filters.delta) cells.push(banzukeDeltaCell(row, side));
    cells.push(banzukeRikishiCell(row, side));
    return cells.join("");
  }
  cells.push(banzukeRikishiCell(row, side));
  cells.push(banzukeDirectionCell(row, side));
  if (state.filters.delta) cells.push(banzukeDeltaCell(row, side));
  if (state.filters.context) cells.push(banzukeResultCell(row, side), banzukeTextCell(row[`${side}_old_chii`]));
  if (state.filters.equelo) cells.push(banzukeEqueloCell(row, side));
  return cells.join("");
}

function renderBanzukeOneColumnTable(rows) {
  const oneColumnRows = rows.flatMap(row => ["east", "west"].map(side => ({ row, side })))
    .filter(item => item.row[`${item.side}_rikishi_id`]);
  return `
    <table class="banzuke-change-table banzuke-change-table-one">
      <thead>
        <tr>
          <th scope="col">Chii</th>
          <th scope="col">Shikona</th>
          <th scope="col" class="center">Move</th>
          ${state.filters.delta ? `<th scope="col" class="right">Delta</th>` : ""}
          ${state.filters.context ? `<th scope="col">Result</th><th scope="col">Previous Chii</th>` : ""}
          ${state.filters.equelo ? `<th scope="col" class="right">Equelo</th>` : ""}
        </tr>
      </thead>
      <tbody>
        ${oneColumnRows.map(({ row, side }) => `
          <tr>
            <th scope="row" class="bcr-rank">${escapeHtml(row[`${side}_chii`])}</th>
            ${banzukeRikishiCell(row, side)}
            ${banzukeDirectionCell(row, side)}
            ${state.filters.delta ? banzukeDeltaCell(row, side) : ""}
            ${state.filters.context ? `${banzukeResultCell(row, side)}${banzukeTextCell(row[`${side}_old_chii`])}` : ""}
            ${state.filters.equelo ? banzukeEqueloCell(row, side) : ""}
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function banzukeSideColumnCount() {
  let count = 2;
  if (state.filters.context) count += 2;
  if (state.filters.delta) count += 1;
  if (state.filters.equelo) count += 1;
  return count;
}

function banzukeRikishiCell(row, side) {
  const rikishiId = row[`${side}_rikishi_id`];
  const shikona = row[`${side}_shikona`] || "";
  const graphShikona = row[`${side}_graph_shikona`] || shikona;
  if (!rikishiId) return `<td class="empty"></td>`;
  const href = `https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}`;
  return `<td class="bcr-shikona ${escapeHtml(side)}"><a href="${href}" target="_blank" rel="noopener">${escapeHtml(shikona || graphShikona)}</a></td>`;
}

function banzukeTextCell(value) {
  return `<td>${escapeHtml(value || "")}</td>`;
}

function banzukeResultCell(row, side) {
  const result = row[`${side}_result`] || "";
  const movement = row[`${side}_result_movement`] || "";
  return `<td>${escapeHtml(result)}${movement ? ` <span class="rank-level-movement">${escapeHtml(movement)}</span>` : ""}</td>`;
}

function banzukeDirectionCell(row, side) {
  const value = row[`${side}_delta`] || "";
  const symbol = value.startsWith("+") ? "&#8593;" : value.startsWith("-") ? "&#8595;" : "&nbsp;";
  return `<td class="bcr-delta-direction center">${symbol}</td>`;
}

function banzukeDeltaCell(row, side) {
  const value = row[`${side}_delta`] || "";
  const deltaClass = (row[`${side}_delta_class`] || "").split(/\s+/).filter(Boolean).map(escapeHtml).join(" ");
  return `<td class="bcr-delta-value right ${deltaClass}">${escapeHtml(value.replace(/^[+-]/, ""))}</td>`;
}

function banzukeEqueloCell(row, side) {
  return `<td class="right">${escapeHtml(row[`${side}_equelo`] || "")}</td>`;
}

function visibleColumnsForTableArtifact(artifact) {
  const presetId = state.filters.metric_group_preset;
  const preset = (artifact.groupVisibilityPresets || []).find(item => item.id === presetId);
  const visibleGroups = new Set(
    preset ? preset.visible_groups : (artifact.columnGroups || []).map(group => group.id)
  );
  return (artifact.columns || [])
    .filter(column => column.always_visible || visibleGroups.has(column.group))
    .sort((left, right) => columnOrderForGroups(artifact.columnGroups || [], artifact.columns || [], left) - columnOrderForGroups(artifact.columnGroups || [], artifact.columns || [], right));
}

function includeStandingsRow(row) {
  if (state.filters.current_only && String(row.is_current) !== "1") {
    return false;
  }
  if (state.filters.division && state.filters.division !== "all") {
    return divisionForChii(row.chii) === state.filters.division;
  }
  return true;
}

function standingsTitle(envelope, artifact, metadata) {
  const division = labelForFilter(envelope, "division", state.filters.division) || "All";
  const sortLabel = (artifact.columns || []).find(item => item.id === state.sort?.column)?.heading || "Selected Column";
  const end = metadata?.effective_end_date || "";
  return `${division} Standings by ${sortLabel}${end ? ` after ${bashoMonthYear(end)} Basho` : ""}`;
}

function bashoMonthYear(dateToken) {
  const [year, month] = String(dateToken || "").split("/").map(Number);
  if (!Number.isFinite(year) || !Number.isFinite(month)) return dateToken || "";
  const monthName = new Date(year, month - 1, 1).toLocaleString("en-GB", { month: "long" });
  return `${monthName} ${year}`;
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

function divisionId(label) {
  return String(label || "").trim().toLocaleLowerCase();
}

async function renderIndexedTable(envelope, pa) {
  const artifact = pa.artifact;
  const index = await fetchJson(artifact.indexedSource.index_path);
  state.index = index;
  const selected = state.filters[artifact.selectorFilter] && state.filters[artifact.selectorFilter] !== "latest"
    ? state.filters[artifact.selectorFilter]
    : index.default_basho;
  const entry = (index.entries || []).find(item => String(item.basho) === String(selected));
  if (!entry) throw new Error(`No Basho Results index entry exists for ${selected}`);
  state.indexEntry = entry;
  state.filters[artifact.selectorFilter] = entry.basho;
  const rows = await fetchCsvRows(entry[artifact.indexedSource.payload_path_field]);
  state.rows = rows;
  normalizeDivisionFilter(envelope);
  renderFilters(envelope);

  const visibleColumns = visibleColumnsForArtifact(artifact);
  const visibleRows = rows.filter(row => !state.filters.division || row.division_id === state.filters.division);
  const sortedRows = sortRows(visibleRows, artifact);
  document.getElementById("pa-section").innerHTML = `
    <div class="table-panel">
      <h3 class="table-title">${escapeHtml(tableTitle(envelope, entry))}</h3>
      <p class="runtime-note">Generated ${escapeHtml(index.generated_at || "")}. Payload state: ${escapeHtml(entry.status || "")}${entry.latest_day ? `, Day ${escapeHtml(entry.latest_day)}` : ""}.</p>
      <div class="table-wrap">
        <table>
          ${renderTableHead(artifact, visibleColumns)}
          <tbody>${sortedRows.map((row, index) => renderTableRow(row, index, visibleColumns)).join("")}</tbody>
        </table>
      </div>
    </div>
  `;
  renderNotes(envelope);
  wireTableHeaders(artifact);
}

function normalizeDivisionFilter(envelope) {
  const divisions = dynamicFilterValues({ id: "division" }) || [];
  if (!divisions.some(item => item.value === state.filters.division)) {
    state.filters.division = divisions[0]?.value || state.filters.division;
    writeUrlState(envelope);
  }
}

async function renderChart(envelope, pa) {
  const artifact = pa.artifact;
  if (artifact.renderer === "standing_win_probability_chart") {
    normalizeStandingWinProbabilityFilters(envelope, artifact);
  }
  const source = dataSourceForFilters(artifact) || primaryDataSource(artifact);
  if (!source) throw new Error(`No chart data source is configured for ${pa.id}`);
  const rows = await fetchCsvRows(source.path);
  state.rows = rows;
  if (artifact.renderer === "division_stability_chart") {
    renderGroupedLineChart(envelope, pa, rows);
    return;
  }
  if (artifact.renderer === "banzuke_division_by_era_chart") {
    renderStackedBarChart(envelope, pa, rows);
    return;
  }
  if (artifact.renderer === "makuuchi_rank_by_era_chart") {
    renderStackedBarChart(envelope, pa, rows);
    return;
  }
  if (artifact.renderer === "first_chii_appearance_chart") {
    renderOrdinalBarChart(envelope, pa, rows);
    return;
  }
  if (artifact.renderer === "rank_group_bar_chart") {
    renderCategoryBarChart(envelope, pa, rows);
    return;
  }
  if (artifact.renderer === "standing_win_probability_chart") {
    renderStandingWinProbabilityChart(envelope, pa, rows, source);
    return;
  }
  if (artifact.renderer === "finish_by_chii_chart") {
    await renderFinishByChiiChart(envelope, pa);
    return;
  }
  throw new Error(`Unsupported chart renderer: ${artifact.renderer}`);
}

function primaryDataSource(artifact) {
  return (artifact.dataSources || []).find(source => source.id === artifact.primarySource)
    || (artifact.dataSources || [])[0];
}

async function renderFinishByChiiChart(envelope, pa) {
  const artifact = pa.artifact;
  const sources = Object.fromEntries((artifact.dataSources || []).map(source => [source.id, source]));
  const [topRows, bottomRows] = await Promise.all([
    fetchCsvRows(sources.top.path),
    fetchCsvRows(sources.bottom.path)
  ]);
  state.finishByChiiRows = topRows;
  normalizeChiiFilter(envelope);
  renderFilters(envelope);

  const direction = state.filters[artifact.directionFilter] || "top";
  const source = direction === "bottom" ? sources.bottom : sources.top;
  const rows = direction === "bottom" ? bottomRows : topRows;
  state.rows = rows;

  const division = state.filters[artifact.divisionFilter] || "makuuchi";
  const chii = state.filters[artifact.chiiFilter] || "Y1e";
  const probabilityField = direction === "bottom"
    ? "p_no_better_than_mth_worst"
    : "p_no_worse_than_n";
  const selectedRows = rows
    .filter(row => divisionId(row.division) === division && row.chii === chii)
    .sort((left, right) => Number(left.threshold) - Number(right.threshold));
  if (!selectedRows.length) {
    document.getElementById("pa-section").innerHTML = `
      <div class="status-box">No finish-by-Chii rows match the selected filters.</div>
    `;
    renderNotes(envelope);
    return;
  }
  const sampleSize = selectedRows[0].n;
  const divisionLabel = labelForFilter(envelope, "division", division) || selectedRows[0].division || division;
  const directionLabel = source.label || (direction === "bottom" ? "Bottom finish" : "Top finish");
  document.getElementById("pa-section").innerHTML = `
    <div class="chart-panel">
      <h3 class="chart-title">${escapeHtml(divisionLabel)} ${escapeHtml(chii)}: ${escapeHtml(directionLabel)}</h3>
      <p class="runtime-note">Sample size: ${escapeHtml(sampleSize)}. ${direction === "bottom" ? "Probability of finishing no better than nth-worst." : "Probability of finishing no worse than n."}</p>
      <div class="line-chart-wrap">
        ${renderFinishByChiiBars(selectedRows, probabilityField, direction)}
      </div>
    </div>
  `;
  renderNotes(envelope);
}

function normalizeChiiFilter(envelope) {
  const values = dynamicFilterValues({ id: "chii" }) || [];
  if (!values.some(item => item.value === state.filters.chii)) {
    state.filters.chii = values[0]?.value || state.filters.chii;
    writeUrlState(envelope);
  }
}

function renderFinishByChiiBars(rows, probabilityField, direction) {
  const width = 860;
  const height = 420;
  const margin = { top: 24, right: 24, bottom: 70, left: 70 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const barGap = 10;
  const barWidth = plotWidth / Math.max(1, rows.length) - barGap;
  const yMax = 1;
  const scaleY = value => margin.top + (1 - value / yMax) * plotHeight;
  const tickValues = [0, 0.25, 0.5, 0.75, 1];
  const xTitle = direction === "bottom" ? "nth-worst finish" : "finish position n";
  const yTitle = direction === "bottom" ? "No better than nth-worst" : "No worse than n";
  return `
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(yTitle)}">
      ${tickValues.map(value => `
        <line class="grid-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${scaleY(value)}" y2="${scaleY(value)}"></line>
        <text class="tick-label" x="${margin.left - 10}" y="${scaleY(value) + 4}" text-anchor="end">${Math.round(value * 100)}%</text>
      `).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${margin.top + plotHeight}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${margin.top + plotHeight}" y2="${margin.top + plotHeight}"></line>
      ${rows.map((row, index) => {
        const value = Number(row[probabilityField]) || 0;
        const x = margin.left + index * (plotWidth / Math.max(1, rows.length)) + barGap / 2;
        const y = scaleY(value);
        const height = margin.top + plotHeight - y;
        return `
          <rect class="finish-bar" x="${x}" y="${y}" width="${Math.max(1, barWidth)}" height="${height}"></rect>
          <text class="tick-label" x="${x + Math.max(1, barWidth) / 2}" y="${margin.top + plotHeight + 24}" text-anchor="middle">${escapeHtml(row.threshold)}</text>
        `;
      }).join("")}
      <text class="axis-label" x="${margin.left + plotWidth / 2}" y="${height - 24}" text-anchor="middle">${escapeHtml(xTitle)}</text>
      <text class="axis-label" transform="translate(20 ${margin.top + plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(yTitle)}</text>
    </svg>
  `;
}

async function renderCareerLengthCharts(pa, host) {
  const selected = state.filters.chart || "distribution";
  const source = (pa.artifact.dataSources || []).find(item => item.id === selected);
  if (!source) throw new Error(`No career length chart source exists for ${selected}`);
  const rows = await fetchCsvRows(source.path);
  host.innerHTML = `
    <div class="chart-panel">
      <h4 class="sub-pa-title">${escapeHtml(source.label)}</h4>
      <div class="line-chart-wrap">
        ${selected === "distribution"
          ? renderCareerDistribution(rows)
          : renderCareerProbabilityChart(rows, selected)}
      </div>
    </div>
  `;
}

function renderCareerDistribution(rows) {
  const width = 860;
  const height = 420;
  const margin = { top: 24, right: 24, bottom: 58, left: 64 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xValues = rows.map(row => Number(row.nearest_years)).filter(Number.isFinite);
  const yMax = Math.max(...rows.map(row => Number(row.total_count) || 0), 1);
  const barWidth = plotWidth / Math.max(1, xValues.length);
  const scaleX = index => margin.left + index * barWidth;
  const scaleY = value => margin.top + (1 - value / yMax) * plotHeight;
  return `
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Career length distribution">
      ${renderCareerAxes({ width, height, margin, plotWidth, plotHeight, yMax, yFormat: value => String(Math.round(value)) })}
      ${rows.map((row, index) => {
        const retired = Number(row.retired_count) || 0;
        const active = Number(row.active_count) || 0;
        const activeY = scaleY(active);
        const retiredY = scaleY(active + retired);
        const x = scaleX(index) + 1;
        const width = Math.max(1, barWidth - 2);
        return `
          <rect class="bar-retired" x="${x}" y="${retiredY}" width="${width}" height="${activeY - retiredY}"></rect>
          <rect class="bar-active" x="${x}" y="${activeY}" width="${width}" height="${margin.top + plotHeight - activeY}"></rect>
        `;
      }).join("")}
      ${careerXTicks(rows, margin, plotWidth).map(tick => `
        <text class="tick-label" x="${tick.x}" y="${height - 24}" text-anchor="middle">${escapeHtml(tick.label)}</text>
      `).join("")}
      <text class="axis-label" x="${margin.left + plotWidth / 2}" y="${height - 6}" text-anchor="middle">Nearest integer years</text>
      <text class="axis-label" transform="translate(18 ${margin.top + plotHeight / 2}) rotate(-90)" text-anchor="middle">Rikishi count</text>
    </svg>
    <div class="chart-legend">
      <span><span class="legend-swatch bar-retired-swatch"></span>Retired</span>
      <span><span class="legend-swatch bar-active-swatch"></span>Active</span>
    </div>
  `;
}

function renderCareerProbabilityChart(rows, selected) {
  const fieldByChart = {
    pmf: "probability",
    cdf: "cumulative_probability",
    survival: "survival_probability"
  };
  const titleByChart = {
    pmf: "Probability",
    cdf: "Cumulative probability",
    survival: "Survival probability"
  };
  const field = fieldByChart[selected];
  const width = 860;
  const height = 420;
  const margin = { top: 24, right: 24, bottom: 58, left: 64 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xValues = rows.map(row => Number(row.nearest_years)).filter(Number.isFinite);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMax = selected === "pmf"
    ? Math.max(...rows.map(row => Number(row[field]) || 0), 0.2)
    : 1;
  const scaleX = value => margin.left + ((value - xMin) / Math.max(1, xMax - xMin)) * plotWidth;
  const scaleY = value => margin.top + (1 - value / yMax) * plotHeight;
  const points = rows.map(row => ({
    x: scaleX(Number(row.nearest_years)),
    y: scaleY(Number(row[field])),
    value: Number(row[field])
  })).filter(point => Number.isFinite(point.x) && Number.isFinite(point.y));
  return `
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(titleByChart[selected])}">
      ${renderCareerAxes({ width, height, margin, plotWidth, plotHeight, yMax, yFormat: value => `${Math.round(value * 100)}%` })}
      <polyline class="trace-line career-line" points="${points.map(point => `${point.x},${point.y}`).join(" ")}"></polyline>
      ${points.map(point => `<circle class="trace-point" cx="${point.x}" cy="${point.y}" r="2.5"></circle>`).join("")}
      ${careerXTicks(rows, margin, plotWidth).map(tick => `
        <text class="tick-label" x="${tick.x}" y="${height - 24}" text-anchor="middle">${escapeHtml(tick.label)}</text>
      `).join("")}
      <text class="axis-label" x="${margin.left + plotWidth / 2}" y="${height - 6}" text-anchor="middle">Nearest integer years</text>
      <text class="axis-label" transform="translate(18 ${margin.top + plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(titleByChart[selected])}</text>
    </svg>
  `;
}

function renderCareerAxes({ margin, plotWidth, plotHeight, yMax, yFormat }) {
  const ticks = [0, 0.25, 0.5, 0.75, 1].map(value => value * yMax);
  const scaleY = value => margin.top + (1 - value / yMax) * plotHeight;
  return `
    ${ticks.map(value => `
      <line class="grid-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${scaleY(value)}" y2="${scaleY(value)}"></line>
      <text class="tick-label" x="${margin.left - 10}" y="${scaleY(value) + 4}" text-anchor="end">${escapeHtml(yFormat(value))}</text>
    `).join("")}
    <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${margin.top + plotHeight}"></line>
    <line class="axis-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${margin.top + plotHeight}" y2="${margin.top + plotHeight}"></line>
  `;
}

function careerXTicks(rows, margin, plotWidth) {
  const maxTicks = 10;
  const step = Math.max(1, Math.ceil(rows.length / maxTicks));
  const selected = rows.filter((_, index) => index % step === 0 || index === rows.length - 1);
  const xValues = rows.map(row => Number(row.nearest_years)).filter(Number.isFinite);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  return selected.map(row => {
    const value = Number(row.nearest_years);
    return {
      label: row.nearest_years,
      x: margin.left + ((value - xMin) / Math.max(1, xMax - xMin)) * plotWidth
    };
  });
}

async function renderCareerLengthLongest(envelope, branch, pa, host) {
  const source = (pa.artifact.dataSources || []).find(item => item.id === "longest");
  const rows = await fetchCsvRows(source.path);
  const filtered = state.filters.active === "active"
    ? rows.filter(row => row.active === "True")
    : rows;
  const rankedRows = filtered.slice(0, 100).map((row, index) => ({ ...row, rank: String(index + 1) }));
  const columns = pa.artifact.columns || [];
  host.innerHTML = `
    <div class="table-panel">
      <h3 class="table-title">${state.filters.active === "active" ? "Active Rikishi" : "Longest Careers"}</h3>
      <div class="table-wrap table-wrap-compact">
        <table>
          <thead><tr>${columns.map(column => renderHeaderCell(column)).join("")}</tr></thead>
          <tbody>${rankedRows.map((row, index) => renderTableRow(row, index, columns)).join("")}</tbody>
        </table>
      </div>
    </div>
  `;
}

function renderGroupedLineChart(envelope, pa, rows) {
  const artifact = pa.artifact;
  const trace = (artifact.traces || [])[0];
  const groups = groupRows(rows, trace.group_by);
  const chart = lineChartModel(groups, trace, artifact);
  document.getElementById("pa-section").innerHTML = `
    <div class="chart-panel">
      <h3 class="chart-title">${escapeHtml(pa.title)}</h3>
      <div class="line-chart-wrap">
        ${renderLineChartSvg(chart)}
      </div>
      ${renderChartLegend(chart)}
    </div>
  `;
  renderNotes(envelope);
}

function renderStackedBarChart(envelope, pa, rows) {
  const artifact = pa.artifact;
  const trace = (artifact.traces || [])[0];
  const chart = stackedBarChartModel(rows, trace, artifact);
  document.getElementById("pa-section").innerHTML = `
    <div class="chart-panel">
      <h3 class="chart-title">${escapeHtml(pa.title)}</h3>
      <div class="line-chart-wrap">
        ${renderStackedBarChartSvg(chart)}
      </div>
      ${renderStackedBarLegend(chart)}
    </div>
  `;
  renderNotes(envelope);
}

function stackedBarChartModel(rows, trace, artifact) {
  const width = 1040;
  const height = 560;
  const margin = { top: 24, right: 24, bottom: 88, left: 78 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xValues = [...new Set(rows.map(row => row[trace.x]))];
  const stackOrder = [...(artifact.provenance?.division_order || []), ...new Set(rows.map(row => row[trace.group_by]))]
    .filter((value, index, values) => value && values.indexOf(value) === index)
    .reverse();
  const totals = new Map(xValues.map(xValue => [
    xValue,
    rows
      .filter(row => row[trace.x] === xValue)
      .reduce((total, row) => total + (Number(row[trace.y]) || 0), 0)
  ]));
  const yMax = Math.max(...totals.values(), 1);
  const baseColours = {
    Jonokuchi: "#bc6c25",
    Jonidan: "#8d6a9f",
    Sandanme: "#2a9d8f",
    Makushita: "#457b9d",
    Juryo: "#355c7d",
    Makuuchi: "#6d597a"
  };
  const palette = ["#6d597a", "#355c7d", "#457b9d", "#2a9d8f", "#8d6a9f", "#bc6c25", "#b7791f", "#7a6f46", "#8c4b2f"];
  const colours = Object.fromEntries(stackOrder.map((group, index) => [
    group,
    baseColours[group] || palette[index % palette.length]
  ]));
  return {
    artifact,
    trace,
    rows,
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    xValues,
    stackOrder,
    yMax,
    colours,
    scaleY: value => margin.top + (1 - value / yMax) * plotHeight
  };
}

function renderStackedBarChartSvg(chart) {
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map(value => value * chart.yMax);
  const slotWidth = chart.plotWidth / Math.max(1, chart.xValues.length);
  const barWidth = Math.max(18, slotWidth * 0.64);
  return `
    <svg class="line-chart" viewBox="0 0 ${chart.width} ${chart.height}" role="img" aria-label="${escapeHtml(chart.artifact.renderer)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.scaleY(value)}" y2="${chart.scaleY(value)}"></line>
        <text class="tick-label" x="${chart.margin.left - 10}" y="${chart.scaleY(value) + 4}" text-anchor="end">${Math.round(value)}</text>
      `).join("")}
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left}" y1="${chart.margin.top}" y2="${chart.margin.top + chart.plotHeight}"></line>
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.margin.top + chart.plotHeight}" y2="${chart.margin.top + chart.plotHeight}"></line>
      ${chart.xValues.map((xValue, index) => renderStackedBar(chart, xValue, index, slotWidth, barWidth)).join("")}
      ${chart.xValues.map((xValue, index) => {
        const x = chart.margin.left + index * slotWidth + slotWidth / 2;
        return `<text class="tick-label angled-tick" transform="translate(${x} ${chart.margin.top + chart.plotHeight + 24}) rotate(-35)" text-anchor="end">${escapeHtml(xValue)}</text>`;
      }).join("")}
      <text class="axis-label" x="${chart.margin.left + chart.plotWidth / 2}" y="${chart.height - 18}" text-anchor="middle">${escapeHtml(chart.artifact.xAxis?.label || chart.trace.x)}</text>
      <text class="axis-label" transform="translate(20 ${chart.margin.top + chart.plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.artifact.yAxis?.label || chart.trace.y)}</text>
    </svg>
  `;
}

function renderStackedBar(chart, xValue, index, slotWidth, barWidth) {
  const rowsByGroup = new Map(chart.rows
    .filter(row => row[chart.trace.x] === xValue)
    .map(row => [row[chart.trace.group_by], row]));
  const x = chart.margin.left + index * slotWidth + (slotWidth - barWidth) / 2;
  let cumulative = 0;
  return chart.stackOrder.map(group => {
    const value = Number(rowsByGroup.get(group)?.[chart.trace.y]) || 0;
    const y = chart.scaleY(cumulative + value);
    const bottom = chart.scaleY(cumulative);
    cumulative += value;
    return `<rect class="stack-bar" x="${x}" y="${y}" width="${barWidth}" height="${Math.max(0, bottom - y)}" style="fill:${chart.colours[group] || "#777"}"></rect>`;
  }).join("");
}

function renderStackedBarLegend(chart) {
  const legendOrder = [...chart.stackOrder].reverse();
  return `
    <div class="chart-legend">
      ${legendOrder.map(group => `
        <span><span class="legend-swatch" style="background:${chart.colours[group] || "#777"}"></span>${escapeHtml(group)}</span>
      `).join("")}
    </div>
  `;
}

function renderOrdinalBarChart(envelope, pa, rows) {
  const artifact = pa.artifact;
  const trace = (artifact.traces || [])[0];
  const orderedRows = [...rows].sort((left, right) => {
    const orderField = artifact.xAxis?.order_field;
    if (!orderField) return String(left[trace.x]).localeCompare(String(right[trace.x]));
    return Number(left[orderField]) - Number(right[orderField]);
  });
  const chart = ordinalBarChartModel(orderedRows, trace, artifact);
  document.getElementById("pa-section").innerHTML = `
    <div class="chart-panel">
      <h3 class="chart-title">${escapeHtml(pa.title)}</h3>
      <div class="line-chart-wrap">
        ${renderOrdinalBarChartSvg(chart)}
      </div>
    </div>
  `;
  renderNotes(envelope);
}

function ordinalBarChartModel(rows, trace, artifact) {
  const width = 1240;
  const height = 560;
  const margin = { top: 24, right: 24, bottom: 92, left: 86 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const yMax = Math.max(...rows.map(row => Number(row[trace.y]) || 0), 1);
  const maxLabels = artifact.provenance?.max_x_tick_labels || 40;
  const tickStep = Math.max(1, Math.ceil(rows.length / maxLabels));
  return {
    artifact,
    trace,
    rows,
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    yMax,
    tickStep,
    scaleY: value => margin.top + (1 - value / yMax) * plotHeight
  };
}

function renderOrdinalBarChartSvg(chart) {
  const slotWidth = chart.plotWidth / Math.max(1, chart.rows.length);
  const barWidth = Math.max(1, slotWidth - 1);
  const yTicks = ordinalDateTicks(chart.yMax);
  return `
    <svg class="line-chart" viewBox="0 0 ${chart.width} ${chart.height}" role="img" aria-label="${escapeHtml(chart.artifact.renderer)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.scaleY(value)}" y2="${chart.scaleY(value)}"></line>
        <text class="tick-label" x="${chart.margin.left - 10}" y="${chart.scaleY(value) + 4}" text-anchor="end">${escapeHtml(monthIndexLabel(value))}</text>
      `).join("")}
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left}" y1="${chart.margin.top}" y2="${chart.margin.top + chart.plotHeight}"></line>
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.margin.top + chart.plotHeight}" y2="${chart.margin.top + chart.plotHeight}"></line>
      ${chart.rows.map((row, index) => {
        const value = Number(row[chart.trace.y]) || 0;
        const x = chart.margin.left + index * slotWidth;
        const y = chart.scaleY(value);
        const height = chart.margin.top + chart.plotHeight - y;
        return `<rect class="ordinal-bar" x="${x}" y="${y}" width="${barWidth}" height="${height}"></rect>`;
      }).join("")}
      ${chart.rows.map((row, index) => {
        if (index % chart.tickStep !== 0 && index !== chart.rows.length - 1) return "";
        const x = chart.margin.left + index * slotWidth + slotWidth / 2;
        return `<text class="tick-label angled-tick" transform="translate(${x} ${chart.margin.top + chart.plotHeight + 24}) rotate(-45)" text-anchor="end">${escapeHtml(row[chart.trace.x])}</text>`;
      }).join("")}
      <text class="axis-label" x="${chart.margin.left + chart.plotWidth / 2}" y="${chart.height - 16}" text-anchor="middle">${escapeHtml(chart.artifact.xAxis?.label || chart.trace.x)}</text>
      <text class="axis-label" transform="translate(18 ${chart.margin.top + chart.plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.artifact.yAxis?.label || chart.trace.y)}</text>
    </svg>
  `;
}

function ordinalDateTicks(maxMonthIndex) {
  const step = 120;
  const values = [];
  for (let value = 0; value <= maxMonthIndex; value += step) values.push(value);
  if (!values.includes(maxMonthIndex)) values.push(maxMonthIndex);
  return values;
}

function monthIndexLabel(monthIndex) {
  const baseYear = 1958;
  const baseMonth = 1;
  const totalMonths = baseMonth - 1 + Math.round(monthIndex);
  const year = baseYear + Math.floor(totalMonths / 12);
  const month = (totalMonths % 12) + 1;
  return `${String(year).padStart(4, "0")}/${String(month).padStart(2, "0")}`;
}

function renderCategoryBarChart(envelope, pa, rows) {
  const artifact = pa.artifact;
  const trace = (artifact.traces || [])[0];
  const orderValues = artifact.xAxis?.order_values || [];
  const orderedRows = orderValues.length
    ? orderValues.map(value => rows.find(row => row[trace.x] === value)).filter(Boolean)
    : [...rows].sort((left, right) => String(left[trace.x]).localeCompare(String(right[trace.x])));
  const chart = categoryBarChartModel(orderedRows, trace, artifact);
  document.getElementById("pa-section").innerHTML = `
    <div class="chart-panel">
      <h3 class="chart-title">${escapeHtml(pa.title)}</h3>
      <div class="line-chart-wrap">
        ${renderCategoryBarChartSvg(chart)}
      </div>
    </div>
  `;
  renderNotes(envelope);
}

function categoryBarChartModel(rows, trace, artifact) {
  const width = 860;
  const height = 430;
  const margin = { top: 24, right: 24, bottom: 64, left: 76 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const yMax = Math.max(...rows.map(row => Number(row[trace.y]) || 0), 1);
  return {
    artifact,
    trace,
    rows,
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    yMax,
    scaleY: value => margin.top + (1 - value / yMax) * plotHeight
  };
}

function renderCategoryBarChartSvg(chart) {
  const slotWidth = chart.plotWidth / Math.max(1, chart.rows.length);
  const barWidth = Math.max(18, slotWidth * 0.62);
  const tickStep = Math.max(1, Math.ceil(chart.yMax / 5));
  const yTicks = Array.from({ length: 6 }, (_, index) => Math.round(index * chart.yMax / 5 / tickStep) * tickStep);
  return `
    <svg class="line-chart" viewBox="0 0 ${chart.width} ${chart.height}" role="img" aria-label="${escapeHtml(chart.artifact.renderer)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.scaleY(value)}" y2="${chart.scaleY(value)}"></line>
        <text class="tick-label" x="${chart.margin.left - 10}" y="${chart.scaleY(value) + 4}" text-anchor="end">${escapeHtml(value)}</text>
      `).join("")}
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left}" y1="${chart.margin.top}" y2="${chart.margin.top + chart.plotHeight}"></line>
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.margin.top + chart.plotHeight}" y2="${chart.margin.top + chart.plotHeight}"></line>
      ${chart.rows.map((row, index) => {
        const value = Number(row[chart.trace.y]) || 0;
        const x = chart.margin.left + index * slotWidth + (slotWidth - barWidth) / 2;
        const y = chart.scaleY(value);
        const height = chart.margin.top + chart.plotHeight - y;
        return `
          <rect class="category-bar" x="${x}" y="${y}" width="${barWidth}" height="${height}"></rect>
          <text class="tick-label" x="${x + barWidth / 2}" y="${chart.margin.top + chart.plotHeight + 24}" text-anchor="middle">${escapeHtml(row[chart.trace.x])}</text>
        `;
      }).join("")}
      <text class="axis-label" x="${chart.margin.left + chart.plotWidth / 2}" y="${chart.height - 14}" text-anchor="middle">${escapeHtml(chart.artifact.xAxis?.label || chart.trace.x)}</text>
      <text class="axis-label" transform="translate(18 ${chart.margin.top + chart.plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.artifact.yAxis?.label || chart.trace.y)}</text>
    </svg>
  `;
}

function renderStandingWinProbabilityChart(envelope, pa, rows, source) {
  const artifact = pa.artifact;
  normalizeStandingWinProbabilityFilters(envelope, artifact);
  const trace = (artifact.traces || [])[0];
  const groups = standingTraceGroups(rows, trace);
  const selectedGroup = selectedStandingGroup(groups, artifact);
  if (!selectedGroup) {
    document.getElementById("pa-section").innerHTML = `<div class="status-box">No win-probability rows match the selected filters.</div>`;
    renderNotes(envelope);
    return;
  }
  const chart = standingWinProbabilityModel(selectedGroup, trace, artifact, source);
  document.getElementById("pa-section").innerHTML = `
    <div class="chart-panel">
      <h3 class="chart-title">${escapeHtml(source.label || pa.title)}: ${escapeHtml(selectedGroup.key)}</h3>
      <p class="runtime-note">Showing ${escapeHtml(selectedGroup.key)} against visible opponent standings for ${escapeHtml(state.filters.division || "All")}.</p>
      <div class="line-chart-wrap">
        ${renderStandingWinProbabilitySvg(chart)}
      </div>
    </div>
  `;
  renderNotes(envelope);
}

function normalizeStandingWinProbabilityFilters(envelope, artifact) {
  const contents = envelope.contentPanel.contents || {};
  const sourceFilter = (contents.filters || []).find(filter => filter.id === "source");
  const divisionFilter = (contents.filters || []).find(filter => filter.id === "division");
  const sourceValues = sourceFilter?.values || [];
  const divisionValues = divisionFilter?.values || [];
  const matchingSource = sourceValues.find(item => String(item.value).toLocaleLowerCase() === String(state.filters.source).toLocaleLowerCase());
  const matchingDivision = divisionValues.find(item => String(item.value).toLocaleLowerCase() === String(state.filters.division).toLocaleLowerCase());
  if (matchingSource && state.filters.source !== matchingSource.value) {
    state.filters.source = matchingSource.value;
  }
  if (!matchingSource && sourceFilter) {
    state.filters.source = sourceFilter.default;
  }
  if (matchingDivision && state.filters.division !== matchingDivision.value) {
    state.filters.division = matchingDivision.value;
  }
  if (!matchingDivision && divisionFilter) {
    state.filters.division = divisionFilter.default;
  }
  const dataSourceIds = new Set((artifact.dataSources || []).map(item => item.id));
  if (!dataSourceIds.has(state.filters.source) && sourceFilter) {
    state.filters.source = sourceFilter.default;
  }
}

function standingTraceGroups(rows, trace) {
  const division = state.filters.division || "Makuuchi";
  const grouped = new Map();
  for (const row of rows) {
    if (!displayStandingChii(row.selected_chii) || !displayStandingChii(row.opponent_chii)) continue;
    if (division !== "All" && displayDivisionForChii(row.selected_chii) !== division) continue;
    if (!grouped.has(row.selected_chii)) grouped.set(row.selected_chii, []);
    grouped.get(row.selected_chii).push(row);
  }
  return [...grouped.entries()]
    .map(([key, groupRows]) => ({
      key,
      ordinal: Number(groupRows[0]?.selected_ordinal) || 0,
      rows: groupRows.sort((left, right) => Number(left[trace.x === "opponent_chii" ? "opponent_ordinal" : trace.x]) - Number(right[trace.x === "opponent_chii" ? "opponent_ordinal" : trace.x]))
    }))
    .sort((left, right) => left.ordinal - right.ordinal);
}

function selectedStandingGroup(groups, artifact) {
  const preferred = artifact.provenance?.default_display_trace || "Y1";
  return groups.find(group => group.key === preferred) || groups[0] || null;
}

function standingWinProbabilityModel(group, trace, artifact, source) {
  const width = 1040;
  const height = 540;
  const margin = { top: 24, right: 24, bottom: 90, left: 76 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const rows = group.rows;
  const yMin = artifact.yAxis?.minimum ?? 0;
  const yMax = artifact.yAxis?.maximum ?? 1;
  const categories = orderedStandingCategories(rows);
  const categoryIndex = new Map(categories.map((label, index) => [label, index]));
  return {
    artifact,
    trace,
    source,
    group,
    rows,
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    yMin,
    yMax,
    categories,
    categoryIndex,
    scaleX: label => margin.left + (categoryIndex.get(label) / Math.max(1, categories.length - 1)) * plotWidth,
    scaleY: value => margin.top + (1 - ((value - yMin) / Math.max(0.0001, yMax - yMin))) * plotHeight
  };
}

function renderStandingWinProbabilitySvg(chart) {
  const points = chart.rows.map(row => ({
    row,
    x: chart.scaleX(row.opponent_chii),
    y: chart.scaleY(Number(row[chart.trace.y])),
    value: Number(row[chart.trace.y])
  })).filter(point => Number.isFinite(point.x) && Number.isFinite(point.y));
  const yTicks = [0, 0.25, 0.5, 0.75, 1];
  const xTicks = standingXTicks(points);
  const showErrorBars = chart.source.id === "observed" && state.filters.error_bars;
  return `
    <svg class="line-chart" viewBox="0 0 ${chart.width} ${chart.height}" role="img" aria-label="${escapeHtml(chart.artifact.renderer)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.scaleY(value)}" y2="${chart.scaleY(value)}"></line>
        <text class="tick-label" x="${chart.margin.left - 10}" y="${chart.scaleY(value) + 4}" text-anchor="end">${Math.round(value * 100)}%</text>
      `).join("")}
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left}" y1="${chart.margin.top}" y2="${chart.margin.top + chart.plotHeight}"></line>
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.margin.top + chart.plotHeight}" y2="${chart.margin.top + chart.plotHeight}"></line>
      ${showErrorBars ? points.map(point => renderStandingErrorBar(point, chart)).join("") : ""}
      <polyline class="trace-line career-line" points="${points.map(point => `${point.x},${point.y}`).join(" ")}"></polyline>
      ${points.map(point => `<circle class="trace-point" cx="${point.x}" cy="${point.y}" r="2.5"></circle>`).join("")}
      ${xTicks.map(point => `
        <text class="tick-label angled-tick" transform="translate(${point.x} ${chart.margin.top + chart.plotHeight + 24}) rotate(-45)" text-anchor="end">${escapeHtml(point.row.opponent_chii)}</text>
      `).join("")}
      <text class="axis-label" x="${chart.margin.left + chart.plotWidth / 2}" y="${chart.height - 16}" text-anchor="middle">Opponent sideless chii</text>
      <text class="axis-label" transform="translate(18 ${chart.margin.top + chart.plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.artifact.yAxis?.label || chart.trace.y)}</text>
    </svg>
  `;
}

function renderStandingErrorBar(point, chart) {
  const low = Number(point.row.ci95_lower);
  const high = Number(point.row.ci95_upper);
  if (!Number.isFinite(low) || !Number.isFinite(high)) return "";
  const yLow = chart.scaleY(low);
  const yHigh = chart.scaleY(high);
  return `
    <line class="error-bar" x1="${point.x}" x2="${point.x}" y1="${yHigh}" y2="${yLow}"></line>
    <line class="error-bar" x1="${point.x - 4}" x2="${point.x + 4}" y1="${yHigh}" y2="${yHigh}"></line>
    <line class="error-bar" x1="${point.x - 4}" x2="${point.x + 4}" y1="${yLow}" y2="${yLow}"></line>
  `;
}

function standingXTicks(points) {
  const maxTicks = 34;
  const step = Math.max(1, Math.ceil(points.length / maxTicks));
  return points.filter((_, index) => index % step === 0 || index === points.length - 1);
}

function orderedStandingCategories(rows) {
  const keyed = new Map();
  for (const row of rows) {
    const label = row.opponent_chii;
    const order = Number(row.opponent_ordinal);
    if (!label || !Number.isFinite(order)) continue;
    keyed.set(label, order);
  }
  return [...keyed.entries()]
    .sort((left, right) => left[1] - right[1])
    .map(([label]) => label);
}

function displayStandingChii(chii) {
  const sanyaku = new Set(["Y1", "O1", "S1", "K1"]);
  if (chii?.startsWith("Y")) return sanyaku.has(chii);
  if (chii?.startsWith("O")) return sanyaku.has(chii);
  if (chii?.startsWith("S") && !chii.startsWith("Sd")) return sanyaku.has(chii);
  if (chii?.startsWith("K")) return sanyaku.has(chii);
  return Boolean(chii);
}

function displayDivisionForChii(chii) {
  if (!chii) return "Other";
  if (chii.startsWith("Ms")) return "Makushita";
  if (chii.startsWith("Sd")) return "Sandanme";
  if (chii.startsWith("Jd")) return "Jonidan";
  if (chii.startsWith("Jk")) return "Jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "Makuuchi";
  if (chii.startsWith("J")) return "Juryo";
  return "Other";
}

function groupRows(rows, groupField) {
  const grouped = new Map();
  for (const row of rows) {
    const key = row[groupField] || "Series";
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(row);
  }
  return [...grouped.entries()].map(([key, groupRows]) => [
    key,
    groupRows.sort((left, right) => dateOrdinal(left.date) - dateOrdinal(right.date))
  ]);
}

function lineChartModel(groups, trace, artifact) {
  const width = 1040;
  const height = 540;
  const margin = { top: 24, right: 24, bottom: 76, left: 70 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const allRows = groups.flatMap(([, groupRows]) => groupRows);
  const xValues = allRows.map(row => dateOrdinal(row[trace.x])).filter(Number.isFinite);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = artifact.yAxis?.minimum ?? 0;
  const yMax = artifact.yAxis?.maximum ?? 1;
  const visible = new Set(artifact.provenance?.default_visible || []);
  const palette = ["#0f6f6a", "#8c4b2f", "#6257a5", "#b7791f", "#2f6f3e", "#a03c64"];
  return {
    artifact,
    trace,
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    yMin,
    yMax,
    scaleX: value => margin.left + ((value - xMin) / Math.max(1, xMax - xMin)) * plotWidth,
    scaleY: value => margin.top + (1 - ((value - yMin) / Math.max(0.0001, yMax - yMin))) * plotHeight,
    series: groups.map(([key, groupRows], index) => ({
      key,
      rows: groupRows,
      color: palette[index % palette.length],
      emphasized: !visible.size || visible.has(key)
    }))
  };
}

function renderLineChartSvg(chart) {
  const yTicks = [0, 0.25, 0.5, 0.75, 1];
  const xTicks = representativeDateTicks(chart.series[0]?.rows || []);
  return `
    <svg class="line-chart" viewBox="0 0 ${chart.width} ${chart.height}" role="img" aria-label="${escapeHtml(chart.artifact.renderer)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.scaleY(value)}" y2="${chart.scaleY(value)}"></line>
        <text class="tick-label" x="${chart.margin.left - 10}" y="${chart.scaleY(value) + 4}" text-anchor="end">${Math.round(value * 100)}%</text>
      `).join("")}
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left}" y1="${chart.margin.top}" y2="${chart.margin.top + chart.plotHeight}"></line>
      <line class="axis-line" x1="${chart.margin.left}" x2="${chart.margin.left + chart.plotWidth}" y1="${chart.margin.top + chart.plotHeight}" y2="${chart.margin.top + chart.plotHeight}"></line>
      ${xTicks.map(row => `
        <text class="tick-label" x="${chart.scaleX(dateOrdinal(row.date))}" y="${chart.margin.top + chart.plotHeight + 24}" text-anchor="middle">${escapeHtml(row.date)}</text>
      `).join("")}
      <text class="axis-label" x="${chart.margin.left + chart.plotWidth / 2}" y="${chart.height - 20}" text-anchor="middle">${escapeHtml(chart.artifact.xAxis?.label || chart.trace.x)}</text>
      <text class="axis-label" transform="translate(20 ${chart.margin.top + chart.plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.artifact.yAxis?.label || chart.trace.y)}</text>
      ${chart.series.map(series => renderLineSeries(series, chart)).join("")}
    </svg>
  `;
}

function renderLineSeries(series, chart) {
  const points = series.rows.map(row => ({
    x: chart.scaleX(dateOrdinal(row[chart.trace.x])),
    y: chart.scaleY(Number(row[chart.trace.y])),
    row
  })).filter(point => Number.isFinite(point.x) && Number.isFinite(point.y));
  const polyline = points.map(point => `${point.x},${point.y}`).join(" ");
  const className = series.emphasized ? "trace-line" : "trace-line trace-muted";
  return `<polyline class="${className}" points="${polyline}" style="stroke:${series.color}"></polyline>`;
}

function representativeDateTicks(rows) {
  const maxTicks = 10;
  const step = Math.max(1, Math.ceil(rows.length / maxTicks));
  return rows.filter((_, index) => index % step === 0 || index === rows.length - 1);
}

function renderChartLegend(chart) {
  return `
    <div class="chart-legend">
      ${chart.series.map(series => `
        <span class="${series.emphasized ? "" : "muted"}">
          <span class="legend-swatch" style="background:${series.color}"></span>
          ${escapeHtml(series.key)}
        </span>
      `).join("")}
    </div>
  `;
}

function dateOrdinal(value) {
  const [year, month] = String(value || "").split("/").map(Number);
  if (!Number.isFinite(year) || !Number.isFinite(month)) return Number.NaN;
  return year * 12 + month;
}

function visibleColumnsForArtifact(artifact) {
  const visibleGroups = new Set((artifact.columnGroups || [])
    .filter(group => group.always_visible)
    .map(group => group.id));
  if (state.filters.previous_context) visibleGroups.add("previous_basho");
  return (artifact.columns || []).filter(column => {
    if (column.id === "nu_chii" && !state.filters.nu_chii) return false;
    if (["equelo", "delta_equelo"].includes(column.id) && !state.filters.rating_context) return false;
    return column.always_visible || visibleGroups.has(column.group);
  }).sort((left, right) => columnOrder(artifact, left) - columnOrder(artifact, right));
}

function columnOrder(artifact, column) {
  return columnOrderForGroups(artifact.columnGroups || [], artifact.columns || [], column);
}

function columnOrderForGroups(groups, columns, column) {
  const groupIndex = groups.findIndex(group => (group.columns || []).includes(column.id));
  const withinGroup = groups[groupIndex]?.columns?.indexOf(column.id) ?? 0;
  if (groupIndex >= 0) return groupIndex * 1000 + withinGroup;
  return 100000 + columns.findIndex(item => item.id === column.id);
}

function renderTableHead(artifact, columns) {
  const groups = artifact.columnGroups || [];
  const groupForColumn = new Map(columns.map(column => [column.id, groups.find(group => group.id === column.group)]));
  const groupCells = [];
  let index = 0;
  while (index < columns.length) {
    const group = groupForColumn.get(columns[index].id);
    const groupColumns = [];
    while (index < columns.length && groupForColumn.get(columns[index].id)?.id === group?.id) {
      groupColumns.push(columns[index]);
      index += 1;
    }
    groupCells.push(`<th colspan="${groupColumns.length}" class="center">${escapeHtml(group?.heading || "")}</th>`);
  }
  return `
    <thead>
      <tr>${groupCells.join("")}</tr>
      <tr>${columns.map(column => renderHeaderCell(column)).join("")}</tr>
    </thead>
  `;
}

function renderHeaderCell(column) {
  const active = state.sort?.column === column.id;
  const marker = active ? (state.sort.descending ? " v" : " ^") : "";
  const classes = [column.align || "", column.sortable ? "sortable" : "", column.id === "row_number" ? "row-number" : ""].filter(Boolean).join(" ");
  return `<th class="${escapeHtml(classes)}" data-column-id="${escapeHtml(column.id)}">${escapeHtml(column.heading)}${marker}</th>`;
}

function renderTableRow(row, index, columns) {
  return `<tr>${columns.map(column => renderTableCell(row, index, column)).join("")}</tr>`;
}

function renderTableCell(row, index, column) {
  const classes = [column.align || "", column.id === "row_number" ? "row-number" : ""].filter(Boolean).join(" ");
  return `<td class="${escapeHtml(classes)}">${formatCell(row, index, column)}</td>`;
}

function formatCell(row, index, column) {
  if (column.formatter === "row_number") return String(index + 1);
  if (column.formatter === "competition_rank") return competitionRank(row, column);
  const raw = column.source_field ? row[column.source_field] : "";
  if (column.formatter === "integer") return formatNumber(raw, 0);
  if (column.formatter === "signed_integer") return formatSignedInteger(raw);
  if (column.formatter === "decimal_2") return formatNumber(raw, 2);
  if (column.formatter === "percent_1") return `${formatNumber(raw, 1)}%`;
  if (column.id === "previous_delta_direction") {
    return formatDeltaDirection(raw);
  }
  if (column.id === "previous_result") {
    return formatResultWithRankLevelMovement(raw, row.previous_rank_level_movement);
  }
  if (column.link === "rikishi" && row.rikishi_id) {
    return `<a class="rikishi-link" href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(row.rikishi_id)}" target="_blank" rel="noopener">${escapeHtml(raw)}</a>`;
  }
  return escapeHtml(raw);
}

function competitionRank(row, column) {
  const source = column.source_field || column.sort_key;
  const sorted = [...state.rows]
    .filter(includeStandingsRow)
    .sort((left, right) => comparePrimitive(
      valueForSort(right, { sort_key: source, source_field: source, sort_kind: "numeric" }),
      valueForSort(left, { sort_key: source, source_field: source, sort_kind: "numeric" })
    ));
  const target = Number(row[source]);
  const found = sorted.findIndex(candidate => Number(candidate[source]) === target);
  return found >= 0 ? String(found + 1) : "";
}

function formatDeltaDirection(value) {
  if (value !== "↑" && value !== "↓") return "";
  return `<span class="delta-direction">${escapeHtml(value)}</span>`;
}

function formatResultWithRankLevelMovement(result, marker) {
  const resultText = escapeHtml(result);
  if (!marker) return resultText;
  return `${resultText} <span class="rank-level-movement">${escapeHtml(marker)}</span>`;
}

function renderNotes(envelope) {
  const notes = (envelope.contentPanel.contents.notes || []).filter(noteApplies);
  const host = document.getElementById("notes-section");
  host.innerHTML = notes.length
    ? `<h3>Notes</h3><ol>${notes.map(note => `<li>${formatNote(note)}</li>`).join("")}</ol>`
    : "";
}

function noteApplies(note) {
  const applies = note.applies_to || ["all"];
  if (applies.includes("all") || applies.includes(state.filters.metric_group_preset)) return true;
  if (applies.includes(`branch:${state.filters.branch}`)) return true;
  if (applies.includes("context")) return Boolean(state.filters.context);
  if (applies.includes("delta")) return Boolean(state.filters.delta);
  if (applies.includes("equelo")) return Boolean(state.filters.equelo);
  if (applies.includes("previous_basho")) return Boolean(state.filters.previous_context);
  if (applies.includes("rating_context")) return Boolean(state.filters.rating_context);
  if (applies.includes("nu_chii")) return Boolean(state.filters.nu_chii);
  return false;
}

function formatNote(note) {
  return note.format === "html" ? note.text : escapeHtml(note.text);
}

function wireTableHeaders(artifact) {
  document.querySelectorAll("th[data-column-id]").forEach(header => {
    const column = (artifact.columns || []).find(item => item.id === header.dataset.columnId);
    if (!column?.sortable) return;
    header.addEventListener("click", async () => {
      if (state.sort?.column === column.id) {
        state.sort.descending = !state.sort.descending;
      } else {
        state.sort = { column: column.id, descending: defaultSortDescending(column) };
      }
      writeUrlState(state.envelope);
      await renderContent(state.envelope);
    });
  });
}

function sortRows(rows, artifact) {
  if (!state.sort) return rows;
  const column = (artifact.columns || []).find(item => item.id === state.sort.column);
  if (!column) return rows;
  return [...rows].sort((a, b) => {
    const result = comparePrimitive(valueForSort(a, column), valueForSort(b, column));
    return state.sort.descending ? -result : result;
  });
}

function valueForSort(row, column) {
  const value = row[column.sort_key || column.source_field] ?? "";
  if (["numeric", "chii_ordinal"].includes(column.sort_kind)) {
    const number = Number(value);
    return Number.isFinite(number) ? number : Number.POSITIVE_INFINITY;
  }
  return String(value).toLocaleLowerCase();
}

function comparePrimitive(left, right) {
  if (left < right) return -1;
  if (left > right) return 1;
  return 0;
}

function defaultSort(envelope) {
  const contents = envelope.contentPanel.contents;
  const sort = contents.grammar === "G2b"
    ? selectedG2bBranch(contents)?.pa?.artifact?.defaultSort
    : contents.pas?.[0]?.artifact.defaultSort;
  return sort ? { column: sort.column, descending: sort.descending } : null;
}

function defaultSortDescending(column) {
  return !(column.sort_kind === "text" || column.sort_kind === "chii_ordinal");
}

function tableTitle(envelope, entry) {
  const division = labelForFilter(envelope, "division", state.filters.division) || state.filters.division || "";
  const label = entry.label || entry.basho || "";
  if (entry.latest_day && Number(entry.latest_day) < 15) {
    return `${division} Results (Day ${entry.latest_day}) for ${label}`;
  }
  return `${division} Results for ${label}`;
}

function labelForFilter(envelope, filterId, value) {
  const filter = (envelope.contentPanel.contents.filters || []).find(item => item.id === filterId);
  return filter?.values?.find(item => String(item.value) === String(value))?.label;
}

function writeUrlState(envelope) {
  const params = new URLSearchParams(window.location.search);
  for (const filter of collectFilters(envelope)) {
    params.set(filter.url_key || filter.id, String(state.filters[filter.id]));
  }
  if (state.sort) {
    params.set("sort", state.sort.column);
    params.set("desc", String(state.sort.descending));
  }
  const next = `${window.location.pathname}?${params.toString()}${window.location.hash}`;
  history.replaceState(null, "", next);
}

function coerceFilterValue(filter, value) {
  if (filter.kind === "boolean") return value === true || value === "true";
  const matching = (filter.values || []).find(item => String(item.value) === String(value));
  return matching ? matching.value : value;
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
  return response.json();
}

async function fetchCsvRows(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
  return parseCsv(await response.text());
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
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
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

function formatNumber(value, digits) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : escapeHtml(value);
}

function formatSignedInteger(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return escapeHtml(value);
  return number > 0 ? `+${number}` : String(number);
}

function renderError(error) {
  document.getElementById("pa-section").innerHTML = `
    <div class="status-box">
      <strong>Could not render make_site2 content.</strong>
      <pre>${escapeHtml(error.stack || error.message || String(error))}</pre>
    </div>
  `;
}

function escapeHtml(value) {
  const span = document.createElement("span");
  span.textContent = value ?? "";
  return span.innerHTML;
}

function cssEscape(value) {
  return String(value).replace(/["\\]/g, "\\$&");
}
