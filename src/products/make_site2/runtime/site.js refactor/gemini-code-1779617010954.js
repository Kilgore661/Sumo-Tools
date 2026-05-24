/**
 * Generic helper utilities handling basic DOM string manipulations.
 */

export function escapeHtml(string) {
  return String(string || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function divisionId(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, "_");
}

export function normalizedSourceValue(value, normalizer) {
  if (normalizer === "division_id") return divisionId(value);
  return value;
}

export function compareValues(left, right) {
  if (left < right) return -1;
  if (left > right) return 1;
  return 0;
}