import { escapeHtml } from "../utils/html.js";

const TRANSITIONAL_TABLE_SPEC = [
  group("reference", "Reference", [
    column("row_number", "#"),
    column("shikona", "Shikona"),
  ]),
  group("before", "Before Basho", [
    group("rba", "", [
      column("bp", "BP"),
      column("result", "Result"),
      column("equelo", "Equelo"),
    ]),
  ]),
  group("state", "Current/After", [
    group("rba", "", [
      column("bp", "BP"),
      column("result", "Result"),
      column("equelo", "Equelo"),
      column("next_bp", "nuChii"),
    ]),
  ]),
  group("comparison", "Comparison", [
    column("delta_equelo", "Delta Equelo"),
  ]),
];

function buildBashoResultsPresentationModel({ rows, state, entry, title }) {
  const visiblePaths = bashoResultsVisiblePaths(state);
  return {
    header: bashoResultsHeader(title, entry),
    table_spec: resolveStateHeading(TRANSITIONAL_TABLE_SPEC, entry),
    values: rows.map((row, index) => transitionalRowValues(row, index)),
    projection: { visible_paths: visiblePaths },
  };
}

function renderBashoResultsPresentationTable(model) {
  const visiblePaths = new Set(model.projection?.visible_paths || []);
  const leaves = terminalNodes(model.table_spec || [], [], visiblePaths);
  return [
    renderBashoResultsHeader(model.header),
    '<table class="artifact-table brb-table brb-redesign-table">',
    renderNestedHead(model.table_spec || [], visiblePaths),
    '<tbody>',
    ...(model.values || []).map(row => [
      '<tr>',
      ...leaves.map(leaf => `<td data-column-path="${escapeHtml(leaf.path)}">${escapeHtml(valueAtPath(row, leaf.path))}</td>`),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function bashoResultsHeader(title, entry) {
  return {
    heading: title || "Basho Results",
    subheading: bashoResultsSubheading(entry),
  };
}

function bashoResultsSubheading(entry) {
  const latestDay = Number(entry?.latest_day);
  if (latestDay && latestDay < 15) return `After Day ${latestDay}`;
  return "Final";
}

function resolveStateHeading(spec, entry) {
  const stateHeading = Number(entry?.latest_day) && Number(entry.latest_day) < 15
    ? "Current"
    : "After Basho";
  return spec.map(node => node.key === "state" ? { ...node, label: stateHeading } : node);
}

function bashoResultsVisiblePaths(state) {
  const visible = [
    "reference.row_number",
    "reference.shikona",
    "state.rba.bp",
    "state.rba.result",
  ];
  if (state.previous_context) {
    visible.push("before.rba.bp", "before.rba.result");
  }
  if (state.rating_context) {
    if (state.previous_context) visible.push("before.rba.equelo");
    visible.push("state.rba.equelo", "comparison.delta_equelo");
  }
  if (state.nu_chii) {
    visible.push("state.rba.next_bp");
  }
  return visible;
}

function transitionalRowValues(row, index) {
  return {
    "reference.row_number": String(index + 1),
    "reference.shikona": row.shikona || "",
    "before.rba.bp": row.previous_chii || "",
    "before.rba.result": resultWithMovement(row.previous_result, row.previous_rank_level_movement),
    "before.rba.equelo": row.previous_equelo || "",
    "state.rba.bp": row.chii || "",
    "state.rba.result": row.score || "",
    "state.rba.equelo": row.equelo || "",
    "state.rba.next_bp": row.nu_chii || "",
    "comparison.delta_equelo": row.delta_equelo || "",
  };
}

function resultWithMovement(result, movement) {
  return [result || "", rankLevelMovementMarker(movement)].filter(Boolean).join(" ");
}

function rankLevelMovementMarker(value) {
  if (value === "\u2191" || value === "\u2193") return value;
  return "";
}

function renderBashoResultsHeader(header) {
  if (!header) return "";
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(header.heading || "")}</h4>`,
    header.subheading ? `<p>${escapeHtml(header.subheading)}</p>` : "",
    '</div>',
  ].join("");
}

function renderNestedHead(nodes, visiblePaths) {
  const rows = headerRows(nodes, visiblePaths);
  return [
    '<thead>',
    ...rows.map(row => [
      '<tr>',
      ...row.map(cell => `<th colspan="${cell.colspan}" rowspan="${cell.rowspan}" data-column-path="${escapeHtml(cell.path)}">${escapeHtml(cell.label)}</th>`),
      '</tr>',
    ].join("")),
    '</thead>',
  ].join("");
}

function headerRows(nodes, visiblePaths) {
  const depth = maxDepth(nodes, visiblePaths);
  const rows = Array.from({ length: depth }, () => []);
  appendHeaderCells(rows, nodes, [], visiblePaths, depth, 0);
  return rows;
}

function appendHeaderCells(rows, nodes, path, visiblePaths, depth, level) {
  for (const node of nodes || []) {
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) {
      const childLeaves = terminalNodes(node.children, nextPath, visiblePaths);
      if (!childLeaves.length) continue;
      rows[level].push({
        colspan: childLeaves.length,
        label: node.label || node.key,
        path: pathText,
        rowspan: 1,
      });
      appendHeaderCells(rows, node.children, nextPath, visiblePaths, depth, level + 1);
    } else if (isVisiblePath(pathText, visiblePaths)) {
      rows[level].push({
        colspan: 1,
        label: node.label || node.key,
        path: pathText,
        rowspan: depth - level,
      });
    }
  }
}

function maxDepth(nodes, visiblePaths, path = [], level = 1) {
  const depths = (nodes || []).flatMap(node => {
    const nextPath = [...path, node.key];
    if (node.children) return [maxDepth(node.children, visiblePaths, nextPath, level + 1)];
    return isVisiblePath(nextPath.join("."), visiblePaths) ? [level] : [];
  });
  return Math.max(level, ...depths);
}

function terminalNodes(nodes, path, visiblePaths) {
  return (nodes || []).flatMap(node => {
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) return terminalNodes(node.children, nextPath, visiblePaths);
    return isVisiblePath(pathText, visiblePaths) ? [{ ...node, path: pathText }] : [];
  });
}

function isVisiblePath(path, visiblePaths) {
  return !visiblePaths.size || visiblePaths.has(path);
}

function valueAtPath(row, path) {
  const value = row?.[path];
  if (value === null || value === undefined) return "";
  return String(value);
}

function group(key, label, children) {
  return { key, label, children };
}

function column(key, label) {
  return { key, label };
}

export { buildBashoResultsPresentationModel, renderBashoResultsPresentationTable, terminalNodes, headerRows };
