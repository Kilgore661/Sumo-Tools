import assert from "node:assert/strict";
import test from "node:test";

import {
  prospectsLayout,
  prospectsCandidateLabel,
  prospectsRikishiOptions,
  prospectsTraces,
  renderProspectsChart,
  renderProspectsControls,
} from "../src/products/make_site89/runtime/site-refactor/ui/charts/prospects.js";

const columns = [
  "basho", "date", "age", "exact_age", "division", "rank_number", "chii",
  "point_kind", "probability", "cohort_observations", "cohort_rikishi",
  "cohort_success", "cohort_failure", "cohort_unresolved", "cohort_resolved",
  "support_tier",
];
const data = {
  columns,
  rikishi: [{ id: 2, shikona: "Test Rikishi" }],
  points_by_rikishi: {
    2: [
      ["2000/01", "2000-01-09", 20, 20.5, "M", 2, "M2e", "cohort_probability", 0.25, 12, 10, 2, 6, 2, 8, "very_low"],
      ["2000/03", "2000-03-12", 20, 20.7, "K", 1, "K1e", "sanyaku_attainment", 1, null, null, null, null, null, null, "attained"],
    ],
  },
};

test("Prospects controls default to age and provide searchable selection", () => {
  const html = renderProspectsControls("age");
  assert.match(html, /value="age" checked/);
  assert.match(html, /career-comparison-mode-table/);
  assert.match(html, /role="combobox"/);
  assert.match(html, /career-comparison-candidates/);
});

test("Prospects chart includes the same titled host used for an empty-state message", () => {
  const html = renderProspectsChart({ heading: "San'yaku Prospects" });
  assert.match(html, /artifact-title-block/);
  assert.match(html, /San&#39;yaku Prospects/);
  assert.match(html, /id="prospects-chart"/);
});

test("Prospects candidate labels disambiguate duplicate shikona only", () => {
  const options = prospectsRikishiOptions({ rikishi: [
    { id: 1, shikona: "Same" }, { id: 2, shikona: "Same" }, { id: 3, shikona: "Unique" },
  ] });
  assert.equal(prospectsCandidateLabel(options[0], options), "Same (1)");
  assert.equal(prospectsCandidateLabel(options[2], options), "Unique");
});

test("Prospects options are sorted by shikona", () => {
  const options = prospectsRikishiOptions({ rikishi: [
    { id: 2, shikona: "Zed" }, { id: 1, shikona: "Alpha" }, { id: 3, shikona: "Beta" },
  ] });
  assert.deepEqual(options.map(option => option.label), ["Alpha", "Beta", "Zed"]);
});

test("Prospects layout uses the transparent site chart theme", () => {
  const layout = prospectsLayout({ provenance: { legend_title: "Rikishi" } }, "age");
  assert.equal(layout.paper_bgcolor, "rgba(0,0,0,0)");
  assert.equal(layout.plot_bgcolor, "rgba(0,0,0,0)");
  assert.equal(layout.font.color, "#ffffff");
});

test("Prospects traces include a thin line, support marker, and attainment star", () => {
  const traces = prospectsTraces(data, ["2"], "age");
  assert.equal(traces[0].line.width, 1);
  assert.deepEqual(traces[0].x, [20.5, 20.7]);
  assert.equal(traces[1].marker.size, 4);
  assert.equal(traces[1].marker.color, "#e31a1c");
  assert.equal(traces[1].marker.line.color, "#e31a1c");
  assert.equal(traces[1].marker.line.width, 0.5);
  assert.equal(traces[1].hoverlabel.bgcolor, traces[0].line.color);
  assert.equal(traces[2].marker.symbol, "star");
  assert.equal(traces[2].showlegend, false);
  assert.equal(traces[2].hoverlabel.bgcolor, traces[0].line.color);
  assert.equal(traces[2].y[0], 1);
  assert.equal(traces.length, 3);
  assert.ok(traces.every(trace => trace.meta.rikishiId === "2"));
});

test("Date mode uses exact basho dates", () => {
  const traces = prospectsTraces(data, ["2"], "date");
  assert.deepEqual(traces[0].x, ["2000-01-09", "2000-03-12"]);
});
