/**
 * State synchronization brokers managing History and address configuration strings.
 */

const PAGE_PARAM = "page";

export function readFilterUrlState(filters) {
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(filters.map(filter => [
    filter.id,
    params.get(filter.url_key || filter.id)
  ]));
}

export function writePageUrl(pageId, { replace }) {
  const params = new URLSearchParams();
  if (pageId) {
    params.set(PAGE_PARAM, pageId);
  } else {
    params.delete(PAGE_PARAM);
  }
  const search = params.toString();
  const next = `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
  if (next === `${window.location.pathname}${window.location.search}${window.location.hash}`) return;
  if (replace) {
    history.replaceState(null, "", next);
  } else {
    history.pushState(null, "", next);
  }
}

export function writePanelUrl(pageId, filters, state, { replace }) {
  const params = new URLSearchParams();
  if (pageId) params.set(PAGE_PARAM, pageId);
  for (const filter of filters) {
    params.set(filter.url_key || filter.id, String(state[filter.id]));
  }
  const search = params.toString();
  const next = `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
  if (next === `${window.location.pathname}${window.location.search}${window.location.hash}`) return;
  if (replace) {
    history.replaceState(null, "", next);
  } else {
    history.pushState(null, "", next);
  }
}