# Basho Results Table (7.1) Redesign - Part 2

## Status

Continuation of `Basho Results Table (7.1) Redesign.md`.

---

## 7. Resolution

Resolution is driven by:

```text
selected basho
current calendar datetime
```

Operational data availability may lag the ideal datetime-derived state. That
is implementation robustness, not the pure semantic model.

### Before

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

### During

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

### After

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

---

## 8. Projection Options

The selected basho is an input to table resolution. Other UI options are
projection controls over the resolved table.

Examples:

```text
Previous Basho
  projects before-basho context.

Equelo Ratings
  projects Equelo and rating/banzuke analysis values.

nuChii
  projects next-banzuke BP values where known under the current implementation
  meaning of nuChii as "new Chii".
```

Projection may also choose compact display forms. For example, decomposed
result values may be rendered as one visible score/result cell, but the
underlying presentation model should keep the distinct values.

---

## 9. Code Impact

The redesign is a contained vertical slice, not a whole-site rewrite.

Keep:

- page/navigation shell;
- build/output staging;
- broad filter plumbing;
- shared table chrome and scrolling ideas;
- other pages and renderers; and
- current `nuChii` implementation meaning.

Treat as prototype:

- current compact 7.1 producer payload columns;
- flat `columns + column_groups` as the full table model;
- indexed-table rendering that assumes one flat header row; and
- runtime rules that parse compact result strings for meaning.

Likely affected files:

```text
src/analysis/sumo_history/basho_results/*
src/products/make_site2/artifact_model.py
src/products/make_site2/manifest/artifacts.py
src/products/make_site2/runtime/site-refactor/ui/tables.js
src/products/make_site2/runtime/site-refactor/panels/render-content-panel.js
tests/test_make_site2_*.py
```

---

## 10. First Implementation Slice

Start by adding the presentation-model boundary for 7.1.

The first safe slice should:

1. define a recursive table-spec representation;
2. define a `BashoResultsPresentationModel` shape;
3. map the existing 7.1 payload into that presentation model as a transitional
   bridge; and
4. render the transitional model without changing producer semantics yet.

Only after that boundary exists should the producer payload be expanded toward
the full maximal 7.1 structure.

