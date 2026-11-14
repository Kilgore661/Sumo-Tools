import { escapeHtml } from "../../utils/html.js";
import { PLOTLY_CONFIG, axisTitle } from "./shared.js";

const COLORS = ["#ab63fa", "#ef553b", "#636efa", "#00cc96", "#ffa15a", "#19d3f3"];
const SUPPORT = { supported: "#00a651", low: "#ffb000", very_low: "#e31a1c" };
const TRASH_ICON_PATH = "assets/trash.svg";
const EYE_ICON_PATH = "assets/eye.svg";
const EYE_CLOSED_ICON_PATH = "assets/eye-closed.svg";
const state = { selected: [], hidden: new Set(), highlighted: null };

function renderProspectsControls(axis = "age") {
  return [
    '<form class="filter-section career-comparisons-controls prospects-controls" aria-label="Prospect chart options">',
    '<h4>Options</h4>',
    '<fieldset class="career-comparison-mode-fieldset"><legend class="visually-hidden">X-axis</legend>',
    '<table class="career-comparison-mode-table">',
    '<thead><tr><th></th><th scope="col">Age</th><th scope="col">Date</th></tr></thead>',
    '<tbody><tr><th scope="row">X-axis</th>',
    renderAxisChoice("age", axis), renderAxisChoice("date", axis),
    '</tr></tbody></table></fieldset>',
    '<div class="career-comparison-selector">',
    '<span class="career-comparison-selector-caption">Selected Rikishi</span>',
    '<ul class="career-comparison-selected prospects-selected" aria-label="Selected rikishi"></ul>',
    '<div class="filter-control career-comparison-search"><label for="prospects-rikishi-search">Add</label>',
    '<div class="career-comparison-combobox">',
    '<input id="prospects-rikishi-search" type="text" name="rikishi_search" autocomplete="off" role="combobox" aria-autocomplete="list" aria-haspopup="listbox" aria-expanded="false" aria-controls="prospects-rikishi-candidates" autofocus tabindex="0">',
    '<ul id="prospects-rikishi-candidates" class="career-comparison-candidates" role="listbox" hidden></ul>',
    '</div></div></div></form>',
  ].join("");
}

function renderAxisChoice(value, selected) {
  const checked = value === selected ? " checked" : "";
  return `<td><label class="radio-control career-comparison-mode"><input type="radio" name="prospects_x" value="${value}"${checked}><span class="visually-hidden">${value}</span></label></td>`;
}

function renderProspectsChart(artifact = { heading: "San'yaku Prospects" }) {
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<div id="prospects-chart" class="plotly-chart" aria-label="San\'yaku prospects chart"></div>',
  ].join("");
}

function prospectsRikishiOptions(data) {
  return (data.rikishi || []).map(item => ({
    id: String(item.id),
    label: String(item.shikona || item.id),
    prefixes: [item.shikona, item.id].map(value => String(value).toLowerCase()),
  })).sort((left, right) => left.label.localeCompare(right.label) || Number(left.id) - Number(right.id));
}

