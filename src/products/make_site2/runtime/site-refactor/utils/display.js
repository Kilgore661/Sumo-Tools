// Public display formatting helpers.

function dateLikeDisplay(value) {
  const text = String(value ?? "");
  return text.replace(/^(\d{4})\/(\d{1,2})(?:\/(\d{1,2}))?$/, (_, year, month, day) => {
    const monthText = month.padStart(2, "0");
    if (!day) return `${year}-${monthText}`;
    return `${year}-${monthText}-${day.padStart(2, "0")}`;
  });
}

function dateLikeDisplayFromParts(year, month, day = null) {
  return dateLikeDisplay([year, month, day].filter(value => value !== null && value !== undefined && value !== "").join("/"));
}

export { dateLikeDisplay, dateLikeDisplayFromParts };
