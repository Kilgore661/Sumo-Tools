import test from "node:test";
import assert from "node:assert/strict";

import {
  banzukeScanColumns,
  renderBanzukeScanTable,
  renderBanzukeStyleTable,
} from "../src/products/make_site2/runtime/site-refactor/ui/tables/banzuke-changes.js";

const artifact = { id: "banzuke_changes" };

function tableHead(html) {
  return html.match(/<thead>[\s\S]*?<\/thead>/)?.[0] || "";
}

test("scan view derives a Previous Basho group from the visible leaf columns", () => {
  const state = { delta: true, context: true, equelo: true };
  const html = renderBanzukeScanTable(artifact, [], state);
  const head = tableHead(html);

  assert.deepEqual(
    banzukeScanColumns(state).map(column => column.id),
    ["row_number", "chii", "shikona", "direction", "delta", "result", "old_chii", "equelo"],
  );
  assert.match(head, /data-column-path="previous_basho"[^>]*colspan="4"|colspan="4"[^>]*data-column-path="previous_basho"/);
  assert.match(head, />Previous Basho<\/th>/);
  for (const columnId of ["row_number", "chii", "shikona", "direction"]) {
    assert.match(
      head,
      new RegExp(`data-column-id="${columnId}"[^>]*rowspan="2"`),
    );
  }
  assert.equal((head.match(/<tr>/g) || []).length, 2);
});

test("Previous Basho group contracts and disappears from the option projection", () => {
  const contextHead = tableHead(renderBanzukeScanTable(
    artifact,
    [],
    { delta: false, context: true, equelo: false },
  ));
  assert.match(contextHead, /data-column-path="previous_basho"[^>]*colspan="2"|colspan="2"[^>]*data-column-path="previous_basho"/);

  const bareHead = tableHead(renderBanzukeScanTable(
    artifact,
    [],
    { delta: false, context: false, equelo: false },
  ));
  assert.doesNotMatch(bareHead, /Previous Basho/);
  assert.equal((bareHead.match(/<tr>/g) || []).length, 1);
});

test("paired banzuke presentation keeps its East Rank West structure", () => {
  const head = tableHead(renderBanzukeStyleTable([], {
    delta: true,
    context: true,
    equelo: true,
  }));

  assert.match(head, />East<\/th>/);
  assert.match(head, />Rank<\/th>/);
  assert.match(head, />West<\/th>/);
});
