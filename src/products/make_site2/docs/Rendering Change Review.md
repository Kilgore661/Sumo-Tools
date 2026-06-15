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

### 2.1 Help/Popover Marker Affordance

Help/popover markers currently use a visible `?` indicator.

The proposed change is to control the visibility of the info-here indicator by a
new URL parameter:

```text
debug_show_notes=true
```

When `debug_show_notes` is absent or set to `false`, there should be no visible
info-here indicator. When `debug_show_notes=true`, the indicator should be
visible so reviewers can find and audit popover-bearing items.

When the indicator is visible, it should use a circled-info style symbol rather
than `?`.

This makes the marker a reader/reviewer-selected diagnostic display mode rather
than an unconditional development-vs-production distinction. The parameter name
is deliberately diagnostic: it shows note/help affordance markers, but does not
open the Notes panel on page load.

Open issue: decide whether `--prod` should also suppress stylistic debugging
features, including `debug_show_notes` and any future style-debug URL modes, or
whether such URL-selected diagnostics should remain available in product builds
unless explicitly disabled.

### 2.2 Shared Table Visual Language

The proposed table visual changes are:

- increase whitespace above and below table headings, roughly `1ex`, whether the
  heading is simple or two-part;
- give all tables a bounding box;
- draw a line under the lowest heading row;
- draw left and right lines for every declared column group;
- draw no other table grid lines;
- make alternating row colours brighter and increase the contrast between the two
  alternating colours;
- introduce a muted foreground colour derived from the normal text colour but
  close to the background colour;
- render date-like public display values with `-` where they currently use `/`.

These are intended as shared visible language for table-like PAs rather than
page-local tweaks.

For tables other than 7.1 Basho Results, there shall be a mechanism for defining
column groups. The default is that no column groups are declared. In that default
state, the table receives the general bounding box and heading rule, but no
additional column-group boundary treatment is inferred merely from individual
columns.

Exact colour values, transparency settings, border colours, border weights and
related visual tokens are implementer choices. They should be chosen as reasonable
initial values and adjusted if visual review rejects them.

### 2.3 Table Structure and Semantic Policy

Several proposed changes concern table structure, not merely table appearance.

The current intent is not to move ordinary tables into the general table theory
or recursive table model. These declarations are interim, PA-local rendering
metadata where needed.

#### Initial column-group catalogue

The current column-group declarations are:

```text
2.1 Banzuke Changes:
  groups: East, Rank, West

7.1 Basho Results:
  leaves in the heading tree are not groups
  all non-leaf heading-tree nodes are groups

7.3.1 Longest:
  no groups

7.4.*:
  no groups

9.1:
  groups:
    unnamed left group containing #, Shikona, Chii and Wins
    Wins per Basho
    Wins per bout

6.2.1:
  special custom case
  each table should look like any other table as far as it makes sense and is
  possible
```

For 9.1, the unnamed left group has no heading because those columns do not need
one. It must not be treated as a missing heading and must not force introduction
of a placeholder heading such as `Context`. The group exists only to support the
interim rendering policy. If a later general table model is adopted, this ad hoc
9.1 rule should be revisited and may become redundant.

#### Section 6.2.1 table headings

In page/section 6.2.1, the heading above each of the three tables should become a
column heading that spans the two columns in its table, as far as that makes sense
for this custom PA.

#### Section 9.1 grouped headings

In page/section 9.1, simple headings such as `#`, `Shikona`, `Chii` and `Wins`
should vertically span the two heading rows occupied by grouped headings such as
`Wins per Basho / Average` and `Wins per Basho / #`.

This is resolved for now by the interim 9.1 column-group declaration above. It is
not a commitment to making 9.1 a recursive table.

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

A popover has a Notes action if and only if its text contains the exact word
`Notes`.

If a popover contains the exact word `Notes`, the whole popover is clickable.
Clicking anywhere in that popover should:

- make the Notes bar/panel visible if it is currently hidden;
- identify the relevant note;
- highlight that note, for example by underlining it.

Inside such a popover, the word `Notes` may be styled to look link-like, but it
is not a link, does not own the click and does not have a separate handler. The
popover owns the click.

If a popover does not contain the exact word `Notes`, it should not be clickable
at all.

A later validation pass should check that every popover containing `Notes` has a
corresponding Note to reveal and highlight.

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
a navigation button. The semantics of such a change are to show the same public
page for a different date/basho state.

If the user chooses a year/month for which there are no results, the content
panel should say:

```text
There was no basho in MMMM YYYY
```

Anything the browser can show through this selector, including no-basho states,
should be representable by a URL.

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

The subsections below classify each proposed change by ownership and
implementation impact. Section 4 then groups the work into likely implementation
streams.

### 3.1 Help/popover marker URL state

The visible info-here marker is no longer primarily a production/development
split. It is proposed as an explicit URL-selected diagnostic mode owned by the
public/runtime state layer:

```text
debug_show_notes=true
```

This is a runtime presentation-state feature. It should be treated similarly to a
reader/reviewer display mode: absent or false hides the indicator; true shows it.

The `--prod` question remains separate. `--prod` may or may not imply removal of
stylistic debugging features, but that is an open build-mode policy decision and
should not be assumed by the `debug_show_notes` design.

### 3.2 Table heading spacing

