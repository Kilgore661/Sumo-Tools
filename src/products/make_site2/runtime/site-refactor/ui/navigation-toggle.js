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

export { bootNavigationToggle, applyNavigationCollapsedState };
