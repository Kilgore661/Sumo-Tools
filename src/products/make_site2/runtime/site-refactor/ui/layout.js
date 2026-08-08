// PA-panel layout hooks for sticky headings and scrollable table shells.

let resizeListenerAttached = false;

// Apply layout upgrades after a panel render.
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

// Split a table into fixed header and scrollable body tables.
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

  const frame = document.createElement("div");
  frame.className = "artifact-table-frame";

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
  frame.append(headerRegion, bodyRegion);
  shell.append(frame);
  bodyRegion.addEventListener("scroll", () => {
    headerRegion.scrollLeft = bodyRegion.scrollLeft;
  });

  table.replaceWith(shell);
}

// Keep artifact titles below the sticky content title.
function updateStickyArtifactHeaders() {
  document.querySelectorAll(".artifact-table-shell").forEach(syncTableShellColumns);
}

// Synchronize header/body column widths in a scrollable table shell.
function syncTableShellColumns(shell) {
  const frame = shell.querySelector(":scope > .artifact-table-frame");
  const headerTable = shell.querySelector(":scope .artifact-table-header-region > table");
  const bodyRegion = shell.querySelector(":scope .artifact-table-body-region");
  const bodyTable = bodyRegion?.querySelector(":scope > table");
  if (!frame || !headerTable || !bodyRegion || !bodyTable) return;

  frame.style.width = "";
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
  // Collapsed cell borders can make the rendered table wider than its assigned
  // column total. Size the frame from the rendered tables, then reserve the
  // vertical scrollbar gutter owned by the body.
  const renderedTableWidth = Math.ceil(Math.max(
    headerTable.getBoundingClientRect().width,
    bodyTable.getBoundingClientRect().width,
  ));
  const scrollbarGutter = Math.max(0, bodyRegion.offsetWidth - bodyRegion.clientWidth);
  frame.style.width = `${renderedTableWidth + scrollbarGutter}px`;
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
