# Rating Changes Requirements

## Status of the prototype

The existing `rating_changes` code is a prototype. It was written to make the problem concrete, generate sample tables, and expose design questions. It is not a source of truth for the public artifact.

These requirements, and the specification/design documents that follow them, take precedence over the prototype. During requirements, specification, and design work, the prototype should normally be left alone. Production code should be written after the design is settled. Prototype code may be reused only if it turns out to match the final design closely enough to justify reuse.

This document therefore describes what the page should deliver, not what the current exploratory implementation happens to do.

## Purpose

The Rating Changes page helps readers identify rikishi whose Equelo ratings have changed most over a recent trailing-basho window.

The primary question is:

> Who gained or lost the most Equelo over the selected window?

The go-to statistic is the raw rating change, `delta`:

```text
delta = rating_at_end - rating_at_start
```

The page is about rating movement, not banzuke/rank movement. Rank/chii values provide context only.

## Non-goals

Rating Changes is not a winning-streak table. It does not require the rikishi's rating to have moved in the same direction in every basho in the window.

A separate winning/losing streak artifact may be designed later. That artifact would answer a different question: whose rating has been moving consecutively in one direction?

## Window definition

For a target basho date `T` and a window size `n`, the n-change is:

```text
rating at end of target basho T
minus
rating at end of the nth previous basho before T
```

For example, with target date `2026-05`:

```text
n = 1: end of 2026-05 minus end of 2026-03
n = 2: end of 2026-05 minus end of 2026-01
```

The first public version uses the latest represented basho as the target date. It does not include a public basho/date selector.

The intended public `n` values are a small fixed set, currently:

```text
1, 2, 3, 4, 5, 6, 12
```

The exact literals may change, but the page should be designed around a fixed selector, not arbitrary user input.

## Public data requirements

For each supported `n`, the page needs data sufficient to show one row per rikishi with:

```text
identity/context
rating at the start and end of the window
rating change over the window
expected-bout exposure over the window
actual-bout exposure over the window
rating change per expected bout
rating change per actual bout
optional K-normalised per-bout measures
```

The public page only needs latest-basho data in the first version. Generating historical `(date, n)` datasets for every represented basho is deferred.

Changing `n` changes the underlying dataset. Changing presentation filters such as Basis or Normalised should not require a different dataset; those filters project different columns or column groups from the same selected `n` data.

## Context values

Each row should identify the rikishi and the window endpoints:

```text
rikishi id
shikona
chii/rank at start
chii/rank at end
rating at start
rating at end
delta
```

The chii/rank values should be sortable by their ordinal values, but the ordinal values are not themselves reader-facing context.

`delta` is measured in Equelo rating points and remains the primary public measure.

## Expected-bout basis

The Expected basis measures change against the full opportunity window.

Expected bouts are counted by basho/division status:

```text
15 for sekitori basho
7 otherwise
```

The start baseline basho is excluded from the expected-bout sum. The target basho and all intervening basho are included.

The Expected basis should support:

```text
expected bouts
delta per expected bout
optional K-normalised value per expected bout
```

This is the preferred default basis because it avoids over-emphasising rikishi with very few actual bouts.

## Actual-bout basis

The Actual basis measures change against bouts actually fought.

The Actual basis should support:

```text
actual bouts
delta per actual bout
optional K-normalised value per actual bout
```

This basis may be useful to readers who care about performance intensity in bouts that actually happened. It is less suitable as the default because low-bout cases can be noisy or misleading.

## K-normalised measures

Equelo rating updates are division-sensitive because the K-factor varies by division/chii. A raw rating-point change in a high-K division and the same raw rating-point change in a low-K division do not have the same interpretation.

For one rated bout, the update has the form:

```text
rating_delta = K * (actual - expected)
```

Dividing by the K used for that rikishi in that bout gives:

```text
rating_delta / K = actual - expected
```

Across a window, the K-normalised total is therefore the sum of `actual - expected` over rated bouts. It is approximately wins above/below Equelo expectation.

This is analytically useful but harder to explain than raw `delta`. It should be available as an optional/advanced presentation, not as the main default statistic.

## Public filters

The page should provide these public controls.

### n

A fixed selector for the trailing basho window.

Changing `n` changes the selected dataset.

### Basis

A mutually exclusive selector with an optional combined view:

```text
Expected
Actual
Both
```

Default:

```text
Expected
```

Meaning:

```text
Expected
  show measures based on possible/expected bouts in the full window

Actual
  show measures based on bouts actually fought

Both
  show both groups side by side
```

### Normalised

A checkbox.

Default:

```text
unchecked
```

When unchecked, the page shows raw rating-point measures. When checked, it also shows or otherwise exposes K-normalised per-bout measures for the selected Basis. The exact projection behaviour may be finalised in the specification/design stage.

## Rendered table shape

The data may be flat, but the rendered page should present a grouped table. The intended top-level column groups are:

```text
Context
Expected
Actual
```

Context should always be visible. Expected and Actual are shown according to the Basis filter. K-normalised columns are controlled by the Normalised filter.

The page should follow the UI-model-based approach used elsewhere in `make_site2`, especially the Basho Results Browser pattern: raw data is transformed by a bridge/projection layer into the table model required by the renderer.

## Sorting expectations

The default sort should support the primary question of the page: biggest gainers first by raw `delta`.

Readers should be able to sort by visible numeric measures. Chii/rank columns should sort by their ordinal values rather than by display string.

A later design may decide whether there should be a direct way to switch between gainers and losers, or whether ordinary table sorting is sufficient.

## Notes and explanatory text

The page will need explanatory notes/popovers for at least:

```text
delta
Expected versus Actual basis
K-normalised values
```

The notes should make clear that raw `delta` is the main public statistic, while K-normalised values are interpretive measures that account for division-dependent K-factors.

Fusen-sho and fusen-pai may require explanation or special treatment later, but they are out of scope for the first requirement pass.

## Deferred questions

```text
- Whether fusen-sho and fusen-pai require special treatment.
- Final public labels for per-bout and K-normalised measures.
- Whether Normalised should add columns, replace columns, or open an advanced projection.
- Whether table sorting alone is enough for losing changes, or whether a separate gain/loss control is needed.
- Whether a final publication build should generate historical `(date, n)` datasets for all represented basho.
- Whether a separate winning/losing streak table should be added later.
```
