import { careerComparisonsState } from "./state.js";

function readCareerComparisonSelectionFromUrl(data) {
  const params = new URLSearchParams(window.location.search);
  const ids = String(params.get("rikishi") || "")
    .split(",")
    .map(value => value.trim())
    .filter(Boolean);
  const knownIds = new Set(Object.keys(data.points_by_rikishi || {}));
  const availableIds = ids.filter(id => knownIds.has(id));
  const unavailableIds = ids.filter(id => !knownIds.has(id));
  careerComparisonsState.selectedRikishiIds = availableIds;
  if (unavailableIds.length) {
    alertUnavailableRikishi(unavailableIds);
    writeCareerComparisonSelectionToUrl();
  }
}

function alertUnavailableRikishi(rikishiIds) {
  const label = rikishiIds.length === 1 ? "Rikishi" : "Rikishi";
  const verb = rikishiIds.length === 1 ? "is" : "are";
  window.alert(`${label} ${rikishiIds.join(", ")} ${verb} not available in Rikishi History data.`);
}

function writeCareerComparisonSelectionToUrl() {
  const url = new URL(window.location.href);
  if (careerComparisonsState.selectedRikishiIds.length) {
    url.searchParams.set("rikishi", careerComparisonsState.selectedRikishiIds.join(","));
  } else {
    url.searchParams.delete("rikishi");
  }
  history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
}

export {
  readCareerComparisonSelectionFromUrl,
  writeCareerComparisonSelectionToUrl,
  alertUnavailableRikishi,
};
