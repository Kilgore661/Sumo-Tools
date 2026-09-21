# UI Requirements - Fastest and Slowest Progression

## Purpose

The artifact lets a reader compare how quickly rikishi progressed from one
starting rank group to a higher rank group. It presents a historical ranking,
not a prediction and not a comparison between unlike starting cohorts.

The page consumes precomputed output from the `analysis.fastest` producer. The
first implementation deliberately uses the current `make_site89` historical
scope rather than waiting for the wider production architecture to be revised.

The public identity is:

```text
page id:    fastest_risers
menu label: Fastest risers
page title: Fastest and Slowest Risers
summary:    Rikishi ranked by the number of basho taken to progress between selected rank groups.
```

The menu item belongs in **Records**, immediately after **Longest careers**.

## Rank groups

The ordered groups are:

```text
Jk, Jd, Sd, Ms, J, M, KS, O, Y
```

Their display labels are Jonokuchi, Jonidan, Sandanme, Makushita, Juryo,
Maegashira, Komusubi/Sekiwake, Ozeki, and Yokozuna. `M` means Maegashira only;
`KS` combines Komusubi and Sekiwake while the table retains the exact chii.

Each rikishi belongs to the cohort defined by the first rank group in which he
appeared on the represented banzuke History. The page does not adjust for the
exact starting rank within that group. Boundary incumbents first observed on
the supporting epoch banzuke are excluded from cohorts and rankings.

## Historical scope and proof-of-concept epoch

The analytically obvious requirement is to use the complete banzuke History:
`1958/01` as the supporting boundary and `1958/03` as the first eligible
starting banzuke. Promotions do not depend on ratings, so the Elo epoch does
not create a data requirement for this artifact.

That requirement is deliberately not implemented in the proof of concept.
The current `make_site89` production path consistently gives its artifact
producers History beginning at `1989/01`, even when an artifact is not
rating-dependent. Correcting that architecture would expand this work beyond
the progression artifact.

The producer therefore exposes an explicit CLI epoch and defaults it to
`1989/01`. That banzuke is supporting boundary data only: everyone already on
it is excluded from starter cohorts. The first eligible starters appear on
`1989/03`, and their subsequent progress is followed through the latest
represented banzuke.

This makes the first website version a proof of concept covering post-boundary
entrants, not a complete historical answer. The page must disclose that its
cohorts begin with first appearances from `1989/03`. A later architectural
repair can run the same parameterised producer at `1958/01` without changing
the UI contract.

## Controls

The page has five controls.

### Starting division

Radio buttons choose the starting cohort. Their order follows rank-group order
from lowest to highest. The default is Jonokuchi (`Jk`). Only groups for which
the produced data contains a valid starting cohort appear.

Under the `1989/01` proof-of-concept epoch the represented starting cohorts are
`Jk`, `Sd`, and `Ms`; there are no Jd starters. A future `1958/01` production
may add `Jd` automatically if the produced routes contain that cohort.

### Division of interest

A select control chooses the destination group. Its default on initial page
load is Maegashira (`M`). The available choices must be dynamically restricted
to groups higher than the selected starting group and supported by a produced
route. It remains a dropdown regardless of the number of choices. If a
starting-group change leaves the current destination valid, retain it. If not,
select `M` when it is valid and otherwise select the first valid higher group.

A produced route remains selectable when its reached count is zero. Such a
selection presents the cohort count and an empty-result explanation rather
than silently removing a meaningful negative result.

### Direction

Radio buttons choose `Fastest` or `Slowest`. The default is `Fastest`.

The choice selects the corresponding producer-supplied position. Equal elapsed
times do not share positions; the producer's deterministic secondary ordering
is authoritative.

### Ranking range

A select control labelled **Ranking range** offers:

```text
Top 10
Top 20
Top 50
All
```

The default is `Top 10`. `All` makes the complete qualifying population
available, including for browser text search for a particular rikishi.

### Retired-rikishi filter

An unchecked checkbox is labelled **Hide retired rikishi**. Its help text is:

> Filters the selected ranking range. Positions are not recalculated and the
> table is not refilled.

This deliberately differs from the `Active Rikishi Only` control on
`standings_by_wins`. That page restricts the population before ranking. This
artifact first selects a range from the complete historical ranking and then
optionally hides retired rikishi within that range.

For example, if only six members of the historical top 50 are active, checking
the box displays those six with their original positions. It does not add
rikishi from positions 51 onward or renumber the visible rows from 1 to 6.

## Selection and filtering order

The UI must apply state in this order:

1. select the route identified by starting and destination groups;
2. order the complete route by fastest or slowest position;
3. take the first 10, 20, 50, or all records;
4. when requested, hide records whose producer-supplied `active` value is
   false.

Changing controls must not cause the browser to recalculate elapsed basho,
positions, cohort membership, or active status.

## Table

