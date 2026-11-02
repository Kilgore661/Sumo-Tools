# Elo89a Implementation Design

## Status

Implemented design for the approved Elo89a viability experiment.

This design owns experimental code only. Production Elo-89 and canonical P1
remain unchanged.

## Pipeline

The implementation is a sequence of explicit transformations:

```text
History + published final records
  -> NonAppearanceLedger

History + prior map + divisional k + arm + NonAppearanceLedger
  -> ReplayResult

repeated ReplayResult + chii aggregation + canonical recentering
  -> FixedPointResult

control FixedPointResult + Elo89a FixedPointResult + canonical P1
  -> persisted experiment artefacts
```

## Modules and ownership

### `model.py`

Owns immutable experiment types:

- `ExperimentArm` identifies `control` and `elo89a`;
- `NonAppearanceCount` records FP and absence counts for one rikishi-basho;
- `NonAppearanceLedger` is the complete date/rikishi mapping;
- `BashoAdjustment` records replay accounting;
- `ReplayResult` records basho boundary ratings and adjustments;
- `IterationRow` and `IterationPrior` record solver history; and
- `FixedPointResult` records one arm's solved state.

### `ledger.py`

Transforms `History` and parsed final records into the explicit
`NonAppearanceLedger`. It counts FP directly from represented results and takes
absence counts only from the published `A` field. It requires a final record
for every ranked rikishi in every selected basho and does not infer missing
events.

### `replay.py`

Owns the paired replay shared by both arms. It consumes production Elo-89's
canonical rated-bout selection, uses Elo-89 active-population and normalisation
semantics, and accepts a chii-prior map rather than the production adopted
prior object. Unranked entrants use the experiment base rating and the ordinary
Elo-89 missing-chii `k` value of 35.

The only arm-dependent transition is the Elo89a basho-end deduction. Replay
then performs the common end normalisation.

### `solve.py`

Owns the fixed-point loop. It starts every chii at the canonical P1 base,
aggregates normalised basho-start ratings by chii, and calls the canonical P1
support-proportional recentering function. It retains the complete prior after
every iteration.

### `run.py` and `__main__.py`

Own the dirty boundaries and persisted artefacts. The runner loads one explicit
History zip, published final records, the divisional-k configuration and the
canonical P1 reference. It solves both arms and writes one output directory.

## Input interval

The first selected basho defaults to `1989/01`. The last selected basho defaults
to the latest published final-record basho. An explicit end may select an
earlier basho but not a basho lacking final records.

Every selected final-record date must exist in History. Every selected History
date through the chosen end must have a final-record table, and every ranked
rikishi must have a final record. Violations fail at the input boundary.

## Persisted schemas

The runner writes:

- `manifest.json`: source identities and hashes, interval, constants,
  convergence results and output filenames;
- `basho_adjustments.csv`: one row per arm and basho;
- `iterations.csv`: one convergence row per arm and iteration;
- `iteration_priors.csv`: one row per arm, iteration and chii;
- `prior_comparison.csv`: canonical P1, control and Elo89a values by chii; and
- `findings.md`: factual convergence summary and selected landmarks.

CSV rows use stable textual arm names and chii labels. The manifest hashes the
History zip and `k` configuration directly. It hashes the parsed selected final
records deterministically so that the actual evidence consumed by the
experiment is reproducible.

## Failure behaviour

Internal mappings use strict lookups. Missing chii priors, selected dates,
final records or ranked rikishi records raise immediately. The CLI returns `2`
only when a valid run completes without convergence; invalid inputs fail with
their ordinary exception and traceback.

## Next

Inspect the generated `findings.md` and `prior_comparison.csv`, with particular
attention to low-support chii. Any further model change requires a new proposal
or an explicit revision of the existing experiment contract.
