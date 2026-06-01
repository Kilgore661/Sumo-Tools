import { escapeHtml } from "../utils/html.js";

const BASHO_RESULTS_TABLE_ID = "basho_results_browser";
const DEFAULT_BASHO_RESULTS_SORT_PATH = "selected.context.skill.bp";
const bashoResultsSortStates = new Map();

const PRESENTATION = {
  DEFAULT: "default",
  NAME: "name",
  RANK_CODE: "rank_code",
  RATING: "rating",
  COMPACT_COUNT: "compact_count",
  MOVEMENT_SYMBOL: "movement_symbol",
  NUMERIC_MAGNITUDE: "numeric_magnitude",
  COMPACT_TEXT: "compact_text",
};

const PRIZE_DISPLAY_ORDER = ["Y", "D", "J", "K", "S", "G"];

const TRANSITIONAL_TABLE_SPEC = [
  group("reference", "Reference", [
    column("row_number", "#", { sort_kind: "none", presentation: PRESENTATION.NUMERIC_MAGNITUDE }),
    column("shikona", "Shikona", { sort_kind: "text", presentation: PRESENTATION.NAME }),
  ]),
  group("before", "Before Basho", recordSpec()),
  group("selected", "Current/After", [
    ...recordSpec(),
    column("next_bp", "nuChii", {
      sort_kind: "chii_ordinal",
      sort_path: "next_bp_ordinal",
      presentation: PRESENTATION.RANK_CODE,
    }),
  ]),
  group("changes", "Changes", [
    column("delta_equelo", "ΔEq", { sort_kind: "numeric", presentation: PRESENTATION.RATING }),
    group("movement", "⇅", [
      column("bp", "Chii", { sort_kind: "text", presentation: PRESENTATION.MOVEMENT_SYMBOL }),
      column("division", "Div", { sort_kind: "text", presentation: PRESENTATION.MOVEMENT_SYMBOL }),
    ]),
  ]),
];

