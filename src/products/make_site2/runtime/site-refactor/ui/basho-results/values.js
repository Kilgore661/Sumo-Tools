// Basho Results row value derivation and compact-result parsing.

// Derive before/selected rating-order analysis for all displayed rows.
function buildRecordAnalyses(rows) {
  return {
    before: buildRecordAnalysis(rows, {
      bpField: "previous_chii",
      bpOrdinalField: "previous_chii_ordinal",
      ratingField: "previous_equelo",
    }),
    selected: buildRecordAnalysis(rows, {
      bpField: "chii",
      bpOrdinalField: "chii_ordinal",
      ratingField: "equelo",
    }),
  };
}

// Compare banzuke order with rating order for one record context.
function buildRecordAnalysis(rows, fields) {
  const candidates = rows.map((row, index) => {
    const bpOrdinal = numericValue(row[fields.bpOrdinalField]);
    const rating = numericValue(row[fields.ratingField]);
    if (bpOrdinal === null || rating === null) return null;
    return {
      index,
      bp: row[fields.bpField] || "",
      bpOrdinal,
      rating,
    };
  }).filter(Boolean);

  const byBanzuke = [...candidates].sort((left, right) =>
    compareValues(left.bpOrdinal, right.bpOrdinal) || compareValues(left.rating, right.rating)
  );
  const byRating = [...candidates].sort((left, right) =>
    compareValues(right.rating, left.rating) || compareValues(left.bpOrdinal, right.bpOrdinal)
  );
  const banzukePositions = new Map();
  const ratingPositions = new Map();
  byBanzuke.forEach((item, index) => banzukePositions.set(item.index, index + 1));
  byRating.forEach((item, index) => ratingPositions.set(item.index, index + 1));

  const values = rows.map(() => emptyRecordAnalysis());
  for (const item of candidates) {
    const banzukePosition = banzukePositions.get(item.index);
    const ratingPosition = ratingPositions.get(item.index);
    const rbbpSlot = byBanzuke[ratingPosition - 1];
    if (!banzukePosition || !ratingPosition || !rbbpSlot) continue;
    const signedDelta = banzukePosition - ratingPosition;
    values[item.index] = {
      direction: signedDelta > 0 ? "\u2191" : signedDelta < 0 ? "\u2193" : "",
      magnitude: signedDelta === 0 ? "" : String(Math.abs(signedDelta)),
      rbbp: rbbpSlot.bp,
      rbbpOrdinal: String(rbbpSlot.bpOrdinal),
    };
  }
  return values;
}

function emptyRecordAnalysis() {
  return {
    direction: "",
    magnitude: "",
    rbbp: "",
    rbbpOrdinal: "",
  };
}

function numericValue(value) {
  const number = Number(value);
  return Number.isNaN(number) ? null : number;
}

// Flatten a producer row into terminal-path values for the recursive table.
function transitionalRowValues(row, index, analyses) {
  const beforeResult = parseResult(row.previous_result);
  const selectedResult = parseResult(row.score);
  const beforeAnalysis = analyses.before[index] || emptyRecordAnalysis();
  const selectedAnalysis = analyses.selected[index] || emptyRecordAnalysis();
  return {
    "reference.row_number": String(index + 1),
    "reference.shikona": row.shikona || "",
    "reference.rikishi_id": row.rikishi_id || "",
    "before.context.skill.bp": row.previous_chii || "",
    "before.context.skill.bp_ordinal": row.previous_chii_ordinal || "",
    "before.context.skill.equelo": row.previous_equelo || "",
    "before.context.analysis.banzuke_error.direction": beforeAnalysis.direction,
    "before.context.analysis.banzuke_error.magnitude": beforeAnalysis.magnitude,
    "before.context.analysis.rbbp": beforeAnalysis.rbbp,
    "before.context.analysis.rbbp_ordinal": beforeAnalysis.rbbpOrdinal,
    "before.result.wins": beforeResult.wins,
    "before.result.losses": beforeResult.losses,
    "before.result.absences": beforeResult.absences,
    "before.result.prizes": beforeResult.prizes,
    "selected.context.skill.bp": row.chii || "",
    "selected.context.skill.bp_ordinal": row.chii_ordinal || "",
    "selected.context.skill.equelo": row.equelo || "",
    "selected.context.analysis.banzuke_error.direction": selectedAnalysis.direction,
    "selected.context.analysis.banzuke_error.magnitude": selectedAnalysis.magnitude,
    "selected.context.analysis.rbbp": selectedAnalysis.rbbp,
    "selected.context.analysis.rbbp_ordinal": selectedAnalysis.rbbpOrdinal,
    "selected.result.wins": selectedResult.wins,
    "selected.result.losses": selectedResult.losses,
    "selected.result.absences": selectedResult.absences,
    "selected.result.prizes": selectedResult.prizes,
    "selected.next_bp": row.nu_chii || "",
    "selected.next_bp_ordinal": row.nu_chii_ordinal || "",
    "changes.movement.bp": bpMovementBetween(row.chii_ordinal, row.nu_chii_ordinal),
    "changes.movement.division": rankLevelMovementBetween(row.chii, row.nu_chii),
    "changes.delta_equelo": row.delta_equelo || "",
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

function rankLevelMovementMarker(value) {
  if (value === "\u2191" || value === "\u2193") return value;
  if (value === "Ã¢â€ â€˜") return "\u2191";
  if (value === "Ã¢â€ â€œ") return "\u2193";
  return "";
}

function bpMovementBetween(fromOrdinal, toOrdinal) {
  const from = Number(fromOrdinal);
  const to = Number(toOrdinal);
  if (Number.isNaN(from) || Number.isNaN(to) || from === to) return "";
  return to < from ? "\u2191" : "\u2193";
}

function rankLevelMovementBetween(fromBp, toBp) {
  const fromIndex = rankLevelIndex(fromBp);
  const toIndex = rankLevelIndex(toBp);
  if (fromIndex === null || toIndex === null || fromIndex === toIndex) return "";
  return toIndex < fromIndex ? "\u2191" : "\u2193";
}

function rankLevelIndex(bp) {
  const text = String(bp || "");
  if (!text || text === "-") return null;
  const match = text.match(/^(Y|O|S|K|Ms|Sd|Jd|Jk|M|J)/);
  if (!match) return null;
  return { Y: 0, O: 1, S: 2, K: 3, M: 4, J: 5, Ms: 6, Sd: 7, Jd: 8, Jk: 9 }[match[1]] ?? null;
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
  buildRecordAnalyses,
  buildRecordAnalysis,
  emptyRecordAnalysis,
  numericValue,
  transitionalRowValues,
  parseResult,
  rankLevelMovementMarker,
  bpMovementBetween,
  rankLevelMovementBetween,
  rankLevelIndex,
  compareValues,
};
