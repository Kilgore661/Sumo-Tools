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

## Boundary-aligned recomputation

The literal M12--M18 comparison combines different positions relative to the
Makuuchi-Juryo boundary because the number of maegashira and sanyaku positions
changes. The `boundary_rating_probe` therefore recalculated the same 1989+
ratings by position from the bottom of each basho's actual Makuuchi banzuke.

Adjacent individual slots were paired to match the toy experiment:

```text
raw bottom slots 1 and 2   -> top_bottom_1
raw bottom slots 3 and 4   -> top_bottom_2
...
raw bottom slots 13 and 14 -> top_bottom_7
```

The source run is:

```text
files/output/analysis/clean_elo/boundary_rating_probe/
  2026-07-29_14-27-29/
```

Its seven-group means were:

| Group | Support | Mean rating | Standard error |
|---|---:|---:|---:|
| top_bottom_7 | 439 | 1937.85 | 9.46 |
| top_bottom_6 | 436 | 1932.63 | 9.50 |
| top_bottom_5 | 444 | 1924.28 | 9.13 |
| top_bottom_4 | 432 | 1931.35 | 9.33 |
| top_bottom_3 | 438 | 1923.83 | 8.81 |
| top_bottom_2 | 440 | 1914.23 | 8.42 |
| top_bottom_1 | 436 | 1928.55 | 7.49 |

The endpoint difference was:

\[
1928.55-1937.85=-9.31
\]

or approximately \(-0.0103q\). The largest local reversal was the final
increase from `top_bottom_2` to `top_bottom_1`, approximately \(+14.32\).

The naive isotonic test produced:

| Quantity | Result |
|---|---:|
| Lack-of-fit statistic | 1.906533 |
| Bootstrap simulations | 10,000 |
| Bootstrap exceedances | 5,519 |
| p-value | 0.551945 |

The boundary-relative data therefore does not reject monotonicity. The curve
contains small local changes, but not the systematic endpoint reversal seen
when historically variable banzuke structures are combined under literal
M12--M18 labels.

### Why the M12--M18 endpoint reversal disappears

The literal-rank chart treats `M12`, `M13`, ..., `M18` as though each label
identified the same structural position in every basho. It does not. The
number of sanyaku and maegashira positions varies, so a literal maegashira
number can be a different distance from the Makuuchi--Juryo boundary in
different basho. The lowest available maegashira labels also occur only in
the banzuke structures that have room for them. Consequently, the observations
for `M18` are not simply a lower-ranked version of the observations for
`M12`: they are drawn from a different selection of basho and boundary
positions.

Boundary alignment replaces the printed rank number with the rikishi's actual
position above the lower edge of Makuuchi in that basho:

- `top_bottom_1` is the bottom pair of Makuuchi rikishi;
- `top_bottom_2` is the next pair above them;
- and so on.

An `M16` can therefore belong to `top_bottom_1` in one banzuke while an `M18`
belongs to `top_bottom_1` in another. This compares structurally corresponding
positions rather than assuming that the same printed rank number always has
the same relationship to the boundary.

On the literal-rank chart, the mean falls towards `M12` and then rises towards
`M18`, suggesting that the lowest printed maegashira ranks are systematically
stronger than `M12`. After boundary alignment, the mean at `top_bottom_7` is
1937.85 and the mean at `top_bottom_1` is 1928.55. The endpoint difference is
therefore \(-9.31\): the group closest to Juryo has the lower mean rating, in
the expected direction.

This does not make the boundary-aligned curve perfectly monotonic. There are
two upward steps when moving towards the boundary:

- `top_bottom_5` to `top_bottom_4`: approximately \(+7.08\);
- `top_bottom_2` to `top_bottom_1`: approximately \(+14.32\).

The latter is the larger local reversal, not the only one. The bootstrap
result (\(p=0.551945\)) says that the complete seven-point curve does not
provide evidence against monotonicity; it does not prove that every local
change is meaningful or that the underlying relationship is exactly
monotonic.

Thus, "the endpoint reversal disappears" has a specific meaning. The data no
longer supports the broad description that the bottom of Makuuchi rises above
the ranks farther from the boundary. It does not mean that every adjacent
boundary group is ordered or that all irregularity has vanished. The original
M12--M18 upturn was substantially a consequence of using historically
variable literal ranks as though they were a stable boundary coordinate.

## BP4 lower-maegashira cutoff series

The `bp4_cutoff_probe` tested whether successively ignoring lower-maegashira
bouts produces a monotonic BP4 mean-rating sequence from Y through the last
retained M rank. The source run is:

```text
files/output/analysis/clean_elo/bp4_cutoff_probe/
2026-07-30_19-15-08
```

