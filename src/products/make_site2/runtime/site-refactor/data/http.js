import { parseCsv } from "./csv.js";

async function fetchJson(path) {
  const response = await fetch(cacheBustedUrl(path));
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return response.json();
}
async function fetchCsv(path) {
  const response = await fetch(cacheBustedUrl(path));
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return parseCsv(await response.text());
}
function cacheBustedUrl(path) {
  if (document.body.dataset.cacheMode !== "dev" || !document.body.dataset.cacheBust) {
    return path;
  }
  const url = new URL(path, window.location.href);
  url.searchParams.set(document.body.dataset.cacheBustParam || "cb", document.body.dataset.cacheBust);
  return url.toString();
}

export { fetchJson, fetchCsv, cacheBustedUrl };
