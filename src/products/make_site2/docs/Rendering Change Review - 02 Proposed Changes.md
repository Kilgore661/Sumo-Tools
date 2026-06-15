# Rendering Change Review - 02 Proposed Changes

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
- highlight that note.

Implemented behavior: Notes popovers stay visible long enough to be clicked,
clicking the floating popover opens the Notes panel, scopes note lookup to the
Notes panel, scrolls/focuses the relevant note and highlights it for five
seconds. If no matching rendered note exists, the popover closes and the runtime
shows `No such note`.

Inside such a popover, the word `Notes` may be styled to look link-like, but it
is not a link, does not own the click and does not have a separate handler. The
popover owns the click.

If a popover does not contain the exact word `Notes`, it should not be clickable
at all.

A later validation pass should check that every popover containing `Notes` has a
corresponding Note to reveal and highlight.

### 2.5 Basho Selector Redesign

The method of selecting a basho should be redesigned.

The selected implementation treats this as a PA-specific Basho Results control
inside the existing `FilterSection`, not as a general new `FilterSection` layout
model.

The implemented control shape is:

```text
Basho
    Year  <year dropdown>
    Month <month dropdown>
    <<  <  >  >>
```

The Year and Month rows are indented under `Basho`; their dropdown left edges are
aligned. The button row is indented with the same Basho sub-control block.

The Month dropdown contains only the six sumo months:

```text
January, March, May, July, September, November
```

The navigation buttons have the usual semantics:

- `<<` moves to the first available indexed basho;
- `<` moves to the previous available indexed basho;
- `>` moves to the next available indexed basho;
- `>>` moves to the last available indexed basho;
- attempts to move beyond either end are ignored.

The displayed basho changes whenever the user changes a dropdown or clicks a
navigation button. The semantics of such a change are to show the same public
page for a different date/basho state.

If the user chooses a supported year and one of the six sumo months for which
there are no results, the content panel says:

```text
There was no basho in MMMM YYYY
```

No-basho states are not intended as an important UX feature. They exist so the
code does not crash when a valid sumo calendar slot has no indexed basho.

The canonical public URL shape is:

```text
?page=basho_results_browser&year=YYYY&month=MM&division=makuuchi
```

Legacy `basho=YYYYMM` and `basho_date=YYYYMM` inputs may be accepted and
canonicalized, but public state should prefer `year` and `month`.

Bad URLs are separate from no-basho states. For now, bad URLs show the JS message
`Bad URL` and navigate/replace to the same target as clicking `Home`. A richer
bad-URL handler is still TBD.

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
