import test from "node:test";
import assert from "node:assert/strict";

import {
  careerComparisonCandidateLabel,
  groupCareerComparisonOptionsByLabel,
  moveCareerComparisonCandidateHighlight,
  renderCareerComparisonsControls,
  resolveCareerComparisonCandidate,
} from "../src/products/make_site2/runtime/site-refactor/ui/charts/career-comparisons/controls.js";

const options = [
  { id: "1", label: "Fuji", prefixes: ["fuji", "1"] },
  { id: "2", label: "Fujika", prefixes: ["fujika", "2"] },
  { id: "3", label: "Hakuho", prefixes: ["hakuho", "3"] },
  { id: "4", label: "Hakuho", prefixes: ["hakuho", "4"] },
];
const optionsByLabel = groupCareerComparisonOptionsByLabel(options);
const optionsById = new Map(options.map(option => [option.id, option]));

test("chooser markup uses an application-controlled combobox and listbox", () => {
  const html = renderCareerComparisonsControls({ skill: "equelo", x_base: "date", log: false });

  assert.match(html, /role="combobox"/);
  assert.match(html, /role="listbox"/);
  assert.doesNotMatch(html, /<datalist/);
});

test("Return resolution requires a highlighted or exact unambiguous candidate", () => {
  assert.equal(
    resolveCareerComparisonCandidate("Fuji", null, optionsByLabel, optionsById, []),
    options[0],
  );
  assert.equal(
    resolveCareerComparisonCandidate("Fuj", null, optionsByLabel, optionsById, []),
    null,
  );
  assert.equal(
    resolveCareerComparisonCandidate("Hakuho", null, optionsByLabel, optionsById, []),
    null,
  );
  assert.equal(
    resolveCareerComparisonCandidate("Hakuho (3)", null, optionsByLabel, optionsById, []),
    options[2],
  );
  assert.equal(
    resolveCareerComparisonCandidate("Fuj", "2", optionsByLabel, optionsById, []),
    options[1],
  );
});

test("Return resolution excludes rikishi that are already selected", () => {
  assert.equal(
    resolveCareerComparisonCandidate("Fuji", null, optionsByLabel, optionsById, ["1"]),
    null,
  );
});

test("duplicate candidate labels are visibly disambiguated by rikishi id", () => {
  assert.equal(careerComparisonCandidateLabel(options[0], optionsByLabel), "Fuji");
  assert.equal(careerComparisonCandidateLabel(options[2], optionsByLabel), "Hakuho (3)");
  assert.equal(careerComparisonCandidateLabel(options[3], optionsByLabel), "Hakuho (4)");
});

test("arrow navigation establishes and cycles the highlighted candidate", () => {
  assert.equal(moveCareerComparisonCandidateHighlight(options, null, 1), "1");
  assert.equal(moveCareerComparisonCandidateHighlight(options, null, -1), "4");
  assert.equal(moveCareerComparisonCandidateHighlight(options, "4", 1), "1");
  assert.equal(moveCareerComparisonCandidateHighlight(options, "1", -1), "4");
});
