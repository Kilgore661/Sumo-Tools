import { POINT_SHIKONA } from "./constants.js";

function careerComparisonRikishiOptions(data) {
  const rows = Object.entries(data.points_by_rikishi || {}).map(([id, points]) => {
    const lastPoint = points[points.length - 1] || [];
    return { id, shikona: String(lastPoint[POINT_SHIKONA] || id) };
  });
  return rows
    .map(row => {
      const label = row.shikona;
      return {
        ...row,
        label,
        prefixes: [label, row.shikona, row.id].map(value => String(value).toLowerCase()),
      };
    })
    .sort((left, right) => left.label.localeCompare(right.label));
}

function displayNameForRikishi(rikishiId, data) {
  const options = careerComparisonRikishiOptions(data);
  return options.find(option => option.id === rikishiId)?.label || rikishiId;
}

export {
  careerComparisonRikishiOptions,
  displayNameForRikishi,
};
