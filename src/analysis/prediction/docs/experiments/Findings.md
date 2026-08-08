# Findings: Basic Elo Predictive Behaviour from 1989

## Status

Consolidated findings from Proposal 1, Proposal 2, Proposal 2b, Proposal 3,
Proposal 4, Proposal 5 and Proposal 6.
This is an interim research account under the wider aims in `Aims.md`, not a
selection of a preferred Elo model.

## Experiment held fixed

The principal baseline is one chronological pass through the represented
1989/01–2026/07 results:

```text
q = 400
k = 35
initial rating = equal 1500
rating identity = RikId
eligible result = W/L, irrespective of kimarite
rating persistence = permanent
reference forecast = 50%
```

There are 224 represented basho, 579,426 evaluated W/L bouts and 3,022 excluded
FS/FP results. Blank kimarite does not exclude an observed W/L result. Every
forecast is produced before its result updates the ratings.

The common initial value 1500 is arbitrary: translating every rating by the
same constant changes no probability. The equality of the initial ratings is
an externally imposed initial condition and is a substantive assumption.

## Reading the losses

The charts show Basic Elo loss minus the loss of always predicting 50%.
Negative values favour Basic Elo.

Log loss measures the probability assigned to the result that occurred and
penalizes confident errors strongly. Brier loss is squared probability error.
The neutral predictor has mean log loss 0.693147 and mean Brier loss 0.25.

The 50% comparator is not merely a convenient mathematical baseline. Torikumi
may be formed with the intention or effect of producing competitive bouts,
although its exact formation policy is unknown. A small improvement over 50%
can therefore represent residual predictive information within an already
balanced set of contests. The observed concentration of final records around
8–7 and 7–8 is compatible with balanced outcomes, but it has not been used as
evidence in these experiments and does not by itself establish a torikumi
mechanism.

## Finding 1: Basic Elo is modestly predictive overall

Across every eligible bout, equal-initialization Basic Elo has:

| Measure | Basic Elo | 50% reference | Reduction |
|---|---:|---:|---:|
| Mean log loss | 0.682608 | 0.693147 | 1.5% |
| Mean Brier loss | 0.244614 | 0.250000 | 2.2% |

Thus Basic Elo extracts useful predictive information over the complete epoch,
but the average advantage is modest.

The all-bout rolling curves initially perform worse than 50%. Their first
persistently favourable values occur at 2000/03 for the 6- and 12-basho
windows and at 2000/11 for the 24-basho window. These are descriptive crossings
of overlapping curves, not an identified intrinsic warm-up duration.

## Finding 2: Sekitori and sub-sekitori tell different stories

All 579,426 bouts continue to update the ratings in both subgroup experiments.
A bout is evaluated only if both participants belong to the domain under
consideration.

### Sekitori

The sekitori evaluation contains 106,905 bouts:

| Measure | Basic Elo | 50% reference | Reduction |
|---|---:|---:|---:|
| Mean log loss | 0.674671 | 0.693147 | 2.7% |
| Mean Brier loss | 0.241227 | 0.250000 | 3.5% |

The first defined rolling estimates already favour Basic Elo. Their pointwise
95% intervals first lie wholly below zero between 1990/09 and 1993/09,
depending on window length. The decade-long early underperformance in the
all-bout curves therefore does not describe sekitori bouts.

Sekitori performance improves until the early 2010s and then deteriorates. The
best log-loss differences occur at 2011/09, 2012/03 and 2013/05 for the 6-,
12- and 24-basho windows. At 2026/07 their respective differences are
-0.007635, -0.011390 and -0.011820. The 6-basho endpoint interval includes
zero; the 12- and 24-basho endpoint intervals remain below zero.

The decline means that Elo's advantage over 50% becomes smaller. It does not
mean that the longer-window sekitori predictions are worse than 50% at the end
of the epoch. Its cause has not been established.

### Sub-sekitori

The complementary evaluation contains 469,959 bouts:

| Measure | Basic Elo | 50% reference | Reduction |
|---|---:|---:|---:|
| Mean log loss | 0.684398 | 0.693147 | 1.3% |
| Mean Brier loss | 0.245379 | 0.250000 | 1.8% |

