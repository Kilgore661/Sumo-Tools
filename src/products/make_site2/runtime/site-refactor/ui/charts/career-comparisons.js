// Career Comparisons chart controls, selector and Plotly rendering.

import { escapeHtml } from "../../utils/html.js";
import { PLOTLY_CONFIG } from "./shared.js";

const POINT_DATE = 0;
const POINT_SHIKONA = 1;
const POINT_CHII = 2;
const POINT_EQUELO = 3;
const CHII_LEVELS = ["Y", "O", "S", "K", "M", "J", "Ms", "Sd", "Jd", "Jk"];
const DEFAULT_STATE = {
  selectedRikishiIds: [],
  candidateLimit: 12,
};

let careerComparisonsState = { ...DEFAULT_STATE };

function renderCareerComparisonsPanel(artifact, state, data) {
  const options = careerComparisonRikishiOptions(data);
  return [
    renderCareerComparisonsControls(state),
    '<section class="pa-panel">',
    '<div class="pa-slot">',
    renderCareerComparisonsChart(artifact, data, options),
    '</div>',
    '</section>',
  ].join("");
}

function renderCareerComparisonsControls(state) {
  return [
    '<form class="filter-section career-comparisons-controls" aria-label="Career comparison options">',
    '<h4>Options</h4>',
    '<fieldset class="career-comparison-mode-fieldset">',
    '<legend class="visually-hidden">Chart</legend>',
    '<table class="career-comparison-mode-table">',
    '<thead><tr><th></th><th scope="col">Date</th><th scope="col">Hatsu</th></tr></thead>',
    '<tbody>',
    ...["chii", "equelo"].map(skill => [
      '<tr>',
      `<th scope="row">${escapeHtml(skillLabel(skill))}</th>`,
      ...["date", "basho"].map(xBase => `<td>${renderModeChoice(skill, xBase, state)}</td>`),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
    '</fieldset>',
    '<label class="checkbox-control career-comparison-log-control">',
    `<input type="checkbox" name="log"${state.log ? " checked" : ""}>`,
    '<span>Log</span>',
    '</label>',
    '<div class="career-comparison-selector">',
    '<label class="filter-control career-comparison-search">',
    '<span>Rikishi</span>',
    '<input type="search" name="rikishi_search" autocomplete="off" list="career-comparison-candidates">',
    '</label>',
    '<datalist id="career-comparison-candidates"></datalist>',
    '<ul class="career-comparison-selected" aria-label="Selected rikishi"></ul>',
    '<button type="submit" class="career-comparison-go">Go</button>',
    '</div>',
    '</form>',
  ].join("");
}

function renderModeChoice(skill, xBase, state) {
  const id = `career-comparison-${skill}-${xBase}`;
  const checked = state.skill === skill && state.x_base === xBase ? " checked" : "";
  return [
    '<label class="radio-control career-comparison-mode">',
    `<input id="${id}" type="radio" name="career_comparison_mode" value="${skill}:${xBase}"${checked}>`,
    `<span class="visually-hidden">${escapeHtml(modeLabel(skill, xBase))}</span>`,
    '</label>',
  ].join("");
}

function modeLabel(skill, xBase) {
  const skillText = skillLabel(skill);
  const xLabel = xBase === "basho" ? "Basho" : "Date";
  return `${skillText} / ${xLabel}`;
}

function skillLabel(skill) {
  return skill === "equelo" ? "Equelo" : "Chii";
}

function renderCareerComparisonsChart(artifact, data, options = null) {
  const resolvedOptions = options || careerComparisonRikishiOptions(data);
  if (!resolvedOptions.length) return "<p>No Career Comparisons data is available.</p>";
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<div id="career-comparisons-chart" class="plotly-chart"></div>',
  ].join("");
}

function wireCareerComparisonsControls(panel, artifact, state, data, writeState) {
  const form = document.querySelector(".career-comparisons-controls");
  if (!form) return;
  readCareerComparisonSelectionFromUrl(data);
  const options = careerComparisonRikishiOptions(data);
  const optionsByLabel = new Map(options.map(option => [option.label, option]));
  const optionsById = new Map(options.map(option => [option.id, option]));
  const input = form.elements.rikishi_search;
  const datalist = form.querySelector("#career-comparison-candidates");
  const selectedList = form.querySelector(".career-comparison-selected");

  updateCareerComparisonCandidates(input, datalist, options);
  renderSelectedRikishiList(selectedList, optionsById);
  renderCareerComparisonsPlot(artifact, state, data);

  input.addEventListener("input", () => {
    if (consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById)) {
      return;
    }
    updateCareerComparisonCandidates(input, datalist, options);
  });
  input.addEventListener("change", () => {
    consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById);
  });
  selectedList.addEventListener("click", event => {
    const button = event.target.closest("button[data-rikishi-id]");
    if (!button) return;
    careerComparisonsState.selectedRikishiIds = careerComparisonsState.selectedRikishiIds
      .filter(id => id !== button.dataset.rikishiId);
    renderSelectedRikishiList(selectedList, optionsById);
  });
  form.addEventListener("submit", event => {
    event.preventDefault();
    const nextState = careerComparisonControlState(form, state);
    writeState(panel, nextState);
    writeCareerComparisonSelectionToUrl();
    renderCareerComparisonsPlot(artifact, nextState, data);
  });
}

