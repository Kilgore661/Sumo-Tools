# Rating Changes Implementation

## 1. Implementation stance

The production `Rating Changes` implementation should be written from the requirements, specification, and design documents.

The exploratory `src/analysis/equelo/rating_changes` package is not the implementation baseline. It should remain in place as prototype evidence. It may be consulted for algorithmic examples, sanity-check outputs, and metric exploration, but production modules should be new unless a specific piece of prototype code is deliberately reviewed and judged to match the final design.

The implementation should therefore introduce new production names for producer modules, make_site2 wiring, and runtime paths as needed. The exact names are less important than the separation of responsibilities.

## 2. Implementation inventory

The first production implementation is expected to touch these layers:

```text
analysis / producer layer
  production Rating Changes data producer

make_site2 build layer
  data-output step for Rating Changes payloads

make_site2 publication model / manifest layer
  page declaration
  artifact declaration
  filters
  notes

runtime layer
  data-source selection by n
  raw-row to presentation-model bridge
  grouped table specification
  grouped table rendering path
```

This document does not prescribe exact file names. It records the intended integration boundaries so that the eventual code can be reviewed against the UI model rather than against the prototype package.

## 3. Production producer

The producer should emit data at this grain for the first public version:

```text
latest represented basho × n
```

The supported `n` values should be the fixed public selector values from the specification. The producer/build path should provide one logical raw table for each supported `n`.

For the make_site2 implementation, Rating Changes uses the same broad indexed-table source pattern as Basho Results Browser. The build output should include:

```text
current-sumo/rating-changes/data/rating_changes_index.json
current-sumo/rating-changes/data/<payload for n>.csv
```

Each index entry represents one supported `n` value and supplies the CSV `payload_path` that the runtime artifact should load when that `n` is selected. The exact payload filenames are not important so long as the index is correct and stable.

The producer should calculate or provide enough data for the bridge to render:

```text
identity and context
rating endpoints
raw rating delta
expected-bout exposure
actual-bout exposure
raw per-bout measures
K-normalised per-bout measures
sort support for chii/rank fields
```

The production producer should not include streak length in this artifact. Streaks are a separate deferred artifact.

## 4. Metric boundary

The implementation should keep the following metric boundary clear.

Raw rating movement:

```text
delta = rating_at_end - rating_at_start
```

This is the primary public statistic and the default sort measure.

Expected-bout and actual-bout per-bout measures are derived from raw `delta` and the appropriate denominator:

```text
delta_per_expected_bout = delta / expected_bouts
delta_per_actual_bout   = delta / actual_bouts
```

K-normalised measures are derived by dividing each bout's rating movement by the K-factor used for that rikishi in that bout:

```text
rating_delta / K = actual - expected
```

The K-normalised total is useful as an intermediate calculation, but it is not expected to be a main visible public column in the first page. The public projection uses K-normalised per-bout measures when the `Normalised` filter is enabled.

Rows with a zero denominator must be handled deterministically. The bridge may omit derived values, render blanks, or otherwise follow a documented rule, but the renderer should not perform divide-by-zero logic ad hoc.

## 5. Data source selection versus projection

The implementation must preserve the main-parameter/projection distinction.

`n` is a data selector:

```text
changing n loads/selects a different raw table
```

`Basis` and `Normalised` are projection filters:

```text
changing Basis reuses the loaded rows and changes visible column groups
changing Normalised reuses the loaded rows and changes visible terminal columns
```

This distinction should be visible in the runtime code. Data loading should not be intermingled with column projection logic.

## 6. make_site2 page and artifact wiring

The page should be declared as a normal make_site2 page/artifact instance.

Working identity:

```text
page id: rating_changes
title: Rating Changes
```

The artifact should be an indexed table-style artifact with:

```text
index path:
  current-sumo/rating-changes/data/rating_changes_index.json

payload path field:
  payload_path

main data selector:
  n

projection filters:
  Basis
  Normalised

notes:
  delta
  Expected versus Actual basis
  K-normalised / Normalised values
```

