# Rendering Change Review

## Status

Review note for proposed `make_site2` rendering changes.

This document records a first-pass comprehension and classification of proposed
styling, rendering, UI model, PA model and runtime interaction changes. It is not
yet a normative rendering design. Settled rendering policy should move into
`05 Rendering Design.md`; unresolved or provisional rendering decisions should be
tracked in `06 Rendering Audit and Changes.md`; model-level changes should be
reflected in the relevant `04.*` model documents before implementation.

## Review Question

The current layout is broadly solid, but several visible treatments are
suboptimal. The purpose of this review is to determine whether the requested
changes are merely presentation adjustments or whether they affect the Public UI
Model, Published Artifact model, runtime state, or build-mode policy.

The main risk is making changes that look like CSS tweaks while silently changing
UI ownership, PA semantics or public interaction contracts.

## First-Pass Answer

Yes, the requested changes are understandable. Most are tight enough to begin
design work, but they do not all belong to the same layer.

The natural grouping is:

```text
A. Pure presentation policy
B. Rendering-policy changes that need shared CSS/renderer rules
C. PA/table/chart model changes
D. Runtime interaction/state changes
E. Build-mode / development-vs-production policy
```

The important conclusion is that the request is not a bag of cosmetic tweaks. It
contains presentation tokens, shared rendering rules, model changes and runtime
interaction changes. The safe next step is to classify each item by owner before
writing implementation code.

## Table-Related Items

### Development-only help/popover marker

The request is clear:

- Production should not show a visible `?` marker merely to indicate “hover over
  me for info”.
- Development may still need an affordance to reveal where popovers/gloss exist.
- Even in development, the marker should be changed from `?` to the circled-info
  style symbol.

This is not purely CSS if production and development diverge. It requires an
explicit build/runtime context policy. The existing `--prod` flag currently needs
separate review before it is treated as a broader public-product mode rather than
only a cache-mode switch.

### Table heading spacing

The request is clear: tables should have more whitespace above and below the
heading, around `1ex`, regardless of whether the heading is simple or two-part.

This is shared table/PA-caption rendering policy. It belongs to table-like PA
presentation and/or PA caption spacing, not to the Public UI Model.

### Section 6.2.1 table headings as spanning column headings

The visual target is understood: the heading above each of the three tables
should become a table-level heading cell spanning both columns.

This is not merely CSS. It changes table structure and semantics. The design
question is whether those headings are captions above separate tables, group
headings inside one sectioned table, or `colspan=2` heading rows within each
table.

### Table border policy

The requested shared table border policy is understood:

- every table has a bounding box;
- there is a line under the lowest heading row;
- there are left and right lines for every column group;
- there are no other lines.

This is mostly shared table rendering policy. However, “column group” requires
the renderer to know which headings/groups exist. For recursive/grouped tables
that is model-driven; for flat tables it may require an explicit grouping
vocabulary or a default “each column is its own group” rule.

### Alternating row colours

The request is clear: alternating row colours are too subtle; both should be a
bit brighter and the difference between them should be increased.

This is pure theme/token tuning inside an already accepted shared table rule.

### Shikona links

The requirement is understood:

```text
normal click -> SumoDB rikishi page
Alt-click    -> make_site2 Career Comparisons chart
popover      -> "Click for SumoDB; Alt-click for chart."
```

The chart target should be:

```text
index.html?page=career_comparisons&skill=chii&x=date&log=true&rikishi=<rik id>
```

This is runtime interaction and public-link policy, not styling. It should be
shared shikona-link semantics so all table renderers behave consistently.

### Basho selector redesign

The request is clear. The desired control is:

```text
Basho
  Year  <year dropdown>
  Month <month dropdown>

<<  <  >  >>
```

The displayed basho should change immediately when either dropdown changes or a
button is clicked. Movement beyond either end should be ignored. If the user
chooses a year/month with no basho, the content panel should say:

```text
There was no basho in MMMM YYYY
```

This is model/runtime work rather than CSS. It changes the filter model from a
single finite basho selector into a compound selector plus navigation controls
plus an unavailable selected-state message. It should be specified either as a
richer `FilterSection` form or as a PA-specific Basho Results control.

### Section 9.1 vertically spanning headings

The request is understood. Simple headings such as `#`, `Shikona`, `Chii` and
`Wins` should vertically span the two heading rows occupied by grouped headings
such as `Wins per Basho / Average` and `Wins per Basho / #`.

This is not CSS-only. It is table heading model/rendering. The likely issue is
that ordinary tables do not currently have the same recursive/grouped table model
used by 7.1 Basho Results.

### Muted foreground colour

The request is clear: define a muted font colour based on the text colour but
close to the background colour.

