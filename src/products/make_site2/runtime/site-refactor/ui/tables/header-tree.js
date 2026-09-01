// Structural operations for tables whose headings form a tree.

function headerRows(nodes, visiblePaths) {
  const depth = maxDepth(nodes, visiblePaths);
  const rows = Array.from({ length: depth }, () => []);
  appendHeaderCells(rows, nodes, [], visiblePaths, depth, 0);
  return rows;
}

function appendHeaderCells(rows, nodes, path, visiblePaths, depth, level) {
  for (const node of nodes || []) {
    if (node.hidden) continue;
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) {
      const childLeaves = terminalNodes(node.children, nextPath, visiblePaths);
      if (!childLeaves.length) continue;
      rows[level].push({
        colspan: childLeaves.length,
        label: node.label ?? node.key,
        help: node.help || "",
        note_id: node.note_id || "",
        path: pathText,
        rowspan: 1,
        is_group: true,
      });
      appendHeaderCells(rows, node.children, nextPath, visiblePaths, depth, level + 1);
    } else if (isVisiblePath(pathText, visiblePaths)) {
      rows[level].push({
        colspan: 1,
        label: node.label ?? node.key,
        help: node.help || "",
        note_id: node.note_id || "",
        path: pathText,
        rowspan: depth - level,
        is_group: false,
      });
    }
  }
}

function maxDepth(nodes, visiblePaths, path = [], level = 1) {
  const depths = (nodes || []).flatMap(node => {
    if (node.hidden) return [];
    const nextPath = [...path, node.key];
    if (node.children) {
      if (!terminalNodes(node.children, nextPath, visiblePaths).length) return [];
      return [maxDepth(node.children, visiblePaths, nextPath, level + 1)];
    }
    return isVisiblePath(nextPath.join("."), visiblePaths) ? [level] : [];
  });
  return depths.length ? Math.max(...depths) : level - 1;
}

function terminalNodes(nodes, path, visiblePaths) {
  return (nodes || []).flatMap(node => {
    if (node.hidden) return [];
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) return terminalNodes(node.children, nextPath, visiblePaths);
    return isVisiblePath(pathText, visiblePaths)
      ? [{ ...node, path: pathText, sort_path: resolveLeafSortPath(node, nextPath) }]
      : [];
  });
}

function groupBoundaryMap(nodes, visiblePaths, leaves = null) {
  const visibleLeaves = leaves || terminalNodes(nodes, [], visiblePaths);
  const starts = new Set();
  const ends = new Set();
  collectGroupBoundaries(nodes, [], visiblePaths, starts, ends);
  return {
    starts,
    ends,
    position(path) {
      const start = starts.has(path);
      const end = ends.has(path);
      if (start && end) return "only";
      if (start) return "start";
      if (end) return "end";
      return "";
    },
    leaves: visibleLeaves,
  };
}

function collectGroupBoundaries(nodes, path, visiblePaths, starts, ends) {
  for (const node of nodes || []) {
    if (node.hidden) continue;
    const nextPath = [...path, node.key];
    if (!node.children) continue;
    const childLeaves = terminalNodes(node.children, nextPath, visiblePaths);
    if (!childLeaves.length) continue;
    starts.add(childLeaves[0].path);
    ends.add(childLeaves[childLeaves.length - 1].path);
    collectGroupBoundaries(node.children, nextPath, visiblePaths, starts, ends);
  }
}

function groupBoundaryAttributes(groupPosition = "") {
  if (groupPosition === "only") return ['data-group-start="true"', 'data-group-end="true"'];
  if (groupPosition === "start") return ['data-group-start="true"'];
  if (groupPosition === "end") return ['data-group-end="true"'];
  return [];
}

function resolveLeafSortPath(node, path) {
  if (!node.sort_path) return path.join(".");
  if (node.sort_path.includes(".")) return node.sort_path;
  return [...path.slice(0, -1), node.sort_path].join(".");
}

function isVisiblePath(path, visiblePaths) {
  return !visiblePaths.size || visiblePaths.has(path);
}

export {
  headerRows,
  appendHeaderCells,
  maxDepth,
  terminalNodes,
  groupBoundaryMap,
  collectGroupBoundaries,
  groupBoundaryAttributes,
  resolveLeafSortPath,
  isVisiblePath,
};
