# Session Handover - Rendering Review

## Scope

This handover covers the recent `make_site2` rendering-review pass on branch `dev`.

The review source has been split so the long original can be read and maintained in smaller parts:

- `Rendering Change Review.md` — short index/status page.
- `Rendering Change Review - 01 Purpose and Status.md`.
- `Rendering Change Review - 02 Proposed Changes.md`.
- `Rendering Change Review - 03 Design Classification.md`.
- `Rendering Change Review - 04 Work Groups and Routing.md`.

## Current chart-axis review progress

This later chart-rendering pass focused on Plotly x-axis title emphasis, tick-label
angle and tick-label density in the generic chart renderers.

### Settled during this pass

- Bold Plotly axis titles are implemented as shared chart presentation and are
  now incorporated into `05 Rendering Design 3.md`.
- The old monolithic generic chart module was split into smaller files:
  - `runtime/site-refactor/ui/charts/generic.js` is now a facade.
  - `runtime/site-refactor/ui/charts/generic-traces.js` owns generic trace helpers.
  - `runtime/site-refactor/ui/charts/generic-layouts.js` owns generic Plotly layout builders.
  - `runtime/site-refactor/ui/charts/generic-renderers.js` owns generic renderer entry points.
- The refactor was intended to be behavior-preserving; later chart-axis changes
  were made after the split.

### Chart-specific x-axis findings and current state

- `BANZUKE_DIVISION_BY_ERA_ARTIFACT` / Average Banzuke Composition by Era:
  - Provenance now uses `"x_tickangle": "auto"`.
  - User verified the behavior as acceptable: horizontal labels when there is
    room and Plotly rotation when the chart narrows.
- `MAKUUCHI_RANK_BY_ERA_ARTIFACT` / Makuuchi Rank Appearances by Era:
  - Provenance now uses `"x_tickangle": "auto"`.
  - Plotly may jump from horizontal to vertical because the rank labels are
    dense; this was accepted as good enough for now.
- `FIRST_CHII_APPEARANCE_ARTIFACT` / First Chii Appearance:
  - The ordered-bar layout has a chart-specific branch for
    `artifact.id === "first_chii_appearance"`.
  - That branch lets Plotly own both x tick-label angle and x tick-label density:
    it sets `tickangle: "auto"`, `tickmode: "auto"`, and `nticks: 20`, and it
    deliberately omits explicit `tickvals` and `ticktext`.
  - Other ordered-bar charts still use the existing `sparseTickText(...)` path.
- `DIVISION_STABILITY_ARTIFACT` / Division Persistence:
  - A one-line trial changed `"x_tickangle": -45` to `"auto"`, but the user
    asked to undo it before evaluating a rebuild.
  - Current state is restored to `"x_tickangle": -45`.
  - Do not assume the First Chii treatment applies here. Division Persistence is
    a grouped-line chart, not an ordered-bar chart using the `sparseTickText`
    path.

### Plotly context established in discussion

- Plotly's default auto tick-angle candidates are effectively `0`, `30` and
  `90`; it may skip straight to `90` if it judges intermediate rotation
  insufficient.
- `tickangle: "auto"` lets Plotly choose the angle during Plotly layout
  recalculation.
- If the runtime supplies `tickvals` and `ticktext`, label density is explicit
  and Plotly is no longer choosing tick labels automatically.
- For Plotly-controlled label density, use `tickmode: "auto"` plus an `nticks`
  hint and omit `tickvals` / `ticktext`.
- Plotly auto behavior recalculates when Plotly is redrawn or resized. Browser
  window resizing works when Plotly responsive mode is active; internal layout
  changes may need an explicit Plotly resize or redraw.

### Process warnings from this pass

- Avoid full-file rewrites of large files such as `manifest/artifacts.py` unless
  there is no safer option. The GitHub connector lacks a patch operation, and
  full replacement of large files caused accidental unrelated edits that had to
  be cleaned up.
- Prefer the smallest file that owns the behavior. For chart runtime behavior,
  `generic-layouts.js` was the correct owner file and was small enough to edit
  directly.
- Do not create placeholder, policy, wrapper or probe files to work around a
  simple edit. This is now recorded in `docs/LLM Guide.md` under “LLM Edit
  Discipline.”

Important recent commits:

