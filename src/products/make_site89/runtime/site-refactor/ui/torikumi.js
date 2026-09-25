// Rating-annotated future Torikumi controls and grouped table.

import { escapeHtml } from "../utils/html.js";
import { renderRikishiLink } from "./tables/shared.js";

function selectedTorikumiEntry(index, requestedDay = null) {
  const entries = (Array.isArray(index?.entries) ? index.entries : [])
    .filter(entry => entry.disabled !== true && entry.payload_path);
  if (!entries.length) return null;
  const defaultEntry = entries.find(
    entry => String(entry.day) === String(index.default_day)
  ) || entries[entries.length - 1];
  const day = String(requestedDay ?? "");
  if (!day || day === "latest" || day === "first") return defaultEntry;
  const selected = entries.find(entry => String(entry.day) === day);
  if (!selected) throw new Error("Error. Never do that again.");
  return selected;
}

function renderTorikumiTable(rows) {
  return [
    '<table class="artifact-table torikumi-table">',
    '<thead>',
    '<tr><th colspan="3">East</th><th colspan="3">West</th></tr>',
    '<tr><th>Shikona</th><th>Elo89</th><th>P(win)</th><th>P(win)</th><th>Elo89</th><th>Shikona</th></tr>',
    '</thead>',
    '<tbody>',
    ...rows.map(row => [
      '<tr>',
      `<td>${renderRikishiLink(row.east_shikona, row.east_id)}</td>`,
      `<td class="numeric">${escapeHtml(row.east_elo89)}</td>`,
      `<td class="numeric probability-east">${escapeHtml(row.east_probability)}</td>`,
      `<td class="numeric probability-west">${escapeHtml(row.west_probability)}</td>`,
      `<td class="numeric">${escapeHtml(row.west_elo89)}</td>`,
      `<td>${renderRikishiLink(row.west_shikona, row.west_id)}</td>`,
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

export { selectedTorikumiEntry, renderTorikumiTable };
