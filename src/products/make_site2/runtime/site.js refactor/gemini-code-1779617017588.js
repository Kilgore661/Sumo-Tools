/**
 * HTTP abstraction engines managing structured ingestion of assets.
 */

export async function fetchJson(path) {
  const response = await fetch(appendCacheBust(path));
  if (!response.ok) throw new Error(`Failed to load JSON asset: ${path}`);
  return response.json();
}

export async function fetchCsv(path) {
  const response = await fetch(appendCacheBust(path));
  if (!response.ok) throw new Error(`Failed to load CSV asset: ${path}`);
  const text = await response.text();
  return parseCsv(text);
}

export function parseCsv(text) {
  const rows = csvRows(text.trim());
  const headers = rows.shift() || [];
  return rows.map(row => Object.fromEntries(headers.map((header, index) => [header, row[index] || ""])));
}

export function csvRows(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (quoted && char === '"' && next === '"') {
      field += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (!quoted && char === ",") {
      row.push(field);
      field = "";
    } else if (!quoted && (char === "\n" || char === "\r")) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function appendCacheBust(path) {
  if (!document.body || !document.body.dataset || !document.body.dataset.cacheBust) {
    return path;
  }
  const url = new URL(path, window.location.href);
  url.searchParams.set(document.body.dataset.cacheBustParam || "cb", document.body.dataset.cacheBust);
  return url.toString();
}