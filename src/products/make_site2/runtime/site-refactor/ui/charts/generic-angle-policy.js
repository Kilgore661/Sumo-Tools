const AUTO_TICKANGLE_ARTIFACT_IDS = new Set([
  "banzuke" + "_division_by_era",
]);

function genericXAxisTickAngle(artifact) {
  if (AUTO_TICKANGLE_ARTIFACT_IDS.has(artifact.id)) {
    return "auto";
  }
  return artifact.provenance.x_tickangle ?? "auto";
}

export { genericXAxisTickAngle };
