# Basho Results (7.1) Outcome

## Status

Definitive account of the recent 7.1 Basho Results table redesign.

This document replaces the working notes that explored the 7.1 model, recursive
table specs, and rendering approach. Those notes are historical evidence only
after archival.

---

## 1. Job

Page **7.1 Basho Results** remains **Basho Results**.

It is the public place to inspect results for a basho represented in the site's
History:

- completed historical bashos;
- the latest/current basho once results exist; and
- in-progress bashos where results are known only up to a represented day.

Page **2.1 Banzuke Changes** remains separate. It answers the
new-banzuke-before-results question. The 7.1 work does not change 2.1 unless a
later decision makes rating/banzuke analysis intrinsically part of "previous
basho" data.

The page should not be renamed `Latest Results`: the selected-basho historical
reading is important.

---

## 2. Design Decision

The old 7.1 table was a useful prototype, but it flattened unrelated concerns:

```text
score
previous_result
previous_chii
equelo
delta_equelo
nu_chii
```

The redesigned table is a temporal comparison table. Its visible structure
should expose that model rather than presenting repeated headings such as
`Chii` without context.

The working design vocabulary is MVC-shaped:

```text
Model
  domain facts and computations

Controller / presentation mapping
  resolves table structure, headings, values and visible projection

View
  writes the prepared presentation model
```

The View should not compute domain meaning such as Division Change, Banzuke
Error, RBBP, basho lifecycle state, or result decomposition. The current code
still contains transitional parsing where the producer has not yet emitted the
final decomposed shape.

---

## 3. Table Shape

A table-like artefact is:

```text
Table
  Header?
  TableSpec

Header
  Heading
  Subheading?
```

`TableSpec` is an ordered recursive keyed structure:

```text
TableSpec ::= S+
S ::= <k> : (<t> | TableSpec)
```

For 7.1:

```text
BashoResultsFrame ::=
[
  reference: ReferenceSpec,
  before: RBASpec,
  state: RBASpec,
  comparison: ComparisonSpec
]
```

The `state` group is headed `Current` during an in-progress basho and `After
Basho` for a completed basho.

---

## 4. Maximal 7.1 Structure

```text
reference
  row_number
  shikona

before
  rba
    bp
    result
      wins
      losses
      absences
      prizes
      division_change
    equelo
    rbbc
      banzuke_error
        direction
        magnitude
      rbbp

state
  rba
    bp
    result
      wins
      losses
      absences
      prizes
      division_change
    equelo
    rbbc
      banzuke_error
        direction
        magnitude
      rbbp

comparison
  delta_equelo
```

`prizes` remains a compact value. Other result fields are logically
decomposable even if a later view chooses a compact display.

---

## 5. Resolution

The maximal structure is fixed. Terminal paths resolve to concrete values or
nulls. Options project or hide parts of the resolved table; options do not
decide whether values exist.

For the `before` group:

```text
before.rba.bp
  predecessor-basho BP

before.rba.result.*
  predecessor-basho result values

before.rba.result.division_change
  predecessor performance's significant promotion/demotion into the selected
  basho's broad division or rank level

before.rba.equelo
  pre-selected-basho Equelo state

before.rba.rbbc
  selected-basho banzuke slots plus pre-selected-basho rating order
```

For an in-progress basho:

```text
state.rba.bp
  selected-basho BP

state.rba.result.*
  selected-basho results through the represented day

state.rba.result.division_change
  null

state.rba.equelo
  day-end Equelo state after the represented day

state.rba.rbbc
  selected-basho banzuke slots plus day-end rating order
```

For a completed basho:

```text
state.rba.bp
  selected-basho BP

state.rba.result.*
  final selected-basho result values

state.rba.result.division_change
  significant promotion/demotion into the successor basho's broad division or
  rank level when the successor banzuke is known; otherwise null

state.rba.equelo
  post-basho/final-day Equelo state

state.rba.rbbc
  selected-basho banzuke slots plus post-basho rating order
```

Operational data availability may lag the ideal date/time-derived state. That
is an operations concern, not the pure table model.

---

## 6. Movement Terms

Three arrow-like concepts are distinct:

```text
Division Change
  Whether a result caused a significant promotion/demotion into a different
  broad division or rank level.

Movement
  Whether a rikishi actually moved up/down in the official banzuke from one
  basho to the next. This is the 2.1 Banzuke Changes movement feature.

Banzuke Error
  Whether rating order places the rikishi above/below their official BP order,
  plus the size of that discrepancy.
```

---

## 7. Implementation Outcome

The branch now contains a transitional 7.1 presentation-model renderer.

Implemented outcomes:

- Basho Results uses a nested header structure for `Reference`, `Before
  Basho`, `Current`/`After Basho`, and `Comparison`.
- Result values are displayed as separate terminal cells for wins, losses,
  absences, prizes, and Division Change.
- Prize heading uses the package glyph.
- Shikona remains left-aligned.
- Current/final Division Change is derived from selected BP to `nuChii`.
- Previous-context Division Change is derived from predecessor BP to selected
  BP.
- The producer emits current `score` with prize suffixes, matching previous
  result behaviour.

This is a successful transitional slice: the visible table now shows the
intended model structure and the rest of the site continues to work.

---

## 8. Remaining Work

Stress-test the design and implementation.

Examples:

- add `DeltaBZ` / Banzuke Error columns and confirm they fit the model;
- add RBBP values and confirm they sit under the intended RBA groups;
- inspect in-progress basho behaviour when only partial results exist;
- verify completed-but-no-successor-banzuke behaviour;
- audit unusual score strings such as `2-6--1`; and
- decide how much transitional compact-result parsing may remain.

The active open issues are tracked in `10 Open Issues and Deferred Design.md`.

