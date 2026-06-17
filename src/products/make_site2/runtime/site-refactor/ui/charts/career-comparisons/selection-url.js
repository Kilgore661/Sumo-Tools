import { careerComparisonsState } from "./state.js";

function readCareerComparisonSelectionFromUrl(data) {
  const params = new URLSearchParams(window.location.search);
  const ids = String(params.get("rikishi") || "")
    .split(",")
    .map(value => value.trim())
    .filter(Boolean);
  const knownIds = new Set(Object.keys(data.points_by_rikishi || {}));
  careerComparisonsState.selectedRikishiIds = ids.filter(id => knownIds.has(id));
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
};
