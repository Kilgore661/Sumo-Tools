import { renderIndexedTableContentPanel, renderBanzukeChangesContentPanel, renderSectionedTableContentPanel } from './tables.js';
import { renderStandingsContentPanel } from './standings.js';
import { renderChartContentPanel } from './charts.js';

/**
 * Registry mapping table routing configurations into modular pipeline hooks.
 */

const REGIN_MAP = {
  indexed_table: renderIndexedTableContentPanel,
  sectioned_table: renderSectionedTableContentPanel,
  banzuke_changes: renderBanzukeChangesContentPanel,
  standings: renderStandingsContentPanel,
  chart: renderChartContentPanel
};

export async function delegateContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet) {
  const rendererHook = REGIN_MAP[artifact.kind];
  if (!rendererHook) {
    throw new Error(`Unsupported artifact kind: ${artifact.kind}`);
  }
  await rendererHook(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet);
}