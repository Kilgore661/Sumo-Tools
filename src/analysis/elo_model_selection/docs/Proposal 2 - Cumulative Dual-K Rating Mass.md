# Proposal 2: Cumulative Dual-K Rating Mass

## Status

Implemented diagnostic specification.

## Purpose

Measure the rating mass created or destroyed when the two participants in a
bout use different `k` values in the completed controlled post-1988 model
comparison.

This is a narrow follow-up to the selection of provisional
\(B'=B_{kP}\). Sumo rating inflation caused by entrants and departures is
already established. This experiment does not rediscover that mechanism and
does not choose a normalisation policy.

## Source

The sole analytical input is the persisted `forecast_ledger.csv` produced by:

```text
python -m src.analysis.elo_model_selection
```

The source ledger is hashed in the experiment manifest. Consuming the ledger
ensures that the diagnostic measures the exact model runs used for model
selection rather than a similar replay with accidentally different policy.

## Definitions

For one forecast-ledger row:

\[
\Delta M = \Delta_a + \Delta_b.
\]

An unequal-`k` bout is one for which:

\[
k_a \ne k_b.
\]

The experiment reports:

- **net mass change**: the signed sum of \(\Delta M\);
- **gross absolute mass change**: the sum of \(|\Delta M|\);
- positive and negative flows separately;
- affected-bout counts and shares;
- mean and maximum per-bout changes;
- breakdowns by unordered `k` pair; and
- basho-level net, gross and cumulative net change.

## Questions

1. How many bouts use unequal `k` values?
2. What cumulative signed rating mass do they create or destroy?
3. How much gross flow lies behind that signed total?
4. Which `k` boundaries contribute the affected bouts and net mass?
5. Does the result differ between `B_k` and `B_kP` despite their identical
   `k` schedule and bout population?

## Interpretation boundary

This experiment measures bout-update mass. It does not directly measure:

- entrant or departure rating mass;
- the endpoint active-population mean;
- the amount of bout-created mass still held by active rikishi;
- an appropriate normalisation correction; or
- whether preserving or changing rating differences is desirable.

Some rikishi who receive bout-created mass later leave the active population.
Consequently, cumulative bout mass must not be divided by the endpoint active
population and presented as endpoint mean inflation.

## Invariants

- `B` and `B_P` must contain no unequal-`k` bouts.
- Same-`k` bout updates must sum to zero apart from floating-point
  representation.
- `B_k` and `B_kP` must have identical rated-bout and unequal-`k` bout counts.
- K-pair and basho totals must reconcile with each model summary.

## Run

```powershell
python -m src.analysis.elo_model_selection.dual_k_mass `
  --ledger "files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/forecast_ledger.csv"
```

The default output directory is `dual_k_mass` beside the input ledger. The
experiment writes:

```text
manifest.json
summary.csv
by_k_pair.csv
by_basho.csv
report.md
```
