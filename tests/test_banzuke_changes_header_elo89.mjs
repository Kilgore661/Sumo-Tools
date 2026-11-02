import test from "node:test";
import assert from "node:assert/strict";

import {
  renderBanzukeScanTable,
} from "../src/products/make_site89/runtime/site-refactor/ui/tables/banzuke-changes.js";

const artifact = { id: "banzuke_changes" };

function tableHead(html) {
  return html.match(/<thead>[\s\S]*?<\/thead>/)?.[0] || "";
}

test("delta-only Elo-89 scan view uses one compact ΔBz heading", () => {
  const head = tableHead(renderBanzukeScanTable(
    artifact,
    [],
    { delta: true, context: false, rating: false },
  ));

  assert.match(head, /data-column-path="previous_basho\.delta"[^>]*>.*ΔBz/);
  assert.doesNotMatch(head, /Previous Basho/);
  assert.doesNotMatch(head, />Change/);
  assert.equal((head.match(/<tr>/g) || []).length, 1);
});

test("contextual Elo-89 scan view retains its Previous Basho group", () => {
  const head = tableHead(renderBanzukeScanTable(
    artifact,
    [],
    { delta: true, context: true, rating: false },
  ));

  assert.match(head, />Previous Basho<\/th>/);
  assert.match(head, /data-column-path="previous_basho\.delta"[^>]*>.*ΔBz/);
  assert.equal((head.match(/<tr>/g) || []).length, 2);
});
