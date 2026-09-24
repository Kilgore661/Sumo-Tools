import test from "node:test";
import assert from "node:assert/strict";

import {
  annotatedShikona,
  renderPromotionAnnotation,
} from "../src/products/make_site89/runtime/site-refactor/ui/tables/shared.js";


test("annotations render after canonical linked shikona in their fixed order", () => {
  const html = annotatedShikona("Fred", "123", {
    highestChii: "true",
    promotionKind: "yokydj",
    promotionStatus: "open",
    promotionPreviousResult: "Y",
  });

  assert.match(html, />Fred<\/a> <span[^>]*>\(<span[^>]*>\*<\/span> <span[^>]*>!<\/span>\)<\/span>$/);
  assert.match(html, /career-high rank for the first time/);
  assert.match(html, /Y, D or J result/);
});


test("Ozeki32 rendering uses producer-provided remaining wins", () => {
  const html = annotatedShikona("Bill", "456", {
    highestChii: true,
    promotionKind: "ozeki32",
    promotionStatus: "open",
    promotionRequired: "7",
  });

  assert.match(html, />Bill<\/a> <span[^>]*>\(<span[^>]*>\*<\/span> <span[^>]*>7<\/span>\)<\/span>$/);
  assert.doesNotMatch(html, /\(\(7\)\)/);
});


test("a highest-chii marker uses the same single suffix group", () => {
  const html = annotatedShikona("Tom", "789", { highestChii: "true" });

  assert.match(html, />Tom<\/a> <span[^>]*>\(<span[^>]*>\*<\/span>\)<\/span>$/);
});


test("achieved and impossible promotion states have distinct presentation", () => {
  assert.match(renderPromotionAnnotation({
    promotionKind: "ozeki32",
    promotionStatus: "achieved",
  }), />✓<\/span>$/);
  assert.equal(renderPromotionAnnotation({
    promotionKind: "ozeki32",
    promotionStatus: "impossible",
    promotionRequired: "1",
  }), "");
});