function careerComparisonControlState(form, state) {
  const checkedMode = form.querySelector("input[name='career_comparison_mode']:checked");
  const [skill, xBase] = String(checkedMode?.value || "chii:date").split(":");
  return {
    ...state,
    skill,
    x_base: xBase,
    log: Boolean(form.elements.log?.checked),
  };
}

function updateCareerComparisonCandidates(input, datalist, options) {
  const query = input.value.trim().toLowerCase();
  const selected = new Set(careerComparisonsState.selectedRikishiIds);
  const matches = options
    .filter(option => !selected.has(option.id))
    .filter(option => !query || option.prefixes.some(prefix => prefix.startsWith(query)))
    .slice(0, careerComparisonsState.candidateLimit);
  datalist.innerHTML = matches
    .map(option => `<option value="${escapeHtml(option.label)}"></option>`)
    .join("");
}

function consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById) {
  const label = input.value.trim();
  if (!optionsByLabel.has(label)) return false;
  addSelectedRikishi(label, optionsByLabel);
  input.value = "";
  input.blur();
  updateCareerComparisonCandidates(input, datalist, options);
  renderSelectedRikishiList(selectedList, optionsById);
  return true;
}

function addSelectedRikishi(label, optionsByLabel) {
  const option = optionsByLabel.get(label);
  if (!option) return;
  if (careerComparisonsState.selectedRikishiIds.includes(option.id)) return;
  careerComparisonsState.selectedRikishiIds = [
    ...careerComparisonsState.selectedRikishiIds,
    option.id,
  ];
}

function renderSelectedRikishiList(selectedList, optionsById) {
  selectedList.innerHTML = careerComparisonsState.selectedRikishiIds
    .map(id => {
      const option = optionsById.get(id);
      if (!option) return "";
      return [
        '<li>',
        `<span>${escapeHtml(option.label)}</span>`,
        `<button type="button" data-rikishi-id="${escapeHtml(id)}" aria-label="Remove ${escapeHtml(option.label)}">X</button>`,
        '</li>',
      ].join("");
    })
    .join("");
}

function renderCareerComparisonsPlot(artifact, state, data) {
  const host = document.getElementById("career-comparisons-chart");
  if (!host) return;
  if (!careerComparisonsState.selectedRikishiIds.length) {
    host.innerHTML = '<p class="career-comparison-empty">Select one or more rikishi, then click Go.</p>';
    return;
  }
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  const traces = careerComparisonTraces(artifact, state, data);
  if (!traces.length) {
    host.innerHTML = '<p class="career-comparison-empty">No plottable points are available for the selected rikishi and chart options.</p>';
    return;
  }
  if (host.querySelector(".career-comparison-empty")) {
    host.innerHTML = "";
  }
  Plotly.react(host, traces, careerComparisonLayout(artifact, state, data), PLOTLY_CONFIG)
    .then(() => attachCareerComparisonLegendHandler(host));
}

function careerComparisonTraces(artifact, state, data) {
  const chiiScale = state.skill === "chii" ? buildChiiScale(artifact, state, data) : null;
  return careerComparisonsState.selectedRikishiIds
    .map(rikishiId => careerComparisonTrace(rikishiId, artifact, state, data, chiiScale))
    .filter(Boolean);
}

