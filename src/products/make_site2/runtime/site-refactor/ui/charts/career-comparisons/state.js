import { DEFAULT_STATE } from "./constants.js";

let careerComparisonsState = { ...DEFAULT_STATE };
let careerComparisonSession = createCareerComparisonSession();

function createCareerComparisonSession() {
  return {
    traceColoursByRikishiId: new Map(),
    nextTraceColourIndex: 0,
  };
}

function resetCareerComparisonsState() {
  careerComparisonsState = { ...DEFAULT_STATE };
  careerComparisonSession = createCareerComparisonSession();
}

export {
  careerComparisonsState,
  careerComparisonSession,
  createCareerComparisonSession,
  resetCareerComparisonsState,
};
