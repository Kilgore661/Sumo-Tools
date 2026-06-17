// Career Comparisons chart controls, selector and Plotly rendering.

import { escapeHtml } from "../../utils/html.js";
import { dateLikeDisplay } from "../../utils/display.js";
import { renderLabelWithHelp } from "../help.js";
import { PLOTLY_CONFIG, axisTitle } from "./shared.js";

const POINT_DATE = 0;
const POINT_SHIKONA = 1;
const POINT_CHII = 2;
const POINT_EQUELO = 3;
const FLOAT_DP = 2;
const CHII_LEVELS = ["Y", "O", "S", "K", "M", "J", "Ms", "Sd", "Jd", "Jk"];
const CAREER_COMPARISON_TRACE_COLOURS = [
  "#1f77b4",
  "#ff7f0e",
  "#2ca02c",
  "#d62728",
  "#9467bd",
  "#8c564b",
  "#e377c2",
  "#7f7f7f",
  "#bcbd22",
  "#17becf",
];
const DEFAULT_STATE = {
  selectedRikishiIds: [],
  candidateLimit: 12,
};

let careerComparisonsState = { ...DEFAULT_STATE };
let careerComparisonSession = createCareerComparisonSession();

function createCareerComparisonSession() {
  return {
    traceColoursByRikishiId: new Map(),
    nextTraceColourIndex: 0,
  };
}

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
    `<thead><tr><th></th><th scope="col">${renderLabelWithHelp("Date", "Use calendar date on the x-axis.")}</th><th scope="col">${renderLabelWithHelp("Hatsu", "Use basho since first appearance on the x-axis.")}</th></tr></thead>`,
    '<tbody>',
    ...["chii", "equelo", "both"].map(skill => [
      '<tr>',
      `<th scope="row">${renderLabelWithHelp(skillLabel(skill), skillHelp(skill))}</th>`,
      ...["date", "basho"].map(xBase => `<td>${renderModeChoice(skill, xBase, state)}</td>`),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
    '</fieldset>',
    '<label class="checkbox-control career-comparison-log-control">',
    `<input type="checkbox" name="log"${state.log ? " checked" : ""}>`,
    `<span>${renderLabelWithHelp("Compress", "Compress lower banzuke divisions.")}</span>`,
    '</label>',
    '<div class="career-comparison-selector">',
    '<label class="filter-control career-comparison-search">',
    '<span>Rikishi</span>',
    '<input type="text" name="rikishi_search" autocomplete="off" list="career-comparison-candidates" autofocus tabindex="0">',
    '</label>',
    '<datalist id="career-comparison-candidates"></datalist>',
    '<ul class="career-comparison-selected" aria-label="Selected rikishi"></ul>',
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
  const xLabel = xBase === "basho" ? "Hatsu" : "Date";
  return `${skillText} / ${xLabel}`;
}

function skillLabel(skill) {
  if (skill === "both") return "Both";
  return skill === "equelo" ? "Equelo" : "Chii";
}

function skillHelp(skill) {
  if (skill === "both") return "Show chii and rating together.";
  if (skill === "equelo") return "Show rating achieved.";
  return "Show chii achieved.";
}

function renderCareerComparisonsChart(artifact, data, options = null) {
  const resolvedOptions = options || careerComparisonRikishiOptions(data);
  if (!resolvedOptions.length) return "<p>No Rikishi History data is available.</p>";
  return [
    '<div class="artifact-title-block">',
    `<h4 id="career-comparisons-pa-heading">${escapeHtml(artifact.heading)}</h4>`,
    '<h5 id="career-comparisons-pa-subheading" hidden></h5>',
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
  const applyState = () => {
    const nextState = careerComparisonControlState(form, state);
    Object.assign(state, nextState);
    writeState(panel, nextState);
    writeCareerComparisonSelectionToUrl();
    renderCareerComparisonsPlot(artifact, nextState, data);
  };

  updateCareerComparisonCandidates(input, datalist, options);
  renderSelectedRikishiList(selectedList, optionsById);
  renderCareerComparisonsPlot(artifact, state, data);
  focusCareerComparisonSearch(input);

  input.addEventListener("input", () => {
    enableCareerComparisonDatalist(input);
    if (consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById)) {
      applyState();
      return;
    }
    updateCareerComparisonCandidates(input, datalist, options);
  });
  input.addEventListener("change", () => {
    enableCareerComparisonDatalist(input);
    if (consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById)) {
      applyState();
    }
  });
  selectedList.addEventListener("click", event => {
    const button = event.target.closest("button[data-rikishi-id]");
    if (!button) return;
    careerComparisonsState.selectedRikishiIds = careerComparisonsState.selectedRikishiIds
      .filter(id => id !== button.dataset.rikishiId);
    renderSelectedRikishiList(selectedList, optionsById);
    applyState();
  });
  form.addEventListener("change", event => {
    const control = event.target;
    if (control.name === "career_comparison_mode" || control.name === "log") {
      applyState();
    }
  });
  form.addEventListener("submit", event => {
    event.preventDefault();
    applyState();
  });
}