This is shared table/PA-caption rendering policy. It belongs to table-like PA
presentation and/or PA caption spacing, not to the Public UI Model.

### 3.3 Interim table structure and column groups

The table structure requests are deliberately narrower than a general table
model. The implementation should use an interim, easy-to-remove mechanism for
non-7.1 column-group declarations.

The steer is: choose the approach that is easiest to remove later when a general
table model supersedes it. Avoid spreading table-group theory across unrelated
renderers and avoid migrating ordinary tables into the recursive table model as
part of this change.

### 3.4 Table border and column-group policy

The general table bounding box, lowest-heading underline and suppression of other
grid lines are shared table rendering policy.

Column-group boundary lines require explicit column-group knowledge. For 7.1
Basho Results, that knowledge is already model-driven by the recursive/grouped
table structure. For tables other than 7.1, there shall be a mechanism for
defining column groups. The default is “no groups here”; individual flat columns
must not automatically imply column groups.

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

Changing the selector state means showing the same public page for a different
date/basho state. Every state the browser can render through this selector should
be URL-addressable, including states for year/month combinations with no basho.

The design should decide whether this belongs to a richer `FilterSection` form or
to a PA-specific Basho Results control.

### 3.8 Section 9.1 vertically spanning headings

This is currently resolved by the interim 9.1 column-group declaration. If a later
general table model is adopted, this rule should be revisited and may become
redundant.

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

This is a shared data-formatting/rendering rule for date-like values in public
rendered display. It should not be assumed to change source data, CSV contracts,
filenames, URL parameters, internal identifiers or other non-display contexts
where `/` is normal unless a later requirement says so.

### 3.13 Popovers that mention Notes

This is runtime interaction/state plus a text-triggered popover action rule. The
qualifying condition is exact text occurrence of `Notes`; the whole popover owns
the click.

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
| Diagnostic display affordances | `debug_show_notes` URL state, info symbol, possible debug CSS variants | Runtime presentation state / debug policy |
| Shared table visual language | spacing, borders, row colours, muted colour, date-like display format | Rendering policy/CSS plus shared formatter |
| Interim table structure metadata | 2.1/7.1/9.1 column groups, 6.2.1 custom handling | Ad hoc PA-local metadata, easiest-to-remove later |
| Table semantic model | row numbers, superlative `#` columns | Published Artifact/table model |
| Link/popover/notes interactions | shikona Alt-click, link popover text, clickable Notes popovers | Runtime interaction plus explicit metadata/text rule |
| Basho Results control model | year/month selector and navigation buttons, URL-addressable no-basho state | Filter/control model or PA-specific control |
| Shared chart rendering | tick-angle rule, bold axis titles | Chart rendering policy |
| PA-specific chart semantics | line-vs-column chart changes, 6.3.1 error-bar colour | PA contract / chart renderer selection |
| Build-mode policy | whether `--prod` suppresses stylistic debugging | Open build/operations decision |

## 5. Implementation-Routing Notes

These notes are intentionally non-final. They preserve likely routes without
settling implementation design prematurely.

### 5.1 `debug_show_notes`

The proposed immediate control for visible info-here indicators is the URL
parameter `debug_show_notes`.

Required behavior:

```text
absent                 -> no info-here indicator
debug_show_notes=false -> no info-here indicator
debug_show_notes=true  -> show info-here indicator
```

The visible marker should be the circled-info style symbol rather than `?`.

This parameter shows diagnostic affordance markers. It does not open the Notes
panel on page load.

### 5.2 `--prod`

There is an existing `--prod` CLI flag. An open issue remains: should `--prod`
imply that stylistic debugging features are removed or disabled?

This question should be resolved separately from the `debug_show_notes` URL-state
rule. The `debug_show_notes` rule defines when the info-here marker is displayed;
the `--prod` issue asks whether a production build should make such diagnostic
display modes unavailable regardless of URL parameters.

### 5.3 `debug_layout`

The existing `debug_layout=true` overlay is useful for structure inspection. A
future extension such as `debug_layout=headings_v4` could support experimental
CSS or rendering diagnostics, but that should be treated as debug/development
instrumentation rather than as public rendering policy.

### 5.4 Column groups in non-7.1 tables

For tables other than 7.1 Basho Results, implement a mechanism for declaring
column groups. The default state is explicitly no declared groups.

The renderer should not infer a column group for every individual column. Column
boundary treatment should appear only where a group is declared, while the table
still receives the general bounding box and heading underline rules.

Because this mechanism is expected to be removed if/when a general table model is
introduced, prefer the easiest-to-remove implementation. A small ad hoc
configuration close to the current make_site2 rendering/manifest boundary is
preferable to a broad model migration.

### 5.5 Visual tokens

Exact visual token choices are delegated to implementation and review. Choose
reasonable initial values for muted foreground, row backgrounds, border colour,
border weight and spacing. If the result looks wrong, revise the tokens after
visual inspection.

### 5.6 Basho selector URL state

The Basho selector changes the date/basho state of the same public page. Any
state the browser can render should have a URL representation, including selected
year/month states for which there was no basho and no results.

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

The highest-risk items are the Basho selector, row-number/ranking policy and
popover-to-note behavior. The current column-group work is intentionally interim
and ad hoc; it should not become the first step toward a general table theory.
