// Development-only structural layout debug mode.

const DEBUG_LAYOUT_PARAM = "debug_layout";
const PAGE_PARAM = "page";

function bootLayoutDebug() {
  const params = new URLSearchParams(window.location.search);
  const enabled = isTruthyDebugValue(
    params.get(DEBUG_LAYOUT_PARAM) ?? embeddedDebugLayoutValue(params)
  );
  document.body.classList.toggle("layout-debug", enabled);
}

function isTruthyDebugValue(value) {
  return ["1", "true", "yes", "on"].includes(String(value || "").toLowerCase());
}

function embeddedDebugLayoutValue(params) {
  const page = params.get(PAGE_PARAM) || "";
  const queryStart = page.indexOf("?");
  if (queryStart < 0) return null;
  return new URLSearchParams(page.slice(queryStart + 1)).get(DEBUG_LAYOUT_PARAM);
}

export { DEBUG_LAYOUT_PARAM, bootLayoutDebug, isTruthyDebugValue, embeddedDebugLayoutValue };
