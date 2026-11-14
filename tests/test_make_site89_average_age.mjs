import assert from "node:assert/strict";

import { attachGroupedLineLegendHandler, groupedChartLayout, groupedLineTraces, groupedLineVisibility, strictLegendVisibility } from "../src/products/make_site89/runtime/site-refactor/ui/charts/generic.js";

const artifact = {
  id: "average_age_by_division",
  data_binding: { sources: ["average_ages"] },
  traces: [{
    kind: "scatter", x: "basho", y: "mean_age_years", group_by: "division",
    error_y: ["min_age_years", "max_age_years"],
  }],
  provenance: {
    group_order: ["Makuuchi", "Juryo"],
    hover_fields: ["start_date"],
    hover_template: "Mean=%{y:.2f}<extra></extra>",
  },
  x_axis: { label: "Basho", order_values: [], minimum: null, maximum: null },
  y_axis: { label: "Age (years)", order_values: [], minimum: null, maximum: null },
};
const rowsBySource = { average_ages: [
  { basho: "2020/01", division: "Makuuchi", mean_age_years: "28", min_age_years: "20", max_age_years: "40", start_date: "2020-01-12" },
  { basho: "2020/01", division: "Juryo", mean_age_years: "25", min_age_years: "19", max_age_years: "35", start_date: "2020-01-12" },
  { basho: "2020/03", division: "Juryo", mean_age_years: "", min_age_years: "", max_age_years: "", start_date: "2020-03-08" },
] };

const withoutRanges = groupedLineTraces(artifact, rowsBySource, { error_bars: false });
assert.equal(withoutRanges.length, 2);
assert.deepEqual(withoutRanges.map(trace => trace.name), ["Makuuchi", "Juryo"]);
assert.ok(withoutRanges.every(trace => trace.visible === true));
assert.ok(withoutRanges.every(trace => !("error_y" in trace)));
assert.deepEqual(withoutRanges[1].y, [25, null]);

const withRanges = groupedLineTraces(artifact, rowsBySource, { error_bars: true });
assert.deepEqual(withRanges[0].error_y.array, [12]);
assert.deepEqual(withRanges[0].error_y.arrayminus, [8]);
assert.equal(withRanges[0].hovertemplate, artifact.provenance.hover_template);

const makuuchiDefault = {
  ...artifact,
  provenance: { ...artifact.provenance, default_visible: ["Makuuchi"] },
};
assert.deepEqual(
  groupedLineTraces(makuuchiDefault, rowsBySource, { error_bars: false }).map(trace => trace.visible),
  [true, "legendonly"],
);
const savedVisibility = groupedLineVisibility({ data: [
  { name: "Makuuchi", visible: "legendonly" },
  { name: "Juryo", visible: true },
] });
assert.deepEqual(savedVisibility, { Makuuchi: false, Juryo: true });
assert.deepEqual(
  groupedLineTraces(makuuchiDefault, rowsBySource, { error_bars: true, group_visibility: savedVisibility })
    .map(trace => trace.visible),
  ["legendonly", true],
);

const persistenceArtifact = {
  id: "division_stability",
  data_binding: { sources: ["persistence"] },
  traces: [{ kind: "scatter", x: "date", y: "mean_persistence", group_by: "division" }],
  provenance: { group_order: ["Makuuchi", "Juryo"], default_visible: ["Makuuchi"] },
};
const persistence = groupedLineTraces(persistenceArtifact, { persistence: [
  { date: "2020/01", division: "Makuuchi", mean_persistence: "0.9" },
  { date: "2020/01", division: "Juryo", mean_persistence: "0.8" },
] });
assert.deepEqual(persistence.map(trace => trace.visible), [true, "legendonly"]);
assert.ok(persistence.every(trace => !("error_y" in trace)));

assert.deepEqual(
  strictLegendVisibility([{ name: "Makuuchi" }, { name: "Juryo" }], 0),
  [true, "legendonly"],
);
assert.deepEqual(
  strictLegendVisibility([{ name: "Makuuchi" }, { name: "Juryo" }], 0),
  [true, "legendonly"],
  "double-clicking an already isolated trace must not restore all traces",
);
assert.equal(strictLegendVisibility([], 0), null);
const groupedLayout = groupedChartLayout(artifact, rowsBySource);
assert.equal(groupedLayout.legend.itemclick, "toggle");
assert.equal(groupedLayout.legend.itemdoubleclick, false);

const handlers = {};
const restyles = [];
globalThis.Plotly = { restyle: (...args) => restyles.push(args) };
const host = {
  data: [{ name: "Makuuchi", visible: true }, { name: "Juryo", visible: "legendonly" }],
  on: (eventName, handler) => { handlers[eventName] = handler; },
};
attachGroupedLineLegendHandler(host);
assert.equal(handlers.plotly_legenddoubleclick({ curveNumber: 0 }), false);
assert.deepEqual(restyles[0][1], { visible: [true, "legendonly"] });
