# Specification Patch: Introduce `ActivityBasis`

## Purpose

Extend the existing standings model by introducing a new comparison-population dimension named `ActivityBasis`.

This dimension governs which rikishi are eligible to participate in a displayed standings comparison.

It is distinct from existing metric-definition dimensions such as `WinPolicy`, `BashoBasis`, and `BoutBasis`.

[Ed. This is the infrastrcuture for an alternative to the idea of a UI Include Retirees? switch viz an Include Inactive Rikishi? switch]

---

## Rationale

Existing dimensions determine how standings metrics are calculated for included rikishi.

They do not address a separate question:

> which rikishi should be compared at all?

In longer reporting windows, rikishi no longer part of the current competitive scene may remain highly ranked due to historical results.

This may be mathematically valid while contrary to ordinary user expectations of current standings.

`ActivityBasis` addresses this issue.

---

## Definition

`ActivityBasis` is a binary-valued comparison-population dimension.

Initial supported values shall be:

* `ALL`
* `CURRENT`

---

## Semantics

### `ActivityBasis.ALL`

All rikishi represented in the standings result set for the selected reporting window are eligible for comparison.

This corresponds to unrestricted historical inclusion.

### `ActivityBasis.CURRENT`

Only rikishi appearing on the terminal banzuke of the selected reporting window are eligible for comparison.

“Terminal banzuke” means the banzuke of the most recent basho in the selected reporting window.

---

## Scope

`ActivityBasis` affects:

* which rows are eligible for display
* displayed standings positions
* displayed row numbering

`ActivityBasis` does not affect:

* wins
* averages
* bout counts
* percentages
* other metric calculations for eligible rikishi

---

## Relationship to Existing Dimensions

`ActivityBasis` is a population-selection dimension.

It is separate from metric-configuration dimensions:

* `WinPolicy`
* `BashoBasis`
* `BoutBasis`

Those dimensions govern metric interpretation after eligibility has been determined.

---

## Default Behaviour

Where a default is required for user-facing standings presentation, implementations should prefer:

> `ActivityBasis.CURRENT`

unless a historical unrestricted mode is explicitly requested.

---

## Future Extension

Additional values may be introduced later if justified by user requirements, for example activity definitions based on recent participation rather than terminal-banzuke membership.

No such values are required at present.

---

# GSSWD Patch Proposal: Activity Filter (`ALL` / `CURRENT`)

## Purpose

Add a user interface control allowing users to choose the comparison-population basis used in displayed standings tables.

This replaces the narrower previously-considered retiree filter with a more general and robust activity filter.

---

## Requirements

The page shall provide a control allowing users to choose between:

* all eligible historical rikishi in the selected standings window
* current rikishi only

The default setting shall be:

> current rikishi only

Changing the control shall immediately update the displayed table.

Displayed standings positions and row numbering shall be recomputed after filtering.

The feature shall integrate cleanly with existing division filters and sorting behaviour.

---

## User-Facing Meaning

### All Rikishi

Show all rikishi represented in the selected standings window.

### Current Rikishi Only

Show only rikishi appearing on the terminal banzuke of the selected reporting window.

---

## Why This Replaces the Retirement Filter

The core user concern is not retirement as biography.

It is whether compared rikishi belong to the same current competitive scene.

A rikishi absent because of retirement, disappearance, suspension, or similar circumstances is handled automatically by the general activity rule.

This avoids special-case status logic.

---

## Browser Behaviour

The browser shall treat activity selection as a population filter.

Filtering order shall conceptually be:

1. load published standings rows
2. apply division filter
3. apply activity filter
4. sort surviving rows
5. recompute visible positions
6. render table

---

## Ranking Consequence

Because filtering changes the eligible row set, rankings change accordingly.

Example:

* with `ALL`, rikishi A may rank 23rd
* with `CURRENT`, rikishi A may be excluded and lower rows move upward

This is correct behaviour.

---

## UI Control

Any simple binary control is acceptable:

* select list
* toggle
* radio buttons

Suggested labels:

* `Activity: All / Current`
* `Show: All Rikishi / Current Only`

The default must clearly indicate `CURRENT`.

---

## Data Requirement

Published standings rows shall contain sufficient row-level metadata to determine whether each rikishi satisfies `CURRENT`.

How that metadata is derived is an implementation matter.

---

## Code Impact

### HTML

Add one control in the existing options area.

### JavaScript

Add:

* one new state value for `ActivityBasis`
* control event handling
* one additional row-filter predicate

Existing sort/render logic remains unchanged.

### Published Data

Add one row-level field sufficient to support `CURRENT` filtering.

---

## Documentation Impact

### Requirements

Mention optional activity filtering.

### Specification

Record `ActivityBasis` and its values.

### Design Notes

Record that activity status is determined upstream and consumed by browser filtering.

---

## Rationale