The sub-sekitori curves reproduce the long initial underperformance. Their
first persistently favourable values occur at 2001/01, 2001/07 and 2002/01 for
the three rolling windows. This locates the all-bout early pattern primarily in
the much larger lower-division evaluation population.

The later trajectory is the opposite of the sekitori trajectory. Sub-sekitori
performance continues improving, with the best rolling values occurring around
2023–2025. At 2026/07 all three endpoint intervals remain wholly below zero.
Consequently, the aggregate curve conceals contrary movements in its two main
populations.

The subgroup populations deliberately exclude cross-boundary bouts. There are
2,555 ranked sekitori/sub-sekitori cross-boundary bouts. Seven additional bouts
involve an unranked participant because of the History defect described below.

## Finding 3: A retrospective Chii prior helps only partly

Proposal 3 tests whether equal initialization creates the long sub-sekitori
transition. The equal-initialization pass supplies a retrospective prior:

1. At each basho start, carried ratings are associated with exact Chii values.
2. Each basho snapshot is translated to a common mean of 1500.
3. The last ten observations at each exact Chii are averaged.
4. Missing Chii are interpolated by ordered Chii position.
5. No monotonicity is imposed.

The resulting audit surface contains 991 chii ordinals and 9,227 retained
observations. Of the mapped Chii, 973 have observed trailing means and 18 use
interpolation or an edge. There are 501 adjacent reversals in the nominal
stronger-to-weaker direction; these were retained rather than made monotonic.
The reversal count describes the raw, exact-Chii surface and does not by itself
prove that official rank and ability are unrelated.

Whole-epoch results are:

| Evaluation population | Equal initialization | Chii prior | Change in log loss |
|---|---:|---:|---:|
| All eligible bouts | 0.682608 | 0.682259 | -0.000349 |
| Both participants sekitori | 0.674671 | 0.676900 | +0.002229 |
| Both participants sub-sekitori | 0.684398 | 0.683407 | -0.000991 |

The Chii prior modestly improves the all-bout and sub-sekitori results but
worsens the sekitori result.

For sub-sekitori, the dates after which the rolling log-loss differences remain
favourable change as follows:

| Window | Equal initialization | Chii prior |
|---|---|---|
| 6 basho | 2001/01 | 2000/07 |
| 12 basho | 2001/07 | 2000/07 |
| 24 basho | 2002/01 | 2001/07 |

The prior makes some short-window estimates favourable much earlier, but those
curves cross zero again. Persistent superiority advances by only six to twelve
months. The experiment therefore supports the initialization hypothesis only
partly: uniform initialization contributes to the early penalty, but does not
explain most of its duration.

The Chii prior is derived from later outcomes also evaluated by the second
pass. It is an oracle diagnostic, not an out-of-sample model and not evidence
that this mapping could be used prospectively.

## Finding 4: Division carries most of the initialization structure

Proposal 4 compares the genuine Chii prior with two placebo families made from
exactly the same 991 rating values:

- a global permutation assigns values among all Chii;
- a within-division permutation assigns values only inside Makuuchi, Juryo,
  Makushita, Sandanme, Jonidan or Jonokuchi.

There are 100 fixed-seed mappings of each kind. Their 5th-to-95th ordered ranges
describe sensitivity to the mapping; they are not sampling intervals for the
historical bouts.

Global randomization is severely damaging, particularly for sub-sekitori
bouts. At 12 basho its median all-bout log loss is 0.835463, compared with
0.703747 for equal initialization and 0.695441 for genuine Chii. None of the
100 global mappings beats equal or genuine at any declared all-bout or
sub-sekitori horizon. Arbitrary differentiation is therefore harmful, and the
correct association of ratings with broad rank position is consequential.

Preserving division changes the result. For all and sub-sekitori bouts,
genuine Chii is best through the first 12 basho, but the cumulative ordering
reverses by 30 basho. Complete-epoch log losses are:

| Evaluation population | Equal | Genuine Chii | Within-division median |
|---|---:|---:|---:|
| All eligible bouts | 0.682608 | 0.682259 | 0.681900 |
| Both participants sekitori | 0.674671 | 0.676900 | 0.676580 |
| Both participants sub-sekitori | 0.684398 | 0.683407 | 0.683038 |

