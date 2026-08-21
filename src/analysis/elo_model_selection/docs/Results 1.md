# Results 1: Controlled Retrospective Comparison

## Status

This document summarises the declared comparison of the four post-1988
Elo-family models. It records both the numerical result and the interpretation
agreed after inspecting it.

The run covers 1989/01--2026/07 and scores 574,863 eligible bouts. It uses
`q=400`, predicts before updating, and compares every model on the same bouts.
The exact inputs, hashes, exclusions and bootstrap settings are preserved in
the run manifest beneath:

```text
files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/
```

## Models

| Model | `k` policy | Initialisation |
|---|---|---|
| `B` | constant 35 | constant |
| `B_k` | divisional | constant |
| `B_P` | constant 35 | adopted prior `P` |
| `B_kP` | divisional | adopted prior `P` |

The adopted prior is used exactly as persisted: there is no rescaling,
smoothing or recentering for this comparison.

## Aggregate result

Lower loss is better. A constant 50--50 forecast has log loss
`log(2) = 0.693147` and Brier loss `0.25`.

| Model | Mean log loss | Mean Brier loss | Log-loss difference from `B` |
|---|---:|---:|---:|
| `B` | 0.682753 | 0.244687 | -- |
| `B_k` | 0.682015 | 0.244355 | -0.000738 |
| `B_P` | 0.678055 | 0.242439 | -0.004698 |
| `B_kP` | 0.676945 | 0.241968 | -0.005808 |

All four models beat 50--50 on the declared aggregate criterion. Each of the
three modified models is superior to `B` on mean log loss, with a one-sided
95% bootstrap upper bound below zero. Log loss and Brier loss agree about the
ordering. `B_kP` is the best aggregate model.

Relative to the neutral forecast, `B` gains 0.010394 nats per bout and
`B_kP` gains 0.016202. Thus `B_kP` increases the measured log-loss advantage
over 50--50 by about 56%. This is a comparison of information scores, not a
56% increase in prediction accuracy.

## What the factorial comparison says

The paired factorial contrasts separate the effects of the two policies:

| Contrast | Mean log-loss difference |
|---|---:|
| divisional `k` under constant initialisation | -0.000738 |
| `P` under constant `k` | -0.004698 |
| `P` under divisional `k` | -0.005070 |
| divisional `k` under informed initialisation | -0.001110 |
| `k`-by-`P` interaction | -0.000372 |

Negative differences are favourable. Most of the aggregate improvement comes
from informed initialisation. Divisional `k` supplies a smaller improvement,
and the negative interaction means that the two policies work slightly better
together than their isolated effects would suggest.

## Interpretation of the adopted priors

The prior artifact was derived from the broad history being scored. Its
retrospective performance is therefore not an out-of-sample prediction test.
That qualification limits the claim that can be made about this experiment;
it does not make the experiment uninformative or prevent operational use of
the priors.

The run supplies two useful sanity checks:

1. With either `k` policy, the adopted priors are decisively better than
   constant initialisation over the retrospective history.
2. For newly initialised rikishi, the prior models have point log losses just
   below the fair-coin loss, whereas the constant-initialisation models are
   worse than it. The smaller sample does not establish the former difference
   from 50--50 at the declared confidence level.

The benefit of `P` is largest when one participant has little rating history
and diminishes as recorded experience accumulates. This is the expected shape
of an initialisation effect. It supports the interpretation that the prior is
doing the job for which it was introduced.

Using the complete available history to fit a model after the latest basho
and then forecasting the next basho is chronologically legitimate: all model
inputs precede the forecast target. The next and subsequent basho can provide
genuinely prospective evidence for the fixed model. The retrospective nature
of this run is therefore a disclosure about evidence, not a bar to naming
`B'`.

## Limited rating history

The experience groups are based on the smaller number of previously rated
bouts held by either participant. They are not rank groups and should not be
described simply as Jonokuchi or Jonidan results. In particular, they include:

- the artificial initial population at the January 1989 boundary, including
  established rikishi at every rank;
- genuine later entrants, most but not all of whom enter near the bottom of
  the banzuke; and
- bouts between a less-established participant and an experienced opponent.

No rating model can infer an individual's ability reliably from only a few
performances. The informed prior substantially reduces the resulting error
but cannot replace personal evidence. The relatively weak early-history
scores are therefore an expected limitation and a useful diagnostic, not a
show-stopper for selecting `B'`.

## Cross-boundary bouts

There are 2,533 bouts between a sekitori and a sub-sekitori, about 0.44% of the
scored population.

| Model | Cross-boundary log loss | Advantage over 50--50 |
|---|---:|---:|
| `B` | 0.685322 | 0.007826 |
| `B_k` | 0.685507 | 0.007640 |
| `B_P` | 0.688356 | 0.004791 |
| `B_kP` | 0.691737 | 0.001410 |
| 50--50 | 0.693147 | 0 |

