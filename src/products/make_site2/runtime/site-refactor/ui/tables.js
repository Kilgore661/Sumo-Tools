// Public table runtime facade.

export {
  renderSectionedTable,
  renderTableSection,
  renderIndexedTable,
  isColumnVisible,
  cellValue,
  resultWithMovement,
  rankLevelMovementMarker,
} from "./tables/generic.js";

export {
  renderBanzukeChangesTable,
  renderBanzukeStyleTable,
  renderBanzukeScanTable,
  banzukeSideColumns,
  banzukeScanColumns,
  renderBanzukeSideCell,
  renderBanzukeScanCell,
  banzukeCellAttributes,
  movementDirection,
  banzukeSideValue,
} from "./tables/banzuke-changes.js";

export {
  renderStandingsTable,
  standingsVisibleColumns,
  standingsVisibleGroups,
  renderStandingsTableHead,
  standingsCellValue,
  standingsRowsForState,
  standingsDivisionMatches,
  sortedStandingsRows,
  defaultStandingsSortColumn,
  competitionPositions,
} from "./tables/standings.js";

export {
  decimal,
  compareValues,
  currentTableSortState,
  firstSortableColumn,
  isSortableColumn,
  sortDefaultDirection,
  sortRows,
  compareNullableSortValues,
  compareSortValues,
  sortValue,
  recordWins,
  renderTableHeading,
  wireTableSorting,
  toggledSortDirection,
  tableCellAttributes,
  renderRikishiLink,
} from "./tables/shared.js";
