# GOAT-o-Matic implementation plan

The project follows the iterative approach described in
`prototype-strategy.md`. In particular, the first useful prototype is a set of
spreadsheet-ready factual and descriptive CSVs. A website follows after those
CSVs have been used to explore and refine possible GOAT criteria.

## 1. Purpose and architectural boundary

The implementation has two deliberately separate parts:

```text
History (live store or canonical zip)
        |
        v
src/goat
  extract, classify, calculate, validate and publish data
        |
        v
files/output/goat
  versioned, auditable public artifacts
        |
        v
src/products/GOAT
  copy/package artifacts and publish the standalone website
        |
        v
browser
  filter, select criteria, rank and explain
```

`src/goat` owns all domain interpretation and calculation. It may read a
`History`, rikishi biographical data and explicitly identified supplementary
sources. It must not contain presentation code.

`src/products/GOAT` owns the standalone web product. It must not calculate sumo
statistics or reinterpret raw `History` data. It publishes the artifacts from
`src/goat` and performs only user-directed table operations and ranking over
already defined values.

This boundary should make later incorporation into the main Sumo Tools site a
change of product shell rather than a rewrite of the GOAT calculations.

## 2. Implementation principles

1. Build facts before scores. The statistical explorer is useful before the
   combined GOAT ranking exists and gives us a way to validate every measure.
2. Preserve missingness. Missing, incomplete and inapplicable data must not be
   converted to zero.
3. Keep calculation definitions explicit. Every metric has a stable identifier,
   label, direction, unit, numerator/denominator description and evidence rule.
4. Calculate once. Python production code creates public values; JavaScript
   filters, sorts, combines and explains them.
5. Retain provenance. Every output set identifies the source `History` and any
   supplementary source used.
6. Avoid a hidden house definition of greatness. Defaults may provide a useful
   demonstration, but the product does not endorse a definitive weighting.
7. Do not introduce Elo, BAR or any inferred/compensated strength measure into
   the initial implementation.

## 3. Proposed production package

The detailed module split can change as the code reveals better boundaries,
but the intended responsibilities are:

```text
src/goat/
    model.py          internal fact and result value objects
    extract.py        History -> normalized GOAT facts
    eligibility.py    cohort, active and partial-career rules
    bouts.py          scheduled/contested/fusen classification
    playoffs.py       optional playoff-detail adapter and availability
    banzuke_level.py  Y/O/S/K/Mn level mapping
    metrics/
        achievement.py
        championships.py
        winning.py
        distribution.py
        longevity.py
        peak.py
        opposition.py
    catalogue.py      public definitions and relationships between metrics
    validate.py       invariants and reconciliation reports
    output.py         deterministic public artifacts
    __main__.py       live-store/zip command-line entry point
```

The package should consume the normal `History` interface and not depend on
whether that object came from the live store or a zip. Loading belongs at the
entry-point boundary, following existing project conventions.

## 4. Canonical analytical facts

The first production milestone is a normalized, testable fact layer. It should
not be a second general-purpose sumo model; it should contain only facts needed
by the requirements.

### 4.1 Basho appearances

One row per Makuuchi-banzuke rikishi per non-cancelled basho, including:

- basho and rikishi ID;
- published chii and GOAT banzuke level;
- rank group flags (yokozuna, ozeki, san'yaku, Makuuchi);
- wins and losses (`W` and `L`);
- fusen wins and losses (`FS` and `FP`);
- fusensho and fusenpai;
- yusho, doten-yusho and jun-yusho markers;
- zensho, kachi-koshi and make-koshi flags; and
- tournament-status and data-completeness fields.

Presence on the Makuuchi banzuke—not participation in a bout—is the appearance
criterion.

### 4.2 Bout facts

One row per relevant rikishi perspective per bout, including:

- basho and scheduled day, or playoff sequence;
- rikishi and opponent IDs;
- scheduled/playoff classification;
- contested/fusensho/fusenpai classification;
- win/loss outcome where applicable;
- both published chii values and both GOAT banzuke levels; and
- source and completeness status.

This representation makes fusen policy and opposition calculations auditable
without repeatedly interpreting `Summary`.

### 4.3 Rikishi identity and career boundaries

Build a stable rikishi table keyed by SumoDB ID. Public shikona selection must
follow the project's existing full-shikona conventions. Add birth date and
other biography fields only where a requirement needs them and their
availability has been verified.

Career-boundary facts must support:

- first and last Makuuchi-banzuke basho;
- whether the career is in progress at the end of the supplied History;
- whether the professional career is left-truncated by the beginning of the
  supplied History; and
- explicit inclusion/exclusion of partial careers.

## 5. Metric engine

Each metric implementation should return both its value and enough metadata to
explain how it was obtained. A public metric catalogue should describe:

- stable metric ID and display label;
- category;
- value type and unit;
- whether higher or lower is better;
- numerator and denominator definitions, where applicable;
- eligible fact types and date semantics;
- fusen and playoff policy;
- required data capabilities;
- missing-data behaviour; and
- closely related metrics that may double-count the same idea.

Implementation order:

1. banzuke-basho counts and official/contested bout totals;
2. achievement and championship counts/rates;
3. winning rates and basho-result distributions;
4. banzuke-level opposition measures;
5. longevity measures;
6. fixed-window and streak measures; and
7. playoff bout records when detailed data is available.

Rate values should be emitted numerically with their raw numerator and
denominator. Formatting as a percentage belongs to the product.

Fixed-window results must include the winning window's start and end basho and
the precise measure optimized. Ties between windows need a deterministic rule
that is documented before implementation.

## 6. Validation strategy

Validation is part of production, not merely a development aid.

### 6.1 Structural checks

- Every fact refers to a basho and rikishi present in the source history.
- Makuuchi appearance rows correspond exactly to Makuuchi banzuke occupants.
- Scheduled bout perspectives reconcile two-to-one with source bouts.
- Contested, fusensho and fusenpai classes are mutually exclusive and exhaustive
  for recorded scheduled decisions.
- GOAT banzuke levels agree with the published `Chii` level and number.
- Required denominators are never negative and rates with zero denominators are
  unavailable, not zero.

### 6.2 Aggregate reconciliation

- Career totals equal sums of basho totals.
- Yusho counts reconcile with `Y` markers.
- Playoff appearances reconcile with `Y` plus `D` markers in tied Makuuchi
  championships.
- A complete playoff record reconciles its participant set with those markers.
- Opposition distributions sum to contested scheduled plus complete playoff
  bouts only.

### 6.3 Test layers

Use small constructed histories for exact edge cases, selected real basho as
regression fixtures, and whole-history invariant tests against the live store
or canonical zip. Browser ranking and sorting receive separate JavaScript smoke
tests.

## 7. Public artifacts

Production output should be deterministic and written beneath:

```text
files/output/goat/
```

The spreadsheet-first prototype contains only CSV:

```text
manifest.csv
rikishi.csv
basho.csv
banzuke.csv
bouts.csv
markers.csv
playoffs.csv
rikishi_summary.csv
summary_definitions.csv
coverage.csv
validation.csv
```

`manifest.csv` includes the schema version, represented basho range, row counts
and file digests. `coverage.csv` records capability completeness by fact type.
The future website must reject an unsupported schema version rather than guess.
Metric-producer artifacts can be added later without changing the factual
tables.

Evidence views need not publish every raw source field in the first iteration,
but every displayed value must be traceable to included basho and bouts. Large
bout evidence may be partitioned by rikishi or basho and loaded on demand.

## 8. Standalone web product

The initial `src/products/GOAT` product should contain only publishing and UI
concerns:

- a build step that checks and stages the `src/goat` public artifacts;
- a static application shell;
- the statistical explorer;
- the ranking builder;
- definitions, caveats and evidence views; and
- URL-serializable user choices for saving and sharing a ranking.

### 8.1 Explorer first

Implement the explorer before combined scoring. It exercises filtering,
multi-key sorting, metric definitions, eligibility and evidence without first
having to settle normalization.

### 8.2 Ranking second

The ranking builder should:

1. select the eligible cohort;
2. select metrics and career/fixed-window variants;
3. choose weights or priority ordering;
4. show raw values and any normalization;
5. calculate each metric contribution in the browser; and
6. produce the complete ordered ranking with leader and adjacent gaps.

Before this phase, decide and document:

- the supported normalization method or methods;
- treatment of ties;
- treatment of unavailable values;
- whether weights and lexicographic priority are separate modes; and
- the precise URL state format.

The scoring code may run in the browser because it applies the user's declared
choices to already-produced statistics. It must not derive sumo facts from raw
bouts or banzuke data.

## 9. Delivery sequence

### Phase A: contracts and fixtures

- Freeze vocabulary and formulas from the requirements.
- Inventory required source fields and identify genuine gaps.
- Define analytical facts, metric catalogue and output schema.
- Build representative fixtures for absences, fusen, multi-rikishi san'yaku,
  partial careers, cancelled/exceptional tournaments and playoffs.

### Phase B: fact extraction

- Implement Makuuchi appearance extraction.
- Implement scheduled-bout classification.
- Implement banzuke level.
- Add validation and whole-history reconciliation.

### Phase C: independent statistics

- Implement non-playoff-dependent career and basho measures.
- Publish deterministic artifacts and their catalogue.
- Compare headline values against independently calculated known examples.

### Phase D: statistical explorer

- Build the standalone product shell.
- Add cohort filters, selectable columns and multi-key sorting.
- Add definitions, completeness indicators, evidence drill-down and export.

### Phase E: GOAT ranking

- Resolve normalization and missing-value policy.
- Add criteria selection, weighting/priority, contribution display and complete
  ranking.
- Add duplicate-information warnings and shareable URL state.

### Phase F: playoff completion

- Resume the `d=16` investigation.
- Implement parser production of `History.playoffs`.
- Validate it against the `Y`/`D` participant oracle.
- Enable playoff wins/losses and playoff-inclusive contested/opposition values
  wherever complete.

### Phase G: integration and hardening

- Add the GOAT producer to the maintained analysis pipeline.
- Add artifact freshness and schema checks to the site build.
- Test the full live-store and zip paths.
- Profile payload size and browser responsiveness.
- Prepare the product boundary for later inclusion in Sumo Tools.

## 10. Matters to settle before their phases

These need not block the first production work:

- the combined-ranking normalization method;
- the status of cancelled and exceptional basho in source data;
- availability and provenance of birth dates for age measures;
- fixed-window tie-breaking;
- exact treatment of draws, if any appear in the represented Makuuchi data;
- public-artifact partitioning and evidence payload size; and
- detailed playoff ingestion, described separately in `playoffs.md`.

## 11. First executable milestone

The first end-to-end milestone should deliberately exclude combined scoring
and does not require a website:

1. load the same selected `History` from either the live store or a supplied
   canonical zip;
2. produce auditable banzuke, bout, marker and optional playoff facts;
3. calculate a small set of precisely named descriptive aggregates in a
   one-row-per-rikishi summary CSV;
4. emit versioned public artifacts plus coverage and validation results; and
5. explore possible criteria, priority ordering and tie-breakers in a
   spreadsheet.

That milestone proves the data-production contract while leaving the ranking
formula and unavailable playoff detail open. A minimal website prototype is
the following landmark, informed by what the spreadsheet experiments reveal.
