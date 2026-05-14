const NAV_TOGGLE_STORAGE_KEY = "gaspodeSumoLab.navCollapsed";

function bootNavToggle() {
  const shell = document.querySelector("[data-nav-shell]");
  const panel = document.querySelector("[data-nav-panel]");
  const toggle = document.querySelector("[data-nav-toggle]");
  if (!shell || !panel || !toggle) return;

  const storedValue = window.localStorage.getItem(NAV_TOGGLE_STORAGE_KEY);
  const initialCollapsed = storedValue === "true";

  applyNavCollapsedState(shell, panel, toggle, initialCollapsed);

  toggle.addEventListener("click", () => {
    const nextCollapsed = !shell.classList.contains("nav-collapsed");
    applyNavCollapsedState(shell, panel, toggle, nextCollapsed);
    window.localStorage.setItem(NAV_TOGGLE_STORAGE_KEY, String(nextCollapsed));
  });
}

function applyNavCollapsedState(shell, panel, toggle, collapsed) {
  shell.classList.toggle("nav-collapsed", collapsed);
  panel.hidden = collapsed;
  panel.setAttribute("aria-hidden", String(collapsed));
  toggle.setAttribute("aria-expanded", String(!collapsed));
  toggle.setAttribute("aria-label", collapsed ? "Show navigation" : "Hide navigation");
  toggle.title = collapsed ? "Show navigation" : "Hide navigation";
  toggle.textContent = collapsed ? ">" : "<";
}

bootNavToggle();