function wireProspectsControls(artifact, data) {
  const form = document.querySelector(".prospects-controls");
  if (!form) return;
  const params = new URLSearchParams(window.location.search);
  state.selected = (params.get("rikishi") || "").split(",").filter(id => data.points_by_rikishi[id]);
  state.hidden = new Set([...state.hidden].filter(id => state.selected.includes(id)));
  const axis = params.get("x") === "date" ? "date" : "age";
  form.querySelector(`[name="prospects_x"][value="${axis}"]`).checked = true;
  const options = prospectsRikishiOptions(data);
  const optionsById = new Map(options.map(option => [option.id, option]));
  const input = form.elements.rikishi_search;
  const candidateList = form.querySelector("#prospects-rikishi-candidates");
  const selectedList = form.querySelector(".prospects-selected");

  const closeCandidates = () => {
    state.highlighted = null;
    candidateList.hidden = true;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  };
  const refreshCandidates = open => {
    const query = input.value.trim().toLowerCase();
    const selected = new Set(state.selected);
    const matches = options
      .filter(option => !selected.has(option.id))
      .filter(option => !query || option.prefixes.some(prefix => prefix.startsWith(query)))
      .slice(0, 50);
    candidateList.innerHTML = matches.map(option => [
      `<li id="prospects-candidate-${option.id}" role="option" data-rikishi-id="${option.id}" aria-selected="false">`,
      escapeHtml(prospectsCandidateLabel(option, options)), '</li>',
    ].join("")).join("");
    if (!matches.some(option => option.id === state.highlighted)) state.highlighted = null;
    setCandidateHighlight(candidateList, input, state.highlighted);
    const expanded = open && matches.length > 0;
    candidateList.hidden = !expanded;
    input.setAttribute("aria-expanded", String(expanded));
    return matches;
  };
  const refreshSelected = () => {
    selectedList.innerHTML = state.selected.length ? state.selected.map(id => {
      const option = optionsById.get(id);
      const label = option?.label || id;
      const checked = state.hidden.has(id) ? "" : " checked";
      return [
        '<li><span class="career-comparison-selected-row">',
        `<a class="shikona-link" href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(id)}" target="_blank" rel="noopener">${escapeHtml(label)}</a>`,
        `<button type="button" class="career-comparison-remove-control" data-prospects-remove="${id}" aria-label="Remove ${escapeHtml(label)}" title="Remove ${escapeHtml(label)}"><img class="career-comparison-remove-icon" src="${TRASH_ICON_PATH}" alt="" aria-hidden="true" draggable="false"></button>`,
        `<label class="career-comparison-visibility-control" title="Show/hide ${escapeHtml(label)}"><input type="checkbox" data-rikishi-visible-id="${id}" data-prospects-visible="${id}"${checked} aria-label="Show ${escapeHtml(label)}"><img class="career-comparison-visibility-icon career-comparison-visibility-icon-on" src="${EYE_ICON_PATH}" alt="" aria-hidden="true" draggable="false"><img class="career-comparison-visibility-icon career-comparison-visibility-icon-off" src="${EYE_CLOSED_ICON_PATH}" alt="" aria-hidden="true" draggable="false"></label>`,
        '</span></li>',
      ].join("");
    }).join("") : '<li class="career-comparison-selected-empty">(None.)</li>';
  };
  const draw = () => {
    const x = form.querySelector('[name="prospects_x"]:checked')?.value || "age";
    writeUrl(x);
    renderProspectsPlot(artifact, data, state.selected, x, state.hidden);
    refreshSelected();
    refreshCandidates(document.activeElement === input);
  };
  const commit = option => {
    if (!option || state.selected.includes(option.id)) return;
    state.selected.push(option.id);
    state.hidden.delete(option.id);
    input.value = "";
    closeCandidates();
    draw();
    input.focus();
  };

  refreshSelected();
  refreshCandidates(false);
  renderProspectsPlot(artifact, data, state.selected, axis, state.hidden);
  focusProspectsSearch(input);
  input.addEventListener("input", () => { state.highlighted = null; refreshCandidates(true); });
  input.addEventListener("focus", () => refreshCandidates(true));
  input.addEventListener("click", () => refreshCandidates(true));
  input.addEventListener("keydown", event => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const matches = refreshCandidates(true);
      state.highlighted = moveHighlight(matches, state.highlighted, event.key === "ArrowDown" ? 1 : -1);
      setCandidateHighlight(candidateList, input, state.highlighted);
    } else if (event.key === "Escape") {
      event.preventDefault(); closeCandidates();
    } else if (event.key === "Enter") {
      event.preventDefault();
      commit(resolveCandidate(input.value, state.highlighted, options, state.selected));
    }
  });
  input.addEventListener("blur", closeCandidates);
  candidateList.addEventListener("pointerdown", event => {
    if (event.target.closest("[data-rikishi-id]")) event.preventDefault();
  });
  candidateList.addEventListener("click", event => {
    const candidate = event.target.closest("[data-rikishi-id]");
    if (candidate) commit(optionsById.get(candidate.dataset.rikishiId));
  });
  selectedList.addEventListener("click", event => {
    const button = event.target.closest("[data-prospects-remove]");
    if (!button) return;
    const id = button.dataset.prospectsRemove;
    state.selected = state.selected.filter(value => value !== id);
    state.hidden.delete(id);
    draw();
  });
  selectedList.addEventListener("change", event => {
    const control = event.target.closest("[data-prospects-visible]");
    if (!control) return;
    const id = control.dataset.prospectsVisible;
    if (control.checked) state.hidden.delete(id); else state.hidden.add(id);
    setProspectsVisibility(document.getElementById("prospects-chart"), id, control.checked);
  });
  form.addEventListener("change", event => {
    if (event.target.name === "prospects_x") draw();
  });
  form.addEventListener("submit", event => event.preventDefault());
}

function focusProspectsSearch(input) {
  const focus = () => { if (document.activeElement !== input) input.focus(); };
  requestAnimationFrame(focus);
  for (const delay of [50, 150, 400]) setTimeout(focus, delay);
}

