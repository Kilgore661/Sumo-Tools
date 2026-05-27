let resizeListenerAttached = false;

function wirePAPanelLayout() {
  upgradeScrollableTables();
  updateStickyArtifactHeaders();
  window.requestAnimationFrame(updateStickyArtifactHeaders);
  if (!resizeListenerAttached) {
    resizeListenerAttached = true;
    window.addEventListener("resize", () => window.requestAnimationFrame(updateStickyArtifactHeaders));
  }
}

function upgradeScrollableTables() {
  document.querySelectorAll(".pa-slot > .artifact-table, .pa-slot > .artifact-table-shell + .artifact-table").forEach(table => {
    upgradeScrollableTable(table);
  });
}

function upgradeScrollableTable(table) {
  if (table.dataset.scrollRegion === "upgraded") return;
  const thead = table.querySelector(":scope > thead");
  const tbody = table.querySelector(":scope > tbody");
  if (!thead || !tbody) return;

  const shell = document.createElement("div");
  shell.className = "artifact-table-shell";

  const headerRegion = document.createElement("div");
  headerRegion.className = "artifact-table-header-region";

  const bodyRegion = document.createElement("div");
  bodyRegion.className = "artifact-table-body-region";

  const headerTable = document.createElement("table");
  headerTable.className = `${table.className} artifact-table-header`;
  headerTable.dataset.scrollRegion = "header";
  headerTable.append(thead);

  const bodyTable = document.createElement("table");
  bodyTable.className = `${table.className} artifact-table-body`;
  bodyTable.dataset.scrollRegion = "body";
  bodyTable.append(tbody);

  headerRegion.append(headerTable);
  bodyRegion.append(bodyTable);
  shell.append(headerRegion, bodyRegion);
  bodyRegion.addEventListener("scroll", () => {
    headerRegion.scrollLeft = bodyRegion.scrollLeft;
  });

  table.replaceWith(shell);
}

function updateStickyArtifactHeaders() {
  document.querySelectorAll(".artifact-table-shell").forEach(syncTableShellColumns);
}

function syncTableShellColumns(shell) {
  const headerTable = shell.querySelector(":scope > .artifact-table-header-region > table");
  const bodyTable = shell.querySelector(":scope > .artifact-table-body-region > table");
  if (!headerTable || !bodyTable) return;

  clearColumnWidths(headerTable, bodyTable);
  const headerCells = tableHeaderLeafCells(headerTable);
  const bodyRows = [...bodyTable.querySelectorAll("tbody tr")].slice(0, 25);
  const columnCount = Math.max(
    headerCells.length,
    ...bodyRows.map(row => row.children.length),
  );
  if (!columnCount) return;

  const widths = Array.from({ length: columnCount }, (_, index) => {
    const headerWidth = headerCells[index]?.getBoundingClientRect().width || 0;
    const bodyWidth = Math.max(
      0,
      ...bodyRows.map(row => row.children[index]?.getBoundingClientRect().width || 0),
    );
    return Math.ceil(Math.max(headerWidth, bodyWidth, 24));
  });
  applyColumnWidths(headerTable, bodyTable, widths);
}

function clearColumnWidths(...tables) {
  for (const table of tables) {
    table.querySelector(":scope > colgroup")?.remove();
    table.style.width = "";
    table.style.tableLayout = "";
  }
}

function applyColumnWidths(headerTable, bodyTable, widths) {
  const total = widths.reduce((sum, width) => sum + width, 0);
  for (const table of [headerTable, bodyTable]) {
    const colgroup = document.createElement("colgroup");
    for (const width of widths) {
      const col = document.createElement("col");
      col.style.width = `${width}px`;
      colgroup.append(col);
    }
    table.prepend(colgroup);
    table.style.tableLayout = "fixed";
    table.style.width = `${total}px`;
  }
}

function tableHeaderLeafCells(table) {
  const rows = [...table.querySelectorAll("thead tr")];
  const grid = [];
  rows.forEach((row, rowIndex) => {
    grid[rowIndex] ||= [];
    let columnIndex = 0;
    for (const cell of row.children) {
      while (grid[rowIndex][columnIndex]) columnIndex += 1;
      const colspan = Number(cell.getAttribute("colspan") || 1);
      const rowspan = Number(cell.getAttribute("rowspan") || 1);
      for (let rowOffset = 0; rowOffset < rowspan; rowOffset += 1) {
        grid[rowIndex + rowOffset] ||= [];
        for (let colOffset = 0; colOffset < colspan; colOffset += 1) {
          grid[rowIndex + rowOffset][columnIndex + colOffset] = cell;
        }
      }
      columnIndex += colspan;
    }
  });
  return grid[grid.length - 1] || [];
}

export { wirePAPanelLayout, updateStickyArtifactHeaders };