The table uses the following grouped structure:

```text
#
Shikona
Start
    Chii
    Basho
Destination
    Chii
    Basho
Elapsed Basho
```

`#` is the producer-supplied fastest or slowest historical position. Shikona
uses the stable rikishi ID to provide the site's standard rikishi link.

Chii display values come from the producer unchanged, including annotations
such as `TD`. Their adjacent ordinals are sorting keys and need not be visible.
The position column always shows the selected complete historical ranking
position, including when retired rikishi are hidden.

The default table sort is historical position ascending. Position, Shikona,
both Chii values, both Basho dates, and Elapsed Basho are sortable. Range
selection and retired-rikishi hiding occur before any user-selected table sort.
Sorting only reorders the visible rows and never recalculates `#`.

## Heading and cohort context

The dynamic table heading uses this template:

> Fastest promotions from Makushita to Maegashira

`Fastest` changes to `Slowest` with the direction control, and the two rank
group labels change with the selected route.

The subtitle carries the relevant cohort context rather than adding another UI
control. With no retired-rikishi filter it should state how many records are
shown, how many members of the cohort reached the destination, and the total
number of starters, for example:

> Showing 20 of 54 rikishi who reached Maegashira, from 85 Makushita starters.

When retired rikishi are hidden, it must make the post-range filtering explicit,
for example:

> Showing 10 active rikishi among the first 50 of 54 who reached Maegashira,
> from 85 Makushita starters.

The cohort totals remain those of the complete historical route. The filter
does not turn them into active-only cohort statistics.

For `All`, replace “the first N” with “all N”. When the selected route has no
achievers, the table body says, for example:

> No Sandanme starters reached Yokozuna in the represented History.

The subtitle still reports `0` reached from the complete starter cohort.

## URL state and recovery

The page uses these URL-backed state fields:

| State | URL key | Default |
|---|---|---|
| Starting division | `start` | `Jk` |
| Destination | `finish` | `M` |
| Direction | `direction` | `fastest` |
| Ranking range | `range` | `10` |
| Hide retired rikishi | `hide_retired` | `false` |

An unavailable starting group falls back to `Jk`, or to the first produced
starting cohort if `Jk` is unavailable. Destination recovery follows the rule
defined under Division of interest. Invalid direction, range, and boolean
values fall back to their declared defaults. The canonical repaired state is
written back to the URL.

## Notes and disclosure

The artifact Notes must communicate:

1. **Elapsed basho.** Elapsed Basho is the difference between the represented
   banzuke ordinals of the first destination appearance and the starting
   appearance. The starting basho is not counted; the immediately following
   represented banzuke is one basho later.
2. **Starting cohort.** A rikishi's cohort is the rank group of his first
   appearance after the supporting boundary. Exact starting rank is retained
   but does not create a separate cohort.
3. **Historical scope.** This proof of concept uses `1989/01` as supporting
   boundary data, excludes rikishi already present there, and admits first
   appearances from `1989/03`. This is a temporary `make_site89` production
   constraint, not a ratings requirement.
4. **Available starting divisions.** Starting choices are derived from first
   banzuke appearances after the supporting boundary. No eligible rikishi
   first appeared in Jd, so Jd is not offered as a starting division; it
   remains available as a destination for Jk starters.
5. **Top-division groups.** `M` means Maegashira only. `KS` is the first
   appearance at either Komusubi or Sekiwake. Exact chii and annotations remain
   visible in the table.
6. **Equal elapsed times.** Equal elapsed values receive consecutive positions
   using the producer's deterministic secondary ordering; positions are not
   shared.

## Producer contract required by this UI

For every valid route, the UI requires:

- starting and destination group identifiers;
- starter, reached, and not-reached counts;
- every qualifying record, without a producer-side display cutoff;
- consecutive fastest and slowest positions;
- stable rikishi ID and publication shikona;
- exact starting and destination chii, their ordinals, and their dates;
- elapsed basho and the underlying basho ordinals; and
- `active`, true exactly when the rikishi appears on the latest represented
  banzuke.

The producer supplies this contract. Its `active` field completes the data
required by this UI without requiring a separate active-only ranking.

The published source path is:

```text
sumo-history/records/fastest-risers/data/rankings.json
```

Only `rankings.json` is published with the site. The milestone matrix and
missing-bio audit remain producer-side diagnostic outputs.

## Explicitly deferred

This version has no control for exact starting rank, starting year or era,
tsukedashi status, or alternative treatment of incomplete careers. It does not
compare speed across different starting cohorts. It also does not implement a
free-text search control; selecting `All` permits ordinary browser search.

Website code, manifest declarations, styling, navigation, and build integration
are outside this requirements step.

The intended implementation strategy, including the decision to keep the
specialised interaction local rather than generalise the shared page model, is
recorded in `Implementation Approach - Fastest Risers Site Artifact.md`.