function setCandidateHighlight(list, input, rikishiId) {
  list.querySelectorAll("[role='option']").forEach(candidate => {
    const active = candidate.dataset.rikishiId === rikishiId;
    candidate.setAttribute("aria-selected", String(active));
    candidate.classList.toggle("career-comparison-candidate-active", active);
    if (active) candidate.scrollIntoView({ block: "nearest" });
  });
  if (rikishiId) input.setAttribute("aria-activedescendant", `prospects-candidate-${rikishiId}`);
  else input.removeAttribute("aria-activedescendant");
}

function moveHighlight(options, currentId, direction) {
  if (!options.length) return null;
  const index = options.findIndex(option => option.id === currentId);
  if (index < 0) return direction > 0 ? options[0].id : options[options.length - 1].id;
  return options[(index + direction + options.length) % options.length].id;
}

function resolveCandidate(query, highlightedId, options, selectedIds) {
  const selected = new Set(selectedIds);
  if (highlightedId && !selected.has(highlightedId)) return options.find(option => option.id === highlightedId);
  const canonical = query.trim().toLowerCase();
  const matches = options.filter(option => !selected.has(option.id)).filter(option =>
    option.id === canonical || prospectsCandidateLabel(option, options).toLowerCase() === canonical
  );
  return matches.length === 1 ? matches[0] : null;
}

function prospectsCandidateLabel(option, options) {
  const duplicates = options.filter(candidate => candidate.label.toLowerCase() === option.label.toLowerCase());
  return duplicates.length === 1 ? option.label : `${option.label} (${option.id})`;
}

function writeUrl(axis) {
  const url = new URL(window.location.href);
  url.searchParams.set("x", axis);
  if (state.selected.length) url.searchParams.set("rikishi", state.selected.join(","));
  else url.searchParams.delete("rikishi");
  history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
}

function renderProspectsPlot(artifact, data, selected, axis, hidden = new Set()) {
  const host = document.getElementById("prospects-chart");
  if (!host) return;
  if (!selected.length) {
    if (window.Plotly && host.on) Plotly.purge(host);
    host.innerHTML = '<p class="career-comparison-empty">Add one or more rikishi.</p>';
    return;
  }
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  if (host.querySelector(".career-comparison-empty")) host.innerHTML = "";
  const traces = prospectsTraces(data, selected, axis, hidden);
  Plotly.react(host, traces, prospectsLayout(artifact, axis), PLOTLY_CONFIG).then(() => attachProspectsLegendHandler(host));
}

function prospectsLayout(artifact, axis) {
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 116, r: 150, t: 18, b: 70 },
    xaxis: {
      title: axisTitle(axis === "date" ? "Basho date" : "Age at basho (years)"),
      type: axis === "date" ? "date" : "linear", automargin: true,
      gridcolor: "rgba(127,149,192,0.18)", zerolinecolor: "rgba(127,149,192,0.35)", color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle("Historical probability of eventual san'yaku"),
      tickformat: ".0%", range: [0, 1.05], automargin: true,
      gridcolor: "rgba(127,149,192,0.22)", zerolinecolor: "rgba(127,149,192,0.35)", color: "#c9d4ee",
    },
    hovermode: "closest",
    legend: {
      title: { text: artifact.provenance?.legend_title || "Rikishi" },
      orientation: "v", yanchor: "top", y: 1, xanchor: "left", x: 1.02, groupclick: "togglegroup",
    },
    font: { family: "Arial, Helvetica, sans-serif", color: "#ffffff" },
  };
}

function attachProspectsLegendHandler(host) {
  if (!host.on || host.__prospectsLegendHandlerAttached) return;
  host.__prospectsLegendHandlerAttached = true;
  host.on("plotly_legendclick", () => {
    requestAnimationFrame(() => syncProspectsVisibilityFromPlot(host));
  });
  host.on("plotly_restyle", () => syncProspectsVisibilityFromPlot(host));
  host.on("plotly_legenddoubleclick", event => {
    const target = host.data[event.curveNumber]?.meta?.rikishiId;
    if (!target) return false;
    for (const id of state.selected) {
      if (id === target) state.hidden.delete(id); else state.hidden.add(id);
    }
    const visibility = host.data.map(trace => trace.meta?.rikishiId === target ? true : "legendonly");
    Plotly.restyle(host, { visible: visibility });
    syncProspectsVisibilityControls();
    return false;
  });
}

