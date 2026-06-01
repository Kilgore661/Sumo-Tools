import {
  BASHO_RESULTS_TABLE_ID,
  DEFAULT_BASHO_RESULTS_SORT_PATH,
} from "./shared.js";
import {
  compareValues,
  rankLevelMovementMarker,
} from "./values.js";
import { PRIZE_DISPLAY_ORDER } from "./table-spec.js";
import { terminalNodes } from "./render.js";

const bashoResultsSortStates = new Map();

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
  if (leaf.sort_kind === "movement_symbol") return movementSortValue(value);
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

function movementSortValue(value) {
  const movement = rankLevelMovementMarker(value);
  if (movement === "\u2191") return 2;
  if (movement === "\u2193") return 0;
  return 1;
}

function recordWins(value) {
  // Warning! Warning! Dr. Smith! This parses compact result strings because
  // the structured Result emitter shape open issue has not been resolved.
  const match = String(value ?? "").match(/^\s*(\d+)\s*-/);
  return match ? Number(match[1]) : null;
}

export {
  wireBashoResultsPresentationSorting,
  currentBashoResultsSortState,
  firstSortableLeaf,
  isSortableLeaf,
  sortBashoResultsRows,
  sortMultiplierForLeaf,
  sortValueForLeaf,
  compareNullableSortValues,
  compareSortValues,
  sortDefaultDirection,
  toggledSortDirection,
  prizeSortValue,
  movementSortValue,
  recordWins,
};
