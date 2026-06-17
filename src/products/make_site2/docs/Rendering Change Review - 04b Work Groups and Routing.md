### 5.6 Basho selector URL state

Implemented as an interim PA-specific runtime control. The current public URL
shape uses `year=YYYY` and `month=MM`, and the runtime accepts the six sumo
months only. `year=latest&month=latest` may be emitted as an initial/default
view and is canonicalized after the index loads.

The no-basho case is intentionally simple: if a supported sumo calendar slot has
no indexed basho, the ContentPanel is blank except for the no-basho message.

### 5.7 Bad URLs

A general bad-URL handler has not been designed. The current minimal behavior is:

```text
Bad URL -> JS message "Bad URL" -> replace/navigate to Home
```

This is sufficient for the Basho selector work but should be revisited as a
separate routing/UX design topic.

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

Partially implemented as shared table-rendering semantics. A mechanical
`row_number` column is distinct from a meaningful `#` ranking/ordinal column. The
mechanical column is blank-headed, muted and non-sortable; it is recomputed after
sort/filter where applicable. This is currently implemented for 7.1, 7.4-style
generic tables, 9.1 and Banzuke Changes 2.1. In 2.1, banzuke-style rendering
uses a leading blank row-number header spanning the two-row East/Rank/West
heading structure; scan-table rendering uses a leading blank, non-sortable
row-number column.

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

Conditional x-axis tick rotation remains the open shared-chart rendering item.
Its implementation should settle when chart labels are rotated for density or
legibility rather than treating bold axis titles as still open work.

## 6. Review Conclusion

The proposed changes are understandable and mostly precise enough to begin
design. They should not be implemented as an undifferentiated CSS tweak pass.

Basho selector work is now complete as an interim PA-specific/runtime solution.
Clickable Notes popovers, shikona link affordance and Career Length Longest Show
Active are complete as runtime/PA-specific interactions. The highest-risk
remaining items are Notes-popover validation/tightening and the remaining shared
table visual-language token work. The current column-group work is intentionally
interim and ad hoc; it should not become the first step toward a general table
theory.