function syncProspectsVisibilityFromPlot(host) {
  for (const id of state.selected) {
    const traces = host.data.filter(trace => trace.meta?.rikishiId === id);
    const visible = traces.some(trace => trace.visible !== false && trace.visible !== "legendonly");
    if (visible) state.hidden.delete(id); else state.hidden.add(id);
  }
  syncProspectsVisibilityControls();
}

function setProspectsVisibility(host, rikishiId, visible) {
  if (!host || !window.Plotly) return;
  const indexes = host.data.map((trace, index) => trace.meta?.rikishiId === rikishiId ? index : null)
    .filter(index => index !== null);
  if (indexes.length) Plotly.restyle(host, { visible: visible ? true : "legendonly" }, indexes);
}

function syncProspectsVisibilityControls() {
  document.querySelectorAll("[data-prospects-visible]").forEach(control => {
    control.checked = !state.hidden.has(control.dataset.prospectsVisible);
  });
}

function prospectsTraces(data, selected, axis, hidden = new Set()) {
  const columns = Object.fromEntries(data.columns.map((name, index) => [name, index]));
  const traces = [];
  selected.forEach((id, careerIndex) => {
    const points = data.points_by_rikishi[id] || [];
    const item = data.rikishi.find(row => String(row.id) === id);
    const color = COLORS[careerIndex % COLORS.length];
    const x = points.map(point => point[columns[axis === "date" ? "date" : "exact_age"]]);
    const y = points.map(point => point[columns.probability]);
    const customdata = points.map(point => data.columns.map((_, index) => point[index]));
    const visible = hidden.has(id) ? "legendonly" : true;
    traces.push({
      type: "scatter", mode: "lines", name: item?.shikona || id, x, y,
      connectgaps: false, line: { color, width: 1 }, legendgroup: id, visible,
      meta: { rikishiId: id }, hoverinfo: "skip",
    });
    for (const [tier, markerColor] of Object.entries(SUPPORT)) {
      const chosen = points.map((point, index) => ({ point, index })).filter(({ point }) =>
        point[columns.point_kind] === "cohort_probability" && point[columns.support_tier] === tier && point[columns.probability] !== null
      );
      if (!chosen.length) continue;
      traces.push({
        type: "scatter", mode: "markers", showlegend: false, legendgroup: id, visible,
        meta: { rikishiId: id }, x: chosen.map(({ index }) => x[index]),
        y: chosen.map(({ index }) => y[index]), customdata: chosen.map(({ index }) => customdata[index]),
        marker: { size: 4, color: markerColor, line: { color: markerColor, width: 0.5 } },
        hoverlabel: { bgcolor: color, bordercolor: color, font: { color: "#fff" } },
        hovertemplate: hoverTemplate(columns, axis),
      });
    }
    const attained = points.map((point, index) => ({ point, index })).filter(({ point }) =>
      point[columns.point_kind] === "sanyaku_attainment"
    );
    if (attained.length) traces.push({
      type: "scatter", mode: "markers", showlegend: false, legendgroup: id, visible,
      meta: { rikishiId: id }, x: attained.map(({ index }) => x[index]), y: attained.map(() => 1),
      customdata: attained.map(({ index }) => customdata[index]),
      marker: { symbol: "star", size: 18, color: "#d4a017", line: { color: "#5b4300", width: 2 } },
      hoverlabel: { bgcolor: color, bordercolor: color, font: { color: "#fff" } },
      hovertemplate: `<b>${escapeHtml(item?.shikona || id)}</b><br>First san'yaku<br>Basho: %{customdata[${columns.basho}]}<br>Rank: %{customdata[${columns.chii}]}<extra></extra>`,
    });
  });
  return traces;
}

function hoverTemplate(c, axis) {
  const ageLine = axis === "age" ? "Exact age: %{x:.2f}<br>" : `Date: %{customdata[${c.date}]}<br>`;
  return `<b>%{customdata[${c.chii}]}</b><br>Basho: %{customdata[${c.basho}]}<br>${ageLine}Completed age: %{customdata[${c.age}]}<br>Probability: %{y:.1%}<br>Successes: %{customdata[${c.cohort_success}]} / %{customdata[${c.cohort_resolved}]} resolved<br>Unresolved: %{customdata[${c.cohort_unresolved}]}<br>Observations: %{customdata[${c.cohort_observations}]}<extra></extra>`;
}

export {
  renderProspectsControls, renderProspectsChart, wireProspectsControls,
  renderProspectsPlot, prospectsTraces, prospectsLayout, prospectsRikishiOptions,
  focusProspectsSearch, moveHighlight, resolveCandidate, prospectsCandidateLabel,
};
