# Session Handover - Chart Axis Review

## Scope

This handoff records the completed `make_site2` chart-axis rendering review on
branch `dev`. It is a closeout note for the chart-axis work, separate from the
older Rendering Review handover.

The work focused on Plotly chart presentation in the generic chart runtime:

- bold axis titles;
- x-axis tick-label angle;
- x-axis tick-label density;
- behavior differences between stacked bar, ordered bar and grouped line charts.

## Closeout state

The reviewed simple-chart axis work is complete.

- `BANZUKE_DIVISION_BY_ERA_ARTIFACT` uses `"x_tickangle": "auto"`.
- `MAKUUCHI_RANK_BY_ERA_ARTIFACT` uses `"x_tickangle": "auto"`.
- `FIRST_CHII_APPEARANCE_ARTIFACT` uses the ordered-bar runtime path that lets
  Plotly own x tick-label angle and density.
- `DIVISION_STABILITY_ARTIFACT` uses `"x_tickangle": "auto"` with `"nticks": 20`.
- The grouped-line runtime passes artifact-level `nticks` through to Plotly.

The remaining chart-maker, 3.3 Rikishi History, is outside this closeout. It has
a separate follow-up issue.

## Files most relevant to the completed work

```text
src/products/make_site2/manifest/artifacts/
src/products/make_site2/runtime/site-refactor/ui/charts/generic-layouts.js
src/products/make_site2/runtime/site-refactor/ui/charts/generic-renderers.js
src/products/make_site2/runtime/site-refactor/ui/charts/shared.js
src/products/make_site2/docs/05 Rendering Design 3.md
docs/LLM Guide.md
```

## Generic chart runtime split

The old generic chart module was split into smaller files:

- `generic.js` is now a facade.
- `generic-traces.js` owns generic trace helpers.
- `generic-layouts.js` owns Plotly layout builders.
- `generic-renderers.js` owns generic renderer entry points.

For chart-axis behavior, `generic-layouts.js` is usually the smallest owner file.
Prefer editing that file when the behavior is runtime layout behavior.

## Plotly behavior established during discussion

- `tickangle: "auto"` lets Plotly choose tick-label angle during Plotly layout
  calculation.
- Plotly's auto angle candidates are effectively horizontal, 30 degrees and
  vertical; it may jump straight to vertical when labels are dense.
- Plotly label angle is recalculated when Plotly redraws or resizes. Browser
  window resize works when responsive Plotly behavior is active. Internal layout
  changes may need explicit Plotly resize or redraw.
- If the runtime supplies `tickvals` and `ticktext`, label density is explicit;
  Plotly is not choosing tick labels automatically.
- To let Plotly own label density, use `tickmode: "auto"` plus an `nticks` hint,
  and omit `tickvals` / `ticktext`.
- `nticks` is a maximum/hint, not a guaranteed exact number.

## Chart-specific findings

### Average Banzuke Composition by Era

Artifact: `BANZUKE_DIVISION_BY_ERA_ARTIFACT`
Renderer: `stacked_bar_chart`

Current state:

```python
"x_tickangle": "auto"
```

User verified this as acceptable: labels are horizontal with enough room and
rotate when the window narrows.

### Makuuchi Rank Appearances by Era

Artifact: `MAKUUCHI_RANK_BY_ERA_ARTIFACT`
Renderer: `stacked_bar_chart`

Current state:

```python
"x_tickangle": "auto"
```

Plotly may jump from horizontal to vertical because the rank labels are dense.
This was accepted as good enough for now.

### First Chii Appearance

Artifact: `FIRST_CHII_APPEARANCE_ARTIFACT`
Renderer: `ordered_bar_chart`

This chart has many possible x labels. The accepted fix was not just changing
artifact provenance. The runtime now has a special case in `orderedBarLayout`:

```js
const useAutoXTicks = artifact.id === "first_chii_appearance";
...
tickangle: useAutoXTicks ? "auto" : artifact.provenance.x_tickangle || 0,
...
if (useAutoXTicks) {
  xaxis.tickmode = "auto";
  xaxis.nticks = 20;
} else {
  xaxis.tickvals = trace.x;
  xaxis.ticktext = sparseTickText(...);
}
```

Effect:

- Plotly owns x tick-label angle.
- Plotly owns x tick-label density.
- Other ordered-bar charts continue using the existing explicit sparse label
  behavior.

### Division Persistence

Artifact: `DIVISION_STABILITY_ARTIFACT`
Renderer: `grouped_line_chart`

Current accepted state:

```python
"x_tickangle": "auto",
"nticks": 20
```

The grouped-line runtime now passes `artifact.provenance.nticks` to Plotly's
x-axis layout. The artifact declares the density hint; the runtime owns the
Plotly mechanics. This lets Plotly choose the displayed tick labels and label
angle rather than hard-coding sparse tick text for this chart.

## Process cautions for future work

Follow `docs/LLM Guide.md`, especially the `LLM Edit Discipline` section.

Practical lessons from this pass:

- Identify the actual owner file before changing anything.
- Prefer the smallest owner file.
- Do not create placeholder, policy, wrapper or probe files for a simple edit.
- Avoid full-file rewrites of large files; the GitHub connector has no patch
  operation and full replacements can cause accidental unrelated edits.
- If a full-file replacement is unavoidable, verify the net diff before saying
  the change is done.
- Do not treat source inspection as browser verification. The user validates the
  rendered result after rebuilding.

## Closeout

No further action remains in this handover for the simple-chart axis pass.

Do not use this handover as the next-step source for 4.5 Division Persistence;
that work is complete. The remaining chart follow-up is 3.3 Rikishi History.