function focusCareerComparisonSearch(input) {
  const focus = () => {
    if (document.activeElement === input) return;
    input.focus();
    try {
      input.setSelectionRange(input.value.length, input.value.length);
    } catch {
      // Search inputs can reject selection APIs in some browser states.
    }
  };
  requestAnimationFrame(focus);
  for (const delay of [50, 150, 400]) {
    setTimeout(focus, delay);
  }
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
  input.removeAttribute("list");
  datalist.innerHTML = "";
  updateCareerComparisonCandidates(input, datalist, options);
  renderSelectedRikishiList(selectedList, optionsById);
  return true;
}

function enableCareerComparisonDatalist(input) {
  if (!input.hasAttribute("list")) {
    input.setAttribute("list", "career-comparison-candidates");
  }
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
  updateCareerComparisonCaption(artifact, data);
  if (!careerComparisonsState.selectedRikishiIds.length) {
    host.innerHTML = '<p class="career-comparison-empty">Select one or more rikishi.</p>';
    return;
  }
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  host.classList.toggle("career-comparisons-chii-axis", usesChiiAxis(state));
  const traces = careerComparisonTraces(artifact, state, data);
  if (!traces.length) {
    host.innerHTML = '<p class="career-comparison-empty">No plottable points are available for the selected rikishi and chart options.</p>';
    return;
  }
  if (host.querySelector(".career-comparison-empty")) {
    host.innerHTML = "";
  }
  Plotly.react(host, traces, careerComparisonLayout(artifact, state, data, traces), PLOTLY_CONFIG)
    .then(() => {
      attachCareerComparisonLegendHandler(host);
    });
}

function updateCareerComparisonCaption(artifact, data) {
  const heading = document.getElementById("career-comparisons-pa-heading");
  const subheading = document.getElementById("career-comparisons-pa-subheading");
  if (!heading || !subheading) return;
  const caption = careerComparisonCaption(artifact, data);
  heading.textContent = caption.heading;
  subheading.textContent = caption.subheading;
  subheading.hidden = !caption.subheading;
}

function careerComparisonCaption(artifact, data) {
  const selectedIds = careerComparisonsState.selectedRikishiIds;
  if (!selectedIds.length) return { heading: artifact.heading, subheading: "" };
  const names = selectedIds.map(id => displayNameForRikishi(id, data));
  const dates = selectedIds
    .flatMap(id => data.points_by_rikishi[id] || [])
    .map(point => String(point[POINT_DATE] || ""))
    .filter(Boolean)
    .sort();
  return {
    heading: `Career History for ${formatNameList(names)}`,
    subheading: dates.length ? `(${dateLikeDisplay(dates[0])} to ${dateLikeDisplay(dates[dates.length - 1])})` : "",
  };
}