function careerComparisonTrace(rikishiId, artifact, state, data, chiiScale) {
  const points = data.points_by_rikishi[rikishiId] || [];
  if (!points.length) return null;
  const x = [];
  const y = [];
  const customdata = [];
  points.forEach((point, index) => {
    const yValue = careerComparisonYValue(point, artifact, state, chiiScale);
    if (yValue === null || yValue === undefined || Number.isNaN(yValue)) return;
    x.push(state.x_base === "basho" ? index : point[POINT_DATE]);
    y.push(yValue);
    customdata.push([
      point[POINT_SHIKONA],
      point[POINT_DATE],
      point[POINT_CHII],
      point[POINT_EQUELO],
    ]);
  });
  if (!x.length) return null;
  return {
    type: "scatter",
    mode: "lines+markers",
    name: displayNameForRikishi(rikishiId, data),
    x,
    y,
    customdata,
    hovertemplate: careerComparisonHoverTemplate(state),
  };
}

function careerComparisonYValue(point, artifact, state, chiiScale) {
  if (state.skill === "equelo") {
    const rating = point[POINT_EQUELO];
    if (rating === null || rating === undefined) return null;
    const value = Number(rating);
    if (!state.log) return value;
    return Math.log(value) / Math.log(Number(artifact.provenance.equelo_log_base));
  }
  const human = humanChii(point[POINT_CHII]);
  return chiiScale.valuesByHuman.get(human);
}

function careerComparisonHoverTemplate(state) {
  const yLabel = state.skill === "equelo"
    ? (state.log ? "log(Equelo)" : "Equelo")
    : "Chii position";
  const xLabel = state.x_base === "basho" ? "Basho from hatsu" : "Date";
  return [
    "Shikona=%{customdata[0]}",
    `${xLabel}=%{x}`,
    "Chii=%{customdata[2]}",
    "Equelo=%{customdata[3]}",
    `${yLabel}=%{y}`,
    "<extra></extra>",
  ].join("<br>");
}

function careerComparisonLayout(artifact, state, data) {
  const yAxis = state.skill === "chii"
    ? chiiAxisLayout(artifact, state, data)
    : {
      title: state.log ? "log(Equelo)" : "Equelo",
      automargin: true,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    };
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 40, t: 18, b: 70 },
    xaxis: {
      title: state.x_base === "basho" ? "Basho from hatsu" : "Date",
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
      tickangle: state.x_base === "date" ? 45 : 0,
    },
    yaxis: yAxis,
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

function chiiAxisLayout(artifact, state, data) {
  const scale = buildChiiScale(artifact, state, data);
  return {
    title: state.log ? "Chii position (compressed)" : "Chii position",
    automargin: true,
    gridcolor: "rgba(127,149,192,0.22)",
    zerolinecolor: "rgba(127,149,192,0.35)",
    color: "#c9d4ee",
    tickmode: "array",
    tickvals: scale.tickValues,
    ticktext: scale.tickLabels,
  };
}

function buildChiiScale(artifact, state, data) {
  const humansByKey = new Map();
  for (const points of Object.values(data.points_by_rikishi || {})) {
    for (const point of points) {
      const parsed = parseChii(point[POINT_CHII]);
      if (!parsed) continue;
      const human = humanChii(point[POINT_CHII]);
      const existing = humansByKey.get(human);
      if (!existing || parsed.sortKey < existing.sortKey) {
        humansByKey.set(human, { human, sortKey: humanChiiSortKey(human) });
      }
    }
  }
  const labels = [...humansByKey.values()]
    .sort((left, right) => left.sortKey - right.sortKey)
    .map(item => item.human);
  if (!state.log) return linearChiiScale(labels);
  return compressedChiiScale(labels, Number(artifact.provenance.top_chart_prop));
}

function linearChiiScale(labels) {
  const valuesByHuman = new Map();
  labels.forEach((label, index) => {
    valuesByHuman.set(label, labels.length - index);
  });
  const ticks = sparseChiiTicks(labels, 48);
  return {
    valuesByHuman,
    tickValues: ticks.map(label => valuesByHuman.get(label)),
    tickLabels: ticks,
  };
}

function compressedChiiScale(labels, topProp) {
  const topLabels = labels.filter(label => isSekitoriHumanChii(label));
  const bottomLabels = labels.filter(label => !isSekitoriHumanChii(label));
  const valuesByHuman = new Map();
  topLabels.forEach((label, index) => {
    valuesByHuman.set(label, interpolate(1, 1 - topProp, index, topLabels.length));
  });
  bottomLabels.forEach((label, index) => {
    valuesByHuman.set(label, interpolate(1 - topProp, 0, index, bottomLabels.length));
  });
  const ticks = [
    ...sparseChiiTicks(topLabels, 32),
    ...sparseChiiTicks(bottomLabels, 16),
  ];
  return {
    valuesByHuman,
    tickValues: ticks.map(label => valuesByHuman.get(label)),
    tickLabels: ticks,
  };
}

