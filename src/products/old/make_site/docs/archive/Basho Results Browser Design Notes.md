# Basho Results Browser Design Notes

## Status

Working draft for the proposed Basho Results Browser (BRB).

This is not yet a final specification.  It records the current alignment on
page shape, options, table behaviour, and interpretive notes before
implementation work begins.

## Placement

BRB belongs under:

```text
Sumo History
  Basho Results
```

It should become item `7.1` in that section, with later Sumo History items
renumbered accordingly.

## Current Rating Source

BRB should use `fixed_v2` as its Equelo source.

In practical terms:

* row-level rikishi ratings come from fixed_v2 process-rating artefacts;
* start/end basho lookups should be derived from fixed_v2 day-end ratings and
  fixed_v2 entrant initial ratings;
* `Typical Equelo Ratings` are public landmarks for reading the scale, not
  lookup values for individual rikishi rows;
* fixed_v1/Brier-compressed ratings are historical diagnostic context only.

This post-Brier policy is repeated in the rating-column section where it affects
specific calculations, but this is the headline rule for implementation.

## Page Shape

The page uses the standard site tool layout:

```text
title bar
options panel | table/content panel
```

The table is one row per rikishi.  BRB is not a banzuke-style east/west paired
table by default.

The starting point is conceptually close to Banzuke Changes in one-column mode,
but BRB is a new feature rather than a direct date-selector wrapper around
Banzuke Changes.

## Date Selector

The selected basho date is first-class page state.

The date control is a single row of four widgets:

```text
[previous basho] [year] [month] [next basho]
```

Rules:

* the canonical state is a valid basho date/index, not independent year/month
  values;
* the year dropdown lists valid history years in descending order;
* the month dropdown lists valid months for the selected year, displayed as
  full month names;
* previous/next buttons step through valid basho only;
* previous/next buttons are hidden at the relevant history endpoints;
* missing basho, currently `2022/03` and `2011/05`, are skipped by navigation;
* if a year change makes the current month unavailable, choose the nearest
  valid month in that year.

## Options

BRB carries over Banzuke Changes-style controls where they still make sense,
except for Banzuke Style.  Banzuke Style is not an option because BRB is
one-column by design.

Known option families:

* date selector;
* division selector;
* previous-basho context, if included;
* Equelo/rating context, where included;
* column group visibility;
* individual column visibility within groups;
* Reading Guide visibility.

Column group controls:

* meaningful column groups can be shown/hidden as groups;
* individual columns can also be shown/hidden;
* when a group is hidden, its individual controls are visually muted/disabled
  but retain their state;
* turning the group back on restores the previous individual choices;
* Shikona and Score are always shown;
* row number, if present, is not sortable and is not treated as a data column.

Defaults remain undecided.

## Table Title

Initial title shape:

```text
{division} Standings by {sort column} {after/during} {MMMM} {YYYY} Basho
```

The exact words may differ between final historical and live/current modes.

For a purely historical completed-basho view, "Results" may be clearer than
"Standings".  For a live/current-basho view, "Standings" may remain the better
word.

## Table Structure

Initial column group concept:

```text
row number | Shikona | Before | Score | After/Current
```

The table uses a two-row column header where column groups are present.

Long headings should use human-readable words with centred line breaks rather
than implementation-style identifiers.  For example, use "After Basho Chii",
not `after_basho_chii`.

### Before

Potential columns:

* Chii;
* Equelo;
* `muE`;
* `piE`;
* `DeltaBZ`;
* `nuChii`;
* `mu`.

### Score

Always visible.

Display as:

```text
wins-losses
wins-losses-absences
```

Use the latter only when absences are non-zero.

### After/Current

Potential columns:

* `DeltaEquelo`;
* `nuEquelo`;
* Chii;
* `DeltaChii`.

The provenance of After/Current values is page-level state, not repeated on
each data row.  For example:

```text
view_state = final | live
after_chii_kind = actual_next_banzuke | projected | unavailable
```

The table header should reflect this page-level state honestly.

## Table Behaviour

BRB should combine the strongest existing table behaviours:

* Standings for sorting, URL state, and back/forward behaviour;
* Banzuke Changes for column toggles, option-sensitive notes, validation, and
  one-column rendering;
* Career Length -> Longest for in-panel scrolling with sticky headers.

Required behaviours:

* meaningful columns are sortable;
* repeated header click toggles sort direction;
* sort direction indicators are visible;
* chii sorts by ordinal, not alphabetically;
* row number is not sortable;
* hidden active-sort columns need a defined fallback policy;
* table state is reflected in shareable URL state;
* browser back/forward restores state;
* table scrolls inside the content panel with sticky column headers;
* browser-side config/data validation happens before rendering;
* shikona links use the site convention: normal click opens SumoDB, Alt-click
  opens the Gaspode-san graph endpoint.

