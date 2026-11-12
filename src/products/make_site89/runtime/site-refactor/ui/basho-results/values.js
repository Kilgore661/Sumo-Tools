// Basho Results row value derivation and compact-result parsing.

// Flatten a producer row into terminal-path values for the recursive table.
function transitionalRowValues(row, index) {
  const beforeResult = parseResult(row.previous_result);
  const selectedResult = parseResult(row.score);
  return {
    "reference.row_number": String(index + 1),
    "reference.shikona": row.shikona || "",
    "reference.rikishi_id": row.rikishi_id || "",
    "reference.highest_chii": row.highest_chii || "false",
    "reference.promotion_kind": row.promotion_kind || "",
    "reference.promotion_status": row.promotion_status || "",
    "reference.promotion_required": row.promotion_required || "",
    "reference.promotion_previous_result": row.promotion_previous_result || "",
    "before.context.skill.bp": row.previous_chii || "",
    "before.context.skill.bp_ordinal": row.previous_chii_ordinal || "",
    "before.context.skill.rating": row.previous_rating || "",
    "before.result.wins": beforeResult.wins,
    "before.result.wins_losses_separator": "-",
    "before.result.losses": beforeResult.losses,
    "before.result.losses_absences_separator": Number(beforeResult.absences) > 0 ? "-" : "",
    "before.result.absences": beforeResult.absences,
    "before.result.prizes": beforeResult.prizes,
    "selected.context.skill.bp": row.chii || "",
    "selected.context.skill.bp_ordinal": row.chii_ordinal || "",
    "selected.context.skill.rating": row.rating || "",
    "selected.context.skill.rating_delta": row.rating_delta || "",
    "selected.result.wins": selectedResult.wins,
    "selected.result.wins_losses_separator": "-",
    "selected.result.losses": selectedResult.losses,
    "selected.result.losses_absences_separator": Number(selectedResult.absences) > 0 ? "-" : "",
    "selected.result.absences": selectedResult.absences,
    "selected.result.prizes": selectedResult.prizes,
  };
}

// Parse compact result text into wins, losses, absences and prize display text.
function parseResult(value) {
  const text = String(value || "").trim();
  const missing = { wins: "", losses: "", absences: "", prizes: "" };
  if (!text || text === "-") return missing;
  const match = text.match(/^(\d+)-(\d+)(?:-(\d+))?(?:\s+(.+))?$/);
  if (!match) return { ...missing, prizes: text };
  return {
    wins: match[1],
    losses: match[2],
    absences: match[3] || "",
    prizes: match[4] || "",
  };
}

function compareValues(left, right) {
  const leftNumber = Number(left);
  const rightNumber = Number(right);
  if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
    return leftNumber - rightNumber;
  }
  return String(left).localeCompare(String(right));
}

export {
  transitionalRowValues,
  parseResult,
  compareValues,
};
