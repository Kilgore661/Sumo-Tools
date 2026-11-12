import test from "node:test";
import assert from "node:assert/strict";

import {
  banzukeDeltaDisplay,
  banzukeDeltaHtml,
  banzukeResultHtml,
  banzukeScanColumns,
  banzukeSideColumns,
  buildBanzukeRatingsFit,
  ratingsFitErrorHtml,
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

test("Ratings Fit is the final scan-table group", () => {
  const state = { context: true, rating: true, ratings_fit: true };
  assert.deepEqual(
    banzukeScanColumns(state).map(column => column.id),
    [
      "row_number", "chii", "shikona", "delta", "rating",
      "old_chii", "result", "delta_chii", "nu_chii",
    ],
  );
  const head = tableHead(renderBanzukeScanTable(artifact, [], state));
  assert.match(head, /data-column-path="ratings_fit"[^>]*>[\s\S]*Ratings Fit/);
  assert.match(head, />ΔChii/);
  assert.match(head, />νChii/);
  assert.match(head, /data-note-id="note_delta_chii"/);
  assert.match(head, /data-note-id="note_nu_chii"/);
});

test("Banzuke Style mirrors Ratings Fit and Previous Basho subcolumns", () => {
  const state = { context: true, rating: true, ratings_fit: true };
  assert.deepEqual(
    banzukeSideColumns("east", state).map(column => column.id),
    [
      "delta_chii", "nu_chii", "rating", "old_chii", "result", "delta",
      "shikona",
    ],
  );
  assert.deepEqual(
    banzukeSideColumns("west", state).map(column => column.id),
    [
      "shikona", "delta", "result", "old_chii", "rating", "nu_chii",
      "delta_chii",
    ],
  );
  const head = tableHead(renderBanzukeStyleTable([], state));
  assert.equal((head.match(/data-column-id="ratings_fit"/g) || []).length, 2);
  assert.equal((head.match(/data-column-id="previous_basho"/g) || []).length, 2);
  assert.equal((head.match(/>Ratings Fit<\/th>/g) || []).length, 2);
  assert.equal((head.match(/>Previous Basho<\/th>/g) || []).length, 2);
  assert.equal((head.match(/data-note-id="note_delta_chii"/g) || []).length, 2);
  assert.equal((head.match(/data-note-id="note_nu_chii"/g) || []).length, 2);
  assert.equal((head.match(/<tr>/g) || []).length, 3);
});

test("Ratings Fit compares official order with Elo-89 order", () => {
  const rows = [{
    east_rikishi_id: "1",
    east_chii: "M1e",
    east_rating: "1900",
    west_rikishi_id: "2",
    west_chii: "M1w",
    west_rating: "2100",
  }];
  const fit = buildBanzukeRatingsFit(rows);

  assert.deepEqual(fit.get("1"), {
    signedError: -1,
    nuChii: "M1w",
    nuChiiOrdinal: 400003,
  });
  assert.deepEqual(fit.get("2"), {
    signedError: 1,
    nuChii: "M1e",
    nuChiiOrdinal: 400002,
  });
  assert.equal(
    ratingsFitErrorHtml(1),
    '<span class="banzuke-inline-arrow">↑</span> 1',
  );
  assert.equal(
    ratingsFitErrorHtml(-1),
    '<span class="banzuke-inline-arrow">↓</span> 1',
  );
  assert.equal(ratingsFitErrorHtml(0), "");
});
