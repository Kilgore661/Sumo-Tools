function modeLabel(skill, xBase) {
  const skillText = skillLabel(skill);
  const xLabel = xBase === "basho" ? "Hatsu" : "Date";
  return `${skillText} / ${xLabel}`;
}

function skillLabel(skill) {
  if (skill === "both") return "Both";
  return skill === "rating" ? "Elo-89" : "Chii";
}

function skillHelp(skill) {
  if (skill === "both") return "Show chii and rating together.";
  if (skill === "rating") return "Show rating achieved.";
  return "Show chii achieved.";
}

export { modeLabel, skillLabel, skillHelp };
