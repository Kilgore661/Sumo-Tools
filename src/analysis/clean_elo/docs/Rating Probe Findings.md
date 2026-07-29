# Rating Probe: Questions, Methods, and Initial Findings

## Status and scope

This document records the exploratory work performed with `clean_elo` through
29 July 2026. The numerical findings below use the complete-results era
starting in January 1989.

The source rating-probe run is:

```text
files/output/analysis/clean_elo/rating_probe/2026-07-28_16-47-43
```

The source monotonicity-probe run is:

```text
files/output/analysis/clean_elo/monotonicity_probe/2026-07-29_12-34-12
```

The results are provisional research findings, not claims built into the Elo
simulator.

The 1989+ rating run used:

| Setting | Value |
|---|---|
| Start date | 1989/01 |
| Initial rating policy | Constant 1517 |
| k policy | Default FIDE-style divisional policy |
| Elo q scale | 900 |
| Count absences | No |
| Rated bouts | 579,427 |
| Ignored paired fusen results | 3,021 |
| Rikishi-basho rating observations | 152,059 |
| Distinct BP4 indices | 484 |

The simulation uses ordinary Elo updates, persistent ratings, and
end-of-basho mean restoration. It does not calculate Glicko-2 rating deviation
or volatility and does not perform Bayesian posterior inference.

The historical run is also not the theoretical "pure Elo model" in the
strict sense used during the investigation. That idealization assumes a
closed population, fixed abilities, and fixed k. The historical population is
open, abilities change, and this run used the default divisional k policy.

## Research motivation

The original motivation for persistent ratings was incomplete historical
coverage below sekitori level. Before 1989, a lower-division rikishi can appear
occasionally in the recorded data. Reusing a rating acquired on an earlier
appearance may preserve more information than repeatedly assigning the
initial rating, provided the missing intervals are not too long. As the
sub-sekitori data becomes denser toward 1989, the resulting ratings may become
progressively more informative.

The present analysis first uses 1989 onward, where results are complete, to
study a more basic question: what relationship appears between Elo ratings and
banzuke chii?

For exploration, we adopt a deliberately strong point of view:

- the JSA's significance for each chii is treated as stable through time;
- two rikishi holding the same binned index are treated as occupying the same
  category for this purpose;
- a better chii, represented by a lower ordinal, is expected to correspond to
  a higher mean Elo rating.

This is a useful hypothesis, not an assertion that the JSA is infallible or
that chii have actually been immutable.

## Binning

Four policies control the granularity of the chii-derived index:

1. BP1 retains number, side, and annotation.
2. BP2 removes annotations.
3. BP3 removes annotations and sides.
4. BP4 also removes the number from Y, O, S, and K.

An index is not itself a chii. Its ordinal is constructed by replacing
components removed by the policy with zero. The ordinal is meaningful only
together with its binning policy.

BP1 is the least aggregated view. BP4 was expected to suppress distinctions
such as east versus west and unusual numbered sanyaku positions without
discarding the main ordinal structure. The current monotonicity test uses BP4.

Mae-zumo (`Mz`) participants are not meaningfully on the banzuke and are not
assigned a modeled banzuke index. A bout endpoint whose rikishi is absent from
the basho's banzuke is itemised as a data-validation occurrence because the
bout alone supplies no chii to convert.

## Correct temporal correspondence

The appropriate comparison is:

> current chii versus rating at the start of the same basho.

Consequently, the rating probe uses one observation per rikishi-basho. It does
not treat all 15 makuuchi bouts as 15 observations of the relationship between
the start-of-basho chii and rating. Daily ratings change after results, but the
chii does not.

Comparing an end-of-basho rating with the next chii would express the same
temporal relationship at the next boundary, subject to intervening
normalisation and participation.

## Meaning of confidence in this probe

The probe estimates the mean start-of-basho rating associated with an index.
Its confidence interval is an interval for that mean under the stated sampling
model. It is not:

- a probability that an individual rikishi's ability lies in the interval;
- a Glicko-2 rating deviation;
- a Bayesian credible interval;
- evidence that an Elo rating has permanently converged to a true value.

With fixed nonzero k, even an ideal stationary Elo system continues to
fluctuate. The relevant limiting idea is a distribution of possible rating
states, not eventual permanent residence at a single rating. The present
probe asks the narrower empirical question of how precisely the mean rating
at each index is estimated.

More observations tend to reduce the standard error only in combination with
the observed spread. Furthermore, repeated rikishi-basho observations are
dependent, so the naive \(1/\sqrt n\) improvement may exaggerate the available
information.

## Shape of the 1989+ BP4 means

The BP4 mean-rating curve has a clear large-scale structure:

- it begins at its maximum at Y;
- it drops steeply through sanyaku and upper maegashira;
- it generally continues downward through makuuchi, juryo, makushita,
  sandanme, and approximately Jd100;