## Rating Columns

In BRB, legacy "Elo" wording usually means current Equelo.

BRB should use actual fixed_v2 process ratings for individual rikishi.  These
are historical, bout-derived ratings at a represented point in the basho
timeline.

`Typical Equelo Ratings` values are illustrative landmarks only.  They help a
reader understand the approximate public rating scale associated with chii-like
labels, but they must not be used as lookup values for:

* an individual rikishi's rating;
* deserved chii;
* `DeltaBZ`;
* `nuChii`;
* `DeltaChii`;
* any other BRB row calculation.

This distinction matters because actual rikishi ratings need not be monotone
with banzuke order.  A rikishi at `M16` can have a higher actual Equelo rating
than a rikishi at `M12`; that is model information, not a data error.  The
monotone `Typical Equelo Ratings` table is a reading aid, not a rule that
historical individual ratings are expected to obey.

The first implementation should validate this distinction empirically by
comparing actual fixed_v2 process ratings against the illustrative landmarks
for matching/current chii.  The purpose is to understand the spread and decide
whether the public wording needs stronger caveats.

> Updated 2026-05-12: fixed_v2 supersedes fixed_v1 for BRB planning.  The
> Brier compression step is now treated as a historical/diagnostic comparison,
> not as part of the current public/process rating scale.  The current goal is
> that process ratings and `Typical Equelo Ratings` landmarks live on the same
> broad scale, while retaining the rule that landmarks are illustrative and not
> row-level lookup values.

### `muE`

`muE` is the average Equelo-implied win probability for a rikishi against every
other rikishi in the same division.

For division `D` and rikishi `r`:

```text
muE(r) = (1 / (|D| - 1)) * sum p(r beats s)
```

where the sum ranges over every `s` in `D` except `r`.

### `piE`

The old Elo-era explanation of `piE` as a response to drifting rating mass is
not appropriate for fixed_v2 Equelo.

The statistic may still be useful as a relative reading aid:

```text
piE(r) = Equelo(r) / mean Equelo(D)
```

Read it as Equelo relative to the divisional average at the same rating point.

### `DeltaBZ`

`DeltaBZ` compares banzuke order with Equelo order.

One working definition:

```text
DeltaBZ = banzuke_position - equelo_position
```

The Equelo position is the rikishi's ordinal position within the selected
division after sorting actual fixed_v2 process ratings, not the position
obtained by inverting the `Typical Equelo Ratings` landmark curve.

Display examples:

* `2 down` means the rikishi is two banzuke slots higher than their Equelo
  order suggests;
* `4 up` means the rikishi is four banzuke slots lower than their Equelo order
  suggests.

The public display may use arrows and colour, but the note should make clear
that this is model context, not an official banzuke error.

Small values may be unimportant because banzuke structure, protected ranks,
slot availability, and ranking conventions all complicate the comparison.
Larger values are more meaningful.

### `nuChii`

`nuChii` uses Greek nu, read "new Chii".

It is the chii implied by applying `DeltaBZ` to the current banzuke ordering:
find the occupied banzuke slot corresponding to the rikishi's within-division
Equelo order, then use the chii currently occupying that slot.

This is a virtual/new chii, not a banzuke prediction.  It assumes the current
banzuke shape as a fixed slot structure and is most meaningful below ozeki,
where exceptional promotion and rank-protection rules matter less.

### `DeltaChii`

`DeltaChii` is blank until the next banzuke is known.

Once known, it measures movement in occupied banzuke slots, not rank numbers.
For example, `M1e -> M1w -> M2e -> M2w` is three slot-steps.  A movement of
`8 down` is roughly four numbered maegashira ranks.

This is only a rough guide because chii labels do not correspond to fixed
absolute banzuke positions across all basho.  A chii can stay the same while
its absolute banzuke position changes, and a chii can change while the
underlying position changes less than the label suggests.

The same caveat applies to `DeltaBZ`.

## Reading Guide and Notes

BRB needs more explanation than earlier one-line notes can comfortably carry.

The note model remains simple:

* column heading popovers link to short one-line notes;
* option-sensitive notes can be shown or hidden according to visible columns.

The longer explanation is a separate Reading Guide, not part of the note model.

Reading Guide behaviour:

* controlled by a "Reading Guide" or "Show Reading Guide" option;
* off by default;
* when enabled, the guide appears between the table and the notes;
* enabling it scrolls/jumps the content to the guide;
* the Reading Guide state should participate in shareable URL state.