function formatNameList(names) {
  if (names.length <= 2) return names.join(" and ");
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

function careerComparisonTraces(artifact, state, data) {
  const chiiScale = usesChiiAxis(state) ? buildChiiScale(artifact, state, data) : null;
  const seriesSpecs = careerComparisonSeriesSpecs(state);
  return careerComparisonsState.selectedRikishiIds
    .flatMap(rikishiId => seriesSpecs
      .map(series => careerComparisonTrace(rikishiId, artifact, state, data, chiiScale, series))
    )
    .filter(Boolean);
}

function careerComparisonSeriesSpecs(state) {
  if (state.skill === "both") {
    return [
      { skill: "chii", suffix: "Chii", yaxis: "y", dash: "solid" },
      { skill: "equelo", suffix: "Equelo", yaxis: "y2", dash: "dot" },
    ];
  }
  return [
    {
      skill: state.skill,
      suffix: null,
      yaxis: "y",
      dash: "solid",
    },
  ];
}

function careerComparisonTrace(rikishiId, artifact, state, data, chiiScale, series = null) {
  const resolvedSeries = series || careerComparisonSeriesSpecs(state)[0];
  const points = data.points_by_rikishi[rikishiId] || [];
  if (!points.length) return null;
  const x = [];
  const y = [];
  const customdata = [];
  points.forEach((point, index) => {
    const yValue = careerComparisonYValue(point, artifact, state, chiiScale, resolvedSeries.skill);
    if (yValue === null || yValue === undefined || Number.isNaN(yValue)) return;
    x.push(state.x_base === "basho" ? index : dateLikeDisplay(point[POINT_DATE]));
    y.push(yValue);
    customdata.push([
      point[POINT_SHIKONA],
      dateLikeDisplay(point[POINT_DATE]),
      point[POINT_CHII],
      formatOptionalFloat(point[POINT_EQUELO]),
    ]);
  });
  if (!x.length) return null;
  return {
    type: "scatter",
    mode: "lines",
    name: careerComparisonTraceName(rikishiId, data, resolvedSeries),
    yaxis: resolvedSeries.yaxis,
    line: { color: careerComparisonTraceColour(rikishiId), dash: resolvedSeries.dash },
    x,
    y,
    customdata,
    hovertemplate: careerComparisonHoverTemplate(state, resolvedSeries.skill),
  };
}

function careerComparisonTraceName(rikishiId, data, series) {
  const displayName = displayNameForRikishi(rikishiId, data);
  return series.suffix ? `${displayName} - ${series.suffix}` : displayName;
}

function careerComparisonTraceColour(rikishiId) {
  if (!careerComparisonSession.traceColoursByRikishiId.has(rikishiId)) {
    const colour = CAREER_COMPARISON_TRACE_COLOURS[
      careerComparisonSession.nextTraceColourIndex % CAREER_COMPARISON_TRACE_COLOURS.length
    ];
    careerComparisonSession.traceColoursByRikishiId.set(rikishiId, colour);
    careerComparisonSession.nextTraceColourIndex += 1;
  }
  return careerComparisonSession.traceColoursByRikishiId.get(rikishiId);
}

function careerComparisonYValue(point, artifact, state, chiiScale, skill = state.skill) {
  if (skill === "equelo") {
    const rating = point[POINT_EQUELO];
    if (rating === null || rating === undefined) return null;
    const value = Number(rating);
    if (!state.log) return value;
    return Math.log(value) / Math.log(Number(artifact.provenance.equelo_log_base));
  }
  const human = humanChii(point[POINT_CHII]);
  return chiiScale.valuesByHuman.get(human);
}

function careerComparisonHoverTemplate(state, skill = state.skill) {
  const yLabel = skill === "equelo"
    ? (state.log ? "log(Equelo)" : "Equelo")
    : (state.log ? "Chii (Compressed)" : "Chii");
  const yFormat = `:.${FLOAT_DP}f`;
  const xLabel = state.x_base === "basho" ? "Number of Basho since Hatsu Dohyo" : "Date";
  const lines = [
    "Shikona=%{customdata[0]}",
    `${xLabel}=%{x}`,
  ];
  if (state.x_base === "basho") {
    lines.push("Date=%{customdata[1]}");
  }
  lines.push(
    "Chii=%{customdata[2]}",
    "Equelo=%{customdata[3]}",
    `${yLabel}=%{y${yFormat}}`,
    "<extra></extra>",
  );
  return lines.join("<br>");
}

function careerComparisonLayout(artifact, state, data, traces = null) {
  const resolvedTraces = traces || careerComparisonTraces(artifact, state, data);
  const yAxes = careerComparisonYAxes(artifact, state, data, resolvedTraces);
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: usesChiiAxis(state) ? 156 : 116, r: 150, t: 18, b: 70 },
    xaxis: {
      title: axisTitle(state.x_base === "basho" ? "Number of Basho since Hatsu Dohyo" : "Date"),
      ...(state.x_base === "date" ? dateAxisCategoryOrder(traces || []) : bashoAxisTickSettings(traces || [])),
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
      tickangle: state.x_base === "date" ? 45 : 0,
    },
    ...yAxes,
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

function careerComparisonYAxes(artifact, state, data, traces) {
  if (state.skill === "both") {
    const chiiTraces = traces.filter(trace => trace.yaxis === "y");
    const equeloTraces = traces.filter(trace => trace.yaxis === "y2");
    return {
      yaxis: chiiAxisLayout(artifact, state, data, chiiTraces),
      yaxis2: {
        ...equeloAxisLayout(state, equeloTraces),
        overlaying: "y",
        side: "right",
      },
    };
  }
  return {
    yaxis: state.skill === "chii"
      ? chiiAxisLayout(artifact, state, data, traces)
      : equeloAxisLayout(state, traces),
  };
}

function usesChiiAxis(state) {
  return state.skill === "chii" || state.skill === "both";
}

function dateAxisCategoryOrder(traces) {
  return {
    type: "category",
    categoryorder: "array",
    categoryarray: sortedTraceDates(traces),
  };
}

function sortedTraceDates(traces) {
  return [...new Set(traces.flatMap(trace => trace.x || []))]
    .sort((left, right) => String(left).localeCompare(String(right)));
}

function bashoAxisTickSettings(traces) {
  return {
    tick0: 0,
    dtick: integerTickStep(traces.flatMap(trace => trace.x || [])),
    tickformat: "d",
  };
}

function integerTickStep(values) {
  const numbers = values
    .map(value => Number(value))
    .filter(value => Number.isFinite(value));
  if (!numbers.length) return 1;
  const span = Math.max(...numbers) - Math.min(...numbers);
  if (span <= 10) return 1;
  const roughStep = Math.ceil(span / 10);
  const magnitude = 10 ** Math.floor(Math.log10(roughStep));
  for (const multiplier of [1, 2, 5, 10]) {
    const step = multiplier * magnitude;
    if (step >= roughStep) return step;
  }
  return magnitude * 10;
}

function chiiAxisLayout(artifact, state, data, traces = null) {
  const scale = buildChiiScale(artifact, state, data);
  const range = numericTraceRange(traces || [], chiiRangePadding(scale));
  return {
    title: axisTitle(state.log ? "Chii (Compressed)" : "Chii"),
    autorange: range ? false : undefined,
    range,
    automargin: true,
    gridcolor: "rgba(127,149,192,0.22)",
    zerolinecolor: "rgba(127,149,192,0.35)",
    color: "#c9d4ee",
    tickmode: "array",
    tickvals: scale.tickValues,
    ticktext: scale.tickLabels,
    ticklabelstandoff: 24,
  };
}

function equeloAxisLayout(state, traces) {
  const range = numericTraceRange(traces, null);
  return {
    title: axisTitle(state.log ? "log(Equelo)" : "Equelo"),
    autorange: range ? false : undefined,
    range,
    tickformat: equeloTickFormat(state, range),
    automargin: true,
    gridcolor: "rgba(127,149,192,0.22)",
    zerolinecolor: "rgba(127,149,192,0.35)",
    color: "#c9d4ee",
  };
}

function equeloTickFormat(state, range) {
  if (!state.log) return ".0f";
  if (!range) return ".2f";
  const span = Math.abs(Number(range[1]) - Number(range[0]));
  if (!Number.isFinite(span)) return ".2f";
  if (span >= 10) return ".0f";
  if (span >= 1) return ".1f";
  if (span >= 0.1) return ".2f";
  return ".3f";
}

function numericTraceRange(traces, fixedPadding = null) {
  const values = traces
    .flatMap(trace => trace.y || [])
    .map(value => Number(value))
    .filter(value => Number.isFinite(value));
  if (!values.length) return undefined;
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  if (minimum === maximum) {
    const padding = fixedPadding ?? Math.max(1, Math.abs(minimum) * 0.02);
    return [minimum - padding, maximum + padding];
  }
  const padding = fixedPadding ?? (maximum - minimum) * 0.05;
  return [minimum - padding, maximum + padding];
}

function chiiRangePadding(scale) {
  if (scale.kind === "compressed") return 0.02;
  return 0.5;
}

function formatFloatLabel(value) {
  return Number(value).toFixed(FLOAT_DP);
}

function formatOptionalFloat(value) {
  if (value === null || value === undefined || value === "") return "-";
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(FLOAT_DP) : String(value);
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
    kind: "linear",
    tickValues: ticks.map(label => valuesByHuman.get(label)),
    tickLabels: ticks,
  };
}

