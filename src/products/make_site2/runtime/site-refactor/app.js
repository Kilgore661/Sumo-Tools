// Application boot, URL routing and page selection.

import { bootSiteContext, siteContext } from "./core/context.js";
import { contentPanel } from "./core/dom.js";
import { getRuntimeManifest, setRuntimeManifest } from "./core/manifest-store.js";
import { PAGE_PARAM, cleanPageParam, normalizeEmbeddedPageParams, writeCanonicalViewUrl } from "./core/url-state.js";
import { fetchJson } from "./data/http.js";
import { renderContentPanel } from "./panels/render-content-panel.js";
import { installHelpPopovers } from "./ui/help.js";
import { bootLayoutDebug } from "./ui/layout-debug.js";
import { bootNavigationToggle } from "./ui/navigation-toggle.js";
import { escapeHtml } from "./utils/html.js";

const PASSTHROUGH_PARAMS = ["debug_layout", "debug_show_notes"];

bootSiteContext();
bootNavigationToggle();
normalizeEmbeddedPageParams();
bootLayoutDebug();
installHelpPopovers();
boot().catch(error => {
  contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
});

// Load the runtime manifest and wire browser navigation state.
async function boot() {
  setRuntimeManifest(await fetchJson("runtime/site-manifest.json"));
  const navLinks = [...document.querySelectorAll(".nav-link[data-page-id]")];
  for (const link of navLinks) {
    link.addEventListener("click", event => {
      if (!isInPlaceNavigationClick(event)) return;
      event.preventDefault();
      selectPage(link.dataset.pageId, { pushDefaultView: true });
    });
  }
  window.addEventListener("popstate", () => loadStateFromUrl());
  loadStateFromUrl();
}
function isInPlaceNavigationClick(event) {
  return event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;
}
// Read browser URL state and render either the landing panel or selected page.
function loadStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const pageId = cleanPageParam(params);
  if (!pageId) {
    if ([...params.keys()].some(key => !PASSTHROUGH_PARAMS.includes(key))) {
      handleBadUrl();
      return;
    }
    markActivePage("");
    renderLandingPanel();
    return;
  }
  selectPage(pageId, { canonicalizeUnfilteredView: true });
}
function renderLandingPanel() {
  const context = siteContext();
  contentPanel.innerHTML = [
    '<section class="landing-panel">',
    `<h2>${escapeHtml(context.label)}</h2>`,
    '</section>'
  ].join("");
}
function handleBadUrl() {
  window.alert("Bad URL");
  markActivePage("");
  writeCanonicalViewUrl("", [], {}, { replace: true });
  renderLandingPanel();
}
// Resolve a page id to a content panel and render it with canonical URL state.
function selectPage(
  pageId,
  { pushDefaultView = false, canonicalizeUnfilteredView = false } = {},
) {
  const panel = getRuntimeManifest().ui.content_panels.find(candidate => candidate.page_id === pageId);
  if (!panel) {
    handleBadUrl();
    return;
  }
  const filters = panelFilters(panel);
  if (!urlKeysAreAllowed(filters)) {
    handleBadUrl();
    return;
  }
  markActivePage(pageId);
  if (pushDefaultView) {
    writeCanonicalViewUrl(pageId, filters, defaultFilterState(filters), { replace: false });
  } else if (canonicalizeUnfilteredView && !filters.length) {
    writeCanonicalViewUrl(pageId, [], {}, { replace: true });
  }
  renderContentPanel(panel).catch(error => {
    if (error.message === "Bad URL") {
      handleBadUrl();
      return;
    }
    contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  });
}
function urlKeysAreAllowed(filters) {
  const params = new URLSearchParams(window.location.search);
  const allowed = new Set([
    PAGE_PARAM,
    ...PASSTHROUGH_PARAMS,
    ...filters.map(filter => filter.url_key || filter.id),
  ]);
  if (hasFilter(filters, "basho_year") && hasFilter(filters, "basho_month")) {
    allowed.add("basho");
    allowed.add("basho_date");
  }
  return [...params.keys()].every(key => allowed.has(key));
}
function hasFilter(filters, filterId) {
  return filters.some(filter => filter.id === filterId);
}
function panelFilters(panel) {
  return panel.contents.filter_section?.filters || [];
}
function defaultFilterState(filters) {
  return Object.fromEntries(filters.map(filter => [filter.id, filter.default]));
}
function markActivePage(pageId) {
  for (const link of document.querySelectorAll(".nav-link[data-page-id]")) {
    link.classList.toggle("is-active", link.dataset.pageId === pageId);
  }
}

export { boot, isInPlaceNavigationClick, loadStateFromUrl, renderLandingPanel, selectPage, panelFilters, defaultFilterState, markActivePage, handleBadUrl, urlKeysAreAllowed };