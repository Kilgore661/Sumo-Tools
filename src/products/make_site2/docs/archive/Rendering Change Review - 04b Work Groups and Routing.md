### 5.6 Basho selector URL state

Implemented as an interim PA-specific runtime control. The current public URL
shape uses `year=YYYY` and `month=MM`, and the runtime accepts the six sumo
months only. `year=latest&month=latest` may be emitted as an initial/default
view and is canonicalized after the index loads.

The no-basho case is intentionally simple: if a supported sumo calendar slot has
no indexed basho, the ContentPanel is blank except for the no-basho message.

### 5.7 Bad URLs

The richer bad-URL policy is resolved but not implemented.

Deep bad URLs, including pasted URLs, bookmarks, external links and new-tab
links, should alert and then land on Home because there is no prior valid rendered
view in that tab to preserve.

Bad in-site navigation means a navigation attempt intercepted by the running app
while a valid page is already displayed. It should alert and leave the current URL
and rendered view unchanged.

The runtime still uses the minimal implemented behavior: alert, replace the URL
with Home and render Home.

### 5.8 Notes popover interaction

Implemented as runtime interaction. A help popover whose text contains the exact
word `Notes` is clickable. The source help item may remain a normal table header
or sort control; the floating popover owns the Notes click. The runtime opens the
Notes panel if needed, finds the target note inside that panel, scrolls/focuses
it and applies a five-second highlight. Missing rendered targets produce the
message `No such note`.

Open validation/tightening pass: test Banzuke Delta and Result, Basho movement
and result popovers, generic Clean popovers, and 9.1 popovers; confirm popup
timing, clickability, note opening and highlight. Replace placeholder Basho
movement notes with meaningful text and keep a validation pass for popovers
containing `Notes` but lacking a corresponding rendered note.

### 5.9 Career Length Longest routing

Implemented as PA-specific chart/table semantics. Build-time materialization
creates ranked Longest populations from full producer spans. Runtime selects the
appropriate produced population based on the Longest-only `Show Active` control.
Checked/default true shows the all-rikishi population; unchecked false shows the
non-active population. Active Last values render as `-`.

### 5.10 Row-number and ranking routing

Resolved for the current table model and shared renderers. A mechanical
`row_number` column is distinct from a meaningful `#` ranking/ordinal column. The
mechanical column is blank-headed, muted and non-sortable; it is recomputed after
sort/filter where applicable. This is implemented for 7.1, 7.4-style generic
tables, 9.1 and Banzuke Changes 2.1. In 2.1, banzuke-style rendering uses a
leading blank row-number header spanning the two-row East/Rank/West heading
structure; scan-table rendering uses a leading blank, non-sortable row-number
column.

### 5.11 Shikona link affordance

Implemented as shared shikona-link runtime behavior. Normal click retains the
existing SumoDB link behavior. The link exposes the popover text `Click for
SumoDB; Alt-click for chart.` Alt-click opens the make_site2 Career Comparisons
route:

```text
index.html?page=career_comparisons&skill=chii&x=date&log=true&rikishi=<rik id>
```

### 5.12 Shared chart rendering

Bold axis titles are implemented as shared Plotly chart presentation and
incorporated into `05 Rendering Design 3.md`.

Conditional x-axis tick rotation is resolved for the reviewed simple-chart slice.
Dense-axis cases now either let Plotly choose angle/density directly or carry a
local density hint where the chart requires it. 3.3 Rikishi History remains a
separate follow-up.

## 6. Review Conclusion

The proposed changes were understandable and precise enough to separate rendering
policy from PA semantics and runtime interaction.

Basho selector work is complete as an interim PA-specific/runtime solution.
Clickable Notes popovers, shikona link affordance, Career Length Longest Show
Active, row-number/ranking semantics, reviewed table visual language and the
reviewed simple-chart rendering work are complete for the reviewed slice.

Remaining known work: Notes-popover validation/tightening and the separate 3.3
Rikishi History follow-up. Richer bad-URL behavior is specified but not yet
implemented.