```text
b7871fcabccb6614b386a92dc822c208574b8d0b runtime: split generic chart trace helpers
731d812244a6caedb9e47d61fb50a4e3f217309e runtime: split generic chart layout builders
44d5432929ee5e74415b49288ed8c3ee89037e94 runtime: split generic chart render entry points
9f55f5824514f3ec158c173df3b0a7797f526bfe runtime: make generic chart module a facade
7936ba73e1b926de8208411e4613daf63c66a52d artifacts: let era division chart use auto x tick angle
830b1d1e43a4aae6ad6caa840513c8e1cc3691f1 artifacts: let makuuchi rank era chart use auto x tick angle
512f04aee67b9c1430e9d5bba4ddb0416f35d184 runtime: let first chii appearance use Plotly x tick auto
dd6544c0897cd7388aa60391cc4bc7ecb744c653 runtime: hint first chii x tick density to Plotly
eea7fc1ecb53b05b6f2353e6ac4df777edbaf5ed artifacts: restore division persistence tick angle
9d8e481368123775c73f75b75dd5d908f248daf1 docs: add LLM edit discipline guidance
```

Suggested next chart-review step:

1. Continue from `DIVISION_STABILITY_ARTIFACT` / Division Persistence with the
   current restored state (`"x_tickangle": -45`). Decide whether to leave it as
   fixed-angle, retry simple `"auto"`, or add a grouped-line-specific density
   hint after inspecting the rendered behavior.
2. If a pattern is accepted across multiple charts, update the normative
   rendering design docs. Do not document every chart immediately after a local
   visual fix unless it establishes a general rule.

## A/B list status

The A-list and B-list are the selected review action plan. There is no hidden
third level where “do A and B” is one item.

The B-list completed in this pass was:

```text
B1. Update Rendering Change Review
B2. Remove/debug cleanup
B3. Validate and tighten Notes popovers
B4. Shikona link affordance
```

B1, B2 and B4 are complete. B3 was deferred, counted done for this pass, and is
still tracked as open validation/tightening work in the review.

The remaining review action items are listed below in “Remaining review backlog.”

## Completed in this pass

### B1. Update Rendering Change Review

Done.

The original long review was factored into four smaller docs, and the review status now reflects current work:

- Basho selector redesign implemented.
- Clickable Notes popovers implemented.
- Shikona link affordance implemented across the shared helper path and Basho Results.
- Career Length Longest / Show Active implemented with produced ranked populations.
- Row-number vs ranking semantics partially implemented.
- Section 6.2.1 side-by-side layout restored.
- Bad URL handling minimally implemented.

Important commits:

```text
874ba0579838a9e21de59b49337adf440de7bc26 docs: split rendering review purpose
e5b44e7b4ecc32310f4cd1f984bed875133e2997 docs: split rendering review proposed changes
00be52d448aedcabafb9091ac9b797665389a94a docs: split rendering review classification
7fd543b40fd22cf9f7543ba59c3f152137bda24c docs: split rendering review work groups
f40d39ecff576bccfaae36665b2c8680d3b4c570 docs: factor rendering review into parts
af07238fde732cbc8a7a023fecbf809194a469c6 docs: refresh rendering review status
8137b950bef10dae8b1ab550fb726043ca4ebf5c docs: refresh proposed rendering changes
3552f9239888925daf14cf97ac03c911585c30b6 docs: refresh rendering classification status
6174bae0be684288ab330a2c41ab66059ed089ca docs: refresh rendering work groups
6904f30e64f88b7108a893f56b16639d85397f46 docs: mark shikona affordance in status
```

### B2. Remove/debug cleanup

Done.

The temporary diagnostic alert for missing Notes targets was removed. The runtime now reports the generic message:

```text
No such note
```

The useful fixes remain:

- Notes popovers are clickable.
- Notes panel opens if hidden.
- Note lookup is scoped to the Notes panel.
- Matching note is scrolled/focused and highlighted.
- Highlight style is subtle boxed emphasis, not red.

Important commits:

```text
5e6e34df8cc2ce2fe4019719397327241475e9a1 runtime: soften note highlight style
31798e3d5d86c4924198ca0f0ba2a74b334e171a runtime: restore missing note alert text
```

### B3. Validate and tighten Notes popovers

Deferred, counted done for this pass, and explicitly tracked as open review work.

The review now records a validation/tightening pass for:

- Banzuke Delta and Result popovers.
- Basho movement and result popovers.
- Generic Clean popovers.
- 9.1 popovers.
- Popup timing, clickability, note opening and highlight.
- Placeholder Basho movement note text.
- Popovers containing `Notes` but lacking a rendered target note.

Important commit:

```text
6946976af4b2c292efd656f86106a8c9c6887220 docs: add notes popover validation task
```

### B4. Shikona link affordance

Done and manually verified by the user after rebuild.

