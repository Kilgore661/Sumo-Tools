// Browser URL state helpers for page and filter selection.

export const PAGE_PARAM = "page";
const PASSTHROUGH_PARAMS = ["debug_layout"];

// Build the canonical public view URL for a page/filter state.
function publicViewUrl(pageId, filters = [], state = {}) {
  const params = new URLSearchParams();
  if (pageId) params.set(PAGE_PARAM, pageId);
  for (const filter of filters) {
    const value = state[filter.id] ?? filter.default;
    params.set(filter.url_key || filter.id, serializeFilterValue(value));
  }
  appendPassthroughParams(params);
  const search = params.toString();
  return `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
}
function serializeFilterValue(value) {
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
}
// Write a canonical view URL using history push or replace semantics.
function writeCanonicalViewUrl(pageId, filters = [], state = {}, { replace }) {
  const next = publicViewUrl(pageId, filters, state);
  const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (next === current) return;
  if (replace) {
    history.replaceState(null, "", next);
  } else {
    history.pushState(null, "", next);
  }
}
function writePanelUrl(pageId, filters, state, options) {
  writeCanonicalViewUrl(pageId, filters, state, options);
}
// Read the filter subset of the current browser URL.
function readFilterUrlState(filters) {
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(filters.map(filter => [
    filter.id,
    params.get(filter.url_key || filter.id)
  ]));
}

function appendPassthroughParams(targetParams) {
  const currentParams = new URLSearchParams(window.location.search);
  const embeddedParams = embeddedPageParams(currentParams);
  for (const key of PASSTHROUGH_PARAMS) {
    const value = currentParams.get(key) ?? embeddedParams.get(key);
    if (value !== null) targetParams.set(key, value);
  }
}

function embeddedPageParams(params) {
  const page = params.get(PAGE_PARAM) || "";
  const queryStart = page.indexOf("?");
  if (queryStart < 0) return new URLSearchParams();
  return new URLSearchParams(page.slice(queryStart + 1));
}

function cleanPageParam(params) {
  const page = params.get(PAGE_PARAM) || "";
  return page.split("?")[0];
}

function normalizeEmbeddedPageParams() {
  const params = new URLSearchParams(window.location.search);
  const embeddedParams = embeddedPageParams(params);
  if (![...embeddedParams.keys()].length) return;
  params.set(PAGE_PARAM, cleanPageParam(params));
  for (const key of PASSTHROUGH_PARAMS) {
    const value = embeddedParams.get(key);
    if (value !== null) params.set(key, value);
  }
  const search = params.toString();
  history.replaceState(
    null,
    "",
    `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`,
  );
}

export {
  publicViewUrl,
  serializeFilterValue,
  writeCanonicalViewUrl,
  writePanelUrl,
  readFilterUrlState,
  appendPassthroughParams,
  embeddedPageParams,
  cleanPageParam,
  normalizeEmbeddedPageParams,
};
