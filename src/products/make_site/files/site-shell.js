const frame = document.getElementById("content-frame");
const framePanel = document.getElementById("frame-panel");
const welcomePanel = document.getElementById("welcome-panel");
const navLinks = [...document.querySelectorAll(".nav-link")];
const linkByPageId = new Map(navLinks.map(link => [link.dataset.pageId, link]));

ensureVisibleCacheBust();
loadStateFromUrl({ replaceUrl: true });

for (const link of navLinks) {
  link.addEventListener("click", event => {
    event.preventDefault();
    selectPage(link, {}, { pushUrl: true });
  });
}

window.addEventListener("popstate", () => {
  loadStateFromUrl({ replaceUrl: false });
});

window.addEventListener("message", event => {
  const message = event.data;
  if (!message || message.type !== "site:url-state") return;
  if (event.source !== frame.contentWindow) return;
  const activeLink = activeNavLink();
  if (!activeLink || activeLink.dataset.pageId !== message.page) return;
  writeShellUrl(message.page, message.params || {}, { replace: true });
});

function ensureVisibleCacheBust() {
  if (!window.SiteUrl) return;
  const config = SiteUrl.siteUrlConfig();
  if (config.cacheMode !== "dev" || !config.cacheBust) return;
  const next = SiteUrl.withDisplayParams(window.location.href, {
    [config.cacheBustParam]: config.cacheBust
  });
  if (`${window.location.pathname}${window.location.search}${window.location.hash}` !== next) {
    history.replaceState(null, "", next);
  }
}

function loadStateFromUrl({ replaceUrl }) {
  if (!window.SiteUrl) return;
  const state = SiteUrl.readShellState();
  if (!state.page) return;
  const link = linkByPageId.get(state.page);
  if (!link) {
    alert(`Unknown site page: ${state.page}`);
    showWelcome();
    return;
  }
  selectPage(link, state.params, { replaceUrl });
}

function selectPage(link, params = {}, { pushUrl = false, replaceUrl = false } = {}) {
  for (const navLink of navLinks) {
    navLink.classList.toggle("is-active", navLink === link);
  }
  frame.src = frameSrcForLink(link, params);
  welcomePanel.hidden = true;
  framePanel.hidden = false;
  if (pushUrl || replaceUrl) {
    writeShellUrl(link.dataset.pageId, params, { replace: replaceUrl });
  }
}

function frameSrcForLink(link, params) {
  if (!window.SiteUrl) return link.dataset.frameSrc;
  if (link.dataset.acceptsShellParams !== "true") return link.dataset.frameSrc;
  const shellParams = { ...params };
  if (link.dataset.shellParamMode === "pa-runtime" || link.dataset.shellParamMode === "adapter-cache") {
    Object.assign(shellParams, SiteUrl.cacheBustParams());
  }
  return SiteUrl.withDisplayParams(link.dataset.frameSrc, shellParams);
}

function writeShellUrl(pageId, params, { replace }) {
  if (!window.SiteUrl) return;
  const config = SiteUrl.siteUrlConfig();
  const search = SiteUrl.buildShellSearch(pageId, params, config);
  const next = `${window.location.pathname}${search ? `?${search}` : ""}${window.location.hash}`;
  const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (next === current) return;
  if (replace) {
    history.replaceState(null, "", next);
  } else {
    history.pushState(null, "", next);
  }
}

function activeNavLink() {
  return navLinks.find(link => link.classList.contains("is-active"));
}

function showWelcome() {
  for (const navLink of navLinks) {
    navLink.classList.remove("is-active");
  }
  frame.removeAttribute("src");
  welcomePanel.hidden = false;
  framePanel.hidden = true;
}