Expected behavior:

```text
Normal shikona click -> SumoDB rikishi page
Alt-click            -> make_site2 Career Comparisons chart
Popover text         -> Click for SumoDB; Alt-click for chart.
```

Alt-click target:

```text
index.html?page=career_comparisons&skill=chii&x=date&log=true&rikishi=<rik id>
```

Implementation details:

- Shared `renderRikishiLink` in `runtime/site-refactor/ui/tables/shared.js` now emits shikona links with help metadata and an `data-alt-href` target.
- `runtime/site-refactor/ui/help.js` installs the Alt-click handler.
- `runtime/site-refactor/ui/basho-results/render.js` had its own local shikona link renderer; it now delegates to the shared helper.
- The first Basho Results patch accidentally dropped the `visiblePaths` argument in one `isVisiblePath` call; this was corrected immediately.

Important commits:

```text
37a818061280d8e98fe246a1a3bbfb053a699e60 runtime: add shikona link help metadata
4e83d38cd60923bad35c75260df50e91adb9985a runtime: support shikona alt click
41d3c4905734b9a1abcd642b47878b660460995f docs: mark shikona link affordance implemented
c4e9cf0a702e47f817c55eac7421d6c233628e80 runtime: share basho shikona links
e1cba6900a65de9d610ce1434811161c279592c1 runtime: fix basho shikona visibility check
```

## Current known state

### Notes popovers

Implemented behavior is present, but validation/tightening remains open. The current runtime contract is:

- A popover whose text contains the exact word `Notes` is clickable.
- The floating popover owns the click, not the source table heading/help span.
- The popover opens the Notes panel and targets the relevant note.
- Missing targets show `No such note`.

### Shikona links

Implemented across the known shikona rendering paths:

- Shared helper path used by generic tables, Standings, Career Length Longest and Banzuke Changes.
- Basho Results recursive table path.

If a future page still lacks the affordance, look for another local shikona renderer that does not call `renderRikishiLink` from `runtime/site-refactor/ui/tables/shared.js`.

### Career Length Longest / Show Active

Implemented. The Longest table uses produced ranked populations rather than runtime-calculated rank.

- `Show Active` checked/default true uses all-rikishi population.
- `Show Active` unchecked false uses non-active population.
- Active rikishi Last date displays `-`.

### Row-number vs ranking semantics

Partially implemented.

Current policy:

```text
blank muted leading column = mechanical row number
# column                   = meaningful ordinal/ranking/leaderboard position
```

Implemented for:

- 7.1 Basho Results.
- 7.4-style generic tables.
- 9.1 Standings.
- Career Length Longest, with produced rank in `#` and separate mechanical row number.
- 2.1 Banzuke Changes, in both banzuke-style and scan-table views.

### Section 6.2.1

Side-by-side sectioned-table layout is restored as a custom sectioned-table row layout.

Open visual/design follow-up: confirm heading treatment and shared table-language alignment.

### Bold axis titles

Implemented as shared Plotly chart presentation and incorporated into
`05 Rendering Design 3.md`.

The remaining shared chart-rendering item is conditional x-axis tick rotation.

## Remaining review backlog

Recommended next target:

1. Shared table visual-language follow-up.

Completed table-structure/scaffolding pieces:

- Mechanical row-number column implemented in both banzuke-style and
  scan-table views after this handover. Banzuke-style uses a leading blank
  row-number header spanning the two heading rows; scan-table uses a leading
  blank, non-sortable row-number column whose values recompute after sorting.
- Broader East / Rank / West group metadata is provisionally implemented for
  banzuke-style view. The row-number column is represented as its own group so
  the current renderer can simulate row-number-as-skeleton behavior without a
  general table-model change.
- 9.1 has provisional Row number, Context, Wins per Basho and Wins per Bout
  group metadata, with Standings-specific grouped-heading rendering.
- Table bounding boxes are implemented through an explicit
  `artifact-table-frame` for split tables, and direct borders for unsplit
  sectioned tables.
- Artifact title blocks own their trailing whitespace and are followed by a
  defined gap before the table entity.
- Mechanical row-number columns use the shared muted foreground token.
- Public date-like display strings use `-` separators at known table/chart
  display points without rewriting source data, URLs or paths.
- Alternating table rows use the revised row background tokens.
- The heading/data separator is rendered as the top border of the first body row.
- Section 6.2.1 section headings render as table heading cells spanning their
  two columns.
- Keep the interim table-group approach easiest-to-remove later.

Other open items:

2. Shared chart rendering.
- Conditional x-axis tick rotation.
