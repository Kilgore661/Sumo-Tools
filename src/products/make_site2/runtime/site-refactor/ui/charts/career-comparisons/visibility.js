function rikishiTraceIndexes(host, rikishiId) {
  return (host.data || [])
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
  if (!window.Plotly) return Promise.resolve();
  const indexes = rikishiTraceIndexes(host, rikishiId);
  if (!indexes.length) return Promise.resolve();
  return Plotly.restyle(host, { visible: visible ? true : "legendonly" }, indexes);
}

function syncRikishiVisibilityControls(host, selectedList) {
  if (!host || !selectedList) return;
  for (const control of selectedList.querySelectorAll("input[data-rikishi-visible-id]")) {
    control.checked = isAnyRikishiTraceVisible(host, control.dataset.rikishiVisibleId);
  }
}

export {
  rikishiTraceIndexes,
  isTraceVisible,
  isAnyRikishiTraceVisible,
  setRikishiTraceVisibility,
  syncRikishiVisibilityControls,
};
