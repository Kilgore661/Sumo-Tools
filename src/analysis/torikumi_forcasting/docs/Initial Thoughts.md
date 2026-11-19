# Torikumi Forecasting: Initial Thoughts

## Status

This note records the discussion before the first experiment is designed.  It
is not an experiment specification.  In particular, it does not commit the
project to a probabilistic model, fitted parameters or a claim that the JSA's
torikumi-making procedure can be reconstructed.

## Question and terminology

The motivating question is:

> For a late basho day `d`, initially envisaged as `d > 10`, how much of the
> actual torikumi can be forecast using the standings on day `d - 2`?

The chosen term is **torikumi forecasting**.  This separates the question from
the project's existing `analysis/torikumi_prediction` work and from bout-result
prediction.  The object forecast here is the arrangement of bouts itself.

The aim is to measure the extent of predictability, not to reproduce every
historical torikumi.

## Proposed simple starting point

A forum description offered the following rule of thumb for unannounced late
torikumi:

1. Remove kyujo rikishi.
2. Sort the remaining rikishi by wins, breaking ties by banzuke rank.
3. Pair them from the top down.
4. Do not repeat an opponent already faced in the basho.

Two additional hard restrictions are known:

* rikishi from the same heya do not meet in an ordinary torikumi; and
* close relatives do not meet, even when they belong to different heya.

Playoffs are not part of the regular torikumi and are outside this question.

This rule of thumb is attractive as a first baseline because it is simple,
legible and capable of being wrong.  The immediate purpose is to implement an
unrefined version and see how bad it is.  Its errors will help decide whether
further investigation is worthwhile.

## Heya evidence

The parsed rikishi bio store contains an ordered `Heya` list for every
represented bio.  Most rikishi have a single value; some have several.  For a
current-basho forecast, the working assumption can be that the last listed
heya is the current one.  That assumption should be stated rather than treated
as established fact.

The bio list does not date changes of heya.  Historical membership nevertheless
appears recoverable from the archived SumoDB daily-results HTML.  Rikishi-link
metadata has the form:

```text
Japanese shikona, heya, shusshin, birth date, hatsu dohyo, intai, ...
```

For example, rikishi ID 2 is shown with `Fujishima` in November 1992 and
`Futagoyama` in March 1993, while `Tokyo`, the shusshin field, remains
unchanged.  This is evidence for a dated mapping:

```text
(rikid, basho) -> heya
```

The canonical `History` banzuke does **not** currently contain heya.  An audited
historical heya index would therefore have to be extracted separately.  Before
relying on it, the extraction should check coverage, within-basho consistency,
spelling variants and known changes.  Heya history and shikona history must be
treated independently: shikona can change without heya changing, and there is
no present evidence that heya changes always coincide with shikona changes.

## Family relationships

The bio source exposes identity-related fields such as real name, birth date
and shusshin, but it has no systematic family-relationship field.  Those
attributes are not a sound basis for inferring relationships.

If family exclusions prove material, the defensible solution would be a small,
explicit and sourced exception registry.  The first experiment need not solve
this in advance.  It should disclose whether the missing information could
affect any forecast being assessed.

## Why perfect reconstruction is not the objective

Several schedules may satisfy all visible constraints.  The JSA may resolve
such cases using considerations that are unrecorded, unknown, discretionary or
merely absent from the initial rule.  One different choice can also cascade
through the remaining top-down pairings and make several bouts disagree.

Refining the algorithm after inspecting each disagreement could improve its
historical fit without improving its ability to forecast a new torikumi.  A
model approaching 100 percent historical accuracy would therefore be grounds
for examining leakage or overfitting, not automatically a success.

Any later refinement should have a clear substantive reason and should be
tested on basho not used to invent it.  Remaining discrepancies may be the
answer: standings and known restrictions might narrow the plausible opponents
without determining the committee's final choice.

## Deliberate limits of the first step

The first step should not begin with a sophisticated probabilistic model.  Such
a model would introduce fitting and debugging work before the project knows
whether the simple idea has useful signal.

The initial investigation should instead:

* implement one transparent baseline;
* retain enough diagnostics to understand obvious failures;
* measure its performance without repairing individual mistakes; and
* support an early decision that the project is not worth pursuing.

Questions such as the best probabilistic formulation, feature selection and
parameter fitting are deferred.  Even details of the first baseline--including
how a top-down procedure resolves an ineligible adjacent opponent or a greedy
dead end--belong in the forthcoming experiment design rather than being
silently decided here.

## Open matters for the first experiment design

The experiment design will need to settle at least:

* the exact historical range and divisions;
* which late days are included;
* the precise information cutoff represented by `d - 2`;
* whether the already-announced day `d - 1` torikumi is available at that
  cutoff;
* how kyujo status is represented without using later information;
* the literal top-down pairing procedure and its failure behaviour;
* how historical heya is supplied;
* how possible family exclusions are reported; and
* the simplest useful measure of disagreement with the actual torikumi.

These choices should be explicit before results are examined.
