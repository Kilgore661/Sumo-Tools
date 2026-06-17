import { CHII_LEVELS, POINT_CHII } from "./constants.js";

function buildChiiScale(artifact, state, data) {
  const humansByKey = new Map();
  for (const points of Object.values(data.points_by_rikishi || {})) {
    for (const point of points) {
      const parsed = parseChii(point[POINT_CHII]);
      if (!parsed) continue;
      const human = humanChii(point[POINT_CHII]);
      const existing = humansByKey.get(human);
      if (!existing || parsed.sortKey < existing.sortKey) {
        humansByKey.set(human, { human, sortKey: humanChiiSortKey(human) });
      }
    }
  }
  const labels = [...humansByKey.values()]
    .sort((left, right) => left.sortKey - right.sortKey)
    .map(item => item.human);
  if (!state.log) return linearChiiScale(labels);
  return compressedChiiScale(labels, Number(artifact.provenance.top_chart_prop));
}

function linearChiiScale(labels) {
  const valuesByHuman = new Map();
  labels.forEach((label, index) => {
    valuesByHuman.set(label, labels.length - index);
  });
  const ticks = sparseChiiTicks(labels, 48);
  return {
    valuesByHuman,
    kind: "linear",
    tickValues: ticks.map(label => valuesByHuman.get(label)),
    tickLabels: ticks,
  };
}

function compressedChiiScale(labels, topProp) {
  const topLabels = labels.filter(label => isSekitoriHumanChii(label));
  const bottomLabels = labels.filter(label => !isSekitoriHumanChii(label));
  const valuesByHuman = new Map();
  const boundary = 1 - topProp;
  topLabels.forEach((label, index) => {
    valuesByHuman.set(label, interpolate(1, boundary, index, topLabels.length));
  });
  bottomLabels.forEach((label, index) => {
    valuesByHuman.set(label, interpolate(boundary, 0, index, bottomLabels.length));
  });
  const ticks = spacedChiiTicks(labels, valuesByHuman, 0.026);
  return {
    valuesByHuman,
    kind: "compressed",
    tickValues: ticks.map(label => valuesByHuman.get(label)),
    tickLabels: ticks,
  };
}

function interpolate(start, end, index, count) {
  if (count <= 1) return start;
  return start + ((end - start) * index / (count - 1));
}

function sparseChiiTicks(labels, maxLabels) {
  const step = Math.max(1, Math.ceil(labels.length / maxLabels));
  return labels.filter((_, index) => index % step === 0);
}

function spacedChiiTicks(labels, valuesByHuman, minimumGap) {
  const ticks = [];
  let previousValue = Number.POSITIVE_INFINITY;
  for (const label of labels) {
    const value = valuesByHuman.get(label);
    if (value === undefined) continue;
    if (previousValue - value >= minimumGap || ticks.length === 0) {
      ticks.push(label);
      previousValue = value;
    }
  }
  const finalLabel = labels[labels.length - 1];
  if (finalLabel && !ticks.includes(finalLabel)) {
    const finalValue = valuesByHuman.get(finalLabel);
    const previousFinalValue = valuesByHuman.get(ticks[ticks.length - 1]);
    if (
      finalValue !== undefined &&
      previousFinalValue !== undefined &&
      previousFinalValue - finalValue >= minimumGap
    ) {
      ticks.push(finalLabel);
    }
  }
  return ticks;
}

function isSekitoriHumanChii(label) {
  const parsed = parseChii(label);
  return parsed ? parsed.levelIndex <= CHII_LEVELS.indexOf("J") : false;
}

function humanChii(chii) {
  const parsed = parseChii(chii);
  if (!parsed) return String(chii);
  if (["Y", "O", "S", "K"].includes(parsed.level)) return parsed.level;
  return `${parsed.level}${parsed.number}`;
}

function humanChiiSortKey(human) {
  const parsed = parseChii(human);
  if (!parsed) {
    const levelIndex = CHII_LEVELS.indexOf(human);
    return levelIndex < 0 ? Number.MAX_SAFE_INTEGER : levelIndex * 1000;
  }
  return parsed.levelIndex * 1000 + parsed.number;
}

function parseChii(chii) {
  const match = String(chii || "").match(/^(Ms|Sd|Jd|Jk|Y|O|S|K|M|J)(\d*)/);
  if (!match) return null;
  const level = match[1];
  const levelIndex = CHII_LEVELS.indexOf(level);
  const number = match[2] ? Number(match[2]) : 1;
  return {
    level,
    levelIndex,
    number,
    sortKey: levelIndex * 1000 + number,
  };
}

export {
  buildChiiScale,
  linearChiiScale,
  compressedChiiScale,
  interpolate,
  sparseChiiTicks,
  spacedChiiTicks,
  isSekitoriHumanChii,
  humanChii,
  humanChiiSortKey,
  parseChii,
};
