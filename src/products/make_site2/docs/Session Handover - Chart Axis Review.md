# Session Handover - Chart Axis Review

## Scope

This handoff covers the recent `make_site2` chart-axis rendering review on branch
`dev`. It is a standalone handoff for the chart work, separate from the older
Rendering Review handover.

The work focused on Plotly chart presentation in the generic chart runtime:

- bold axis titles
- x-axis tick-label angle
- x-axis tick-label density
- behavior differences between stacked bar, ordered bar and grouped line charts

## Current branch state

The latest confirmed state for this chart pass is:

- `BANZUKE_DIVISION_BY_ERA_ARTIFACT` uses `"x_tickangle": "auto"`.
- `MAKUUCHI_RANK_BY_ERA_ARTIFACT` uses `"x_tickangle": "auto"`.
- `FIRST_CHII_APPEARANCE_ARTIFACT` has a runtime special case in
  `generic-layouts.js` that lets Plotly own both x tick-label angle and label
  density.
- `DIVISION_STABILITY_ARTIFACT` was briefly changed to `"x_tickangle": "auto"`
  but was then restored. Current state is `"x_tickangle": -45`.

The user has not yet evaluated a rebuilt Division Persistence chart after a
new fix. Do not assume the reverted trial was accepted.

## Files most relevant to continue

```text
src/products/make_site2/manifest/artifacts.py
src/products/make_site2/runtime/site-refactor/ui/charts/generic.js
src/products/make_site2/runtime/site-refactor/ui/charts/generic-traces.js
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

Current state after undo:

```python
"x_tickangle": -45
```

A one-line trial changed it to `"auto"`, but the user asked to undo before a
rebuild/evaluation. Current branch has the original fixed angle restored.

Important distinction: Division Persistence is a grouped-line chart. It does not
use the ordered-bar `sparseTickText(...)` path that caused the First Chii density
issue. Do not blindly apply the First Chii special case here.

## Important commits

```text
e45adf47016538ae05e364ce242fe89be527b0bc docs: record bold axis title rendering policy
b339c56f3d0fa80c51d47c6b72c1b53427e32e36 docs: update rendering review chart status
6c070ad0eccf91ede9071b84d1d341443c7db650 docs: clean up bold axis title handover status
b7871fcabccb6614b386a92dc822c208574b8d0b runtime: split generic chart trace helpers
731d812244a6caedb9e47d61fb50a4e3f217309e runtime: split generic chart layout builders
44d5432929ee5e74415b49288ed8c3ee89037e94 runtime: split generic chart render entry points
9f55f5824514f3ec158c173df3b0a7797f526bfe runtime: make generic chart module a facade
7936ba73e1b926de8208411e4613daf63c66a52d artifacts: let era division chart use auto x tick angle
830b1d1e43a4aae6ad6caa840513c8e1cc3691f1 artifacts: let makuuchi rank era chart use auto x tick angle
feb9be8869af18b58e009e29f0ff563410fbd5b7 artifacts: restore basho result note wording
512f04aee67b9c1430e9d5bba4ddb0416f35d184 runtime: let first chii appearance use Plotly x tick auto
dd6544c0897cd7388aa60391cc4bc7ecb744c653 runtime: hint first chii x tick density to Plotly
eea7fc1ecb53b05b6f2353e6ac4df777edbaf5ed artifacts: restore division persistence tick angle
9d8e481368123775c73f75b75dd5d908f248daf1 docs: add LLM edit discipline guidance
```

There were also cleanup commits removing unused placeholder modules created
during failed attempts:

```text
a1e490659cbcae75bb8cdccbda43cf0d9eb6ebe9
07c8c6e059a06bfb4c9e7db66e9f1b0ce6f2f2d7
c7a8bdf437dc8336052c157ec539945626bc2050
```

## Process cautions for the next run

Follow `docs/LLM Guide.md`, especially the `LLM Edit Discipline` section.

Practical lessons from this pass:

- Identify the actual owner file before changing anything.
- Prefer the smallest owner file.
- Do not create placeholder, policy, wrapper or probe files for a simple edit.
- Avoid full-file rewrites of large files such as `manifest/artifacts.py`; the
  GitHub connector has no patch operation and full replacements caused accidental
  unrelated edits during this pass.
- If a full-file replacement is unavoidable, verify the net diff before saying
  the change is done.
- Do not treat source inspection as browser verification. The user validates the
  rendered result after rebuilding.

## Suggested next step

Continue with **4.5 Division Persistence**.

Current restored state is fixed `-45` x tick angle. Reasonable next options are:

1. Leave it fixed if the rendered chart is acceptable.
2. Retry a simple `"x_tickangle": "auto"` and have the user rebuild/evaluate.
3. Inspect grouped-line layout and data density before adding any grouped-line
   specific tick-density hint.

Do not update normative rendering docs after every individual chart. Update the
design docs only when a pattern becomes general policy.
