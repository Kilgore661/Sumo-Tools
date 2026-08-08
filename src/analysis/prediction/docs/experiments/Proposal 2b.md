# Proposal 2b: Sub-sekitori Evaluation of Basic Elo

## Status

Accepted complementary evaluation to `Proposal 2.md`.

## Question

What predictive behaviour does the unchanged Proposal 1 Basic Elo producer
show when evaluation is restricted to bouts wholly inside the sub-sekitori
domain?

## Domains

The rating domain remains every eligible represented W/L bout from 1989/01.
A forecast is evaluated if and only if both participants have a banzuke `Chii`
below sekitori for that basho. A bout with one or no sub-sekitori participants
is ignored by the evaluator but still updates the ratings.

Consequently, Proposal 2 and Proposal 2b apply the same boundary rule:

```text
evaluate only when both participants belong to the domain under consideration
```

Juryo–Makushita and other cross-boundary contests belong to neither evaluated
population. Participants outside the basho banzuke also belong to neither
domain.

## Evaluation

Reuse the immutable Proposal 1 forecasts and the same log loss, Brier loss,
50% reference, basho aggregation, rolling windows, cumulative series and
pointwise basho-block bootstrap.

Compare the resulting curve with the all-bout and sekitori-only results. In
particular, determine whether the all-bout decade of early underperformance and
the later deterioration seen in sekitori predictions occur in the much larger
sub-sekitori population.
