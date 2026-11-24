import assert from "node:assert/strict";

import {
  formatProfitLoss,
  predictionText,
  renderTorikumiSummary,
  renderTorikumiTable,
  selectedTorikumiEntry,
} from "../src/products/make_site89/runtime/site-refactor/ui/torikumi.js";

globalThis.document = { getElementById: () => null };
const { renderFilter, torikumiDayValues } = await import(
  "../src/products/make_site89/runtime/site-refactor/ui/filters.js"
);

const days = Array.from({ length: 15 }, (_, offset) => ({
  day: String(offset + 1),
  label: `Day ${offset + 1}`,
  disabled: offset >= 13,
}));
const bashoEntry = {
  basho: "2026/09",
  year: 2026,
  month: 9,
  label: "September 2026",
  payload_path: "data/by-basho/2026-09.csv",
  days,
};
const index = {
  default_basho: "2026/09",
  default_day: null,
  default_division: "makuuchi",
  divisions: [{ id: "makuuchi", label: "Makuuchi" }],
  entries: [bashoEntry],
};

assert.equal(selectedTorikumiEntry(bashoEntry), null);
assert.equal(selectedTorikumiEntry(bashoEntry, "13").day, "13");
assert.throws(() => selectedTorikumiEntry(bashoEntry, "14"), /Bad URL/);

const state = { basho_year: "2026", basho_month: "9", torikumi_day: "" };
const dayValues = torikumiDayValues(index, state);
assert.equal(dayValues.length, 15);
assert.deepEqual(dayValues[12], { value: "13", label: "Day 13", disabled: false });
assert.deepEqual(dayValues[13], { value: "14", label: "Day 14", disabled: true });
const dayFilter = { id: "torikumi_day", label: "Day", control: "select", default: "" };
const dayControl = renderFilter(dayFilter, state, index);
assert.match(dayControl, /class="torikumi-day-table"/);
assert.match(dayControl, /name="torikumi_day" value=""/);
assert.match(dayControl, /data-torikumi-day="14" aria-pressed="false" disabled/);
assert.equal((dayControl.match(/<tr>/g) || []).length, 4);
assert.match(dayControl, /data-torikumi-day="15"[^>]*>15<\/button><\/td><td aria-hidden="true"><\/td>/);

const correctRow = {
  east_id: "1",
  east_shikona: "Fred",
  east_elo89: "1600.0",
  east_odds: "1.48",
  prediction_side: "east",
  prediction_result: "correct",
  result_type: "normal",
  west_odds: "3.08",
  west_elo89: "1450.0",
  west_shikona: "Bill",
  west_id: "2",
};
assert.equal(predictionText(correctRow), "East to win ✓");
assert.equal(predictionText({ ...correctRow, prediction_side: "west", prediction_result: "incorrect" }), "West to win ✕");
assert.equal(predictionText({ ...correctRow, prediction_result: "pending" }), "East to win");
assert.equal(formatProfitLoss(1), "£1.00 profit");
assert.equal(formatProfitLoss(-2.345), "£2.35 loss");

const table = renderTorikumiTable([correctRow]);
assert.match(table, /<th>East<\/th><th>Elo89<\/th><th>Odds<\/th><th>Elo89 prediction<\/th>/);
assert.match(table, /East to win ✓/);
assert.match(table, />1\.48<\/td>/);
assert.match(table, /href="https:\/\/sumodb\.sumogames\.de\/Rikishi\.aspx\?r=1"/);
assert.match(table, /data-alt-href="index\.html\?page=career_comparisons&amp;skill=chii&amp;x=date&amp;log=true&amp;rikishi=1"/);

const summary = renderTorikumiSummary({
  correct: 7,
  scored: 10,
  favourite_profit: 1.64,
  winner_profit: 6.25,
  chii_scored: 10,
  chii_profit: -2,
  fusen_excluded: 1,
  draw_excluded: 0,
  equal_rating_excluded: 1,
  missing_rating_excluded: 0,
  pending: 0,
});
assert.match(summary, /7\/10 correct — 70\.0%/);
assert.match(summary, /£1\.64 profit/);
assert.match(summary, /£6\.25 profit/);
assert.match(summary, /£1 on each higher-chii rikishi:<\/strong> £2\.00 loss/);
assert.match(summary, /1 fusen bout; 1 equal-rating bout excluded/);
