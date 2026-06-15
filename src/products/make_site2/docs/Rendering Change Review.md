# Rendering Change Review

## Status

Review note for a proposed `make_site2` rendering change set.

This document describes the proposed change before classifying its likely design
and implementation impact. It is not yet normative rendering design.

Settled rendering policy should move into `05 Rendering Design.md`. Unresolved
or provisional rendering decisions should be tracked in
`06 Rendering Audit and Changes.md`. Changes that affect table, chart, filter,
control or interaction semantics should update the relevant `04.*` model design
documents before implementation.

## 1. Review Purpose

The current `make_site2` layout is broadly solid, but a review of rendered pages
identified a collection of suboptimal visible treatments.

The purpose of this document is to record the proposed change set in product and
design terms, then classify which parts are:

- pure presentation/token changes;
- shared rendering-policy changes;
- Published Artifact model changes;
- Public UI Model or Filter/control changes;
- runtime interaction changes; or
- build-mode/development-vs-production policy changes.

The main risk is making changes that look like CSS tweaks while silently changing
UI ownership, PA semantics or public interaction contracts.

## 2. Proposed Change

### 2.1 Development and Production Affordances

Help/popover markers currently use a visible `?` indicator. The proposed change
is:

- production output should not need a visible marker solely to advertise that
  popover/help text exists;
- development output may still need a visible marker so reviewers can find and
  audit popover-bearing items;
- when a marker is shown, it should use a circled-info style symbol rather than
  `?`.

This proposal may require an explicit distinction between development and final
product rendering. The existing `--prod` CLI flag should be reviewed before it is
used for this purpose, because its current intended scope is not yet established
as a general production-rendering mode.

### 2.2 Shared Table Visual Language

The proposed table visual changes are:

- increase whitespace above and below table headings, roughly `1ex`, whether the
  heading is simple or two-part;
- give all tables a bounding box;
- draw a line under the lowest heading row;
- draw left and right lines for every column group;
- draw no other table grid lines;
- make alternating row colours brighter and increase the contrast between the two
  alternating colours;
- introduce a muted foreground colour derived from the normal text colour but
  close to the background colour;
- render dates with `-` where they currently use `/`.

These are intended as shared visible language for table-like PAs rather than
page-local tweaks.

### 2.3 Table Structure and Semantic Policy

Several proposed changes concern table structure, not merely table appearance.

#### Section 6.2.1 table headings

In page/section 6.2.1, the heading above each of the three tables should become a
column heading that spans the two columns in its table.

#### Section 9.1 grouped headings

In page/section 9.1, simple headings such as `#`, `Shikona`, `Chii` and `Wins`
should vertically span the two heading rows occupied by grouped headings such as
`Wins per Basho / Average` and `Wins per Basho / #`.

#### Row-number column

All tables should receive a leading row-number column. The heading for this
mechanical row-number column should be blank. The heading cell and row-number
values should use the muted foreground colour.

#### Superlative/ranking columns

Tables whose titles mention a superlative should use `#` for ordinal/ranking
columns. This `#` column is distinct from the blank, muted, mechanical row-number
column.

The intended distinction is:

```text
blank muted leading column = mechanical row number
# column                   = meaningful ordinal/ranking/leaderboard position
```

### 2.4 Shikona Links and Notes Interactions

#### Shikona links

All shikona links should retain their current ordinary-click behavior and should
also support Alt-click.

The proposed behavior is:

```text
normal click -> SumoDB rikishi page
Alt-click    -> make_site2 Career Comparisons chart
popover      -> "Click for SumoDB; Alt-click for chart."
```

The Alt-click chart target is:

```text
index.html?page=career_comparisons&skill=chii&x=date&log=true&rikishi=<rik id>
```

where `<rik id>` is the linked rikishi id.

#### Popovers that refer to Notes

When a popover mentions Notes, the reference should be interactive. Clicking the
Notes reference should:

- make the Notes bar/panel visible if it is currently hidden;
- identify the relevant note;
- highlight that note, for example by underlining it.

A later validation pass should check that every popover which refers to Notes has
a corresponding Note to reveal and highlight.

### 2.5 Basho Selector Redesign

The method of selecting a basho should be redesigned.

The proposed control shape is:

```text
Basho
    Year  <year dropdown>
    Month <month dropdown>

<<  <  >  >>
```

The navigation buttons have the usual semantics:

- `<<` moves to the first available basho;
- `<` moves to the previous available basho;
- `>` moves to the next available basho;
- `>>` moves to the last available basho;
- attempts to move beyond either end are ignored.

The displayed basho should change whenever the user changes a dropdown or clicks
a navigation button.

If the user chooses a year/month for which there are no results, the content
panel should say:

```text
There was no basho in MMMM YYYY
```

### 2.6 Shared Chart Rendering

The proposed shared chart rendering changes are:

- x-axis tick labels should be angled only when needed for density or legibility;
  low tick-count charts should generally keep horizontal labels;
- x-axis and y-axis titles should be bold.

### 2.7 PA-Specific Chart Changes

The proposed PA-specific chart changes are:

- page 5.1 should use a line chart rather than a column chart;
- page 7.3.1 Distribution should use a line chart rather than a column chart;
- in page 6.3.1, error bars should be pale blue rather than appearing white.

