// Minimal CSV parser for generated runtime data files.

// Parse CSV text into objects keyed by header names.
function parseCsv(text) {
  const rows = csvRows(text.trim());
  const headers = rows.shift() || [];
  return rows.map(row => Object.fromEntries(headers.map((header, index) => [header, row[index] || ""])));
}
// Parse CSV text into raw rows while respecting quoted fields.
function csvRows(text) {
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
  row.push(field);
  rows.push(row);
  return rows;
}

export { parseCsv, csvRows };
