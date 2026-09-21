// Fastest Risers state resolution and presentation model.

const GROUP_ORDER = ["Jk", "Jd", "Sd", "Ms", "J", "M", "KS", "O", "Y"];
const GROUP_LABELS = Object.freeze({
  Jk: "Jonokuchi",
  Jd: "Jonidan",
  Sd: "Sandanme",
  Ms: "Makushita",
  J: "Juryo",
  M: "Maegashira",
  KS: "Komusubi/Sekiwake",
  O: "Ozeki",
  Y: "Yokozuna",
});
const VALID_DIRECTIONS = new Set(["fastest", "slowest"]);
const VALID_RANGES = new Set(["10", "20", "50", "all"]);

function buildFastestRisersPresentationModel(data, requestedState) {
  const routes = validRoutes(data);
  const state = resolveFastestRisersState(routes, requestedState);
  const route = routes.get(`${state.start}:${state.finish}`);
  const positionField = state.direction === "slowest"
    ? "slowest_position"
    : "fastest_position";
  const ranked = [...(route?.records || [])]
    .sort((left, right) => Number(left[positionField]) - Number(right[positionField]));
  const ranged = state.ranking_range === "all"
    ? ranked
    : ranked.slice(0, Number(state.ranking_range));
  const visible = state.hide_retired
    ? ranged.filter(record => record.active === true)
    : ranged;
  const values = visible.map(record => ({
    ...record,
    position: record[positionField],
  }));
  return {
    id: "fastest_risers",
    state,
    route,
    available_starts: availableStarts(routes),
    available_finishes: availableFinishes(routes, state.start),
    header: fastestRisersHeader(state, route, ranged.length, visible.length),
    values,
    empty_message: fastestRisersEmptyMessage(state, route, ranged, visible),
  };
}

function validRoutes(data) {
  const routes = new Map();
  for (const [key, route] of Object.entries(data?.routes || {})) {
    if (!route || !GROUP_ORDER.includes(route.start_group) || !GROUP_ORDER.includes(route.finish_group)) continue;
    if (key !== `${route.start_group}:${route.finish_group}`) continue;
    if (Number(route.starter_count) <= 0) continue;
    routes.set(key, route);
  }
  return routes;
}

function resolveFastestRisersState(routes, requestedState = {}) {
  const starts = availableStarts(routes);
  const requestedStart = String(requestedState.start || "");
  const start = starts.includes(requestedStart)
    ? requestedStart
    : starts.includes("Jk")
      ? "Jk"
      : starts[0] || "Jk";
  const finishes = availableFinishes(routes, start);
  const requestedFinish = String(requestedState.finish || "");
  const finish = finishes.includes(requestedFinish)
    ? requestedFinish
    : finishes.includes("M")
      ? "M"
      : finishes[0] || "M";
  const direction = VALID_DIRECTIONS.has(requestedState.direction)
    ? requestedState.direction
    : "fastest";
  const requestedRange = String(requestedState.ranking_range || "");
  const ranking_range = VALID_RANGES.has(requestedRange) ? requestedRange : "10";
  return {
    ...requestedState,
    start,
    finish,
    direction,
    ranking_range,
    hide_retired: requestedState.hide_retired === true,
  };
}

function availableStarts(routes) {
  const starts = new Set([...routes.values()].map(route => route.start_group));
  return GROUP_ORDER.filter(group => starts.has(group));
}

function availableFinishes(routes, start) {
  const finishes = new Set(
    [...routes.values()]
      .filter(route => route.start_group === start)
      .map(route => route.finish_group)
  );
  return GROUP_ORDER.filter(group => finishes.has(group));
}

function fastestRisersHeader(state, route, rangedCount, visibleCount) {
  const direction = state.direction === "slowest" ? "Slowest" : "Fastest";
  const start = groupLabel(state.start);
  const finish = groupLabel(state.finish);
  return {
    heading: `${direction} promotions from ${start} to ${finish}`,
    subheading: fastestRisersSubheading(state, route, rangedCount, visibleCount),
  };
}

function fastestRisersSubheading(state, route, rangedCount, visibleCount) {
  if (!route) return "No progression route is available for the selected divisions.";
  const reached = Number(route.reached_count) || 0;
  const starters = Number(route.starter_count) || 0;
  const finish = groupLabel(state.finish);
  const start = groupLabel(state.start);
  if (state.hide_retired) {
    const rangeText = state.ranking_range === "all"
      ? `all ${reached}`
      : `the first ${rangedCount} of ${reached}`;
    return `Showing ${visibleCount} active rikishi among ${rangeText} who reached ${finish}, from ${starters} ${start} starters.`;
  }
  if (state.ranking_range === "all") {
    return `Showing all ${reached} rikishi who reached ${finish}, from ${starters} ${start} starters.`;
  }
  return `Showing ${rangedCount} of ${reached} rikishi who reached ${finish}, from ${starters} ${start} starters.`;
}

function fastestRisersEmptyMessage(state, route, ranged, visible) {
  if (!route) return "No progression route is available for the selected divisions.";
  if (Number(route.reached_count) === 0) {
    return `No ${groupLabel(state.start)} starters reached ${groupLabel(state.finish)} in the represented History.`;
  }
  if (state.hide_retired && ranged.length && !visible.length) {
    return "No active rikishi appear within the selected ranking range.";
  }
  return "No rikishi match the selected options.";
}

function groupLabel(group) {
  return GROUP_LABELS[group] || group || "";
}

export {
  GROUP_LABELS,
  GROUP_ORDER,
  availableFinishes,
  availableStarts,
  buildFastestRisersPresentationModel,
  fastestRisersEmptyMessage,
  fastestRisersHeader,
  fastestRisersSubheading,
  groupLabel,
  resolveFastestRisersState,
  validRoutes,
};
