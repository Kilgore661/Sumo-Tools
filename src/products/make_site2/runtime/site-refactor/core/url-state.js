export const PAGE_PARAM = "page";

function publicViewUrl(pageId, filters = [], state = {}) {
  const params = new URLSearchParams();
  if (pageId) params.set(PAGE_PARAM, pageId);
  for (const filter of filters) {
    const value = state[filter.id] ?? filter.default;
    params.set(filter.url_key || filter.id, serializeFilterValue(value));
  }
  const search = params.toString();
  return `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
}
function serializeFilterValue(value) {
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
}
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
function readFilterUrlState(filters) {
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(filters.map(filter => [
    filter.id,
    params.get(filter.url_key || filter.id)
  ]));
}

export { publicViewUrl, serializeFilterValue, writeCanonicalViewUrl, writePanelUrl, readFilterUrlState };
