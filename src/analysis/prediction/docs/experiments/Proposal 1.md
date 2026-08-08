# Proposal 1: Basic Elo Predictive Behaviour from 1989

## Status

Proposed first experiment under the wider aims recorded in `Aims.md`.

This proposal deliberately fixes one rating model and studies the behaviour of
the evaluation framework around it. It does not compare or select models.

## Purpose

Build a rigorous chronological framework that can record and evaluate the
pre-bout predictions produced by one pass of Basic Elo through professional
sumo results from January 1989 onward.

The first rating producer is fixed as:

\[
\operatorname{BasicElo}(q=400, k=35)
\]

The experiment asks:

> How does the predictive performance of Basic Elo change during a single
> chronological pass through complete post-1989 sumo results, and how precisely
> can we describe whether and when its predictions become better than a neutral
> 50% predictor?

The question does not assume that predictive performance improves. The
framework must make improvement, absence of improvement, instability or
deterioration equally visible.

## Relationship to the wider aims

`Aims.md` describes a larger programme for testing Elo-family and later rating
models. This proposal is the first, narrower experiment in that programme.

This proposal does not attempt to:

- choose the best value of \(q\);
- choose the best value or policy for \(k\);
- compare entrant-initialisation policies;
- test Equelo;
- use chii as an estimate of ability;
- select a preferred model;
- merge the incomplete pre-1989 result regime into the principal experiment.

Those questions may be considered only after the Basic Elo producer and its
evaluation framework are understood and trusted.

## Historical domain

The principal data epoch begins at:

```text
1989/01
```

The repository treats 1989 onward as the first substantially complete result
regime across the represented banzuke domain. Earlier results have a different
observability policy, especially below sekitori level. They are excluded from
this experiment rather than repaired, merged or used for initialisation.

Before implementation, the data investigation must confirm the precise 1989
boundary and document the eligible bout population. If the source data do not
support the stated boundary, the discrepancy must be reported before the
experiment proceeds.

## Basic Elo producer

### Parameters

The producer uses:

```text
q = 400
k = 35
```

These values are fixed inputs to the experiment, not parameters to be fitted.

### Initial rating

Every rikishi without an existing rating receives the same initial rating
\(b=1500\) immediately before their first eligible bout. The numerical value
of \(b\) is an arbitrary origin. Adding the same constant to every rating must
leave all probabilities and rating changes unchanged.

The implementation must choose and record one conventional value of \(b\), but
must not interpret its absolute value as ability.

### Population behaviour

Ratings persist after they have been created. A period without a recorded bout
does not itself change or erase a rating.

The producer does not redistribute rating mass when rikishi enter, leave or
become inactive. It performs only ordinary bout-driven Elo updates.

### Prediction and update

For each eligible bout between rikishi \(A\) and \(B\), use the ratings that
exist immediately before the bout:

\[
p_A = \frac{1}{1+10^{(R_B-R_A)/400}}
\]

Record the prediction before observing the result. After the result
\(S_A\in\{0,1\}\) is revealed, update:

\[
R_A' = R_A + 35(S_A-p_A)
\]

\[
R_B' = R_B + 35((1-S_A)-(1-p_A))
\]

The bout must not influence its own prediction or any earlier prediction.

## Bout eligibility

The experiment consumes every post-1988 `BoutResult` whose outcome pair is
exactly `{W, L}`. The kimarite is irrelevant. In particular, a `W/L` result
whose decision is `"blank"` is an eligible observed bout; `"blank"` means that
the kimarite is unavailable, not that the result is unavailable.

`FS/FP` and `DRAW/DRAW` results receive neither a prediction nor a rating
update. Cross-division bouts and eligible bouts involving a participant outside
the represented banzuke remain included. The producer uses stable `RikId`
values and observed outcomes; it has no banzuke-membership requirement.

The analysis trusts the structural contracts of `History`, `BashoState`,
`Summary`, `DailyResults`, `ResultLookup` and `BoutResult`. It does not
revalidate torikumi or add defensive checks for states excluded by those
contracts.

`Chii` and `RikId` are computational domain values. Chii strings and shikona
are presentation strings only and must not drive identity, ordering, grouping
or any other calculation. Proposal 1 does not require chii for its computation.

## One-pass evaluation

The complete eligible sequence is processed exactly once in chronological
order.

There is no predeclared training prefix. Early predictions are not discarded
as warm-up. They are part of the evidence about the cold-start behaviour of
Basic Elo.

For each eligible bout, record at least:

- date, basho and day;
- deterministic bout identity;
- both stable rikishi identifiers;
- both pre-bout ratings;
- predicted probability for the recorded orientation;
- observed binary result;
- both post-bout ratings;
- number of earlier rated bouts for each rikishi;
- per-bout log loss;
- per-bout Brier score.

