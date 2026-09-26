import assert from "node:assert/strict";

import {
  renderTorikumiTable,
  selectedTorikumiEntry,
} from "../src/products/make_site89/runtime/site-refactor/ui/torikumi.js";

globalThis.document = { getElementById: () => null };
const { renderDropdownChoice, renderFilter, torikumiDayValues } = await import(
  "../src/products/make_site89/runtime/site-refactor/ui/filters.js"
);

const index = {
  default_day: "14",
  default_division: "makuuchi",
  divisions: [
    { id: "makuuchi", label: "Makuuchi" },
    { id: "juryo", label: "Juryo" },
    { id: "makushita", label: "Makushita" },
    { id: "sandanme", label: "Sandanme" },
    { id: "jonidan", label: "Jonidan" },
    { id: "jonokuchi", label: "Jonokuchi" },
  ],
  entries: Array.from({ length: 15 }, (_, offset) => {
    const day = String(offset + 1);
    return {
      day,
      label: `Day ${day}`,
      ...(offset < 14 ? { payload_path: `data/day-${day}.csv`, disabled: false } : { disabled: true }),
    };
  }),
};

assert.equal(selectedTorikumiEntry(index).day, "14");
assert.equal(selectedTorikumiEntry(index, "13").day, "13");
assert.throws(
  () => selectedTorikumiEntry(index, "15"),
  /Error\. Never do that again\./,
);
const dayValues = torikumiDayValues(index);
assert.equal(dayValues.length, 15);
assert.deepEqual(dayValues[13], { value: "14", label: "Day 14", disabled: false });
assert.deepEqual(dayValues[14], { value: "15", label: "Day 15", disabled: true });
assert.match(renderDropdownChoice({ id: "day", label: "Day" }, dayValues, "14"), /value="15" disabled/);
const dayFilter = { id: "torikumi_day", label: "Day", control: "choice", default: "14" };
const dayControl = renderFilter(dayFilter, { torikumi_day: "14" }, index);
assert.match(dayControl, /<select name="torikumi_day">/);
assert.doesNotMatch(dayControl, /type="radio"/);

const table = renderTorikumiTable([{
  east_id: "1",
  east_shikona: "Fred",
  east_elo89: "1500",
  east_probability: "25%",
  west_probability: "75%",
  west_elo89: "1600",
  west_shikona: "Bill",
  west_id: "2",
}]);
assert.match(table, /<th colspan="3">East<\/th><th colspan="3">West<\/th>/);
assert.match(table, /<th colspan="2">P\(win\)<\/th>/);
assert.doesNotMatch(table, /Forecast/);
assert.match(table, /Fred/);
assert.match(table, /25%/);
assert.match(table, /75%/);
assert.match(table, /href="https:\/\/sumodb\.sumogames\.de\/Rikishi\.aspx\?r=1"/);
assert.match(table, /data-alt-href="index\.html\?page=career_comparisons&amp;skill=chii&amp;x=date&amp;log=true&amp;rikishi=1"/);
assert.match(table, /href="https:\/\/sumodb\.sumogames\.de\/Rikishi\.aspx\?r=2"/);
