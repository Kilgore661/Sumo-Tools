# Basho Results Table (7.1) Model

## Status

Focused design note for the agreed 7.1 Basho Results table model.

This note refines:

- `Basho Results (7.1) Working Note.md`;
- `Table Structure Design Gap.md`; and
- `Tables as Dicts.md`.

Those documents remain background. This note records the current model to use
before assessing code impact.

---

## 1. Table Model

A table-like artefact has:

```text
Table
  Header?
  TableSpec

Header
  Heading
  Subheading?
```

The abstract `TableSpec` is a fixed ordered recursive keyed structure whose
terminal values are basic values/sorts. The row extent is external to the
specification.

The maximal table structure does not change over time. Instead, terminal paths
resolve to concrete values or nulls according to a resolution model.

---

## 2. Resolution Model

The `TableResolutionModel` is parallel to the abstract `TableSpec`.

For each terminal path it must say:

- the source of the value;
- when the value resolves to a concrete value;
- when the value resolves to null; and
- which domain guarantees let implementation avoid unnecessary defensiveness.

For 7.1, semantic resolution is driven by:

```text
selected basho
current calendar datetime
```

Options do not decide whether table values exist. Options operate over the
resolved maximal table by projecting, hiding or selecting visible parts of it.

Operational data availability may lag the ideal datetime-derived state. That
is an implementation/operations concern, not the pure semantic model.

---

## 3. 7.1 Page Boundary

7.1 remains **Basho Results**.

It is responsible for represented bashos with results:

- in-progress bashos after results exist; and
- completed/historical bashos.

2.1 remains **Banzuke Changes** and answers the separate new-banzuke-before-
results question. 7.1 work does not imply a 2.1 change unless a later decision
makes the new rating/banzuke values intrinsic to "previous basho" data.

---

## 4. Header Resolution

For 7.1, the heading should remain stable and the subheading should carry the
state distinction.

Example:

```text
Heading:    "{division} Results, {date}"
Subheading: "After Day {d}" for an in-progress basho
Subheading: "Final" for a completed basho
```

Header values are state-derived table data. Layout/rendering choices are a
later concern.

---

## 5. 7.1 Maximal Table Spec

Top-level groups:

```text
reference
before
state
comparison
```

The `state` group is headed `Current` during an in-progress basho and `After
Basho` for a completed basho.

Core entities:

```text
RBA = rating/banzuke analysis
  bp
  result
  equelo
  rbbc

RBBC = rating-based banzuke change
  banzuke_error
  rbbp

BanzukeError
  direction
  magnitude
```

`BanzukeError` is the rating-implied discrepancy between official BP order and
rating order. `magnitude` is non-negative.

The proposed 7.1 maximal spec is:

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

`prizes` remains a compact value. Other current compact result fields should be
treated as decomposable model values even if a later view renders them in one
cell.

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

## 7. Before Resolution

For the `before` group:

```text
before.rba.bp
  predecessor-basho BP.

before.rba.result.*
  predecessor-basho result values.

before.rba.result.division_change
  predecessor performance's significant promotion/demotion into the selected
  basho's broad division or rank level.

before.rba.equelo
  pre-selected-basho Equelo state.

before.rba.rbbc
  selected-basho banzuke slots plus pre-selected-basho rating order.
```

---

## 8. State Resolution

During an in-progress basho:

```text
state.rba.bp
  selected-basho BP.

state.rba.result.*
  selected-basho results through the represented day.

state.rba.result.division_change
  null.

state.rba.equelo
  day-end Equelo state after the represented day.

state.rba.rbbc
  selected-basho banzuke slots plus day-end rating order.
```

After a completed basho:

```text
state.rba.bp
  selected-basho BP.

state.rba.result.*
  final selected-basho result values.

state.rba.result.division_change
  significant promotion/demotion into the successor basho's broad division or
  rank level when the successor banzuke is known; otherwise null.

state.rba.equelo
  post-basho/final-day Equelo state.

state.rba.rbbc
  selected-basho banzuke slots plus post-basho rating order.
```

---

## 9. Next Step

The next stage is to assess the impact of this model on the existing code,
drawing a sharp boundary around what should be treated as prototype behaviour.