function compressedChiiScale(labels, topProp) {
  const topLabels = labels.filter(label => isSekitoriHumanChii(label));
  const bottomLabels = labels.filter(label => !isSekitoriHumanChii(label));
  const valuesByHuman = new Map();
  const boundary = 1 - topProp;
  topLabels.forEach((label, index) => {
    valuesByHuman.set(label, interpolate(1, boundary, index, topLabels.length));
  });
  bottomLabels.forEach((label, index) => {
    valuesByHuman.set(label, interpolate(boundary, 0, index, bottomLabels.length));
  });
  const ticks = spacedChiiTicks(labels, valuesByHuman, 0.026);
  return {
    valuesByHuman,
    kind: "compressed",
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

function spacedChiiTicks(labels, valuesByHuman, minimumGap) {
  const ticks = [];
  let previousValue = Number.POSITIVE_INFINITY;
  for (const label of labels) {
    const value = valuesByHuman.get(label);
    if (value === undefined) continue;
    if (previousValue - value >= minimumGap || ticks.length === 0) {
      ticks.push(label);
      previousValue = value;
    }
  }
  const finalLabel = labels[labels.length - 1];
  if (finalLabel && !ticks.includes(finalLabel)) {
    const finalValue = valuesByHuman.get(finalLabel);
    const previousFinalValue = valuesByHuman.get(ticks[ticks.length - 1]);
    if (
      finalValue !== undefined &&
      previousFinalValue !== undefined &&
      previousFinalValue - finalValue >= minimumGap
    ) {
      ticks.push(finalLabel);
    }
  }
  return ticks;
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
  return rows
    .map(row => {
      const label = row.shikona;
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
  careerComparisonSession = createCareerComparisonSession();
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
  careerComparisonTraceColour,
  careerComparisonLayout,
  dateAxisCategoryOrder,
  sortedTraceDates,
  chiiAxisLayout,
  equeloAxisLayout,
  numericTraceRange,
  chiiRangePadding,
  formatFloatLabel,
  formatOptionalFloat,
  buildChiiScale,
  linearChiiScale,
  compressedChiiScale,
  humanChii,
  humanChiiSortKey,
  spacedChiiTicks,
  parseChii,
  careerComparisonRikishiOptions,
  readCareerComparisonSelectionFromUrl,
  writeCareerComparisonSelectionToUrl,
  resetCareerComparisonsState,
};