The point estimate for `B_kP` is worse than that for `B` and gives up most of
`B`'s advantage over a neutral forecast in this subgroup. The direct
`B_kP`-versus-`B` interval includes zero, however, and the subgroup is small.
The result is disappointing and should be investigated, particularly because
adding divisional `k` to the informed-prior model has a clearly adverse effect
within this subgroup. It is recorded as a known trade-off, not treated as a
show-stopper.

## Preliminary model-selection conclusion

The declared primary aggregate score supports designating `B_kP` as `B'`, the
post-1988 successor to Basic Elo. It has the lowest log loss, and the
independent Brier score gives the same ordering. Informed initialisation
supplies most of the improvement over `B`; divisional `k` supplies a smaller
additional improvement.

This selection was always provisional rather than decisive. The absolute
differences are modest, predictions based on very little recorded experience
are necessarily weak, and cross-boundary performance is worse as a point
estimate. The calibration work below supplies a further comparison between
`B_kP` and its closest serious alternative, `B_k`.

## Participant-level calibration

The calibration diagnostic records two observations for every bout. If
rikishi `X` has forecast probability `p` and rikishi `Y` has probability
`1-p`, an `X` win contributes `(p, 1)` for `X` and `(1-p, 0)` for `Y`; a `Y`
win reverses the outcomes. The observations are collected in
five-percentage-point bins. For each bin the diagnostic compares the mean
forecast probability with the observed proportion of wins.

This participant-level construction makes the lower and upper halves
complementary. A point `(p, r)` is accompanied by `(1-p, 1-r)`, giving the
curve 180-degree rotational symmetry around `(0.5, 0.5)`. The lower half is
therefore useful as a complete participant account but contains no independent
information beyond the upper half.

The machine-readable results and interactive chart are in:

```text
files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/
```

The aggregate expected calibration errors are:

| Model | ECE (percentage points) |
|---|---:|
| `B` | 1.9192 |
| `B_k` | 1.3588 |
| `B_P` | 1.7030 |
| `B_kP` (`B'`) | 1.3459 |

Lower is better. `B_kP` is best by this aggregate summary, but only
fractionally better than `B_k`. More generally, all four traces have roughly
the same shape. This is unsurprising: they use the same `q=400` probability
formula, process the same bouts, and differ only in initialisation and `k`
policy.

### Shape of the `B'` curve

`B'` is well calibrated close to an even contest:

| Probability bin | Mean forecast | Observed win rate | Gap |
|---|---:|---:|---:|
| 45--50% | 47.69% | 47.26% | -0.43 points |
| 50--55% | 52.23% | 52.65% | +0.42 points |

These central bins contain more than 558,000 participant forecasts. The close
agreement is therefore not a sparse-data effect.

In the aggregate view, the model becomes overconfident as the nominated
participant becomes a stronger favourite. The largest discrepancy is in the
75--80% bin:

| Probability bin | Mean forecast | Observed win rate | Overconfidence |
|---|---:|---:|---:|
| 70--75% | 72.29% | 65.59% | 6.70 points |
| 75--80% | 77.31% | 67.67% | 9.64 points |
| 80--85% | 82.27% | 73.26% | 9.01 points |

An error approaching ten percentage points initially appeared material. In
particular, this result seemed to imply that an illustrative 74% produced by
the raw Elo formula should not be described as an empirically calibrated 74%
chance of winning. That interpretation was incomplete because the aggregate
view conceals rating maturity.

Calibration improves again for the most extreme mismatches, although `B'`
remains somewhat overconfident:

| Probability bin | Mean forecast | Observed win rate | Overconfidence |
|---|---:|---:|---:|
| 85--90% | 87.31% | 80.12% | 7.18 points |
| 90--95% | 92.26% | 86.87% | 5.38 points |
| 95--100% | 96.96% | 94.47% | 2.49 points |

The aggregate calibration result does not contradict the proper-score
comparison. All four models contain more predictive information than a
constant 50--50 forecast, and `B_kP` improves on `B`. It does, however, combine
ratings at very different stages of formation.

## Taking rating maturity into account

For each bout, rating maturity is represented by the smaller number of prior
rated bouts held by either participant. It is therefore a property of the less
established rating in the match, not the total career length of either
rikishi. Each bout is assigned to exactly one band:

| Minimum prior rated bouts | Bouts | Share |
|---|---:|---:|
| `<30` | 84,716 | 14.7% |
| `30--59` | 72,282 | 12.6% |
| `60--119` | 112,652 | 19.6% |
| `120--239` | 148,563 | 25.8% |
| `240--359` | 77,499 | 13.5% |
| `360--479` | 39,338 | 6.8% |
| `480+` | 39,813 | 6.9% |

The seven groups contain all 574,863 scored bouts. The interactive
distribution is generated as `rating_maturity_distribution.html`.

The career-scale calibration curves reveal what the aggregate curve hides.
For `B_kP`, ECE falls from 8.38 percentage points below 30 prior bouts to 1.12
points at 30--59. In every later band it remains between 0.39 and 2.26 points.
Apart from the `<30` population, the relationship between forecast probability
and observed win rate is therefore close to the ideal line.

