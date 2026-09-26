import assert from "node:assert/strict";

import {
  genericCellValue,
  genericRowsForState,
  renderGenericTable,
} from "../src/products/make_site89/runtime/site-refactor/ui/tables/generic.js";
import {
  sortRows,
} from "../src/products/make_site89/runtime/site-refactor/ui/tables/shared.js";

const artifact = {
  id: "rikishi_bio_data",
  heading: "Rikishi bio data",
  default_sort_column: "row_number",
  columns: [
    { id: "row_number", heading: "", sort_kind: "none", align: "right" },
    { id: "shikona", heading: "Shikona", source_field: "shikona", sort_kind: "text" },
    { id: "chii", heading: "Chii", source_field: "chii", sort_key: "chii_ordinal", sort_kind: "chii_ordinal" },
    { id: "age", heading: "Age", source_field: "age", sort_kind: "numeric" },
    { id: "height_cm", heading: "Height", source_field: "height_cm", sort_kind: "numeric" },
  ],
};
const rows = [
  { rikishi_id: "1", shikona: "Alpha", division: "makuuchi", age: "26", height_cm: "180" },
  { rikishi_id: "2", shikona: "Beta", division: "juryo", age: "", height_cm: "" },
  { rikishi_id: "3", shikona: "Gamma", division: "makuuchi", age: "22", height_cm: "175" },
];

assert.deepEqual(genericRowsForState(rows, { division: "makuuchi" }, artifact), [rows[0], rows[2]]);
assert.deepEqual(genericRowsForState(rows, { division: "all" }, artifact), rows);
assert.equal(genericCellValue(artifact.columns[2], rows[1], 1, artifact), "—");

const sorted = sortRows(rows, artifact.columns, { columnId: "age", direction: "descending" });
assert.deepEqual(sorted.map(row => row.rikishi_id), ["1", "3", "2"]);

const table = renderGenericTable(artifact, rows, { division: "makuuchi" });
assert.match(table, /href="https:\/\/sumodb\.sumogames\.de\/Rikishi\.aspx\?r=1"/);
assert.match(table, /data-alt-href="index\.html\?page=career_comparisons&amp;skill=chii/);
assert.match(table, /data-sort-column="age"/);
assert.doesNotMatch(table, />Beta</);