This is a shared theme token, but it carries semantic meaning wherever used. It
needs a declared owner/scope, such as row numbers, navigation placeholders,
unavailable items or secondary metadata.

### Row-number column on all tables

The request is clear: all tables should have a leading row-number column with a
blank heading, and both heading and row-number values should use the muted font
colour.

This is table model/rendering policy, not merely CSS.

### Superlative tables and ordinal/ranking columns

The distinction is understood:

- blank muted leading column = mechanical row number;
- `#` column = meaningful ordinal/ranking/leaderboard position, especially when
  the page title implies a superlative.

This needs a table-model concept or at least explicit shared table-rendering
policy.

### Date separator

The request is clear: dates should render with `-` where they currently use `/`.

This is a shared data-formatting/rendering rule. It may belong in a shared date
formatter if date values are modelled as dates; if current data arrives as
strings, it may require renderer-side normalization or producer-side output
cleanup.

### Popovers that mention Notes

The request is clear:

- a popover mentioning or implying `Notes` should be clickable;
- clicking it should make the Notes panel visible if hidden;
- it should highlight the relevant note, for example by underlining;
- a later sanity pass should confirm that every such popover has a corresponding
  note to reveal.

This is runtime interaction/state plus explicit popover-to-note relationship. It
should not be implemented by parsing arbitrary popover text if the relationship
can instead be represented directly.

## Chart-Related Items

### Conditional x-axis tick rotation

The request is clear. X-axis tick labels should only be angled when that is
needed for density/legibility. Low tick-count charts should generally keep
horizontal labels.

This is shared chart rendering policy. The current behavior may be applying a
fixed artifact value where a dynamic rule is wanted.

### Bold axis titles

The request is clear: x- and y-axis titles should be bold.

This is a shared Plotly chart presentation rule. It has low model impact, but it
should still be declared as chart rendering policy.

### Specific charts should be line charts

The request is clear: pages 5.1 and 7.3.1/Distribution should be line charts, not
column charts.

This is a product/PA-form change, not CSS. It changes the PA terminal form or
chart renderer choice, and it should be checked against the public analytical
question because bar/column charts and line charts make different claims.

### Section 6.3.1 error bars

The request is clear: the error bars in 6.3.1 should be pale blue rather than
white-looking.

This is a PA-specific chart rendering rule. Because error bars communicate
uncertainty, the colour choice should be declared as belonging to that PA feature.

## Natural Work Groups

| Group | Items | Nature |
| --- | --- | --- |
| Development vs production affordances | help/popover marker visibility, info symbol, possible debug CSS variants | Build/runtime mode policy |
| Shared table visual language | spacing, borders, row colours, muted colour, date format | Rendering policy/CSS plus shared formatter |
| Table semantic model | 6.2.1 spanning headings, 9.1 rowspans, row numbers, superlative `#` columns, column groups | Published Artifact/table model |
| Link/popover/notes interactions | shikona Alt-click, link popover text, clickable Notes popovers | Runtime interaction plus explicit metadata |
| Basho Results control model | year/month selector and navigation buttons, no-basho message | Filter/control model or PA-specific control |
| Shared chart rendering | tick-angle rule, bold axis titles | Chart rendering policy |
| PA-specific chart semantics | line-vs-column chart changes, 6.3.1 error-bar colour | PA contract / chart renderer selection |

## Implementation-Routing Notes

These are not implementation decisions yet, but they record likely routes to
avoid losing the context of the review.

### `--prod`

There is an existing `--prod` CLI flag. Before using it to drive visible
production/development differences, review its current contract and decide
whether it is intended to mean only “no development cache-busting” or a broader
“final public product build”.

The help/popover marker visibility is a candidate for build-mode-dependent
behavior, but only after the build-mode contract is explicit.

### `debug_layout`

The existing `debug_layout=true` overlay is useful for structure inspection. A
future extension such as `debug_layout=headings_v4` could support experimental
CSS or rendering diagnostics, but that should be treated as debug/development
instrumentation rather than as public rendering policy.

## Review Conclusion

The proposed changes are understandable and mostly precise enough to begin
design. They should not be implemented as an undifferentiated CSS tweak pass.

A safe sequence is:

1. classify each item by owner and layer;
2. move settled presentation rules into `05 Rendering Design.md`;
3. record unresolved/provisional decisions in `06 Rendering Audit and Changes.md`;
4. update PA/table/chart model documents where the requested change affects
   structure or semantics;
5. only then design implementation changes.

The highest-risk items are the Basho selector, table heading structure,
row-number/ranking policy and popover-to-note linking. Those can easily look like
layout work while actually changing the UI model, Published Artifact model or
runtime interaction contract.
