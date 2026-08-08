# Proposal 2: Sekitori-only Evaluation of Basic Elo

## Status

Accepted follow-on experiment to Proposal 1.

## Question

What predictive behaviour does the unchanged Proposal 1 Basic Elo producer
show when evaluation is restricted to bouts wholly inside the sekitori domain?

## Fixed rating producer

The rating producer is exactly Proposal 1:

```text
epoch = 1989/01
q = 400
k = 35
initial rating = equal 1500
eligible rating result = W/L, irrespective of kimarite
rating population = every represented participant
ratings persist by RikId
```

Every eligible bout updates the ratings. Lower-division bouts are not removed
from the chronological pass, because doing so would change the ratings later
carried into the sekitori domain.

## Evaluation domain

A forecast is evaluated if and only if both participants are sekitori on the
basho's pre-bout banzuke. Sekitori means that the participant's authoritative
`Chii.level` is an MSD level or `Division.JURYO`.

All other forecasts are ignored by the evaluator:

- a bout with exactly one sekitori participant is excluded;
- a bout with no sekitori participants is excluded;
- a participant outside that basho's banzuke is outside the evaluation domain.

These exclusions do not prevent the bouts from updating the Basic Elo state.
The distinction is therefore:

```text
rating domain = all eligible represented W/L bouts
evaluation domain = W/L bouts with two pre-bout sekitori
```

Chii values determine evaluation membership only. They cannot reach the
prediction producer. Chii strings are presentation values and are not used in
the calculation.

## Evaluation

Reuse the immutable Proposal 1 pre-bout forecasts and their outcomes. Apply the
same log loss, Brier loss, 50% comparator, basho aggregation, 6/12/24-basho
rolling windows, cumulative series and fixed-seed pointwise basho-block
bootstrap.

Report the number of evaluated bouts and the numbers excluded with exactly one
or no sekitori participant. Compare whole-epoch sekitori losses directly with
the all-bout Proposal 1 result.

## Decision boundary

This experiment describes population sensitivity. It does not change Basic
Elo, select parameters, estimate a torikumi policy, or assert that sekitori
bouts are representative of lower-division bouts.