For first-excluded rank \(n\), every bout involving M\(n\) through M18 was
removed without replacement, absence inference was disabled, and Elo was
replayed from 1989/01. Cutoff 19 removed nothing. A violation was any adjacent
increase in the point mean as the BP4 index worsened.

The results were:

| First excluded M | Last included index | Removed bouts | Violations |
|---:|---:|---:|---:|
| 19 | M18 | 0 | 6 |
| 18 | M17 | 81 | 5 |
| 17 | M16 | 1,336 | 4 |
| 16 | M15 | 5,015 | 3 |
| 15 | M14 | 9,921 | 2 |
| 14 | M13 | 14,807 | 2 |
| 13 | M12 | 19,141 | 2 |
| 12 | M11 | 22,902 | 3 |

The run artifacts are:

- `bp4_cutoff_ratings.csv`: the requested cutoff-by-rating table;
- `bp4_index_ordinals.csv`: the ordinal for every BP4 column;
- `bp4_cutoff_violations.csv`: every violating transition and its increase;
- `manifest.json`: run parameters, removed and rated bout counts, and summary
  results.

The unmodified run's six violations were every transition from M12 to M18:

```text
M12->M13  M13->M14  M14->M15
M15->M16  M16->M17  M17->M18
```

For cutoffs 18 through 15, the count fell by exactly one each time because
the final violating transition was removed from the reported sequence. The
violations shared with the preceding run remained. This is deletion of a
violation from the scope, not repair of the retained curve.

At stronger cutoffs, the replay began to create or expose violations farther
up Makuuchi:

| First excluded M | Violating transitions |
|---:|---|
| 14 | M9->M10; M12->M13 |
| 13 | M9->M10; M10->M11 |
| 12 | M5->M6; M9->M10; M10->M11 |

No tested cutoff produced a monotonic point-mean sequence. The minimum was two
violations, at cutoffs 15, 14, and 13. The no-replacement intervention
therefore does not achieve the teleological objective over the tested range.
Instead, sufficiently strong deletion changes the rating history enough for
new small reversals to appear above the removed tail.

This does not show that the new upstream reversals are statistically
distinguishable from sampling variation. For example, some increases are
less than one Elo point. The probe deliberately counts point-mean violations;
it is not the isotonic bootstrap test. Its result is nevertheless decisive
for the literal objective that the computed mean sequence itself contain no
increases: none of the eight sequences satisfies that condition.

## What has and has not been established

Under the naive assumptions, the literal-rank analysis rejects:

> Expected start-of-basho Elo is an immutable non-increasing function of
> literal BP4 chii ordinal across the complete period.

But the boundary-aligned analysis does not reject monotonicity. Consequently,
the literal-rank rejection should not be interpreted as evidence that chii
and Elo necessarily measure performance differently. It shows that literal
rank number is not a stable proxy for position relative to the division
boundary when banzuke structure changes.

The cutoff series adds a separate negative result. Removing progressively
larger lower-maegashira tails without replacement does not make the retained
literal BP4 sequence monotonic. For moderate cutoffs it merely removes the
last violation from the tested scope; for stronger cutoffs the altered Elo
history develops small violations farther up Makuuchi. Thus neither low M18
support alone nor this simple tail-deletion policy explains away the literal
curve's violations.

Other differences between chii and Elo may still arise because:

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

> A time-invariant monotonic mapping from literal BP4 chii to mean Elo does
> not fit the 1989+ data, but the apparent lower-makuuchi endpoint reversal
> disappears when the same ratings are aligned by actual division-boundary
> distance. Successively deleting lower-maegashira bouts without replacement
> does not produce a monotonic retained literal-rank curve for any tested
> cutoff from M18 through M12.

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

The comparison-graph question is implemented as the controlled
`analysis.toy_elo.boundary_monotonicity` experiment. It uses monotonic fixed
skills and compares the evidence-shaped Makuuchi-Juryo scheduler with a
rank-local no-bridge control.

In its first 500-event, 100-run result, the evidence bridge compressed the
seven-group lower-boundary endpoint difference from -465.44 in the control to
-312.39. It therefore changed the recovered gradient strongly in the
direction of flattening. The historical boundary endpoint, scaled from q 900
to the toy q 400, is approximately -4.14, so the toy evidence curve remains
far steeper than history. No individual run had an endpoint that flat.

The historical boundary curve's maximum local reversal is +14.32, or +6.36
on the toy scale. One of 100 evidence-bridge runs exceeded that local target;
none of the control runs did. The simple evidence bridge therefore supplies a
strong flattening mechanism but does not reproduce the nearly flat historical
expected boundary curve.