The guide should explain the table's shared mental model once, including:

* banzuke rows, half-rows, and slots;
* slot-based movement values;
* Equelo-derived context vs official banzuke facts;
* why `DeltaBZ`, `nuChii`, and `DeltaChii` are rough guides;
* how actual and projected After/Current values should be read.

Column notes should remain short and punchy.

## Open Design Questions

* Which proposed columns belong in v1?
* Which columns have data to hand, which need modest joining/work, and which
  need new analysis code?
* Should the first implementation be historical-only, with live/current mode
  added later?
* What exact fallback should apply when changing options hides the active sort
  column?
* Should column group show/hide controls include "show all" and "hide all"?
* What are the initial defaults for division, visible column groups, and sort?

## Python Implementation Gap

This section records what Python/data-production work appears to be needed for
BRB.

### Equelo Basho Lookup

The most obvious missing support layer is a lookup table/API for fixed_v2
Equelo rating at the start and end of a basho:

```text
start_rating(date, rikishi_id, chii)
end_rating(date, rikishi_id)
```

The current fixed_v2 persisted artefact is day-end only:

```text
files/output/Equelo/fixed_v2/day_end_ratings.json
files/output/Equelo/fixed_v2/entrant_initial_ratings.json
```

The simulator produces `basho_start_ratings` in memory, but fixed_v2 does not
persist those snapshots.  The fixed_v2 approach inherits the policy that the first
implementation should not persist basho-start ratings separately; consumers
that need before-day values should derive them from the previous represented
rating point while walking the timeline.

BRB therefore needs a small rating access layer.  A working policy:

* `end_rating(date, rikishi_id)` is the selected basho's last day-end rating;
* `start_rating(date, rikishi_id, chii)` is the previous basho's last day-end
  rating if the rikishi has one;
* if there is no previous rating for the rikishi, use the fixed_v2 entrant
  initial rating for the selected basho chii;
* for the earliest represented basho, all start ratings come from entrant
  initial ratings;
* a later live/current mode can add `current_rating(date, day, rikishi_id)`.

This can start as BRB-local code, but it may deserve promotion to a fixed_v2
consumer API if another page needs the same lookup.

### Data Available Directly

These fields are available from `History` or existing helper code:

* selected basho banzuke membership;
* `rikishi_id`;
* shikona;
* starting chii;
* chii ordinal;
* division;
* final score as wins-losses or wins-losses-absences;
* prize suffixes where wanted;
* date list from sorted `History` keys.

Relevant existing code:

* Banzuke Changes result formatting computes records and prize suffixes;
* Banzuke Changes has division labels/order;
* Banzuke Changes has the current graph-shikona wrapper;
* standings code already computes rolling win averages over selected basho
  windows.

### Data Requiring Joins or Adaptation

These appear to need modest joining/adaptation rather than a new research
model:

* start Equelo, via the new Equelo basho lookup;
* end/current Equelo, via fixed_v2 day-end ratings;
* `DeltaEquelo`, as end/current minus start;
* `piE`, as Equelo divided by divisional mean Equelo at the chosen rating
  point;
* `muE`, as the average Equelo-implied win probability against other rikishi in
  the selected division;
* `mu`, as average wins over the previous up-to-six basho window;
* after/next chii, by joining the next known banzuke when it exists;
* `DeltaChii`, once a slot-position helper exists.

### New BRB-Specific Code

BRB likely needs a new module under:

```text
src/analysis/sumo_history/basho_results/
```

Candidate files:

```text
__init__.py
classes.py
dates.py
records.py
ratings.py
slots.py
build.py
reports.py
cli.py
```

Likely responsibilities:

* define BRB row/config/output dataclasses;
* build the available-basho date index;
* compute one basho's result rows;
* compute all basho bundles for the static site;
* write browser-ready CSV/JSON;
* write page/config metadata for date controls, column groups, column labels,
  sort keys, notes, and defaults;
* provide banzuke slot ordering helpers;
* compute banzuke position by rikishi;
* compute Equelo order by division;
* compute `DeltaBZ`;
* compute `nuChii`;
* compute `DeltaChii`;
* apply boundary policy for virtual/new chii above the top or below the bottom
  of the selected slot list.

### Static Data Size

BRB may need to publish data for every represented basho, currently about 407
basho.

The static data strategy remains open:

* one CSV/JSON per basho;
* grouped files by year or era;
* a single large file plus an index;
* a page config/index file plus lazy-loaded per-basho files.

The date selector design does not require this decision immediately, but the
producer should make the chosen strategy explicit.
