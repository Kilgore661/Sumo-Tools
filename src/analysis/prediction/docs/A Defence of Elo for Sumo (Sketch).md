# A Defence of Elo for Sumo

## Status and purpose

This is the working structure for a reader-facing argument. It is not yet the
finished document.

The experimental documents record how the research developed, including
questions that proved unhelpful and conclusions later revised. This document
will instead present the cleanest claim now supported by the work. It should
begin in ordinary language and add successive layers of explanation and
mathematical detail. A casual sumo follower should be able to stop after the
opening; a statistically sceptical reader should be able to continue through
the complete specification, evidence and limitations.

The intended conclusion is narrow:

> At least one precisely specified Basic Elo system has demonstrable
> predictive power for the represented professional sumo results after 1988.

The document will not argue that this system is optimal. Predictive power
depends on such choices as the epoch, initial ratings, q, k and the population
of bouts being evaluated. We have investigated some of those choices but not
the space of possible Elo-family models.

## Layer 1: the result in ordinary language

Open as directly as possible:

> If you think that the JSA arranges matches so that the outcomes are 50-50,
> imagine a bookmaker who offers evens on every match. Using Basic Elo to
> choose which rikishi to back would historically have returned about 12% on
> the amount staked.

The next sentences need only unpack the arithmetic:

- Basic Elo's favourite won about 56% of the represented bouts.
- At evens, winning 56 bets and losing 44 returns about £12 profit for every
  £100 staked.
- Elo therefore knows something about the outcomes that the 50-50 rule does
  not.

This is the first stopping point. It should not be burdened with the full model
definition or the history of the experiments.

### Evidence required before final wording

The approximate 12% figure has been calculated from Proposal 1's immutable
forecast ledger, but it is not yet a first-class generated artifact. Before
publication:

1. freeze whether the ordinary-language statistic is bout-weighted or the
   expectation from one uniformly selected bout on each represented day;
2. add fixed-£1 stake, favourite win rate, profit and return on stake to a
   reproducible output;
3. apply the fair-coin null calculation to that same fixed-stake statistic;
4. quote the resulting value consistently throughout this document.

The likely choice is one uniformly selected eligible bout per represented day,
matching Proposal 6. The current probability-staked experiment is already a
complete proof of predictive information, but its 14.2% return is not the
simplest opening illustration.

## Layer 2: what we mean by Elo

Suggested transition:

> For the more interested reader, here is what an Elo rating system is and how
> we applied it to sumo.

The eventual section should explain, without initially requiring equations:

- every rikishi has a rating;
- a difference between two ratings produces a predicted win probability;
- after the result, the winner gains and the loser loses rating points;
- a surprising result moves the ratings further than an expected result;
- the prediction is recorded before the result updates either rating;
- ratings belong to stable rikishi identities and are never forgotten.

For now this section may be represented by an ellipsis or adapted from
[Proposal 1](experiments/Proposal%201.md) and
[Architecture 1](experiments/Architecture%201.md).

The exact Basic Elo producer used in the principal demonstration is:

```text
epoch = 1989/01
q = 400
k = 35
initial rating = 1500 for every newly encountered RikId
rating persistence = complete chronological pass
eligible result = W/L, irrespective of kimarite
excluded result = FS/FP or draw
forecast = before the current result update
```

All represented eligible bouts update the rating state. Sekitori and
sub-sekitori are alternative evaluation populations, not separate rating
systems.

## Layer 3: the precise claim

The final wording should be close to:

> For the represented W/L bouts from 1989/01 through 2026/07, Basic Elo with
> q=400, k=35, equal initial ratings and persistent chronological updates
> contains directional information about bout outcomes that is absent from an
> independent 50-50 producer. Its observed advantage is far outside the
> variation produced when the same Elo procedure is applied to complete
> fair-coin histories.

Terms requiring explicit definition at this layer are:

- represented result;
- pre-bout forecast;
- Elo favourite;
- independent 50-50 or fair-coin history;
- historical return;
- complete-epoch mean;
- primary and secondary evaluation populations.

The claim is existential: this model is useful. It is not a universal claim
about every initialization, parameter choice, epoch or selection of bouts.

## Layer 4: the empirical demonstration

### 4.1 Data and chronology

State the source History, its digest, the 1989/01 epoch, the inclusive final
basho and the exact result counts. Explain the predict-then-update boundary and
why later results cannot reach an earlier forecast.

Primary sources:

- [Proposal 1 specification](experiments/Proposal%201.md)
- [Proposal 1 architecture](experiments/Architecture%201.md)
- [Proposal 1 generated report](../../../../files/output/prediction/proposal_1/proposal_1_1989_01_to_2026_07/report.md)

### 4.2 The observed forecasts

Present several translations of the same forecasts and results:

- favourite win rate and fixed-stake return at hypothetical evens;
- probability-staked return and return on stake;
- mean log loss against the neutral forecast;
- mean Brier loss against the neutral forecast;
- accumulated rather than merely per-bout log-score improvement.

