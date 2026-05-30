# Basho Results (7.1) Working Note

## Status

Focused working note for the next `make_site2` modelling step.

This note captures the agreed public-product direction for Page **7.1 Basho
Results**. It is not yet a full replacement for the normative PA/table model.
Its purpose is to keep the intended 7.1 behaviour clear while the table
structure design gap is handled separately.

---

## 1. Page Responsibility

Page **7.1 Basho Results** remains **Basho Results**.

It is the normal public place to inspect results for a basho represented in the
site's History. This includes:

- completed historical bashos;
- the current/latest basho once results exist; and
- in-progress bashos where results are known only up to a represented day.

Page **2.1 Banzuke Changes** remains a distinct new-banzuke change report. It
answers the pre-results question:

```text
A new banzuke has been published before that basho has results of its own.
How does it differ from the preceding represented basho?
```

7.1 shall not be renamed `Latest Results`, because that weakens the historical
selected-basho reading. The word `Results` is deliberately broad enough to
cover historical, final and in-progress result states.

---

## 2. Boundary with 2.1

The current policy boundary is correct:

- use **2.1 Banzuke Changes** for the new-banzuke-before-results situation;
- use **7.1 Basho Results** for represented bashos with results.

No immediate 2.1 change is implied by the 7.1 work.

The only known reason to revisit 2.1 is a later decision that `DeltaBZ` and
`RBBP` are always part of "previous basho" data rather than specifically part
of 7.1's before/current/after result context. That decision has not been made.

---

## 3. One Artifact for During and After

7.1 should remain one Page/artifact family. There should not be separate
Navigation items for "during basho results" and "final basho results".

The same selected basho table has different state-dependent wording:

```text
before results exist
  no results are available for this basho yet

in progress
  results after Day N
  second temporal column group labelled Current

completed
  final results
  second temporal column group labelled After Basho
```

The day/finality state should come from the selected data instance or its
metadata, not from a separate Page identity.

---

## 4. Intended Table Shape

The 7.1 table should be understood as a temporal comparison table, not as a
flat list of unrelated columns.

The current visible duplication of headings such as `Chii` is a symptom that
the temporal structure is not being rendered clearly.

For a completed basho, the table should present grouped columns equivalent to:

```text
Identity
  #
  Shikona

Before Basho
  BP
  Result/context from previous basho where enabled
  Equelo
  DeltaBZ
  RBBP

After Basho
  Result
  Equelo
  Delta Equelo
  DeltaBZ
  RBBP
  nuBP/nuChii where applicable
```

For an in-progress basho, the second temporal group should be labelled
`Current` rather than `After Basho`, and the caption/subcaption should identify
the represented day, for example `Results after Day 7`.

Exact visible column names remain to be settled with the table-structure design
work. The important settled point is the temporal grouping:

```text
Before Basho
Current | After Basho
```

Grid lines, colour treatment or other chrome may support this grouping, but
the grouping itself is semantic and should be represented in the table model,
not only by styling.

---

## 5. DeltaBZ and RBBP

For any represented basho, the actual banzuke rows define the reference slots.

`DeltaBZ` means **change in banzuke position**:

```text
DeltaBZ = official BP-order row index - Equelo-rating-order row index
```

The unit is one row in the actual banzuke ordering used by 7.1, measured across
all divisions.

Example:

```text
official BP-order row index = 2
Equelo-rating-order row index = 5
DeltaBZ = -3
```

`RBBP` means **rating-based BP**. It is not computed by arithmetic on a BP
string. It is found by applying `DeltaBZ` to the actual banzuke row list and
looking up the BP held at the target row.

This is required because actual banzuke rows may contain annotations, unusual
numbers of sanyaku, missing positions or other historical structure. The row
list is the source of truth.

---

## 6. Temporal Rating States

For a represented basho, the BP side is fixed by that basho's banzuke. The
rating side can vary by represented time:

```text
pre-basho
  before any bouts in the basho

day-end
  after each represented day

post-basho
  after the final day
```

Each rating state can produce its own `DeltaBZ` and `RBBP`.

For 7.1 this means:

- pre-basho `DeltaBZ` and `RBBP` belong under `Before Basho`;
- day-end `DeltaBZ` and `RBBP` belong under `Current` for an in-progress basho;
- post-basho `DeltaBZ` and `RBBP` belong under `After Basho` for a completed
  basho.

---

## 7. Next Step

The next task is to sort out the 7.1 model:

- confirm the required producer data for pre/day-end/post rating states;
- decide exact visible columns and headings;
- decide how grouped column structure is represented;
- decide what metadata drives `Current` versus `After Basho` wording; and
- only then implement the rendering/code changes.
