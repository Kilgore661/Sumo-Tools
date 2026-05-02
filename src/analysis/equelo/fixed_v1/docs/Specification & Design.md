# Equelo Fixed v1 Specification & Design

## Status

Initial specification and design.

This document defines the generated artefacts and implementation shape for
`src.analysis.equelo.fixed_v1`.

The model rationale is documented separately in `Model Rationale.md`.

## 1. Product Contract

`fixed_v1` provides the project-level Equelo rating series.

For the fixed v1 model definition, the package shall provide an efficient way
to know the Equelo rating of any represented rikishi at any represented rating
point from January 1958 onward.

The ratings are derived data.  They are computed from canonical `History` plus
the fixed v1 model definition.  They are not observed facts and are not stored
inside `History`.

## 2. Rating Semantics

The persisted rating point is day end.

A day-end rating is the rating after all represented scored bouts on that day
have been processed by the simulator.

The simulator's existing rules define which bouts affect ratings.  In
particular, non-rating events such as fusen and blank bouts follow the existing
Expt1/Expt3c simulator behaviour.

The first implementation shall not persist basho-start ratings separately.
If a consumer needs a rating before a day starts, it should obtain that value
from the previous represented rating point while walking the timeline.

## 3. Generated Artefacts

The generator shall write:

```text
files/output/Equelo/fixed_v1/
  metadata.json
  day_end_ratings.json
```

### 3.1 `metadata.json`

`metadata.json` records what was generated and how.

Required fields:

```json
{
  "model_version": "fixed_v1",
  "generated_at": "...",
  "history_min_date": "1958/01",
  "history_max_date": "...",
  "history_basho_count": 0,
  "rating_points": 0,
  "rating_count": 0,
  "model": {
    "source_history_start": "1958/01",
    "history_cleaning": "Expt1 Oracle",
    "simulator": "src.analysis.equelo.expt1.simulate.simulate",
    "mode": "closed",
    "entrant_policy": "scaled_fixed_point",
    "fixed_point_source": "files/output/Equelo/expt2_combined_final.csv",
    "alpha": 0.55,
    "q": 900,
    "k_policy": "divisional",
    "k_config": "files/input/elo_fide.json",
    "collapse_mode": "annotation-only"
  }
}
```

The implementation may add fields.  It shall not omit the above fields without
an explicit specification change.

### 3.2 `day_end_ratings.json`

`day_end_ratings.json` stores only ratings.

It shall not duplicate chii, shikona, banzuke membership, or other data that is
derivable from `History`.

Shape:

```json
{
  "1958/01": {
    "1": {
      "1234": 1502.25,
      "5678": 1497.75
    },
    "2": {
      "1234": 1505.10,
      "5678": 1494.90
    }
  }
}
```

Keys:

- top level: date string using the project's existing `Date` string form;
- second level: day string;
- third level: rikishi id string;
- value: rating as a JSON number.

The file is sparse by construction.  It contains represented ratings for
represented rikishi at represented day-end points.  It does not contain a dense
matrix across all rikishi and all dates.

## 4. History Dependency

`History` remains the source of truth for:

- banzuke membership;
- chii;
- shikona;
- bout results;
- basho/date/day structure.

The rating artefact stores only the derived rating values.  Consumers that need
display fields should join ratings to `History`.

This separation is intentional.  It avoids duplicating canonical historical
data and keeps the rating artefact focused on the derived model output.

## 5. Failure Semantics

`fixed_v1` follows a design-by-contract, offensive-programming style.

For represented banzuke rikishi at represented rating points, ratings are
required to exist.

Implementation and consumer code should use direct indexing rather than
nullable lookups:

```python
rating = ratings[date][day][rikishi_id]
```

A missing key indicates a violated precondition, stale artefact, corrupted
artefact, or mismatch between `History` and ratings.  The program may fail with
the ordinary exception raised by the underlying data structure.

The implementation should not mask missing ratings with:

- default ratings;
- blank ratings;
- optional return values;
- defensive `dict.get()` fallbacks;
- catch-and-continue recovery paths.

Exceptions should be handled only when the requirements define an expected
failure mode.

## 6. Freshness

The tracker owns the logic for deciding when `History` should be updated.
`fixed_v1` shall not duplicate tracker calendar logic.

The fixed v1 artefacts are fresh only with respect to the `History` snapshot
used to generate them.  `metadata.json` records the `History` coverage used by
the generator, but those fields do not by themselves determine whether the
ratings are calendar-current.

For the first implementation, freshness is operational:

1. the tracker updates or publishes `History`;
2. a human reruns the fixed v1 generator;
3. downstream tools consume the regenerated artefacts.

Later work may integrate fixed v1 generation into the tracker's post-update
workflow.  That integration does not require ratings to become part of
`History`, and it does not require the live store to publish ratings in v1.

## 7. Consumer Contract

Consumers shall load persisted fixed v1 artefacts.  They shall not run the full
Equelo model as part of ordinary report generation or page publication.

The intended consumer flow is:

```text
load History
load fixed_v1 ratings
join by date/day/rikishi id as needed
render or analyse
```

The Banzuke Change Report is expected to be the first consumer, but the API and
artefacts are project-level rather than BCR-specific.

## 8. Implementation Design

The implementation is an orchestrator around existing Equelo components.

It should not create a second rating engine.

### 8.1 Inputs

Inputs:

- canonical `History`;
- bios required by the existing Oracle construction;
- Expt2 combined final chii ratings;
- fixed v1 model constants.

### 8.2 Processing

The generator shall:

1. load or receive canonical `History`;
2. build the cleaned Equelo history using the existing Expt1 Oracle;
3. load Expt2 combined final chii ratings;
4. compute the mean fixed-point rating;
5. scale fixed-point ratings using `alpha = 0.55`;
6. build a chii-based entrant initialiser from the scaled values;
7. run the existing Expt1 simulator in closed mode with fixed v1 parameters;
8. serialise `result.day_end_ratings` to `day_end_ratings.json`;
9. write `metadata.json`.

### 8.3 Output Ordering

JSON object order is not part of the semantic contract, but the writer should
emit dates, days, and rikishi ids in sorted order to make diffs and inspection
easier.

### 8.4 API Shape

The first loader API should be small:

```python
load_day_end_ratings() -> dict[str, dict[str, dict[str, float]]]
load_metadata() -> dict
```

A richer query wrapper may be added once a consumer needs it.  Until then, the
plain nested mapping is the contract.

### 8.5 Batch First

The first implementation shall regenerate the full fixed v1 rating series.
Incremental update is out of scope for v1.

This is acceptable because the immediate goal is a reliable derived artefact,
not the final tracker-integrated operating mode.

## 9. Open Questions

- Should a future version persist start-of-day or basho-start ratings as a
  convenience layer?
- Should metadata eventually include a robust `History` content fingerprint?
- Should tracker integration publish ratings through a live store, or only
  regenerate persisted artefacts?
- Should future model versions revisit divisional K sensitivity?
