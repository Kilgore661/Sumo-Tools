import test from "node:test";
import assert from "node:assert/strict";

import {
  banzukeDeltaDisplay,
  banzukeDeltaHtml,
  banzukeResultHtml,
  banzukeScanColumns,
  renderBanzukeScanTable,
  renderBanzukeStyleTable,
} from "../src/products/make_site89/runtime/site-refactor/ui/tables/banzuke-changes.js";

const artifact = { id: "banzuke_changes" };

function tableHead(html) {
  return html.match(/<thead>[\s\S]*?<\/thead>/)?.[0] || "";
}

test("Elo-89 follows the always-visible ΔBz column in scan view", () => {
  const state = { context: false, rating: true };
  const head = tableHead(renderBanzukeScanTable(artifact, [], state));

  assert.deepEqual(
    banzukeScanColumns(state).map(column => column.id),
    ["row_number", "chii", "shikona", "delta", "rating"],
  );
  assert.match(head, /data-column-path="delta"[^>]*>.*ΔBz/);
  assert.doesNotMatch(head, /Previous Basho/);
  assert.equal((head.match(/<tr>/g) || []).length, 1);
});

test("Previous Basho contains only Chii and Result after ΔBz moves out", () => {
  const head = tableHead(renderBanzukeScanTable(
    artifact,
    [],
    { context: true, rating: true },
  ));

  assert.match(head, />Previous Basho<\/th>/);
  assert.match(
    head,
    /data-column-path="previous_basho"[^>]*colspan="2"|colspan="2"[^>]*data-column-path="previous_basho"/,
  );
  assert.doesNotMatch(head, /previous_basho\.delta/);
  assert.equal((head.match(/<tr>/g) || []).length, 2);
});

test("banzuke style replaces each direction column with ΔBz", () => {
  const head = tableHead(renderBanzukeStyleTable([], {
    context: false,
    rating: true,
  }));

  assert.equal((head.match(/data-column-id="delta"/g) || []).length, 2);
  assert.match(head, /ΔBz/);
  assert.doesNotMatch(head, />⇅<\/th>/);
  assert.doesNotMatch(head, />Change<\/th>/);
});

test("ΔBz renders signed values with arrows", () => {
  assert.equal(banzukeDeltaDisplay("+6"), "↑6");
  assert.equal(banzukeDeltaDisplay("-4"), "↓4");
  assert.equal(banzukeDeltaDisplay("0"), "0");
  assert.equal(banzukeDeltaDisplay(""), "");
  assert.equal(
    banzukeDeltaHtml("+6"),
    '<span class="banzuke-inline-arrow">↑</span> 6',
  );
  assert.equal(
    banzukeDeltaHtml("-4"),
    '<span class="banzuke-inline-arrow">↓</span> 4',
  );
});

test("Result movement arrows use the aligned inline-arrow treatment", () => {
  assert.equal(
    banzukeResultHtml("10-5 K", "↑"),
    '10-5 K <span class="banzuke-inline-arrow">↑</span>',
  );
  assert.equal(banzukeResultHtml("10-5", ""), "10-5");
});
