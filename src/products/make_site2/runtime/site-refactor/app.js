import { bootSiteContext, siteContext } from "./core/context.js";
import { contentPanel } from "./core/dom.js";
import { getRuntimeManifest, setRuntimeManifest } from "./core/manifest-store.js";
import { PAGE_PARAM, writeCanonicalViewUrl } from "./core/url-state.js";
import { fetchJson } from "./data/http.js";
import { renderContentPanel } from "./panels/render-content-panel.js";
import { bootNavigationToggle } from "./ui/navigation-toggle.js";
import { escapeHtml } from "./utils/html.js";

bootSiteContext();
bootNavigationToggle();
boot().catch(error => {
  contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
});

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
function loadStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const pageId = params.get(PAGE_PARAM) || "";
  if (!pageId) {
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
function selectPage(
  pageId,
  { pushDefaultView = false, canonicalizeUnfilteredView = false } = {},
) {
  const panel = getRuntimeManifest().ui.content_panels.find(candidate => candidate.page_id === pageId);
  if (!panel) {
    window.alert(
      `The requested page "${pageId}" is not available in this site build. Showing the home page instead.`
    );
    markActivePage("");
    writeCanonicalViewUrl("", [], {}, { replace: true });
    renderLandingPanel();
    return;
  }
  markActivePage(pageId);
  const filters = panelFilters(panel);
  if (pushDefaultView) {
    writeCanonicalViewUrl(pageId, filters, defaultFilterState(filters), { replace: false });
  } else if (canonicalizeUnfilteredView && !filters.length) {
    writeCanonicalViewUrl(pageId, [], {}, { replace: true });
  }
  renderContentPanel(panel).catch(error => {
    contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  });
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

export { boot, isInPlaceNavigationClick, loadStateFromUrl, renderLandingPanel, selectPage, panelFilters, defaultFilterState, markActivePage };
