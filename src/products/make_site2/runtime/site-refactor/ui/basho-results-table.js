import { escapeHtml } from "../utils/html.js";

const TRANSITIONAL_TABLE_SPEC = [
  group("reference", "Reference", [
    column("row_number", "#"),
    column("shikona", "Shikona"),
  ]),
  group("before", "Before Basho", [
    group("rba", "", [
      column("bp", "BP"),
      group("result", "Result", [
        column("wins", "W"),
        column("losses", "L"),
        column("absences", "A"),
        column("prizes", "\u{1F4E6}"),
        column("division_change", "Div"),
      ]),
      column("equelo", "Equelo"),
    ]),
  ]),
  group("state", "Current/After", [
    group("rba", "", [
      column("bp", "BP"),
      group("result", "Result", [
        column("wins", "W"),
        column("losses", "L"),
        column("absences", "A"),
        column("prizes", "\u{1F4E6}"),
        column("division_change", "Div"),
      ]),
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
    "state.rba.result.wins",
    "state.rba.result.losses",
    "state.rba.result.absences",
    "state.rba.result.prizes",
    "state.rba.result.division_change",
  ];
  if (state.previous_context) {
    visible.push(
      "before.rba.bp",
      "before.rba.result.wins",
      "before.rba.result.losses",
      "before.rba.result.absences",
      "before.rba.result.prizes",
      "before.rba.result.division_change",
    );
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
  const beforeResult = parseResult(row.previous_result);
  const stateResult = parseResult(row.score);
  return {
    "reference.row_number": String(index + 1),
    "reference.shikona": row.shikona || "",
    "before.rba.bp": row.previous_chii || "",
    "before.rba.result.wins": beforeResult.wins,
    "before.rba.result.losses": beforeResult.losses,
    "before.rba.result.absences": beforeResult.absences,
    "before.rba.result.prizes": beforeResult.prizes,
    "before.rba.result.division_change": rankLevelMovementMarker(row.previous_rank_level_movement),
    "before.rba.equelo": row.previous_equelo || "",
    "state.rba.bp": row.chii || "",
    "state.rba.result.wins": stateResult.wins,
    "state.rba.result.losses": stateResult.losses,
    "state.rba.result.absences": stateResult.absences,
    "state.rba.result.prizes": stateResult.prizes,
    "state.rba.result.division_change": rankLevelMovementBetween(row.chii, row.nu_chii),
    "state.rba.equelo": row.equelo || "",
    "state.rba.next_bp": row.nu_chii || "",
    "comparison.delta_equelo": row.delta_equelo || "",
  };
}

function parseResult(value) {
  const text = String(value || "").trim();
  const missing = { wins: "", losses: "", absences: "", prizes: "" };
  if (!text || text === "-") return missing;
  const match = text.match(/^(\d+)-(\d+)(?:-(\d+))?(?:\s+(.+))?$/);
  if (!match) return { ...missing, prizes: text };
  return {
    wins: match[1],
    losses: match[2],
    absences: match[3] || "",
    prizes: match[4] || "",
  };
}

function rankLevelMovementMarker(value) {
  if (value === "\u2191" || value === "\u2193") return value;
  if (value === "â†‘") return "\u2191";
  if (value === "â†“") return "\u2193";
  return "";
}

function rankLevelMovementBetween(fromBp, toBp) {
  const fromIndex = rankLevelIndex(fromBp);
  const toIndex = rankLevelIndex(toBp);
  if (fromIndex === null || toIndex === null || fromIndex === toIndex) return "";
  return toIndex < fromIndex ? "\u2191" : "\u2193";
}

function rankLevelIndex(bp) {
  const text = String(bp || "");
  if (!text || text === "-") return null;
  const match = text.match(/^(Y|O|S|K|Ms|Sd|Jd|Jk|M|J)/);
  if (!match) return null;
  return { Y: 0, O: 1, S: 2, K: 3, M: 4, J: 5, Ms: 6, Sd: 7, Jd: 8, Jk: 9 }[match[1]] ?? null;
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
