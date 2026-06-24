// NavigationBar collapse/expand behaviour.

function bootNavigationToggle() {
  const shell = document.querySelector("[data-nav-shell]");
  const panel = document.querySelector("[data-nav-panel]");
  const content = document.querySelector("[data-nav-content]");
  const toggle = document.querySelector("[data-nav-toggle]");
  if (!shell || !panel || !content || !toggle) return;

  const storageKey = toggle.dataset.storageKey || "gaspodeSumoLab.makeSite2.navCollapsed";
  const initialCollapsed = window.localStorage.getItem(storageKey) === "true";
  applyNavigationCollapsedState(shell, panel, content, toggle, initialCollapsed);

  toggle.addEventListener("click", () => {
    const collapsed = !shell.classList.contains("nav-collapsed");
    applyNavigationCollapsedState(shell, panel, content, toggle, collapsed);
    window.localStorage.setItem(storageKey, String(collapsed));
    resizePlotlyCharts();
  });

  bootNavigationTreeToggles(content);
}

function bootNavigationTreeToggles(root) {
  root.querySelectorAll("[data-nav-tree-panel]").forEach(panel => {
    const toggle = panel.querySelector("[data-nav-tree-toggle]");
    const body = panel.querySelector("[data-nav-tree-body]");
    if (!toggle || !body) return;
    const initiallyCollapsed = toggle.getAttribute("aria-expanded") === "false";
    applyNavigationTreeCollapsedState(panel, body, toggle, initiallyCollapsed);
    toggle.addEventListener("click", () => {
      const collapsed = !body.hidden;
      applyNavigationTreeCollapsedState(panel, body, toggle, collapsed);
      resizePlotlyCharts();
    });
  });
}

function applyNavigationTreeCollapsedState(panel, body, toggle, collapsed) {
  const heading = panel.querySelector(".nav-tree-heading span")?.textContent || "navigation section";
  panel.classList.toggle("nav-tree-panel-collapsed", collapsed);
  body.hidden = collapsed;
  toggle.textContent = collapsed ? "˅" : "˄";
  toggle.setAttribute("aria-label", collapsed ? `Show ${heading}` : `Hide ${heading}`);
  toggle.title = collapsed ? `Show ${heading}` : `Hide ${heading}`;
  toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
}

// Apply the collapsed state to shell classes, ARIA state and Plotly sizing.
function applyNavigationCollapsedState(shell, panel, content, toggle, collapsed) {
  shell.classList.toggle("nav-collapsed", collapsed);
  panel.classList.toggle("site-nav-collapsed", collapsed);
  content.hidden = collapsed;
  content.setAttribute("aria-hidden", String(collapsed));
  toggle.setAttribute("aria-expanded", String(!collapsed));
  toggle.setAttribute("aria-label", collapsed ? "Show navigation" : "Hide navigation");
  toggle.title = collapsed ? "Show navigation" : "Hide navigation";
  toggle.textContent = collapsed ? ">" : "<";
}

function resizePlotlyCharts() {
  window.requestAnimationFrame(() => {
    if (!window.Plotly?.Plots?.resize) return;
    document.querySelectorAll(".plotly-chart").forEach(chart => {
      window.Plotly.Plots.resize(chart);
    });
  });
}

export {
  bootNavigationToggle,
  applyNavigationCollapsedState,
  applyNavigationTreeCollapsedState,
  resizePlotlyCharts,
};