The `<30` group is only 14.7% of bouts, but it contributes disproportionately
to the confident probability bins and drives much of the apparent aggregate
overconfidence. The paired-maturity analysis below shows that this description
can be made more precise. In either form, the result is not good evidence that
the mature `q=400` probability mapping is generally unsound. A global
adjustment to `q` could damage the already good calibration of mature ratings
and is no longer an obvious prerequisite for continuing the story.

## Pairing the two ratings' maturity

Using only the smaller prior-bout count is a weakest-link summary. A bout
really has two support values. The order-independent pair

```text
(minimum prior rated bouts, maximum prior rated bouts)
```

distinguishes two immature ratings from an immature rating facing a mature
one. The triangular paired-maturity heatmaps preserve that distinction.

The coarse view recalculates ECE within the seven career-scale pairings. For
`B_kP` it shows:

- `<30` against `<30`: 0.76 percentage points;
- `<30` against `60--119`: 17.64 points;
- `240--359` against `480+`: 0.41 points;
- `360--479` against `480+`: 0.43 points; and
- `480+` against `480+`: 1.29 points.

Apart from the `<30` row, every coarse `B_kP` cell has ECE no greater than
2.841 percentage points. The main defect is therefore not simply that one
rating has fewer than 30 prior bouts. It is concentrated when that immature
rating faces a more established one. Two immature ratings can be well
calibrated against each other, plausibly because their forecasts remain
cautious and close to 50--50. Low ECE in that cell does not by itself establish
strong discrimination.

The fine view uses uniform 30-bout bands through `570--599` and an open-ended
`600+` band. Excluding the `<30` row, its `B_kP` distribution is:

| ECE | Cells | Bouts |
|---|---:|---:|
| below 1 point | 5 | 16,288 |
| 1--2 points | 64 | 216,001 |
| 2--3 points | 76 | 178,208 |
| 3--4 points | 43 | 58,924 |
| 4--5 points | 17 | 17,697 |
| 5--10 points | 5 | 3,029 |
| 10 points or more | 0 | 0 |

Thus 145 of 210 cells, representing 410,497 of 490,147 bouts (83.8%), have
ECE below three percentage points. The median cell ECE is 2.44 points and the
maximum is 5.74 points. The fine chart contains more mid-range cells than the
coarse chart because ECE is nonlinear: recalculating after pooling forecasts
can cancel signed errors that remain visible in narrower maturity pairings.

Both views are retained deliberately. The coarse
`calibration_ece_by_support_pair_coarse.html` is the clearer story-facing
chart. The uniform-band `calibration_ece_by_support_pair.html` and its CSV are
the detailed exploratory record. Each chart provides a model selector, uses a
common colour scale across models, defines ECE in its subtitle and reports
bout counts on hover.

## Comparing models across rating maturity

The generated `calibration_ece_heatmap.html` compares all four models in every
maturity band. No model has the lowest ECE in every column. Informed priors
help substantially below 60 prior bouts, as intended, but do not improve
calibration consistently throughout later careers. Divisional `k` performs
more consistently across the range.

Weighting the seven independently calculated band ECEs by their bout counts
gives:

| Model | Bout-weighted maturity-band ECE |
|---|---:|
| `B_k` | **2.3061 percentage points** |
| `B_kP` | 2.3587 percentage points |
| `B` | 2.4748 percentage points |
| `B_P` | 2.6763 percentage points |

This statistic makes `B_k` best, but its advantage over `B_kP` is only 0.0526
percentage points. It differs from aggregate ECE because ECE is nonlinear:
pooling all forecasts first permits signed errors from different maturity
groups to cancel within probability bins, whereas calculating absolute errors
within each maturity group before weighting does not. Neither construction is
the uniquely correct calibration summary; they answer different questions.

## Current conclusion about `B'`

`B_k` and `B_kP` are the strongest models, with the preferred model depending
on what is measured:

- `B_kP` wins under the predeclared primary log-loss criterion and under Brier
  loss;
- `B_kP` is also fractionally best on aggregate ECE; and
- `B_k` is fractionally best when calibration is assessed separately within
  rating-maturity groups and then weighted by bout count.

As in the earlier experiments, there is not a great deal to choose between
them. Nevertheless, changing the selection rule after seeing the results
would be difficult to defend. The predeclared primary measure therefore
supports retaining `B_kP` as the provisional `B'`, while `B_k` should be
presented as the serious alternative rather than as a model that was
decisively beaten.

The adopted prior `P` was derived from the available post-1988 history. This
fact belongs in the methodological provenance and means that the historical
comparison is not out-of-sample validation. It is not a recurring objection
to using the fitted model: fitting from all results through the latest basho
and forecasting the next basho is an ordinary past-to-future use. The
retrospective calculation also supplies the intended sanity test that the
derived priors improve on constant initialisation.

The next narrative step can therefore build the proposed full-history Equelo
on provisional `B'=B_kP`. Investigating `q` remains possible as a separate
calibration study, but the maturity analysis removes it as a prerequisite.
