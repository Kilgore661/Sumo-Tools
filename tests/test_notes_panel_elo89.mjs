import test from "node:test";
import assert from "node:assert/strict";

import {
  applyNotesCollapsedState,
  renderNotes,
} from "../src/products/make_site89/runtime/site-refactor/ui/notes.js";

test("Notes toggle carries the title and the body has no duplicate heading", () => {
  const html = renderNotes({
    notes: [{ id: "note_one", applies_to: ["all"], text: "One note." }],
  }, {});

  assert.match(html, />Notes ˅<\/button>/);
  assert.doesNotMatch(html, /<h4>Notes<\/h4>/);
});

test("Notes toggle text follows collapsed state", () => {
  const classes = new Set();
  const panel = {
    classList: {
      toggle(name, enabled) {
        if (enabled) classes.add(name);
        else classes.delete(name);
      },
    },
  };
  const body = { hidden: false };
  const attributes = new Map();
  const toggle = {
    textContent: "",
    title: "",
    setAttribute(name, value) {
      attributes.set(name, value);
    },
  };

  applyNotesCollapsedState(panel, body, toggle, true);
  assert.equal(toggle.textContent, "Notes ˄");
  assert.equal(body.hidden, true);
  assert.equal(attributes.get("aria-expanded"), "false");

  applyNotesCollapsedState(panel, body, toggle, false);
  assert.equal(toggle.textContent, "Notes ˅");
  assert.equal(body.hidden, false);
  assert.equal(attributes.get("aria-expanded"), "true");
});