The section must explain rather than conceal the apparently different scales.
An improvement of 0.010539 nats per bout is numerically small, but it is an
average over 579,426 bouts. The cumulative log-score advantage is about
6,106.65 nats. A small per-bout proper-score difference is not evidence of a
small accumulated distinction.

### 4.3 Ruling out chance under the declared null

Describe the null in ordinary language before giving its formal definition:

1. retain the actual participants, dates, days, bout order and population
   membership;
2. replace every result by an independent 50-50 draw;
3. restart Basic Elo from equal ratings and rebuild it chronologically from
   those simulated results;
4. calculate the same historical statistic;
5. repeat for 2,000 complete histories.

For the existing probability-staked statistic, the all-bout historical mean
profit is £1.2229 per represented basho. The fair-coin 95% range is about
-£0.0231 to £0.0233, and none of the 2,000 histories reaches the
historical value. The add-one Monte Carlo value is 1/2,001.

Primary sources:

- [Proposal 6 specification and result](experiments/Proposal%206.md)
- [Fair-coin null report](../../../../files/output/prediction/fair_coin_null/fair_coin_null_1989_01_to_2026_07/report.md)
- [Fair-coin null summary](../../../../files/output/prediction/fair_coin_null/fair_coin_null_1989_01_to_2026_07/null_summary.csv)

This is the formal answer to the suggestion that Elo merely follows random
winning and losing streaks.

## Layer 5: the mathematical account

This layer should be intelligible to a reader with degree-level mathematics
but should not assume specialist statistical training.

### 5.1 Basic Elo equations

Give the probability and update equations, define every term, and show the
values q=400 and k=35 used here. Explain why adding a constant to every rating
does not change a forecast.

### 5.2 Evens return

If the selected rikishi wins with probability p, a fixed £1 bet at evens
has expected profit

```text
p - (1 - p) = 2p - 1.
```

Thus p=0.56 gives expected profit £0.12 per £1 staked.

### 5.3 Why the proper-score changes look small

Near 50%, fixed-stake evens profit changes linearly with the advantage over
50%, while improvements in proper scores are approximately quadratic. For a
calibrated 56-44 forecast:

```text
fixed-stake evens return = 0.12
log-loss improvement over 50% = about 0.0072 nats
Brier improvement over 50% = 0.0036
```

This reconciles the conspicuous betting return with changes in the third
decimal place. It should be stated when log loss is introduced, not discovered
only after the reader objects to its scale.

### 5.4 The Monte Carlo comparison

Define the complete-history statistic, ordered 95% range and add-one one-sided
Monte Carlo calculation. Distinguish effect size from evidence:

- log-loss or return differences describe the size in their respective units;
- the fair-coin distribution describes how incompatible the historical result
  is with the declared null.

Do not turn the simulation count into a claim that the underlying probability
is exactly 1/2,001. It is the resolution supplied by 2,000 simulations.

## Layer 6: boundaries of the claim

Keep this about the research claim rather than practical betting cautions.

What has been shown:

- one fixed Basic Elo system contains directional predictive information;
- the information is present in all-bout, sekitori and sub-sekitori
  evaluations;
- its historical probability-staked result is incompatible with the
  independent 50-50 null used in Proposal 6;
- small per-bout proper-score changes can accumulate into decisive evidence
  and a substantial return at evens.

What remains open:

- whether q=400 and k=35 are good parameter choices, rather than merely useful
  ones;
- how initialization should be chosen;
- how much warm-up is required under different initial conditions;
- how predictive performance varies through time and between populations;
- whether the numerical probabilities are calibrated;
- whether another Elo-family or non-Elo model performs better;
- what alternative dependent or non-identically distributed null models would
  show.

The unresolved questions qualify the extent and interpretation of Elo's
predictive power. They do not undo the existential demonstration that this
specified model has some.

## Layer 7: supporting research record

The chronological research account remains available for readers who want to
audit how the conclusion was reached:

- [Aims](experiments/Aims.md)
- [Consolidated experimental findings](experiments/Findings.md)
- [Proposed next steps](experiments/Proposed%20next%20steps.md)
- [Experiment specifications and architecture](experiments/)

The finished defence may revise the organization and explanatory language of
those documents retrospectively where they confused a small per-bout score
with weak evidence. Numerical results and experiment definitions must remain
unchanged unless a documented computational correction is made.

## Work needed for the finished document

1. Generate and preserve the fixed-stake 12% statistic and its matching null
   distribution.
2. Draft the omitted non-technical explanation of Elo.
3. Choose a small number of tables and charts, each serving a distinct layer.
4. Add the Basic Elo equations and the derivation connecting 56% accuracy,
   evens return, log loss and Brier score.
5. Check every quoted number against a generated artifact and link the claim
   to that artifact.
6. Have the final mathematical argument reviewed specifically for the
   distinction between discrimination, calibration, effect size and evidence.
