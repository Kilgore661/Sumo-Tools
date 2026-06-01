// HTTP fetch helpers for generated runtime JSON and CSV assets.

import { parseCsv } from "./csv.js";

// Fetch and parse a generated JSON asset.
async function fetchJson(path) {
  const response = await fetch(cacheBustedUrl(path));
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return response.json();
}
// Fetch and parse a generated CSV asset.
async function fetchCsv(path) {
  const response = await fetch(cacheBustedUrl(path));
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return parseCsv(await response.text());
}
// Preserve build cache-busting when the page URL carries a runtime token.
function cacheBustedUrl(path) {
  if (document.body.dataset.cacheMode !== "dev" || !document.body.dataset.cacheBust) {
    return path;
  }
  const url = new URL(path, window.location.href);
  url.searchParams.set(document.body.dataset.cacheBustParam || "cb", document.body.dataset.cacheBust);
  return url.toString();
}

export { fetchJson, fetchCsv, cacheBustedUrl };