function recordSpec() {
  return [
    group("context", "Context", [
      group("skill", "Skill", [
        column("bp", "Chii", {
          sort_kind: "chii_ordinal",
          sort_path: "bp_ordinal",
          presentation: PRESENTATION.RANK_CODE,
        }),
        column("equelo", "Eq", { sort_kind: "numeric", presentation: PRESENTATION.RATING }),
      ]),
      group("analysis", "Analysis", [
        group("banzuke_error", "ΔBZ", [
          column("direction", "Dir", { sort_kind: "text", presentation: PRESENTATION.MOVEMENT_SYMBOL }),
          column("magnitude", "Mag", { sort_kind: "numeric", presentation: PRESENTATION.NUMERIC_MAGNITUDE }),
        ]),
        column("rbbp", "Eq Chii", {
          sort_kind: "chii_ordinal",
          sort_path: "rbbp_ordinal",
          presentation: PRESENTATION.RANK_CODE,
        }),
      ]),
    ]),
    group("result", "Result", [
      column("wins", "W", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("losses", "L", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("absences", "A", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("prizes", "\u{1F4E6}", {
        sort_kind: "prize_set",
        sort_default_direction: "descending",
        presentation: PRESENTATION.COMPACT_TEXT,
      }),
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
      ...leaves.map(leaf => `<td data-column-path="${escapeHtml(leaf.path)}" style="text-align: ${valueAlignment(leaf.presentation)};">${renderBashoResultsCell(row, leaf.path, index)}</td>`),
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
  ];
  if (state.changes_context) {
    visible.push(
      "changes.movement.bp",
      "changes.movement.division",
    );
  }
  if (state.previous_context) {
    visible.push(
      "before.context.skill.bp",
      "before.result.wins",
      "before.result.losses",
      "before.result.absences",
      "before.result.prizes",
    );
  }
  if (state.rating_context) {
    if (state.previous_context) visible.push("before.context.skill.equelo");
    visible.push("selected.context.skill.equelo");
    if (state.changes_context) visible.push("changes.delta_equelo");
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
    "selected.next_bp": row.nu_chii || "",
    "selected.next_bp_ordinal": row.nu_chii_ordinal || "",
    "changes.movement.bp": bpMovementBetween(row.chii_ordinal, row.nu_chii_ordinal),
    "changes.movement.division": rankLevelMovementBetween(row.chii, row.nu_chii),
    "changes.delta_equelo": row.delta_equelo || "",
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

function bpMovementBetween(fromOrdinal, toOrdinal) {
  const from = Number(fromOrdinal);
  const to = Number(toOrdinal);
  if (Number.isNaN(from) || Number.isNaN(to) || from === to) return "";
  return to < from ? "\u2191" : "\u2193";
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
  const presentation = leaf?.presentation || PRESENTATION.DEFAULT;
  const alignment = headingAlignment(presentation);
  const attributes = [
    `colspan="${cell.colspan}"`,
    `rowspan="${cell.rowspan}"`,
    `data-column-path="${escapeHtml(cell.path)}"`,
    `style="text-align: ${alignment};"`,
  ];
  if (!isSortableLeaf(leaf)) {
    return `<th ${attributes.join(" ")}>${escapeHtml(cell.label)}</th>`;
  }
  const active = sortState?.path === leaf.path;
  const direction = active ? sortState.direction : "none";
  const indicator = active ? (sortState.direction === "ascending" ? " ▲" : " ▼") : "";
  const escapedLabel = escapeHtml(cell.label);
  const reservedSortText = `${escapedLabel} ▼`;
  const visibleSortText = `${escapedLabel}${indicator}`;
  return [
    `<th ${attributes.join(" ")} aria-sort="${direction}">`,
    `<button type="button" class="table-sort-button" data-basho-results-sort-path="${escapeHtml(leaf.path)}" style="display: inline-grid; place-items: center; ${buttonMarginStyle(alignment)} text-align: ${alignment};">`,
    `<span class="table-sort-width-reserver" aria-hidden="true" style="grid-area: 1 / 1; visibility: hidden; white-space: nowrap;">${reservedSortText}</span>`,
    `<span class="table-sort-visible-content" style="grid-area: 1 / 1; white-space: nowrap;">${visibleSortText}</span>`,
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
  const multiplier = sortMultiplierForLeaf(leaf, sortState.direction);
  return [...rows].sort((left, right) =>
    compareNullableSortValues(
      sortValueForLeaf(leaf, left),
      sortValueForLeaf(leaf, right),
      leaf,
      multiplier,
    )
  );
}

function sortMultiplierForLeaf(leaf, direction) {
  if (leaf?.sort_kind === "chii_ordinal") {
    return direction === "descending" ? 1 : -1;
  }
  return direction === "descending" ? -1 : 1;
}

function sortValueForLeaf(leaf, row) {
  const value = row[leaf.sort_path || leaf.path];
  if (leaf.sort_kind === "record") return recordWins(value);
  if (leaf.sort_kind === "prize_set") return prizeSortValue(value);
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
  if (leaf.sort_kind === "chii_ordinal") return "descending";
  if (leaf.sort_kind === "text") return "ascending";
  return "descending";
}

function toggledSortDirection(direction) {
  return direction === "ascending" ? "descending" : "ascending";
}

function prizeSortValue(value) {
  // HACK: current Basho Results output serializes Result as a compact display
  // string, so the runtime has to derive prize ordering from parsed display
  // text. See Open Issues: Structured Result emitter shape.
  // The string display order is most-to-least valuable; shifting left through
  // that order leaves the least valuable prize as bit 0.
  const awarded = new Set(String(value ?? "").trim().split(""));
  return PRIZE_DISPLAY_ORDER.reduce((total, prize) =>
    (total << 1) | (awarded.has(prize) ? 1 : 0), 0
  );
}

function recordWins(value) {
  // Warning! Warning! Dr. Smith! This parses compact result strings because
  // the structured Result emitter shape open issue has not been resolved.
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

function headingAlignment(presentation) {
  if (presentation === PRESENTATION.NAME) return "left";
  return "center";
}

function valueAlignment(presentation) {
  if (presentation === PRESENTATION.NAME) return "left";
  if (presentation === PRESENTATION.RATING || presentation === PRESENTATION.NUMERIC_MAGNITUDE) return "right";
  return "center";
}

function buttonMarginStyle(alignment) {
  if (alignment === "left") return "margin-right: auto;";
  if (alignment === "right") return "margin-left: auto;";
  return "margin: 0 auto;";
}

function group(key, label, children) {
  return { key, label, children };
}

function column(key, label, options = {}) {
  return { key, label, presentation: PRESENTATION.DEFAULT, ...options };
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