For the complete epoch, 81 of 100 within-division mappings beat genuine Chii
on all-bout log loss and 75 beat it on sub-sekitori log loss. Their Brier
results are stronger still: 97 and 96 respectively beat genuine. Almost every
within-division mapping beats equal initialization for those populations.

This result suggested two possible effects: exact Chii might supply useful
initial information for the January 1989 incumbents, while broad division
membership accounts for most of the durable initialization benefit. Proposal 4
could not separate exact-Chii information from the cost of the random
within-division variation. Proposal 5 tests that distinction directly and
supersedes the tentative exact-Chii interpretation below.

Sekitori remains different. Equal initialization has the lowest observed
complete-epoch log loss, followed by the within-division median, genuine Chii
and the global median. The difference between the best and worst of those four
is 0.003319 nats per bout, about 0.0048 bits per bout. It is small. Proposal 4
does not supply sampling uncertainty or a substantive threshold for that
difference, so the observed ordering should not be described as establishing
an important sekitori advantage.

All genuine and randomized priors retain Proposal 3's use of future outcomes.
Proposal 4 identifies structure inside that oracle construction; it does not
make any prior prospective.

## Finding 5: Division means outperform exact Chii

Proposal 5 replaces every exact-Chii value in a division by the unweighted
arithmetic mean of the completed Proposal 3 values in that division:

| Division | Initial rating | Chii values |
|---|---:|---:|
| Makuuchi | 2263.483 | 64 |
| Juryo | 1984.347 | 28 |
| Makushita | 1715.160 | 123 |
| Sandanme | 1452.466 | 204 |
| Jonidan | 1251.177 | 420 |
| Jonokuchi | 1221.737 | 152 |

The mean is the expected rating assigned to any fixed Chii by Proposal 4's
uniform within-division permutation. Unlike an individual permutation, it
removes all unsupported within-division variation. Every newly encountered
RikId receives the mean for its first represented division; ratings then
persist and update exactly as in Basic Elo.

Complete-epoch proper scores are:

| Population | Equal log | Exact-Chii log | Division log | Equal Brier | Division Brier |
|---|---:|---:|---:|---:|---:|
| All eligible bouts | 0.682608 | 0.682259 | **0.677888** | 0.244614 | **0.242338** |
| Both participants sekitori | **0.674671** | 0.676900 | 0.675728 | **0.241227** | 0.241584 |
| Both participants sub-sekitori | 0.684398 | 0.683407 | **0.678299** | 0.245379 | **0.242471** |

For all bouts, division-only improves log loss over equal initialization by
0.004720 nats per bout. For sub-sekitori the improvement is 0.006099. Measured
as the reduction from the neutral log loss, division initialization increases
the observed all-bout gain by about 45% and the sub-sekitori gain by about 70%
relative to equal initialization. These are appreciably larger than the gains
from exact Chii, although no experiment has supplied a threshold for practical
importance or sampling uncertainty.

Division-only lies below Proposal 4's entire within-division 5th-to-95th
ordered range at every declared all-bout and sub-sekitori horizon. It also
outperforms exact Chii from the first six-basho horizon onward. The tentative
Proposal 4 suggestion that exact Chii helps the epoch incumbents is therefore
rejected: the useful early information is division membership, while the
fine-grained exact-Chii surface adds observed loss.

The difference between a division mean and a randomized within-division
mapping is substantive. Within-division rating ranges are wide: approximately
1704 to 2611 in Makuuchi and 956 to 1462 in Jonidan. Random permutations retain
that spread and create unsupported rating differences. Because log and Brier
loss penalize the resulting probability errors, the score of a random mapping
need not equal the score produced by its mean rating. Collapsing to the mean
removes this source of forecast noise.

The effect is not confined to the epoch population. Over bouts after the first
60 basho, division-minus-equal mean log-loss differences remain -0.002285 for
all bouts and -0.003402 for sub-sekitori bouts. Division-level initialization
therefore continues helping later lower-division entrants, although less than
during the first 60 basho. Its cumulative loss first becomes lower than equal
at 1989/05 for both populations and first becomes lower than the neutral
forecast at 1990/03 for all bouts and 1990/05 for sub-sekitori bouts. These are
cumulative landmarks and should not be confused with Proposal 1's rolling
crossings.

