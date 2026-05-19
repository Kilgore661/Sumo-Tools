(function () {
  const PAGE_PARAM = "page";
  const BRB_PAGE_ID = "basho_results_browser";
  const BRB_ROUTE_BASE = "sumo-history/basho-results/";
  const BRB_INDEX_PATH = `${BRB_ROUTE_BASE}data/basho_results_index.json`;
  const VISIBLE_COLUMNS = [
    ["chii", "Chii"],
    ["shikona", "Shikona"],
    ["score", "Score"],
    ["previous_chii", "Previous Chii"],
    ["previous_result", "Previous Result"]
  ];

  const contentPanel = document.getElementById("content-panel");
  const navLinks = [...document.querySelectorAll(".nav-link[data-page-id]")];
  const linkByPageId = new Map(navLinks.map(link => [link.dataset.pageId, link]));

  bootNavigationToggle();

  for (const link of navLinks) {
    link.addEventListener("click", event => {
      event.preventDefault();
      selectPage(link.dataset.pageId, { pushUrl: true });
    });
  }

  window.addEventListener("popstate", () => {
    loadStateFromUrl();
  });

  loadStateFromUrl();

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
    if (pageId === BRB_PAGE_ID) {
      renderBashoResults().catch(error => {
        contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
      });
    } else {
      contentPanel.replaceChildren();
    }
  }

  function markActivePage(pageId) {
    for (const link of navLinks) {
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

  async function renderBashoResults() {
    contentPanel.innerHTML = "<p>Loading Basho Results...</p>";
    const index = await fetchJson(BRB_INDEX_PATH);
    const entry = defaultEntry(index);
    const rows = await fetchCsv(`${BRB_ROUTE_BASE}${entry.payload_path}`);
    const divisionRows = rows.filter(row => row.division_id === "makuuchi").slice(0, 20);
    contentPanel.innerHTML = [
      '<section class="content-panel" aria-labelledby="content-title">',
      '<header class="content-heading">',
      '<h2 id="content-title">Basho Results</h2>',
      '<p>Historical and current basho results by division.</p>',
      '</header>',
      '<form class="filter-section" aria-label="Basho Results filters">',
      renderBashoSelect(index.entries, entry.basho),
      renderDivisionSelect(),
      renderCheckbox("previous_context", "Previous Basho"),
      renderCheckbox("rating_context", "Equelo Ratings"),
      renderCheckbox("nu_chii", "nuChii"),
      '</form>',
      renderTable(divisionRows),
      '</section>'
    ].join("");
  }

  function defaultEntry(index) {
    const entries = index.entries || [];
    return entries.find(entry => entry.basho === index.default_basho) || entries[entries.length - 1];
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

  function renderBashoSelect(entries, selected) {
    return [
      '<label class="filter-control">',
      '<span>Basho</span>',
      '<select name="basho">',
      ...entries.map(entry => {
        const selectedAttr = entry.basho === selected ? " selected" : "";
        return `<option value="${escapeHtml(entry.basho)}"${selectedAttr}>${escapeHtml(entry.label)}</option>`;
      }),
      '</select>',
      '</label>'
    ].join("");
  }

  function renderDivisionSelect() {
    return [
      '<label class="filter-control">',
      '<span>Division</span>',
      '<select name="division">',
      '<option value="makuuchi" selected>Makuuchi</option>',
      '</select>',
      '</label>'
    ].join("");
  }

  function renderCheckbox(name, label) {
    return [
      '<label class="checkbox-control">',
      `<input type="checkbox" name="${escapeHtml(name)}">`,
      `<span>${escapeHtml(label)}</span>`,
      '</label>'
    ].join("");
  }

  function renderTable(rows) {
    return [
      '<table class="brb-table">',
      '<thead><tr>',
      ...VISIBLE_COLUMNS.map(([, label]) => `<th>${escapeHtml(label)}</th>`),
      '</tr></thead>',
      '<tbody>',
      ...rows.map(row => [
        '<tr>',
        ...VISIBLE_COLUMNS.map(([field]) => `<td>${escapeHtml(row[field] || "")}</td>`),
        '</tr>'
      ].join("")),
      '</tbody>',
      '</table>'
    ].join("");
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
