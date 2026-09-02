import { FLOAT_DP } from "./constants.js";

function formatNameList(names) {
  if (names.length <= 2) return names.join(" and ");
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

function formatFloatLabel(value) {
  return Number(value).toFixed(FLOAT_DP);
}

function formatOptionalFloat(value) {
  if (value === null || value === undefined || value === "") return "-";
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(FLOAT_DP) : String(value);
}

export {
  formatNameList,
  formatFloatLabel,
  formatOptionalFloat,
};