This feature is stronger than a retiree-only filter because it solves the broader problem of comparison relevance while avoiding biographical status debates.

It is:

* simple for users to understand
* highly useful on long windows
* low complexity in the browser
* consistent with current filtering architecture

---

## Recommendation

Implement as the preferred population filter after upstream activity-status data becomes available.

# Design / Implementation Notes: `ActivityBasis` UI Feature

## Purpose

Introduce a new browser-facing comparison-population control named `ActivityBasis`.

This control determines which rikishi are eligible to participate in displayed standings comparisons.

It is distinct from metric-definition controls such as `WinPolicy`, `BashoBasis`, and `BoutBasis`.

---

## Conceptual Model

Existing standings controls determine how metrics are calculated for rikishi already included in the result set.

`ActivityBasis` answers a prior question:

> which rikishi should be compared at all?

This is therefore a population-selection feature rather than a metric-calculation feature.

---

## Initial Supported Values

## `ActivityBasis.ALL`

All rikishi represented in the standings result set for the selected reporting window are eligible for display.

This corresponds to unrestricted historical inclusion.

## `ActivityBasis.CURRENT`

Only rikishi appearing on the terminal banzuke of the selected reporting window are eligible for display.

“Terminal banzuke” means the banzuke of the most recent basho in the selected reporting window.

---

## Default Behaviour

For mainstream browser use, the preferred default is:

> `ActivityBasis.CURRENT`

This aligns displayed standings with ordinary expectations of current competitive relevance.

`ALL` remains available as an unrestricted historical mode.

---

## Layer Responsibilities

## Standings Engine

The standings engine remains responsible for computing standings rows and metrics over the selected reporting window.

It does not need to know about `ActivityBasis`.

No standings mathematics changes.

## Publication / Output Stage

After standings rows are produced, rows shall be enriched with row-level activity metadata sufficient for browser filtering.

For the initial implementation this means determining whether each rikishi satisfies `CURRENT`.

## Browser JavaScript

The browser continues its current role of applying client-side view logic to precomputed standings rows.

`ActivityBasis` adds one further population filter.

---

## Upstream Determination of `CURRENT`

## Required Predicate

For the initial implementation, the required domain question is:

> is rikishi `r` on the banzuke at terminal date `d`?

This can be expressed as:

```python
is_on_banzuke_at(h: History, r: RikId, d: Date) -> bool
```

with the obvious implementation:

```python
return r in h[d].banzuke.riks
```

## Efficient Realisation

Repeated identical date lookups should be avoided.

Instead, once per published standings window:

```python
terminal_rikishi = set(h[terminal_date].banzuke.riks)
```

Then per row:

```python
is_current = rikishi_id in terminal_rikishi
```

This provides constant-time row annotation and avoids unnecessary repetition.

---

## Published Data Contract

Each published standings row shall include one row-level field sufficient to support activity filtering.

Suggested names:

* `is_current`
* `on_terminal_banzuke`

A positive boolean is preferred over negative polarity.

No duplicate datasets are required.

No separate “ALL” and “CURRENT” files are required.

---

## Browser Filtering Model

The browser filtering flow becomes:

1. load published standings rows
2. apply division filter
3. apply `ActivityBasis` filter
4. sort surviving rows
5. recompute visible positions
6. render table

This matches the existing architecture and requires no redesign.

---

## Ranking Consequences

Because `ActivityBasis` changes the eligible row set, displayed standings positions shall be recomputed over the filtered rows.

Example:

* under `ALL`, rikishi A may rank 23rd
* under `CURRENT`, rikishi A may be excluded and lower rows move upward

This is correct and expected behaviour.

---

## UI Placement

`ActivityBasis` belongs with scope/population controls such as:

* basho count
* division

It does not belong with metric-definition controls.

Suggested labels:

* `Activity: All / Current`
* `Show: All Rikishi / Current Only`

The default state should clearly indicate `CURRENT`.

---

## Documentation Impact

Small updates only.

### Requirements

Mention optional activity filtering.

### Specification

Define `ActivityBasis`, its values, and default behaviour.

### Design Notes

Record upstream derivation from terminal-banzuke membership and browser-side filtering use.

---

## Non-Goals

This feature does not:

* alter wins
* alter averages
* alter bout counts
* alter percentages
* alter metric semantics for eligible rikishi
* require retirement modelling
* require persistent retirement caches

---

## Rationale

The feature solves a genuine comparison-relevance problem visible in longer reporting windows, while avoiding unnecessary biographical-status logic such as retirement inference.

It is:

* conceptually clean
* cheap to implement
* consistent with current browser architecture
* valuable to mainstream users
* extensible if richer activity definitions are later required

---

## Future Extension

Additional `ActivityBasis` values may later be introduced if justified, for example rules based on recent participation or actual fighting activity.

No such extensions are required for the initial implementation.
