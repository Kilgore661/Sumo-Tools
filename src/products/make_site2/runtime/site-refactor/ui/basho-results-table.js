import { escapeHtml } from "../utils/html.js";

const BASHO_RESULTS_TABLE_ID = "basho_results_browser";
const DEFAULT_BASHO_RESULTS_SORT_PATH = "selected.context.skill.bp";
const bashoResultsSortStates = new Map();

const TRANSITIONAL_TABLE_SPEC = [
  group("reference", "Reference", [
    column("row_number", "#", { sort_kind: "none" }),
    column("shikona", "Shikona", { sort_kind: "text" }),
  ]),
  group("before", "Before Basho", recordSpec()),
  group("selected", "Current/After", [
    ...recordSpec(),
    column("next_bp", "nuChii", { sort_kind: "chii_ordinal", sort_path: "next_bp_ordinal" }),
  ]),
  group("comparison", "Comparison", [
    column("delta_equelo", "Delta Equelo", { sort_kind: "numeric" }),
  ]),
];

function recordSpec() {
  return [
    group("context", "Context", [
      group("skill", "Skill", [
        column("bp", "BP", { sort_kind: "chii_ordinal", sort_path: "bp_ordinal" }),
        column("equelo", "Equelo", { sort_kind: "numeric" }),
      ]),
      group("analysis", "Analysis", [
        group("banzuke_error", "BZ Error", [
          column("direction", "Dir", { sort_kind: "text" }),
          column("magnitude", "Mag", { sort_kind: "numeric" }),
        ]),
        column("rbbp", "RBBP", { sort_kind: "chii_ordinal", sort_path: "rbbp_ordinal" }),
      ]),
    ]),
    group("result", "Result", [
      column("wins", "W", { sort_kind: "numeric" }),
      column("losses", "L", { sort_kind: "numeric" }),
      column("absences", "A", { sort_kind: "numeric" }),
      column("prizes", "\u{1F4E6}", { sort_kind: "text" }),
      column("division_change", "Div", { sort_kind: "text" }),
    ]),
  ];
}

function buildBashoResultsPresentationModel({ rows, state, entry, title }) {
  const visiblePaths = bashoResultsVisiblePaths(state);
  const analyses = buildRecordAnalyses(rows || []);
  return {
    id: BASHO_RESULTS_TABLE_ID,
    header: bashoResultsHeader(title, entry),
    table_spec: resolveSelectedHeading(TRANSITIONAL_TABLE_SPEC, entry),
    values: (rows || []).map((row, index) => transitionalRowValues(row, index, analyses)),
    projection: { visible_paths: visiblePaths },
  };
}