function interpolate(start, end, index, count) {
  if (count <= 1) return start;
  return start + ((end - start) * index / (count - 1));
}

function sparseChiiTicks(labels, maxLabels) {
  const step = Math.max(1, Math.ceil(labels.length / maxLabels));
  return labels.filter((_, index) => index % step === 0);
}

function isSekitoriHumanChii(label) {
  const parsed = parseChii(label);
  return parsed ? parsed.levelIndex <= CHII_LEVELS.indexOf("J") : false;
}

function humanChii(chii) {
  const parsed = parseChii(chii);
  if (!parsed) return String(chii);
  if (["Y", "O", "S", "K"].includes(parsed.level)) return parsed.level;
  return `${parsed.level}${parsed.number}`;
}

function humanChiiSortKey(human) {
  const parsed = parseChii(human);
  if (!parsed) {
    const levelIndex = CHII_LEVELS.indexOf(human);
    return levelIndex < 0 ? Number.MAX_SAFE_INTEGER : levelIndex * 1000;
  }
  return parsed.levelIndex * 1000 + parsed.number;
}

function parseChii(chii) {
  const match = String(chii || "").match(/^(Ms|Sd|Jd|Jk|Y|O|S|K|M|J)(\d*)/);
  if (!match) return null;
  const level = match[1];
  const levelIndex = CHII_LEVELS.indexOf(level);
  const number = match[2] ? Number(match[2]) : 1;
  return {
    level,
    levelIndex,
    number,
    sortKey: levelIndex * 1000 + number,
  };
}

function careerComparisonRikishiOptions(data) {
  const rows = Object.entries(data.points_by_rikishi || {}).map(([id, points]) => {
    const lastPoint = points[points.length - 1] || [];
    return { id, shikona: String(lastPoint[POINT_SHIKONA] || id) };
  });
  const counts = new Map();
  rows.forEach(row => counts.set(row.shikona, (counts.get(row.shikona) || 0) + 1));
  return rows
    .map(row => {
      const label = counts.get(row.shikona) > 1 ? `${row.shikona} (${row.id})` : row.shikona;
      return {
        ...row,
        label,
        prefixes: [label, row.shikona, row.id].map(value => String(value).toLowerCase()),
      };
    })
    .sort((left, right) => left.label.localeCompare(right.label));
}

function readCareerComparisonSelectionFromUrl(data) {
  const params = new URLSearchParams(window.location.search);
  const ids = String(params.get("rikishi") || "")
    .split(",")
    .map(value => value.trim())
    .filter(Boolean);
  const knownIds = new Set(Object.keys(data.points_by_rikishi || {}));
  careerComparisonsState.selectedRikishiIds = ids.filter(id => knownIds.has(id));
}

function writeCareerComparisonSelectionToUrl() {
  const url = new URL(window.location.href);
  if (careerComparisonsState.selectedRikishiIds.length) {
    url.searchParams.set("rikishi", careerComparisonsState.selectedRikishiIds.join(","));
  } else {
    url.searchParams.delete("rikishi");
  }
  history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
}

function displayNameForRikishi(rikishiId, data) {
  const options = careerComparisonRikishiOptions(data);
  return options.find(option => option.id === rikishiId)?.label || rikishiId;
}

function attachCareerComparisonLegendHandler(host) {
  if (!host.on) return;
  if (host.__careerComparisonHandlersAttached) return;
  host.__careerComparisonHandlersAttached = true;
  host.on("plotly_legenddoubleclick", event => {
    const visibility = host.data.map((_, index) =>
      index === event.curveNumber ? true : "legendonly"
    );
    Plotly.restyle(host, { visible: visibility });
    return false;
  });
}

function resetCareerComparisonsState() {
  careerComparisonsState = { ...DEFAULT_STATE };
}

export {
  renderCareerComparisonsPanel,
  renderCareerComparisonsControls,
  renderCareerComparisonsChart,
  wireCareerComparisonsControls,
  renderCareerComparisonsPlot,
  careerComparisonTraces,
  careerComparisonTrace,
  careerComparisonYValue,
  careerComparisonLayout,
  chiiAxisLayout,
  buildChiiScale,
  linearChiiScale,
  compressedChiiScale,
  humanChii,
  humanChiiSortKey,
  parseChii,
  careerComparisonRikishiOptions,
  readCareerComparisonSelectionFromUrl,
  writeCareerComparisonSelectionToUrl,
  resetCareerComparisonsState,
};
