import { careerComparisonsState } from "./state.js";

function rikishiTraceIndexes(host, rikishiId) {
  return (host?.data || [])
    .map((trace, index) => trace.meta?.rikishiId === rikishiId ? index : null)
    .filter(index => index !== null);
}

function isTraceVisible(trace) {
  return trace.visible !== false && trace.visible !== "legendonly";
}

function isAnyRikishiTraceVisible(host, rikishiId) {
  const indexes = rikishiTraceIndexes(host, rikishiId);
  return indexes.some(index => isTraceVisible(host.data[index]));
}

function setRikishiTraceVisibility(host, rikishiId, visible) {
  setStoredRikishiVisibility(rikishiId, visible);
  if (!window.Plotly || !host) return Promise.resolve();
  const indexes = rikishiTraceIndexes(host, rikishiId);
  if (!indexes.length) return Promise.resolve();
  return Plotly.restyle(host, { visible: visible ? true : "legendonly" }, indexes);
}

function setStoredRikishiVisibility(rikishiId, visible) {
  const hiddenIds = new Set(careerComparisonsState.hiddenRikishiIds || []);
  if (visible) {
    hiddenIds.delete(rikishiId);
  } else {
    hiddenIds.add(rikishiId);
  }
  careerComparisonsState.hiddenRikishiIds = [...hiddenIds];
}

function removeStoredRikishiVisibility(rikishiId) {
  careerComparisonsState.hiddenRikishiIds = (careerComparisonsState.hiddenRikishiIds || [])
    .filter(id => id !== rikishiId);
}

function syncRikishiVisibilityControls(host, selectedList) {
  if (!host || !selectedList) return;
  for (const control of selectedList.querySelectorAll("input[data-rikishi-visible-id]")) {
    const visible = isAnyRikishiTraceVisible(host, control.dataset.rikishiVisibleId);
    control.checked = visible;
    setStoredRikishiVisibility(control.dataset.rikishiVisibleId, visible);
  }
}

export {
  rikishiTraceIndexes,
  isTraceVisible,
  isAnyRikishiTraceVisible,
  setRikishiTraceVisibility,
  setStoredRikishiVisibility,
  removeStoredRikishiVisibility,
  syncRikishiVisibilityControls,
};
