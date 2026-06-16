// Career Length chart/table runtime view handling.

import { currentTableSortState, decimal, renderRikishiLink, renderTableHeading, sortRows, wireTableSorting } from "../tables.js";
import { escapeHtml } from "../../utils/html.js";
import { PLOTLY_CONFIG } from "./shared.js";

const CAREER_LENGTH_LONGEST_TABLE_ID = "career_length:longest";

// Render the selected Career Length view, which may be a table or Plotly host.
function renderCareerLengthArtifact(artifact, state, rowsBySource) {
  const view = careerLengthView(artifact, state.view);
  if (view.kind === "table") {
    return renderCareerLengthTable(view, rowsBySource[state.view] || [], state);
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

// Render the tabular Career Length view.
function renderCareerLengthTable(view, rows, state) {
  const columns = careerLengthTableColumns(view);
  const visibleRows = careerLengthRowsForState(rows, state);
  const sortState = currentTableSortState(careerLengthTableArtifact(columns), "rank");
  const sortedRows = sortRows(visibleRows, columns, sortState);
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(view.label)}</h4>`,
    '</div>',
    '<table class="artifact-table">',
    '<thead><tr>',
    ...columns.map(column => renderTableHeading(column, sortState)),
    '</tr></thead>',
    '<tbody>',
    ...sortedRows.map((row, index) => [
      '<tr>',
      ...columns.map(column =>
        `<td ${careerLengthCellAttributes(column)}>${careerLengthCellValue(column, row, index)}</td>`
      ),
      '</tr>'
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function careerLengthRowsForState(rows, state) {
  const population = state.show_active ? "all" : "non_active";
  return rows.filter(row => (row.longest_population || "all") === population);
}

function careerLengthTableColumns(view) {
  return [
    { id: "row_number", heading: "", sort_kind: "none", align: "right", role: "row_number" },
    ...(view.columns || [])
      .filter(column => column.id !== "active")
      .map(column => careerLengthColumn(column)),
  ];
}

function careerLengthColumn(column) {
  if (column.id === "rank") {
    return { ...column, sort_kind: "numeric", sort_key: column.source_field || column.id, sort_default_direction: "ascending" };
  }
  if (column.id === "shikona") {
    return { ...column, sort_kind: "text", sort_key: column.source_field || column.id };
  }
  if (column.id === "participation_years" || column.id === "gap_basho_count") {
    return { ...column, sort_kind: "numeric", sort_key: column.source_field || column.id };
  }
  return { ...column, sort_kind: "text", sort_key: column.source_field || column.id };
}

function careerLengthTableArtifact(columns) {
  return {
    id: CAREER_LENGTH_LONGEST_TABLE_ID,
    columns,
    default_sort_column: "rank",
  };
}

function careerLengthCellAttributes(column) {
  return `data-column-id="${escapeHtml(column.id)}"`;
}

function wireCareerLengthTableSorting(panel, renderPanel) {
  const columns = careerLengthTableColumns(careerLengthViewForSorting());
  wireTableSorting(panel, careerLengthTableArtifact(columns), renderPanel, columns);
}

function careerLengthViewForSorting() {
  return {
    columns: [
      { id: "rank", heading: "#", source_field: "rank" },
      { id: "shikona", heading: "Shikona", source_field: "shikona" },
      { id: "first_appearance", heading: "First", source_field: "first_appearance" },
      { id: "last_appearance", heading: "Last", source_field: "last_appearance" },
      { id: "participation_years", heading: "Years", source_field: "participation_years" },
      { id: "gap_basho_count", heading: "Bg", source_field: "gap_basho_count" },
    ],
  };
}

// Populate the Career Length chart host when the selected view is graphical.
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
    PLOTLY_CONFIG
  );
}

// Convert a Career Length chart view into Plotly traces.
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
  if (column.id === "row_number") return String(index + 1);
  const value = row[column.source_field || column.id] || "";
  if (column.id === "shikona") return renderRikishiLink(value, row.rikishi_id);
  if (column.formatter === "decimal_2") return decimal(value, 2);
  return escapeHtml(value);
}

function isActiveRikishi(value) {
  return value === true || value === "True" || value === "true" || value === "1" || value === "Yes";
}

export {
  renderCareerLengthArtifact,
  renderCareerLengthTable,
  renderCareerLengthPlot,
  wireCareerLengthTableSorting,
  careerLengthTraces,
  careerLengthLayout,
  resolveCareerLengthView,
  careerLengthView,
  careerLengthCellValue,
  careerLengthRowsForState,
  careerLengthTableColumns,
  isActiveRikishi,
};
