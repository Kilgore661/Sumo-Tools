# Banzuke Display Specification

## Status

First settled draft.

This document specifies the first useful display for banzuke news: a
traditional east/west banzuke table enriched with previous-basho context and a
local movement delta.

## 1. Purpose

When a new banzuke is published, the display should remain recognisably a
banzuke while making the changes explainable at a glance.

It should answer:

- where is this rikishi now?
- where were they last basho?
- what was their previous score?
- did they move up or down?
- was the move small or large within this banzuke comparison?

The display is not intended to solve all banzuke-news questions. It is the
baseline view from which more specialised news sections can grow.

## 2. Core Shape

The base display is divisional and east/west:

```text
east        bz_chii   west
Fred        Y1        Bill
Tony        O1        Helen
Jane        O2
Ken         S1        Tina
...
```

The display is built one division at a time.

The centre row heading is called `bz_chii`. Examples:

```text
Y1
O2
M13
J5
Jk24
M3HD
```

`bz_chii` is not a `Chii` in the core model. A true `Chii` includes side and
annotation information, for example `Y1e`, `Y1w`, or `M3wHD`.

Definition:

```text
bz_chii = full Chii display string with side removed and annotation preserved
```

Examples:

```text
M3e   -> M3
M3w   -> M3
M3eHD -> M3HD
M3wHD -> M3HD
```

Rows may have a blank east side or a blank west side. Since displayed `bz_chii`
values come from the banzuke data being shown, a row should never have both
sides blank.

## 3. Annotated Rows

Annotated chii are displayed as distinct `bz_chii` row headings.

For example, if an exceptional banzuke contains three M3 rikishi:

```text
east      bz_chii   west
Fred      M3        Bill
          M3HD      Mike
```

or equivalently:

```text
east      bz_chii   west
Fred      M3        Bill
Mike      M3HD
```

Both are valid. The populated side depends on the actual full `Chii` in the
current banzuke.

Ordering follows the existing `Chii` ordering. The current model gives lower
ordinals to better ranks, and treats annotated chii as lower-ranked than the
same unannotated chii. The ordering among different non-empty annotations is
arbitrary but accepted for display purposes because it does not normally carry
material meaning.

## 4. Enriched Display

The first enriched display adds previous-basho context on each side of the
central `bz_chii` column.

Conceptual columns:

```text
east shikona | east old chii | east previous score/prizes | east Δ |
bz_chii |
west Δ | west previous score/prizes | west old chii | west shikona
```

The display column header for delta should be the capital Greek delta:

```text
Δ
```

In HTML output, this may be written as `&Delta;` if that is clearer for the
renderer.

Example:

```text
Fred | Y1w | 11-4 J | +0.5 | Y1 | -0.5 | 9-3-3 | Y1e | Bill
```

This means:

- Fred is now on the east side of `Y1`.
- Fred was previously `Y1w`.
- Fred went `11-4 J` in the previous basho.
- Fred's local movement delta is `+0.5`.
- Bill is now on the west side of `Y1`.
- Bill was previously `Y1e`.
- Bill went `9-3-3` in the previous basho.
- Bill's local movement delta is `-0.5`.

Exact column ordering may be adjusted for readability, but `bz_chii` should
remain visually central.

## 5. Required Inputs

The display needs:

```text
previous Banzuke
current Banzuke
previous BashoState.summary
```

The previous and current banzuke provide:

- current `Chii`
- previous `Chii`
- current shikona
- previous shikona, if needed
- entering and exiting rikishi

The previous summary provides the data needed to reconstruct:

- score
- prizes
- absences/defaults/non-participation in the final record

If previous summary data is unavailable, the display should still render the
banzuke and movement columns, with score/prize cells blank or marked
unavailable.

## 6. Building Rows

For each current-banzuke rikishi:

1. Take the current full `Chii`.
2. Derive:
   - side: east or west
   - `bz_chii`: side removed, annotation preserved
3. Look up the rikishi in the previous banzuke.
4. If present, attach previous full `Chii`.
5. If previous summary data is available, attach previous score/prizes.
6. Compute local movement delta if previous full `Chii` exists.

Then group by division and `bz_chii`.

The current banzuke drives the main east/west table. Rikishi who exited the
banzuke are news facts, but they do not naturally fit into the current table and
are deferred to a later entrants/exits section.

## 7. Score And Prize Formatting

The initial score/prize display should be simple:

```text
{score} {prizes}
```

Examples:

```text
11-4 J
10-5 JS
8-6-1
```

Multiple prizes are concatenated without separators, e.g. `JS`, not `J, S` or
`J S`.

Absences should be shown where they occur.

Examples:

```text
8-7
```

means the displayed record covers all 15 days without an absence component.

```text
8-6-1
```

means the displayed record includes one absence/default/non-participation day.

Implementation note: `History.summary` stores daily results and performances,
not a precomputed final score string. The display therefore needs a formatter
that reconstructs final records from `Summary`.

## 8. Local Movement Delta

The initial movement metric is pair-local observed-slot delta.

Algorithm:

1. Form the union of all full `Chii` values occurring in either the previous
   banzuke or the current banzuke.
2. Sort that union by `Chii.ordinal()`.
3. Let `old_index` be the index of the rikishi's previous full `Chii`.
4. Let `new_index` be the index of the rikishi's current full `Chii`.
5. Compute:

```text
delta = (old_index - new_index) / 2
```

Interpretation:

- positive delta: moved up
- negative delta: moved down
- zero delta: same observed slot
- `+0.5`: moved one side upward, e.g. `Y1w -> Y1e`
- `-0.5`: moved one side downward, e.g. `Y1e -> Y1w`

The division by 2 makes east/west side movement half a `bz_chii` row movement
in the traditional display.

## 9. Delta Caveat

This delta is local to one pair of banzuke.

It measures movement through the observed full `Chii` values present in the two
compared banzuke. It does not measure distance through an ideal or historically
complete rank ladder.

Therefore it is useful for:

- colouring this display
- sorting changes within this banzuke pair
- explaining local movement at a glance

It is not suitable for:

- comparing movement magnitudes across arbitrary basho pairs
- historical records such as "largest move ever"
- statistical modelling of promotion/demotion size

Example caveat:

If a later banzuke had no ozeki, sekiwake, or komusubi, then the observed-slot
distance from `Y1w` to `M1e` could compress to `-0.5`, because the intermediate
slots do not exist in that pair's observed union.

This is expected behaviour for the local display metric, not a universal rank
distance.

## 10. Colour Encoding

Delta should be colour-coded:

- green: moved up
- red: moved down
- neutral/no colour: unchanged or unavailable
- pale colour: small move
- saturated colour: large move

Initial saturation bands:

```text
low:  abs(delta) 0.5 to 1.5
mid:  abs(delta) 2.0 to 3.0
high: abs(delta) 3.5 and above
```

The colour scale is based on `abs(delta)` within the current comparison.
Because delta is pair-local, saturation is visual emphasis for this display,
not a historically comparable statistic.

## 11. Deferred Items

The following are deliberately deferred from the first table implementation:

- separate entrants section
- separate exits section
- richer career-high and return stories
- performance-consistency judgement
- historical comparison of movement sizes
- richer treatment of shikona changes
