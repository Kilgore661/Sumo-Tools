import { dateLikeDisplay } from "../../../utils/display.js";
import { POINT_DATE } from "./constants.js";
import { careerComparisonsState } from "./state.js";
import { displayNameForRikishi } from "./options.js";
import { formatNameList } from "./format.js";

function careerComparisonCaption(artifact, data) {
  const selectedIds = careerComparisonsState.selectedRikishiIds;
  if (!selectedIds.length) return { heading: artifact.heading, subheading: "" };
  const names = selectedIds.map(id => displayNameForRikishi(id, data));
  const dates = selectedIds
    .flatMap(id => data.points_by_rikishi[id] || [])
    .map(point => String(point[POINT_DATE] || ""))
    .filter(Boolean)
    .sort();
  return {
    heading: `Career History for ${formatNameList(names)}`,
    subheading: dates.length ? `(${dateLikeDisplay(dates[0])} to ${dateLikeDisplay(dates[dates.length - 1])})` : "",
  };
}

export { careerComparisonCaption };