- unusual or sparsely occupied tail positions contain visible reversals and
  noise.

The most striking makuuchi reversal begins around M13. Mean ratings stop
falling and then rise toward M18.

| Index | Support | Mean rating | Naive relative margin |
|---|---:|---:|---:|
| M12 | 439 | 1926.98 | 0.94% |
| M13 | 438 | 1929.76 | 0.89% |
| M14 | 427 | 1933.40 | 0.89% |
| M15 | 384 | 1957.31 | 0.74% |
| M16 | 268 | 1990.87 | 0.73% |
| M17 | 87 | 2031.73 | 0.78% |
| M18 | 6 | 2063.15 | 1.51% |

Here the naive relative margin is the Student-t 95% margin divided by the
absolute mean rating. It is not normalized to a rating range and is not
invariant to a common shift of all Elo ratings.

Support declines sharply, especially at M17 and M18. However, the calculated
relative margin does not increase in parallel: it falls through M16, remains
similar at M17, and rises noticeably only at M18.

This occurs because:

\[
SE=\frac{s}{\sqrt n}
\]

and the observed within-index standard deviation also falls substantially.
Lower support alone therefore does not explain the observed confidence
measure.

The appropriate empirical statement is:

> Mean rating rises while support declines, but the calculated naive
> uncertainty of the means generally does not rise with it.

That does not prove the upturn is an immutable rank effect. In particular,
the small observed spread at rare ranks may itself reflect selection,
historical composition, or chance.

## Monotonicity hypothesis

The formal null hypothesis tested was:

> Expected BP4 mean start-of-basho Elo is a non-increasing function of chii
> ordinal.

The test compares the observed group means with the best weighted
non-increasing isotonic fit. Under the naive independent-normal model, the
M1--M18 result was:

| Quantity | Result |
|---|---:|
| Lack-of-fit statistic | 215.260076 |
| Bootstrap simulations | 10,000 |
| Simulations at least as extreme | 0 |
| Plus-one p-value | 0.00009999 |

The fitted null model pools M8 through M18 at approximately 1963.61. Notable
standardized residuals include:

| Index | Standardized residual |
|---|---:|
| M12 | -3.98 |
| M16 | +3.69 |
| M17 | +8.50 |
| M18 | +8.23 |

The Y--Jd100 scope also produced zero exceedances in 10,000 bootstrap
simulations, with a lack-of-fit statistic of 338.154669. This is not
independent confirmation of the makuuchi result because the broader scope
contains the same indices. Other important departures include J14.

## Tail sensitivity

Exploratory reruns ending at successive maegashira ranks produced:

| Scope | Statistic | Bootstrap p-value |
|---|---:|---:|
| M1--M12 | 0.000000 | 1.0000 |
| M1--M15 | 9.442498 | 0.0996 |
| M1--M16 | 49.506597 | <0.0001 |
| M1--M17 | 144.069409 | <0.0001 |
| M1--M18 | 215.260076 | <0.0001 |

The rejection therefore does not depend on M18's six observations. Under the
naive model, the incompatibility is already decisive when M16, with support
268, is included.

Because these cutoffs were examined after seeing the curve, they are
descriptive sensitivity checks rather than separately pre-registered
hypothesis tests.

## What has and has not been established

Under the assumptions of the present test, the 1989+ data rejects:

> Expected start-of-basho Elo is an immutable non-increasing function of BP4
> chii ordinal.

This is narrower than saying that chii do not measure performance. Chii and
Elo may disagree because they summarize results differently:

- Elo carries information across a longer history;
- a banzuke position depends heavily on the most recent basho;
- the banzuke has structural and population-size constraints;
- rare tail ranks may exist only in particular eras or banzuke
  configurations;
- injury, absence, promotion rules, and selection can affect occupancy;
- both Elo and chii are derived, directly or indirectly, from bout results.

The current analysis also does not justify complete Bayesian confidence
claims. The confidence intervals and bootstrap treat rikishi-basho
observations as independent, despite repeated rikishi, recursive ratings,
shared opponents, temporal dependence, and the result-derived banzuke.

The defensible current conclusion is therefore:

> A simple, time-invariant, monotonic mapping from BP4 chii to mean Elo does
> not fit the 1989+ data under the naive uncertainty model. The lower
> makuuchi reversal is not explained merely by low support.

## Next statistical questions

Natural extensions include:

- cluster or block resampling by rikishi, basho, and era;
- separating cohort and historical banzuke-structure effects;
- repeating the comparison under BP1 through BP4;
- testing sensitivity to initial-rating and k policies;
- studying whether a mapping from results to subsequent chii predicts banzuke
  placement better than a static chii-to-rating mapping;
- repeating the analysis through the progressively incomplete pre-1989 era;
- comparing pure Elo with Glicko-2 or a Bayesian dynamic-ability model.