Sekitori remains the exception. Division-only cumulative loss is lower than
equal from 1990/01 through 2006/01, but equal becomes lower at 2006/03 and ends
ahead by 0.001057 nats per bout. After the first 60 basho, division-only is
worse by 0.002190 nats per sekitori bout. This is consistent with initial
lower-division information losing relevance after a rikishi has accumulated
substantial bout evidence, but the experiment does not identify a cause. The
complete-epoch difference is small and has no attached sampling interval or
substantive threshold.

Proposal 5 establishes a strong retrospective diagnostic conclusion: the
early cumulative penalty under equal initialization is substantially reduced
by a coherent division-level rating state, and exact-Chii differentiation is
unnecessary and counterproductive. It does not establish that the six division
differences could have been estimated before 1989. The values inherit future
outcomes from Proposal 3. Prospective validity requires division constants
estimated from an earlier period and frozen before a later evaluation period.

## Finding 6: Basic Elo decisively beats the independent 50-50 null

Proposal 6 gives the neutral forecast an operational interpretation. A
bookmaker offers evens because every bout is said to be a 50-50 event. Basic
Elo selects the pre-bout favourite and stakes £p, where p is that favourite's
forecast probability. A winning bet earns £p, a losing bet loses £p, and an
exactly 50-50 forecast causes no bet.

The statistic represents one bout selected uniformly from each population on
every represented day. Rather than add noise by making one arbitrary
selection, the experiment averages profit and stake over every eligible bout
on the day. The 15 daily averages are summed, then averaged over all 224
basho. Consequently, every plotted value is a complete-epoch mean profit per
basho; the fair-coin histogram is not a distribution of individual-basho
profits.

The historical results are:

| Population | Mean stake per basho | Mean profit per basho | Return on stake | Fair-coin 95% range |
|---|---:|---:|---:|---:|
| All eligible bouts | £8.6096 | £1.2229 | 14.20% | -£0.0231 to £0.0233 |
| Both participants sekitori | £9.2475 | £1.4440 | 15.62% | -£0.0572 to £0.0521 |
| Both participants sub-sekitori | £8.4620 | £1.1830 | 13.98% | -£0.0259 to £0.0271 |

Each of 2,000 null histories retains the real chronology, participants and
population membership but replaces every result by an independent fair-coin
draw. Basic Elo is restarted at equal ratings and rebuilt from the simulated
results, so it is free to chase the random winning and losing sequences in
each history. The null complete-epoch mean profits are approximately
symmetric around zero. For all bouts their observed minimum and maximum are
-£0.0385 and £0.0452, and their mean is £0.00007.

No null history reaches the historical result in any population. The fixed
one-sided Monte Carlo comparison is therefore `(0 + 1) / (2,000 + 1)`, or
0.00049975, for each population. This is the finite simulation's resolution,
not a claim that the underlying probability is exactly 0.00049975. The
historical result is so far beyond the simulated range that further
replicates would not alter the substantive conclusion.

Under this declared test, the historical directional return is incompatible
with the hypothesis that the represented results are independent 50-50
events. The earlier description of Basic Elo as only "very, very slightly"
better than neutral is therefore not appropriate for this operational
measure. The log-loss improvement is numerically small, but at deliberately
mispriced evens the accumulated ability to select the more likely winner has
a substantial expected return.

This conclusion is narrower than a general endorsement of Elo probabilities.
The betting rule primarily rewards choosing the correct side; it does not
show that the forecast probabilities are calibrated. The odds are
hypothetical, the daily selection is evaluated by its expectation rather than
one realized betting path, and the null is specifically independent fair-coin
outcomes. The experiment is evidence about predictive information, not a
claim about an available sumo gambling strategy.

## What the experiments establish

The evidence currently supports the following statements:

- Basic Elo with q=400 and k=35 predicts represented outcomes better than a
  neutral 50% forecast over the complete post-1988 epoch.
- Its probability-staked historical return at hypothetical evens is decisively
  inconsistent with independent 50-50 results; none of 2,000 complete
  fair-coin histories approaches the observed return.
