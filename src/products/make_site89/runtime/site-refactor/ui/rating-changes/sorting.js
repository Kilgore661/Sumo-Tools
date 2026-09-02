// Rating Changes recursive table sorting state and sort value derivation.

import { DEFAULT_RATING_CHANGES_SORT_PATH } from "./table-spec.js";
import { terminalNodes } from "./render.js";

const ratingChangesSortStates = new Map();

function wireRatingChangesPresentationSorting(panel, model, renderPanel) {
  const visiblePaths = new Set(model.projection?.visible_paths || []);
  const leaves = terminalNodes(model.table_spec || [], [], visiblePaths);
  document.querySelectorAll(".rating-changes-table .table-sort-button[data-rating-changes-sort-path]").forEach(button => {
    button.addEventListener("click", () => {
      const path = button.dataset.ratingChangesSortPath;
      const leaf = leaves.find(item => item.path === path);
      if (!isSortableLeaf(leaf)) {
        throw new Error(`Unsupported Rating Changes sort path: ${path}`);
      }
      const current = currentRatingChangesSortState(model, leaves);
      ratingChangesSortStates.set(model.id || "rating_changes", {
        path,
        direction: current.path === path
          ? toggledSortDirection(current.direction)
          : sortDefaultDirection(leaf),
      });
      renderPanel(panel);
    });
  });
}

function currentRatingChangesSortState(model, leaves) {
  const existing = ratingChangesSortStates.get(model.id || "rating_changes");
  if (existing && leaves.some(leaf => leaf.path === existing.path && isSortableLeaf(leaf))) {
    return existing;
  }
  const leaf = leaves.find(item => item.path === DEFAULT_RATING_CHANGES_SORT_PATH && isSortableLeaf(item))
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

function sortRatingChangesRows(rows, leaves, sortState) {
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

export {
  wireRatingChangesPresentationSorting,
  currentRatingChangesSortState,
  firstSortableLeaf,
  isSortableLeaf,
  sortRatingChangesRows,
  sortMultiplierForLeaf,
  sortValueForLeaf,
  compareNullableSortValues,
  compareSortValues,
  sortDefaultDirection,
  toggledSortDirection,
};