## 3. First-Pass Design Classification

The proposed change set is understandable and mostly precise enough to begin
design work. It should not be implemented as an undifferentiated CSS pass.

The natural grouping is:

```text
A. Pure presentation policy
B. Rendering-policy changes that need shared CSS/renderer rules
C. PA/table/chart model changes
D. Runtime interaction/state changes
E. Build-mode / development-vs-production policy
```

### 3.1 Development-only help/popover marker

This is not purely CSS if production and development diverge. It requires an
explicit build/runtime context policy.

The `--prod` flag is a possible implementation route, but only after its intended
contract is reviewed and either confirmed or extended.

### 3.2 Table heading spacing

This is shared table/PA-caption rendering policy. It belongs to table-like PA
presentation and/or PA caption spacing, not to the Public UI Model.

### 3.3 Section 6.2.1 spanning headings

This changes table structure and semantics. The design question is whether those
headings are captions above separate tables, group headings inside one sectioned
table, or `colspan=2` heading rows within each table.

### 3.4 Table border policy

This is mostly shared table rendering policy. However, “column group” requires
the renderer to know which headings/groups exist. For recursive/grouped tables
that is model-driven; for flat tables it may require an explicit grouping
vocabulary or a default “each column is its own group” rule.

### 3.5 Alternating row colours

This is theme/token tuning inside an already accepted shared table rule.

### 3.6 Shikona links

This is runtime interaction and public-link policy, not styling. It should be
implemented as shared shikona-link semantics so all table renderers behave
consistently.

### 3.7 Basho selector redesign

This is model/runtime work rather than CSS. It changes the control model from a
single finite basho selector into a compound selector plus navigation controls
plus an unavailable selected-state message.

The design should decide whether this belongs to a richer `FilterSection` form or
to a PA-specific Basho Results control.

### 3.8 Section 9.1 vertically spanning headings

This is table heading model/rendering. It is probably related to the distinction
between ordinary tables and the recursive/grouped table model used by 7.1 Basho
Results.

### 3.9 Muted foreground colour

This is a shared theme token, but it carries semantic meaning wherever used. It
needs a declared owner and scope, such as row numbers, navigation placeholders,
unavailable items or secondary metadata.

### 3.10 Row-number column on all tables

This is table model/rendering policy, not merely CSS.

### 3.11 Superlative tables and ordinal/ranking columns

This is part of the same row-number/ranking policy. It needs a table-model
concept or explicit shared table-rendering policy.

### 3.12 Date separator

This is a shared data-formatting/rendering rule. It may belong in a shared date
formatter if date values are modelled as dates. If current data arrives as
strings, it may require renderer-side normalization or producer-side output
cleanup.

### 3.13 Popovers that mention Notes

This is runtime interaction/state plus an explicit popover-to-note relationship.
It should not be implemented by parsing arbitrary popover text if the
relationship can instead be represented directly.

### 3.14 Conditional x-axis tick rotation

This is shared chart rendering policy. The current behavior may be applying a
fixed artifact value where a dynamic rule is wanted.

### 3.15 Bold axis titles

This is a shared Plotly chart presentation rule. It has low model impact, but it
should still be declared as chart rendering policy.

### 3.16 Specific charts should be line charts

This is a product/PA-form change, not CSS. It changes the PA terminal form or
chart renderer choice, and should be checked against the public analytical
question because bar/column charts and line charts make different claims.

### 3.17 Section 6.3.1 error bars

This is a PA-specific chart rendering rule. Because error bars communicate
uncertainty, the colour choice should be declared as belonging to that PA feature.

## 4. Natural Work Groups

| Group | Items | Nature |
| --- | --- | --- |
| Development vs production affordances | help/popover marker visibility, info symbol, possible debug CSS variants | Build/runtime mode policy |
| Shared table visual language | spacing, borders, row colours, muted colour, date format | Rendering policy/CSS plus shared formatter |
| Table semantic model | 6.2.1 spanning headings, 9.1 rowspans, row numbers, superlative `#` columns, column groups | Published Artifact/table model |
| Link/popover/notes interactions | shikona Alt-click, link popover text, clickable Notes popovers | Runtime interaction plus explicit metadata |
| Basho Results control model | year/month selector and navigation buttons, no-basho message | Filter/control model or PA-specific control |
| Shared chart rendering | tick-angle rule, bold axis titles | Chart rendering policy |
| PA-specific chart semantics | line-vs-column chart changes, 6.3.1 error-bar colour | PA contract / chart renderer selection |

## 5. Implementation-Routing Notes

These notes are intentionally non-final. They preserve likely routes without
settling implementation design prematurely.

### 5.1 `--prod`

There is an existing `--prod` CLI flag. Before using it to drive visible
production/development differences, review its current contract and decide
whether it means only “no development cache-busting” or a broader “final public
product build”.

The help/popover marker visibility is a candidate for build-mode-dependent
behavior, but only after the build-mode contract is explicit.

### 5.2 `debug_layout`

The existing `debug_layout=true` overlay is useful for structure inspection. A
future extension such as `debug_layout=headings_v4` could support experimental
CSS or rendering diagnostics, but that should be treated as debug/development
instrumentation rather than as public rendering policy.

## 6. Review Conclusion

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