The first version should not expose a public basho/date selector. The latest represented basho is part of the producer/build selection, not a reader-facing filter.

## 7. Runtime bridge

The runtime should include a page-specific bridge for Rating Changes, following the Basho Results Browser pattern.

Conceptually:

```text
raw row
  -> presentation row values
  -> projected terminal paths
  -> grouped table renderer
```

The bridge owns:

```text
mapping raw fields to presentation terminals
choosing visible terminal paths from Basis and Normalised state
applying display/sort metadata for chii/rank fields
handling missing or divide-by-zero derived values
```

The renderer should consume the presentation model. It should not know producer field names except through the bridge/table specification.

## 8. Grouped table model

The rendered table has two heading levels.

Top-level groups:

```text
Context
Expected
Actual
```

Context is always visible.

`Basis` controls whether `Expected`, `Actual`, or both groups are visible.

`Division` filters rows by end-of-window division after the selected CSV has loaded. Its values match Banzuke Changes division ids, with `All` appended as an unfiltered option.

`Normalised` controls whether K-normalised per-bout terminal columns are visible inside the selected basis groups.

The table should not be rendered as a generic flat table with hand-written heading hacks. It should be represented as a grouped table model, as far as the current make_site2 UI model allows.

## 9. Relationship to Basho Results Browser

Rating Changes should follow the architecture of `page=basho_results_browser`:

```text
flat/simple producer payload
runtime bridge
presentation table model
projection filters
multi-level headings
renderer
```

It should not copy the Basho Results domain model. In particular, Rating Changes should not inherit domain names such as:

```text
before
selected
changes
record
bp
```

Important differences from Basho Results Browser:

```text
no public basho calendar selector in v1
Division is present in v1 as a row filter; it does not select a payload.
one main data selector: n
fewer projection axes
smaller grouped table
```

If existing Basho Results renderer utilities can be factored or reused cleanly, that can be considered during implementation. The initial design assumption is that Rating Changes may need its own small bridge and table spec because the unified grouped-table artifact model is not complete yet.

## 10. Sorting and alignment

Default sort:

```text
delta descending
```

Visible numeric columns should sort numerically.

Chii/rank display fields should sort by ordinal support fields:

```text
chii_at_start -> chii_ordinal_at_start
chii_at_end   -> chii_ordinal_at_end
```

Alignment follows the settled make_site2 table policy:

```text
headings
  centered

value strings that evaluate to numbers
  right-aligned

special non-numerical value strings
  centered

all other value strings
  left-aligned
```

The implementation should express sorting and alignment through table/presentation metadata where possible, not by page-specific CSS selectors.

## 11. Notes and popovers

The implementation should add notes for the concepts readers are likely to need explained:

```text
delta
Expected versus Actual basis
Normalised / K-normalised measures
```

Short filter popovers may be useful for `Basis` and `Normalised`, but longer explanations belong in Notes.

Popover links to Notes should only be used where the target note is present and meaningful for this artifact. The page should not repeat the earlier Options-popover problem where a `See Notes` link points to no note.

## 12. UI model compromises

This page exercises an area where the make_site2 UI model is close to, but not yet fully, unified.

Expected compromises:

```text
n is a filter in the public UI model, but it selects data rather than merely projecting loaded data
Basis and Normalised are filters that project terminal columns
Rating Changes may need a page-specific grouped-table bridge/table spec
```

These compromises should be intentional and visible in the code structure. They should not be hidden as incidental renderer behaviour.

A later unification pass may be able to generalize the grouped-table model across Basho Results Browser and Rating Changes.

## 13. Deferred implementation items

The first implementation should not attempt to solve:

```text
historical basho selection
all historical (date, n) payload generation
winning/losing streak tables
fusen-sho / fusen-pai interpretation changes
a fully universal grouped-table renderer
final/final public labels for every technical metric
```

These belong to open issues or later design work. The first implementation should deliver the latest-basho Rating Changes page cleanly and in line with the UI model.