function renderBashoResultsPresentationTable(model) {
  const visiblePaths = new Set(model.projection?.visible_paths || []);
  const leaves = terminalNodes(model.table_spec || [], [], visiblePaths);
  const sortState = currentBashoResultsSortState(model, leaves);
  const sortedValues = sortBashoResultsRows(model.values || [], leaves, sortState);
  return [
    renderBashoResultsHeader(model.header),
    '<table class="artifact-table brb-table brb-redesign-table">',
    renderNestedHead(model.table_spec || [], visiblePaths, leaves, sortState),
    '<tbody>',
    ...sortedValues.map((row, index) => [
      '<tr>',
      ...leaves.map(leaf => `<td data-column-path="${escapeHtml(leaf.path)}">${renderBashoResultsCell(row, leaf.path, index)}</td>`),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function wireBashoResultsPresentationSorting(panel, model, renderPanel) {
  const visiblePaths = new Set(model.projection?.visible_paths || []);
  const leaves = terminalNodes(model.table_spec || [], [], visiblePaths);
  document.querySelectorAll(".brb-redesign-table .table-sort-button[data-basho-results-sort-path]").forEach(button => {
    button.addEventListener("click", () => {
      const path = button.dataset.bashoResultsSortPath;
      const leaf = leaves.find(item => item.path === path);
      if (!isSortableLeaf(leaf)) {
        throw new Error(`Unsupported Basho Results sort path: ${path}`);
      }
      const current = currentBashoResultsSortState(model, leaves);
      bashoResultsSortStates.set(model.id || BASHO_RESULTS_TABLE_ID, {
        path,
        direction: current.path === path
          ? toggledSortDirection(current.direction)
          : sortDefaultDirection(leaf),
      });
      renderPanel(panel);
    });
  });
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

function resolveSelectedHeading(spec, entry) {
  const selectedHeading = Number(entry?.latest_day) && Number(entry.latest_day) < 15
    ? "Current"
    : "After Basho";
  return spec.map(node => node.key === "selected" ? { ...node, label: selectedHeading } : node);
}

function bashoResultsVisiblePaths(state) {
  const visible = [
    "reference.row_number",
    "reference.shikona",
    "selected.context.skill.bp",
    "selected.result.wins",
    "selected.result.losses",
    "selected.result.absences",
    "selected.result.prizes",
    "selected.result.division_change",
  ];
  if (state.previous_context) {
    visible.push(
      "before.context.skill.bp",
      "before.result.wins",
      "before.result.losses",
      "before.result.absences",
      "before.result.prizes",
      "before.result.division_change",
    );
  }
  if (state.rating_context) {
    if (state.previous_context) visible.push("before.context.skill.equelo");
    visible.push("selected.context.skill.equelo", "comparison.delta_equelo");
  }
  if (state.analysis_context) {
    if (state.previous_context) {
      visible.push(
        "before.context.analysis.banzuke_error.direction",
        "before.context.analysis.banzuke_error.magnitude",
        "before.context.analysis.rbbp",
      );
    }
    visible.push(
      "selected.context.analysis.banzuke_error.direction",
      "selected.context.analysis.banzuke_error.magnitude",
      "selected.context.analysis.rbbp",
    );
  }
  if (state.nu_chii) {
    visible.push("selected.next_bp");
  }
  return visible;
}

function buildRecordAnalyses(rows) {
  return {
    before: buildRecordAnalysis(rows, {
      bpField: "previous_chii",
      bpOrdinalField: "previous_chii_ordinal",
      ratingField: "previous_equelo",
    }),
    selected: buildRecordAnalysis(rows, {
      bpField: "chii",
      bpOrdinalField: "chii_ordinal",
      ratingField: "equelo",
    }),
  };
}

function buildRecordAnalysis(rows, fields) {
  const candidates = rows.map((row, index) => {
    const bpOrdinal = numericValue(row[fields.bpOrdinalField]);
    const rating = numericValue(row[fields.ratingField]);
    if (bpOrdinal === null || rating === null) return null;
    return {
      index,
      bp: row[fields.bpField] || "",
      bpOrdinal,
      rating,
    };
  }).filter(Boolean);

  const byBanzuke = [...candidates].sort((left, right) =>
    compareValues(left.bpOrdinal, right.bpOrdinal) || compareValues(left.rating, right.rating)
  );
  const byRating = [...candidates].sort((left, right) =>
    compareValues(right.rating, left.rating) || compareValues(left.bpOrdinal, right.bpOrdinal)
  );
  const banzukePositions = new Map();
  const ratingPositions = new Map();
  byBanzuke.forEach((item, index) => banzukePositions.set(item.index, index + 1));
  byRating.forEach((item, index) => ratingPositions.set(item.index, index + 1));

  const values = rows.map(() => emptyRecordAnalysis());
  for (const item of candidates) {
    const banzukePosition = banzukePositions.get(item.index);
    const ratingPosition = ratingPositions.get(item.index);
    const rbbpSlot = byBanzuke[ratingPosition - 1];
    if (!banzukePosition || !ratingPosition || !rbbpSlot) continue;
    const signedDelta = banzukePosition - ratingPosition;
    values[item.index] = {
      direction: signedDelta > 0 ? "\u2191" : signedDelta < 0 ? "\u2193" : "",
      magnitude: signedDelta === 0 ? "" : String(Math.abs(signedDelta)),
      rbbp: rbbpSlot.bp,
      rbbpOrdinal: String(rbbpSlot.bpOrdinal),
    };
  }
  return values;
}

function emptyRecordAnalysis() {
  return {
    direction: "",
    magnitude: "",
    rbbp: "",
    rbbpOrdinal: "",
  };
}

function numericValue(value) {
  const number = Number(value);
  return Number.isNaN(number) ? null : number;
}

function transitionalRowValues(row, index, analyses) {
  const beforeResult = parseResult(row.previous_result);
  const selectedResult = parseResult(row.score);
  const beforeAnalysis = analyses.before[index] || emptyRecordAnalysis();
  const selectedAnalysis = analyses.selected[index] || emptyRecordAnalysis();
  return {
    "reference.row_number": String(index + 1),
    "reference.shikona": row.shikona || "",
    "reference.rikishi_id": row.rikishi_id || "",
    "before.context.skill.bp": row.previous_chii || "",
    "before.context.skill.bp_ordinal": row.previous_chii_ordinal || "",
    "before.context.skill.equelo": row.previous_equelo || "",
    "before.context.analysis.banzuke_error.direction": beforeAnalysis.direction,
    "before.context.analysis.banzuke_error.magnitude": beforeAnalysis.magnitude,
    "before.context.analysis.rbbp": beforeAnalysis.rbbp,
    "before.context.analysis.rbbp_ordinal": beforeAnalysis.rbbpOrdinal,
    "before.result.wins": beforeResult.wins,
    "before.result.losses": beforeResult.losses,
    "before.result.absences": beforeResult.absences,
    "before.result.prizes": beforeResult.prizes,
    "before.result.division_change": rankLevelMovementMarker(row.previous_rank_level_movement),
    "selected.context.skill.bp": row.chii || "",
    "selected.context.skill.bp_ordinal": row.chii_ordinal || "",
    "selected.context.skill.equelo": row.equelo || "",
    "selected.context.analysis.banzuke_error.direction": selectedAnalysis.direction,
    "selected.context.analysis.banzuke_error.magnitude": selectedAnalysis.magnitude,
    "selected.context.analysis.rbbp": selectedAnalysis.rbbp,
    "selected.context.analysis.rbbp_ordinal": selectedAnalysis.rbbpOrdinal,
    "selected.result.wins": selectedResult.wins,
    "selected.result.losses": selectedResult.losses,
    "selected.result.absences": selectedResult.absences,
    "selected.result.prizes": selectedResult.prizes,
    "selected.result.division_change": rankLevelMovementBetween(row.chii, row.nu_chii),
    "selected.next_bp": row.nu_chii || "",
    "selected.next_bp_ordinal": row.nu_chii_ordinal || "",
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

function renderNestedHead(nodes, visiblePaths, leaves = null, sortState = null) {
  const rows = headerRows(nodes, visiblePaths);
  const leafByPath = new Map((leaves || terminalNodes(nodes, [], visiblePaths)).map(leaf => [leaf.path, leaf]));
  return [
    '<thead>',
    ...rows.map(row => [
      '<tr>',
      ...row.map(cell => renderNestedHeaderCell(cell, leafByPath.get(cell.path), sortState)),
      '</tr>',
    ].join("")),
    '</thead>',
  ].join("");
}

function renderNestedHeaderCell(cell, leaf, sortState) {
  const attributes = [
    `colspan="${cell.colspan}"`,
    `rowspan="${cell.rowspan}"`,
    `data-column-path="${escapeHtml(cell.path)}"`,
  ];
  if (!isSortableLeaf(leaf)) {
    return `<th ${attributes.join(" ")}>${escapeHtml(cell.label)}</th>`;
  }
  const active = sortState?.path === leaf.path;
  const direction = active ? sortState.direction : "none";
  const indicator = active ? (sortState.direction === "ascending" ? " ▲" : " ▼") : "";
  return [
    `<th ${attributes.join(" ")} aria-sort="${direction}" style="text-align: center;">`,
    `<button type="button" class="table-sort-button" data-basho-results-sort-path="${escapeHtml(leaf.path)}" style="display: inline-flex; align-items: center; justify-content: center; gap: 0.15rem; margin: 0 auto; text-align: center;">`,
    escapeHtml(cell.label),
    `<span class="table-sort-indicator" aria-hidden="true">${indicator}</span>`,
    '</button>',
    '</th>',
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
    return isVisiblePath(pathText, visiblePaths)
      ? [{ ...node, path: pathText, sort_path: resolveLeafSortPath(node, nextPath) }]
      : [];
  });
}

function resolveLeafSortPath(node, path) {
  if (!node.sort_path) return path.join(".");
  if (node.sort_path.includes(".")) return node.sort_path;
  return [...path.slice(0, -1), node.sort_path].join(".");
}

function isVisiblePath(path, visiblePaths) {
  return !visiblePaths.size || visiblePaths.has(path);
}

function currentBashoResultsSortState(model, leaves) {
  const existing = bashoResultsSortStates.get(model.id || BASHO_RESULTS_TABLE_ID);
  if (existing && leaves.some(leaf => leaf.path === existing.path && isSortableLeaf(leaf))) {
    return existing;
  }
  const leaf = leaves.find(item => item.path === DEFAULT_BASHO_RESULTS_SORT_PATH && isSortableLeaf(item))
    || firstSortableLeaf(leaves);
  return {
    path: leaf?.path || "",
    direction: sortDefaultDirection(leaf),
  };
}

function firstSortableLeaf(leaves) {
  return leaves.find(leaf => isSortableLeaf(leaf));
}

function isSortableLeaf(leaf) {
  return Boolean(leaf) && leaf.sort_kind !== "none";
}

function sortBashoResultsRows(rows, leaves, sortState) {
  const leaf = leaves.find(item => item.path === sortState?.path);
  if (!isSortableLeaf(leaf)) return [...rows];
  const multiplier = sortState.direction === "descending" ? -1 : 1;
  return [...rows].sort((left, right) =>
    compareNullableSortValues(
      sortValueForLeaf(leaf, left),
      sortValueForLeaf(leaf, right),
      leaf,
      multiplier,
    )
  );
}

function sortValueForLeaf(leaf, row) {
  const value = row[leaf.sort_path || leaf.path];
  if (leaf.sort_kind === "record") return recordWins(value);
  if (leaf.sort_kind === "numeric" || leaf.sort_kind === "chii_ordinal") {
    const number = Number(value);
    return Number.isNaN(number) ? null : number;
  }
  return value ?? "";
}

function compareNullableSortValues(left, right, leaf, multiplier) {
  if (left === null && right === null) return 0;
  if (left === null) return 1;
  if (right === null) return -1;
  return multiplier * compareSortValues(left, right, leaf);
}

function compareSortValues(left, right, leaf) {
  if (leaf.sort_kind === "text") return String(left).localeCompare(String(right));
  return compareValues(left, right);
}

function compareValues(left, right) {
  const leftNumber = Number(left);
  const rightNumber = Number(right);
  if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
    return leftNumber - rightNumber;
  }
  return String(left).localeCompare(String(right));
}

function sortDefaultDirection(leaf) {
  if (!leaf) return "ascending";
  if (leaf.sort_default_direction) return leaf.sort_default_direction;
  if (leaf.sort_kind === "text" || leaf.sort_kind === "chii_ordinal") return "ascending";
  return "descending";
}

function toggledSortDirection(direction) {
  return direction === "ascending" ? "descending" : "ascending";
}

function recordWins(value) {
  // Warning! Warning! Dr. Smith! This parses compact result strings because
  // TBD "Producer result-field shape" has not been resolved.
  const match = String(value ?? "").match(/^\s*(\d+)\s*-/);
  return match ? Number(match[1]) : null;
}

function renderBashoResultsCell(row, path, index) {
  if (path === "reference.row_number") return escapeHtml(String(index + 1));
  if (path === "reference.shikona") {
    return renderRikishiLink(row["reference.shikona"], row["reference.rikishi_id"]);
  }
  return escapeHtml(valueAtPath(row, path));
}

function renderRikishiLink(shikona, rikishiId) {
  if (!rikishiId) return escapeHtml(shikona || "");
  return [
    `<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}"`,
    ' target="_blank" rel="noopener">',
    escapeHtml(shikona || ""),
    '</a>',
  ].join("");
}

function valueAtPath(row, path) {
  const value = row?.[path];
  if (value === null || value === undefined) return "";
  return String(value);
}

function group(key, label, children) {
  return { key, label, children };
}

function column(key, label, options = {}) {
  return { key, label, ...options };
}

export {
  buildBashoResultsPresentationModel,
  renderBashoResultsPresentationTable,
  wireBashoResultsPresentationSorting,
  terminalNodes,
  headerRows,
  currentBashoResultsSortState,
  sortBashoResultsRows,
};
