import { escapeHtml } from '../utils/dom.js';
import { fetchJson, fetchCsv } from '../utils/network.js';
import { bootSiteContext, siteContext } from './context.js';
import { readFilterUrlState, writePageUrl, writePanelUrl } from './routing.js';
import { delegateContentPanel } from '../components/renderers/index.js';

/**
 * Global App Application Bootstrap and Navigation Core Configuration Lifecycle Controller.
 */

(function () {
  const PAGE_PARAM = "page";
  const contentPanel = document.getElementById("content-panel");
  let runtimeManifest = null;

  bootSiteContext();
  bootNavigationToggle();
  boot().catch(error => {
    contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  });

  async function boot() {
    runtimeManifest = await fetchJson("runtime/site-manifest.json");
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

  function bootNavigationToggle() {
    const shell = document.querySelector("[data-nav-shell]");
    const panel = document.querySelector("[data-nav-panel]");
    const toggle = document.querySelector("[data-nav-toggle]");
    if (!shell || !panel || !toggle) return;

    const storageKey = toggle.dataset.storageKey || "gaspodeSumoLab.makeSite2.navCollapsed";
    const initialCollapsed = window.localStorage.getItem(storageKey) === "true";
    applyNavigationCollapsedState(shell, panel, toggle, initialCollapsed);

    toggle.addEventListener("click", () => {
      const collapsed = !shell.classList.contains("nav-collapsed");
      applyNavigationCollapsedState(shell, panel, toggle, collapsed);
      window.localStorage.setItem(storageKey, String(collapsed));
    });
  }

  function applyNavigationCollapsedState(shell, panel, toggle, collapsed) {
    shell.classList.toggle("nav-collapsed", collapsed);
    panel.hidden = collapsed;
    panel.setAttribute("aria-hidden", String(collapsed));
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.setAttribute("aria-label", collapsed ? "Show navigation" : "Hide navigation");
    toggle.title = collapsed ? "Show navigation" : "Hide navigation";
    toggle.textContent = collapsed ? ">" : "<";
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
    const panel = runtimeManifest.ui.content_panels.find(candidate => candidate.page_id === pageId);
    if (!panel) {
      window.alert(`The requested page "${pageId}" is not available in this site build. Showing the home page instead.`);
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

  async function renderContentPanel(panel, overrideState = null) {
    if (panel.grammar !== "G1") throw new Error(`Unsupported content grammar: ${panel.grammar}`);
    const artifact = runtimeManifest.artifacts[panel.contents.pa.artifact_id];
    if (!artifact) throw new Error(`Unknown artifact: ${panel.contents.pa.artifact_id}`);
    
    await delegateContentPanel(panel, artifact, overrideState, contentPanel, wireFilterSection, fetchArtifactCsvSet);
  }

  async function fetchArtifactCsvSet(artifact) {
    const entries = await Promise.all(
      artifact.data_sources.map(async source => [source.id, await fetchCsv(source.path)])
    );
    return Object.fromEntries(entries);
  }

  function wireFilterSection(panel, state) {
    const form = contentPanel.querySelector(".filter-section");
    if (!form) return;
    form.addEventListener("change", event => {
      const control = event.target;
      if (!(control instanceof HTMLInputElement || control instanceof HTMLSelectElement)) return;
      const filters = panel.contents.filter_section.filters;
      const nextState = { ...state };
      for (const filter of filters) {
        const input = form.elements[filter.id];
        if (!input) continue;
        nextState[filter.id] = filter.control === "checkbox" ? input.checked : input.value;
      }
      writePanelUrl(panel.page_id, filters, nextState, { replace: false });
      renderContentPanel(panel, nextState).catch(error => {
        contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
      });
    });
  }
})();