- Its average advantage is modest but is not uniform across populations or
  historical periods.
- Sekitori predictions are useful much earlier and are stronger over the whole
  epoch than sub-sekitori predictions.
- The apparent decade-long all-bout transition is principally a
  sub-sekitori phenomenon.
- Sekitori predictive performance deteriorates after its early-2010s peak,
  while sub-sekitori performance continues improving.
- A future-informed exact-Chii prior improves sub-sekitori prediction only
  slightly; replacing it with division means produces a substantially larger
  observed improvement.
- Division membership contains the useful initialization structure in these
  oracle experiments. Unsmoothed exact-Chii differentiation is unnecessary and
  increases loss relative to division means.
- The division prior continues improving all-bout and sub-sekitori scores after
  the first 60 basho; its benefit is not solely an epoch-incumbent effect.

The evidence does not establish:

- a universal Elo warm-up duration;
- why sekitori performance deteriorates after the early 2010s;
- the torikumi formation policy;
- that Chii is a direct or monotonic measurement of ability;
- that the retrospective Chii prior is a legitimate predictive model;
- that the six division differences could have been estimated prospectively
  before 1989;
- that every observed score difference is statistically or substantively
  important under a declared threshold (Proposal 6 supplies such a comparison
  for its betting statistic, not for every log-loss or model difference);
- that q=400 and k=35 are optimal.

## Known History defect

RikId 13011 has seven represented W/L bouts in 2026/07 despite being absent
from that basho's banzuke. This violates the History contract and is recorded
in `analysis/sumo_history/README.md`. Proposal 3 temporarily assigns the
weakest-edge prior to this participant so the represented W/L rating domain is
not silently changed. That accommodation is recorded in its manifest.

## Evidence and audit files

- [Proposal 1 report](../../../../../files/output/prediction/proposal_1/proposal_1_1989_01_to_2026_07/report.md)
- [Sekitori report](../../../../../files/output/prediction/sekitori_only/sekitori_only_1989_01_to_2026_07/report.md)
- [Sub-sekitori report](../../../../../files/output/prediction/sub_sekitori_only/sub_sekitori_only_1989_01_to_2026_07/report.md)
- [Chii-initialization report](../../../../../files/output/prediction/chii_initialisation/chii_initialisation_1989_01_to_2026_07/report.md)
- [Chii ordinal-to-rating mapping](../../../../../files/output/prediction/chii_initialisation/chii_initialisation_1989_01_to_2026_07/chii_prior.csv)
- [Retained Chii observations](../../../../../files/output/prediction/chii_initialisation/chii_initialisation_1989_01_to_2026_07/chii_prior_observations.csv)
- [Randomized-prior report](../../../../../files/output/prediction/randomised_chii_prior/randomised_chii_prior_1989_01_to_2026_07/report.md)
- [Division-only report](../../../../../files/output/prediction/division_initialisation/division_initialisation_1989_01_to_2026_07/report.md)
- [Division prior](../../../../../files/output/prediction/division_initialisation/division_initialisation_1989_01_to_2026_07/division_prior.csv)
- [Fair-coin null report](../../../../../files/output/prediction/fair_coin_null/fair_coin_null_1989_01_to_2026_07/report.md)
- [Fair-coin null summary](../../../../../files/output/prediction/fair_coin_null/fair_coin_null_1989_01_to_2026_07/null_summary.csv)

## Next research questions

Proposal 5 creates two distinct follow-up questions. A sensitivity experiment
can vary the five division differences to determine how special their ordering
and magnitudes are. A prospective experiment must instead estimate division
constants from an earlier period, freeze them, and evaluate later untouched
results. Random constants address sensitivity, not prospective validity.

Constant update-rate sensitivity, the 1958–1988 sekitori regime and
Chii-dependent update rates remain later candidates. The post-2011 sekitori
deterioration also merits a bounded diagnostic separating changes in forecast
confidence from changes in the relationship between rating differences and
outcomes. Proposal 6 also makes calibration a concrete separate question:
Basic Elo clearly identifies the more likely winner, but that result alone
does not say whether its numerical probabilities are reliable.
