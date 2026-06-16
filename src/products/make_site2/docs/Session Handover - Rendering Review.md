# Session Handover - Rendering Review

## Scope

This handover covers the recent `make_site2` rendering-review pass on branch `dev`.

The review source has been split so the long original can be read and maintained in smaller parts:

- `Rendering Change Review.md` — short index/status page.
- `Rendering Change Review - 01 Purpose and Status.md`.
- `Rendering Change Review - 02 Proposed Changes.md`.
- `Rendering Change Review - 03 Design Classification.md`.
- `Rendering Change Review - 04 Work Groups and Routing.md`.

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
The date-format display cleanup is still open and belongs under Shared table
visual language as “date-like display separator policy.”

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
- The heading/data separator is rendered as the top border of the first body row.
- Section 6.2.1 section headings render as table heading cells spanning their
  two columns.
- Keep the interim table-group approach easiest-to-remove later.

Other open items:

2. Shared table visual language follow-up.

- Heading spacing.
- Alternating row color/token pass.
- Muted foreground token policy.
- Date-like display separator policy. This is the public display-format cleanup for date-like values that should use `-` where they currently use `/`.

3. `debug_show_notes` / marker affordance.

- Hide normal help marker unless `debug_show_notes=true`.
- Replace `?` marker with circled-info style marker when visible.
- Decide product/debug policy.

4. Shared chart rendering.

- Conditional x-axis tick rotation.
- Bold axis titles.

5. PA-specific chart changes.

- Page 5.1 line chart instead of column.
- Page 7.3.1 Distribution line chart instead of column.
- Page 6.3.1 pale-blue error bars.

6. Richer bad-URL handling.

- Current minimal behavior exists: `Bad URL` message and route Home.
- Richer routing/UX policy remains TBD.

## Files most likely to matter next

```text
src/products/make_site2/docs/Rendering Change Review.md
src/products/make_site2/docs/Rendering Change Review - 01 Purpose and Status.md
src/products/make_site2/docs/Rendering Change Review - 02 Proposed Changes.md
src/products/make_site2/docs/Rendering Change Review - 03 Design Classification.md
src/products/make_site2/docs/Rendering Change Review - 04 Work Groups and Routing.md

src/products/make_site2/runtime/site-refactor/ui/help.js
src/products/make_site2/runtime/site-refactor/ui/notes.js
src/products/make_site2/runtime/site-refactor/ui/tables/shared.js
src/products/make_site2/runtime/site-refactor/ui/tables/generic.js
src/products/make_site2/runtime/site-refactor/ui/tables/standings.js
src/products/make_site2/runtime/site-refactor/ui/tables/banzuke-changes.js
src/products/make_site2/runtime/site-refactor/ui/basho-results/render.js
src/products/make_site2/runtime/site-refactor/ui/charts/career-length.js

src/products/make_site2/manifest/artifacts.py
src/products/make_site2/manifest/builder.py
src/products/make_site2/manifest/filters.py
src/products/make_site2/ui_model.py
src/products/make_site2/render.py
```

## Cautions for next session

- Do not assume all shikona links use the shared helper. Search for local link renderers when a page does not behave as expected.
- Do not treat Notes validation as done; it was deferred and recorded as open.
- Do not let interim table-group work become a general table theory by accident.
- GitHub connector output may truncate long files. Fetch long docs in chunks.
- Some large full-file updates may be blocked by safety checks; smaller targeted updates usually work.
