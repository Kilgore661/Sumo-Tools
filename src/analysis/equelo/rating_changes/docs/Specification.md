# Rating Changes Specification

## 1. Page identity

The public page is named **Rating Changes**.

The page shows rikishi ranked by Equelo rating movement over a selected trailing basho window ending at the latest represented basho.

The first version does not include a public basho/date selector.

## 2. User-facing question

The primary question is:

> Who gained or lost the most Equelo over the selected window?

The primary statistic is raw rating change:

```text
delta = rating_at_end - rating_at_start
```

Raw `delta` is measured in Equelo rating points and is the default ranking basis.

## 3. Main parameters and projections

The page separates main data parameters from presentation projections.

### Main data parameter

```text
n
```

`n` is the trailing basho window size. Changing `n` selects a different underlying dataset.

Supported values for the first version:

```text
1, 2, 3, 4, 5, 6, 12
```

The target date is fixed to the latest represented basho for the first public version.

### Projection filters

```text
Basis
Normalised
```

Changing these filters must not require a new producer dataset. They alter the visible projection of the selected `n` data.

## 4. Data grain and indexed-source contract

The producer/build path must provide one logical table per supported `n` for the latest represented basho. The important data grain is:

```text
latest represented basho × n
```

For the make_site2 public page, Rating Changes follows the Basho Results-style indexed table pattern. The site build provides an index plus CSV payloads:

```text
current-sumo/rating-changes/data/rating_changes_index.json
current-sumo/rating-changes/data/<payload for n>.csv
```

The exact payload filenames are not semantically important. The index is the contract between the producer/build step and the runtime artifact. Each index entry represents one supported `n` value and must provide enough information for the runtime to select the corresponding CSV payload, including a `payload_path` field.

The CSV payload for a selected `n` must contain enough information to render all projections described below.

## 5. Required row fields

Each row represents one rikishi whose start and end ratings can be compared for the selected window.

The logical row model must provide these values, whether as stored fields or derived bridge fields.

### Context

```text
rikishi_id
shikona
division_id
chii_at_start
chii_ordinal_at_start
chii_at_end
chii_ordinal_at_end
rating_at_start
rating_at_end
delta
```

Display expectations:

```text
rikishi_id
  may be retained for disambiguation/debugging; final display is TBD

shikona
  displayed as the row identity

division_id
  used by the Division filter; it is derived from end-of-window chii and uses the same ids as Banzuke Changes, with `all` handled as a filter value rather than a row value

chii_at_start, chii_at_end
  displayed as rank/chii context
  sorted by ordinal fields

rating_at_start, rating_at_end
  displayed as endpoint rating context

delta
  displayed prominently
  default sort descending
```

### Expected basis

```text
expected_bouts
delta_per_expected_bout
normalised_delta_per_expected_bout
```

Definitions:

```text
expected_bouts
  sum of expected/possible bouts across the n-basho window
  15 for sekitori basho
  7 otherwise
  excludes the start baseline basho
  includes intervening basho and the target basho

delta_per_expected_bout
  delta / expected_bouts

normalised_delta_per_expected_bout
  K-normalised total / expected_bouts
```

### Actual basis

```text
actual_bouts
delta_per_actual_bout
normalised_delta_per_actual_bout
```

Definitions:

```text
actual_bouts
  count of rated bouts actually included in the n-basho window

delta_per_actual_bout
  delta / actual_bouts

normalised_delta_per_actual_bout
  K-normalised total / actual_bouts
```

Rows with zero actual bouts should not produce divide-by-zero display values. The final implementation may omit those rows, display blanks for actual-basis derived values, or handle them explicitly in the bridge. This is a design detail, but the behaviour must be deterministic.

## 6. K-normalised total

For each rated bout, the Equelo update for a rikishi has the form:

```text
rating_delta = K * (actual - expected)
```

The K-normalised bout contribution is:

```text
rating_delta / K = actual - expected
```

The K-normalised total over a window is:

```text
sum(actual - expected)
```

This can be read approximately as wins above/below Equelo expectation. Positive values mean the rikishi did better than Equelo expected; negative values mean worse.

This quantity is not the main public statistic. It exists to support the Normalised projection.

## 7. Table structure

The rendered table has two heading levels.

Top-level groups:

```text
Context
Expected
Actual
```

Context is always visible.

Expected and Actual groups are projected according to the Basis filter.

Within Expected and Actual, raw per-bout columns are visible by default. K-normalised columns are controlled by the Normalised filter.

## 8. Filter behaviour

### n

Type:

```text
fixed mutually exclusive selector
```

Changing `n` selects a different data table.

### Basis

Type:

```text
mutually exclusive selector with combined option
```

Values:

```text
Expected
Actual
Both
```

Default:

```text
Expected
```

Projection:

```text
Expected
  Context + Expected

Actual
  Context + Actual

Both
  Context + Expected + Actual
```

### Normalised

Type:

```text
checkbox
```

Default:

```text
unchecked
```

Projection:

```text
unchecked
  show raw per-bout columns for the selected Basis groups

checked
  show raw per-bout columns and K-normalised per-bout columns for the selected Basis groups
```

This specification chooses “add columns” for the first version. A later design may replace this with a different projection if the table becomes too wide.

## 9. Sorting

Default sort:

```text
delta descending
```

All visible numeric columns should be sortable.

Chii/rank display columns sort by their ordinal fields:

```text
chii_at_start -> chii_ordinal_at_start
chii_at_end   -> chii_ordinal_at_end
```

Headings are centred. Value alignment follows the site table alignment policy:

```text
strings that evaluate to numbers: right-aligned
special non-numerical values: centred
everything else: left-aligned
```

## 10. Notes and popovers

The page should have explanatory notes for:

```text
delta
Basis: Expected versus Actual
Normalised / K-normalised values
```

Minimum explanations:

```text
delta
  Equelo rating points gained or lost over the selected window.

Expected basis
  Measures change against all possible/expected bouts in the window.

Actual basis
  Measures change only against bouts actually fought.

K-normalised values
  Divide each bout's rating movement by the K-factor used for that bout.
  This approximately measures performance above or below Equelo expectation.
```

The exact public labels and note text are not fixed here.

## 11. Architectural pattern

The page should follow the UI-model-based pattern used by `make_site2`.

The closest pattern is `page=basho_results_browser`:

```text
producer/build output is flat or simple static data
runtime bridge maps raw rows into a presentation model
projection filters control visible terminal columns
the renderer displays a grouped, multi-heading table
```

Rating Changes differs from Basho Results Browser in the first version because:

```text
there is no public basho selector
the only main data selector is n
the table is smaller and has fewer projection axes
```

## 12. Deferred items

```text
- Historical basho selector and the cost/value of generating all `(date, n)` datasets.
- Fusen-sho/fusen-pai treatment.
- Final public labels for K-normalised measures.
- Whether Normalised should add columns or switch the displayed measure.
- Whether to include rikishi_id in the public table.
- A separate winning/losing streak table.
```
