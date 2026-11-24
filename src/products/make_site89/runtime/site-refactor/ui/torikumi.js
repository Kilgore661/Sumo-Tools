// Historical/current Elo89 Torikumi presentation.

import { escapeHtml } from "../utils/html.js";
import { renderRikishiLink } from "./tables/shared.js";

function selectedTorikumiEntry(bashoEntry, requestedDay = null) {
  const day = String(requestedDay ?? "");
  if (!day || day === "0") return null;
  const entry = (bashoEntry?.days || []).find(candidate => String(candidate.day) === day);
  if (!entry || entry.disabled === true) throw new Error("Bad URL");
  return entry;
}

function renderTorikumiSummary(summary) {
  if (!summary) return "";
  const scored = Number(summary.scored || 0);
  const correct = Number(summary.correct || 0);
  const pending = Number(summary.pending || 0);
  const exclusions = [];
  addExclusion(exclusions, summary.fusen_excluded, "fusen bout", "fusen bouts");
  addExclusion(exclusions, summary.draw_excluded, "drawn bout", "drawn bouts");
  addExclusion(exclusions, summary.equal_rating_excluded, "equal-rating bout", "equal-rating bouts");
  addExclusion(exclusions, summary.missing_rating_excluded, "bout without odds", "bouts without odds");

  const lines = [];
  if (scored) {
    const percentage = (100 * correct / scored).toFixed(1);
    lines.push(`<p><strong>Prediction tally:</strong> ${correct}/${scored} correct — ${percentage}%</p>`);
    lines.push(`<p><strong>£1 on each favourite:</strong> ${escapeHtml(formatProfitLoss(summary.favourite_profit))}</p>`);
    if (Number(summary.chii_scored || 0)) {
      lines.push(`<p><strong>£1 on each higher-chii rikishi:</strong> ${escapeHtml(formatProfitLoss(summary.chii_profit))}</p>`);
    }
    lines.push(`<p><strong>£1 on each winner:</strong> ${escapeHtml(formatProfitLoss(summary.winner_profit))}</p>`);
  } else if (pending) {
    lines.push("<p>Results are not yet known.</p>");
  } else {
    lines.push("<p>No scorable results.</p>");
  }
  if (pending && scored) {
    lines.push(`<p>${pending} ${pending === 1 ? "result" : "results"} pending.</p>`);
  }
  if (exclusions.length) lines.push(`<p>${escapeHtml(exclusions.join("; "))} excluded.</p>`);
  return `<div class="torikumi-day-summary">${lines.join("")}</div>`;
}

function addExclusion(target, rawCount, singular, plural) {
  const count = Number(rawCount || 0);
  if (count) target.push(`${count} ${count === 1 ? singular : plural}`);
}

function formatProfitLoss(rawValue) {
  const value = Number(rawValue || 0);
  const amount = `£${Math.abs(value).toFixed(2)}`;
  if (value > 0) return `${amount} profit`;
  if (value < 0) return `${amount} loss`;
  return `${amount} profit/loss`;
}

function predictionText(row) {
  const side = row.prediction_side === "east"
    ? "East"
    : row.prediction_side === "west"
    ? "West"
    : "";
  if (!side) return row.result_type === "pending" ? "No forecast" : "No favourite";
  if (row.prediction_result === "correct") return `${side} to win ✓`;
  if (row.prediction_result === "incorrect") return `${side} to win ✕`;
  return `${side} to win`;
}

function renderTorikumiTable(rows) {
  return [
    '<table class="artifact-table torikumi-table">',
    '<thead><tr>',
    '<th>East</th><th>Elo89</th><th>Odds</th>',
    '<th>Elo89 prediction</th>',
    '<th>Odds</th><th>Elo89</th><th>West</th>',
    '</tr></thead>',
    '<tbody>',
    ...rows.map(row => [
      '<tr>',
      `<td>${renderRikishiLink(row.east_shikona, row.east_id)}</td>`,
      `<td class="numeric">${escapeHtml(row.east_elo89)}</td>`,
      `<td class="numeric">${escapeHtml(row.east_odds)}</td>`,
      `<td class="torikumi-prediction">${escapeHtml(predictionText(row))}</td>`,
      `<td class="numeric">${escapeHtml(row.west_odds)}</td>`,
      `<td class="numeric">${escapeHtml(row.west_elo89)}</td>`,
      `<td>${renderRikishiLink(row.west_shikona, row.west_id)}</td>`,
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

export {
  formatProfitLoss,
  predictionText,
  renderTorikumiSummary,
  renderTorikumiTable,
  selectedTorikumiEntry,
};
