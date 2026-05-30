# Basho Results Table (7.1) Redesign

## Status

Focused redesign note for implementing the next 7.1 Basho Results table work.

This document starts from the product job and uses the table-model discussion
as supporting design. Earlier notes remain background:

- `Basho Results (7.1) Working Note.md`;
- `Basho Results Table (7.1) Model.md`;
- `Table Structure Design Gap.md`; and
- `Tables as Dicts.md`.

---

## 1. Job

Extend **7.1 Basho Results** so it can present the existing result table plus
new rating/banzuke analysis columns.

The new work must support:

- before-basho context;
- current or final state context;
- Equelo ratings;
- rating-based banzuke change values;
- next-banzuke BP where known; and
- state-dependent headings for in-progress versus completed bashos.

The renderer must not compute domain meaning. It should write a prepared
presentation model.

---

## 2. Prototype Problem

The current implementation is a useful prototype, but it flattens too many
concerns.

Current 7.1 data is emitted as compact display-oriented fields such as:

```text
score
previous_result
previous_chii
equelo
delta_equelo
nu_chii
```

Current `make_site2` metadata describes these with a shallow
`columns + column_groups` shape. That shape is a partial encoding of grouped
table structure, but it is not the full recursive table model now needed by
7.1.

Current rendering assumes a flat list of visible columns and does not render
the 7.1 temporal groups as first-class structure.

The redesign should draw a sharp boundary around this prototype behaviour
rather than treating it as the source of truth.

---

## 3. MVC Approach

Use MVC as the local design vocabulary.

### Model

The Model owns domain facts and computations:

- History and selected basho facts;
- predecessor and successor basho facts;
- banzuke BP rows;
- result facts;
- Equelo ratings;
- Division Change;
- Banzuke Error and RBBP, if treated as domain analysis; and
- next-banzuke BP where known.

The Model does not own visible column layout.

### Controller

The Controller owns table resolution and projection.

It takes:

```text
model facts
selected basho
current calendar datetime
projection options
```

and produces a `BashoResultsPresentationModel`.

It decides:

- heading and subheading values;
- whether the state group is `Current` or `After Basho`;
- which terminal paths resolve to values or nulls;
- how the selected basho/datetime state affects those values; and
- which projection options make which paths visible.

### View

The View owns writing.

It takes a `BashoResultsPresentationModel` and renders:

- the header;
- nested table headings;
- visible terminal values;
- null display;
- sort controls; and
- ordinary table layout/chrome.

The View must not compute Division Change, Banzuke Error, RBBP, basho lifecycle
state or result decomposition.

---

## 4. Presentation Model

Conceptually:

```text
BashoResultsPresentationModel
  Header?
  TableSpec
  resolved_values
  projection
  notes/provenance/sort metadata
```

The table itself is:

```text
Table = Header? . TableSpec
Header = Heading . Subheading?
```

`TableSpec` is the recursive table specification:

```text
TableSpec ::= S+
S ::= <k> : (<t> | TableSpec)
```

The maximal table structure is fixed. Terminal paths resolve to concrete
values or nulls. Options project or hide parts of the resolved table; options
do not decide whether the values exist.

---

## 5. Basho Results Frame

7.1 instantiates `TableSpec` with:

```text
TableSpec_7_1 = BashoResultsFrame

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

---

## 6. Maximal 7.1 Structure

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

Continued in `Basho Results Table (7.1) Redesign - Part 2.md`.