The retained forecast rows are the boundary between rating production and
evaluation. Evaluation must consume those recorded pre-bout forecasts; it must
not reconstruct historical predictions from final ratings.

## Reference predictor and loss

The first reference predictor assigns 50% to every eligible bout.

For outcome \(y_t\) and Basic Elo probability \(p_t\), calculate:

\[
L_t^{\mathrm{log}}
=
-\left[y_t\log(p_t)+(1-y_t)\log(1-p_t)\right]
\]

and:

\[
L_t^{\mathrm{Brier}}=(p_t-y_t)^2
\]

The corresponding 50% reference losses are:

\[
L_{0.5}^{\mathrm{log}}=\log 2
\]

and:

\[
L_{0.5}^{\mathrm{Brier}}=0.25
\]

The principal time-varying quantity is the mean paired loss difference over a
reported group of bouts:

\[
D = \operatorname{mean}(L_{\mathrm{BasicElo}}-L_{0.5})
\]

Therefore:

- \(D<0\) means Basic Elo performed better than the 50% predictor;
- \(D=0\) means no measured difference;
- \(D>0\) means Basic Elo performed worse than the 50% predictor.

Mean log loss is the primary score. Brier score is a secondary view with a
more immediately interpretable numerical scale.

## Predictive-behaviour curves

The experiment must show how predictive loss changes through chronological
time. At minimum, report:

- loss difference grouped by basho;
- rolling mean log-loss difference;
- rolling mean Brier-score difference;
- number of evaluated bouts supporting each displayed estimate;
- cumulative mean loss difference as a separate long-run view;
- uncertainty appropriate to the chosen grouping.

Individual bout losses are too noisy to serve as the main curve. Basho is the
natural first aggregation block. Rolling views must use several predeclared,
clearly labelled window lengths so that the apparent shape is not an artefact
of one convenient smoothing choice.

The predeclared rolling windows are 6, 12 and 24 complete basho.

Cumulative and rolling curves answer different questions. Cumulative means
retain the effect of the initial cold-start period indefinitely; rolling means
make local changes more visible. Neither replaces the other.

## Meaning of “better” and “a while”

This proposal does not define a true or intrinsic warm-up period. Constant-K
Elo has no internal event at which warm-up becomes complete, and new rikishi
continue to enter without prior ratings.

The first report may make statements such as:

- the estimated paired loss difference first crossed zero after a reported
  number of basho;
- it remained on one side of zero for a reported interval;
- an uncertainty interval first excluded zero at a reported point;
- the apparent timing was or was not stable across rolling-window choices.

Such statements describe the observed curve. They must not be presented as an
Elo-defined warm-up completion rule.

If the evidence does not support a precise account of “a while,” the report
must say so.

## Uncertainty

Bouts within a basho and repeated bouts involving the same rikishi are not
independent observations.

The first uncertainty method is a fixed-seed basho-block bootstrap within each
complete rolling window. It produces pointwise 95% intervals for the paired
mean loss difference. The output must record the seed, number of resamples,
number of basho and number of bouts, and must not imply more precision than the
dependency structure supports.

## Required verification

Automated tests must demonstrate that:

- predictions use only ratings produced by earlier eligible bouts;
- each bout is recorded before its result updates the ratings;
- changing a future result cannot change an earlier forecast;
- chronological ordering is deterministic;
- excluded results receive neither forecasts nor updates;
- the two predicted win probabilities sum to one;
- constant-K updates are zero-sum for every rated bout;
- the update equations behave correctly for wins and losses;
- adding a constant to every initial rating leaves predictions unchanged;
- stable rikishi identity survives name changes;
- repeated runs over identical input produce identical forecast rows.

## Required outputs

Produce:

1. A reusable chronological prediction-and-update implementation for the fixed
   Basic Elo producer.

2. A reusable evaluator over immutable pre-bout forecast rows.

3. Automated tests for chronology, updating, eligibility and invariants.

4. One machine-readable row per eligible bout.

5. Basho-level, rolling and cumulative loss tables.

6. Human-readable predictive-behaviour curves with uncertainty.

7. A concise report describing:
   
   - the post-1989 dataset and eligibility rules;
   - the exact Basic Elo definition;
   - the chronological one-pass method;
   - the 50% reference predictor;
   - the observed loss curves;
   - what can and cannot be said about “better” and “a while”;
   - limitations and unresolved questions.

8. Exact commands or documented steps needed to reproduce the outputs.

Generated bulk data belongs in the project’s normal output location and should
not be committed unless repository policy changes.

## Decision boundary

This experiment ends when the fixed Basic Elo run and its predictive-behaviour
curves are reproducible, verified and interpreted at the level supported by
the evidence.

It does not end by selecting a new value of \(q\), a new K policy, an entrant
prior or another rating model. Any such investigation is a later proposal
under the wider aims. `Proposed next steps.md` records the current intended
sequence of those follow-on experiments without changing this proposal's
decision boundary.
