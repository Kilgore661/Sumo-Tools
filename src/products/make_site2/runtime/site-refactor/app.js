import { bootSiteContext } from "./core/context.js";
import { bootNavigationToggle } from "./ui/navigation-toggle.js";

bootSiteContext();
bootNavigationToggle();
boot().catch(error => {
  contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
});

import { siteContext } from "./core/context.js";
import { contentPanel } from "./core/dom.js";
import { getRuntimeManifest, setRuntimeManifest } from "./core/manifest-store.js";
import { PAGE_PARAM, writePageUrl } from "./core/url-state.js";
import { fetchJson } from "./data/http.js";
import { renderContentPanel } from "./panels/render-content-panel.js";
import { escapeHtml } from "./utils/html.js";

async function boot() {
  setRuntimeManifest(await fetchJson("runtime/site-manifest.json"));
  const navLinks = [...document.querySelectorAll(".nav-link[data-page-id]")];
  for (const link of navLinks) {
    link.addEventListener("click", event => {
      event.preventDefault();
      selectPage(link.dataset.pageId, { pushUrl: true });
    });
  }
  window.addEventListener("popstate", () => loadStateFromUrl());
  loadStateFromUrl();
}
function loadStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const pageId = params.get(PAGE_PARAM) || "";
  if (!pageId) {
    markActivePage("");
    renderLandingPanel();
    return;
  }
  selectPage(pageId);
}
function renderLandingPanel() {
  const context = siteContext();
  contentPanel.innerHTML = [
    '<section class="landing-panel">',
    `<h2>${escapeHtml(context.label)}</h2>`,
    '</section>'
  ].join("");
}
function selectPage(pageId, { pushUrl = false, replaceUrl = false } = {}) {
  const panel = getRuntimeManifest().ui.content_panels.find(candidate => candidate.page_id === pageId);
  if (!panel) {
    window.alert(
      `The requested page "${pageId}" is not available in this site build. Showing the home page instead.`
    );
    markActivePage("");
    writePageUrl("", { replace: true });
    renderLandingPanel();
    return;
  }
  markActivePage(pageId);
  if (pushUrl || replaceUrl) {
    writePageUrl(pageId, { replace: replaceUrl });
  }
  renderContentPanel(panel).catch(error => {
    contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  });
}
function markActivePage(pageId) {
  for (const link of document.querySelectorAll(".nav-link[data-page-id]")) {
    link.classList.toggle("is-active", link.dataset.pageId === pageId);
  }
}

export { boot, loadStateFromUrl, renderLandingPanel, selectPage, markActivePage };
