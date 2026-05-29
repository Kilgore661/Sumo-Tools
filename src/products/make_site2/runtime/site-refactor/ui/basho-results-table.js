import { escapeHtml } from "../utils/html.js";

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

export { renderBashoResultsPresentationTable, terminalNodes, headerRows };
