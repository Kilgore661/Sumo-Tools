# Results 1: Rating Maturity, Initialisation Sensitivity and Banzuke Position

## Status and answer

The proposed investigation has been completed over the declared
`1989/01`--`2026/07` History.

The result is mixed and useful:

1. **Exposure is strongly position-dependent.** Rikishi observed in the deep
   lower tail have much less prior bout evidence than rikishi higher on the
   banzuke.
2. **Centred rating states become less sensitive to entrant initialisation as
   evidence accumulates.** This holds in every broad position band in the
   declared endpoint comparison. Forecast sensitivity usually falls too, but
   the deepest band is an informative exception.
3. **Maturity composition does not explain away the lower-tail rating
   upturn.** The final normalized-position band remains above the preceding
   band under every maturity restriction, and the literal-chii reversal rate
   does not improve consistently.

The evidence therefore supports the exposure component of the churn
explanation and the general claim that initialization matters during an early
rating transient. It does not support the stronger claim that this mechanism
is sufficient to explain the observed rating anomaly below approximately
`Jd100`.

## Declared run

The source run is:

```text
files/output/analysis/career_bout_volume/rating_maturity/
2026-08-24_09-08-25/
```

| Quantity | Value |
|---|---:|
| First basho | 1989/01 |
| Last basho | 2026/07 |
| Basho | 222 |
| Eligible W/L bouts | 574,863 |
| Rikishi-basho observations | 158,995 |
| Distinct rikishi | 4,524 |
| Fusen exclusions | 2,998 |
| Draw exclusions | 0 |
| Start-of-basho observations without model state | 318 |
| Participant forecast rows | 1,149,726 |

The History, adopted-prior and divisional-`k` hashes match the controlled Elo
model-selection run. The final manifest records clean Git commit `8147ae0`.
The adopted prior is future-informed, so this remains a retrospective
diagnostic rather than prospective validation.

## Experimental correspondence

The analysis replays the selected `B_k` and `B_kP` models over exactly the same
chronological eligible bouts and results. They differ only in entrant
initialisation. An automated regression test confirms bout-by-bout equality
with the existing `elo_model_selection` implementations, including forecasts
and prior rated-bout counts.

Stage 1 retains every ranked rikishi-basho observation. Model state is born at
the first eligible rated bout. A rikishi who will contest an eligible bout in
the current basho is initialized from that basho's chii before the
start-of-basho snapshot. Ranked observations with no eligible bout yet retain
null ratings and remain in the audit data.

Ratings are centred separately within each model over ranked rikishi with
available model state at the snapshot. This removes a common translation that
has no forecasting significance.

## Stage 1: exposure

### Normalized-position gradient

For entrants first observed after the `1989/01` boundary, prior rated-bout
support falls steadily as current normalized position worsens:

| Mean normalized-position band | Observations | Rikishi | Q25 | Median | Q75 | Below 60 | Below 120 | Below 180 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0000--<0.2000 | 23,147 | 754 | 203 | 363 | 581 | 4.8% | 12.4% | 21.1% |
| 0.2000--<0.4000 | 24,899 | 1,446 | 154 | 252 | 387 | 6.1% | 17.5% | 31.2% |
| 0.4000--<0.6000 | 26,877 | 2,033 | 112 | 202 | 336 | 9.6% | 27.2% | 44.3% |
| 0.6000--<0.8395 | 34,637 | 2,936 | 56 | 119 | 244 | 26.1% | 50.1% | 64.6% |
| 0.8395--1.0000 | 24,573 | 3,674 | 9 | 35 | 105 | 61.1% | 77.8% | 84.2% |

The gradient is not a small Jd100-local effect. Median support falls from 363
bouts in the highest fifth to 35 in the inherited lowest band. Nearly half
of the lowest-band observations have fewer than 30 prior rated bouts, compared
with 1.7% in the highest band.

### Literal Jd100 comparison

The observed-entrant literal comparison is:

| Current literal group | Observations | Rikishi | Median prior bouts | Below 30 | Below 60 | Below 120 | Below 180 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Above Jd100 | 106,472 | 2,833 | 224 | 5.1% | 11.5% | 26.8% | 40.4% |
| Jd100 | 366 | 315 | 91 | 20.2% | 35.0% | 60.9% | 75.4% |
| Below Jd100 | 27,295 | 3,677 | 41 | 43.8% | 61.9% | 81.6% | 89.1% |

The exact Jd100 row lies between the groups above and below it. This cautions
against treating Jd100 as an empirically discovered discontinuity. The data
supports a strong lower-tail exposure gradient, with Jd100 retained as an
evidence-motivated reference point.

Boundary incumbents show the same broad ordering, but their support before
1989 is unknown. They are not used as a substitute for the observed-entrant
result.

### Stage 1 answer

> Deep lower-banzuke observations have materially less accumulated rated-bout
> evidence. The exposure component of the proposed explanation is strongly
> supported.

## Stage 2: sensitivity to entrant initialisation

### Rating and forecast endpoints within position

An overall comparison by support alone is misleading because support and
position are strongly associated. Low-support observations are concentrated
near the bottom, while the mature population contains proportionally more
higher-ranked rikishi. The relevant descriptive comparison is therefore made
within each position band:

| Position band | Median centred-rating disagreement, <15 | Median centred-rating disagreement, 240+ | Mean forecast disagreement, <15 | Mean forecast disagreement, 240+ |
|---|---:|---:|---:|---:|
| 0.0000--<0.2000 | 195.32 | 79.77 | 0.2501 | 0.0292 |
| 0.2000--<0.4000 | 147.41 | 9.21 | 0.1799 | 0.0183 |
| 0.4000--<0.6000 | 46.78 | 17.90 | 0.0377 | 0.0096 |
| 0.6000--<0.8395 | 59.00 | 24.52 | 0.0068 | 0.0045 |
| 0.8395--1.0000 | 64.86 | 24.16 | 0.0013 | 0.0023 |

Median centred-rating disagreement is lower at 240 or more prior bouts in all
five bands. The reduction is particularly large in the upper two bands. This
is empirical historical evidence that the rating state becomes less dependent
on the entrant policy as evidence accumulates, under these declared coupled
models.

Mean forecast disagreement falls in four of the five bands. In the deepest
band it rises from 0.00135 to 0.00234 despite the large fall in rating-state
disagreement. Both forecast effects are small: below 15 prior bouts, 4.4% of
deep-tail participant forecasts differ by more than 0.005 and 2.2% differ by
more than 0.01. At 240 or more bouts those proportions are 9.0% and 3.9%.

This is not contradictory. Forecasts depend on the difference between the two
participants' ratings, not on either centred rating in isolation. Near the
bottom, paired rank-informed initial values can move neighbouring opponents
similarly and therefore produce very similar initial forecasts even while the
two complete rating states remain different. This is a plausible
interpretation of the observed combination, not a separately tested causal
mechanism.

### Stage 2 answer

> Accumulated evidence is associated with substantially less remaining
> initialisation sensitivity in centred ratings. Forecast sensitivity also
> declines through most of the banzuke, but it is already very small in the
> deepest low-support band and does not decline there.

## Stage 3: relationship to the lower-tail anomaly

### Normalized-position view

The most direct structural comparison is the step from normalized position
`0.90--<0.95` to the final `0.95--1.00` band:

| Minimum prior rated bouts | Penultimate-band mean | Final-band mean | Final-band step | Final-band observations |
|---:|---:|---:|---:|---:|
| 0 | -316.72 | -250.66 | +66.06 | 7,818 |
| 30 | -399.08 | -377.29 | +21.78 | 2,574 |
| 60 | -409.45 | -375.47 | +33.98 | 1,818 |
| 120 | -415.85 | -372.79 | +43.06 | 1,100 |
| 180 | -422.19 | -380.63 | +41.57 | 801 |

The final band remains higher under every maturity restriction. The upturn is
smallest at 30 prior bouts but then increases again; there is no monotonic
attenuation as the requirement becomes stricter. Hundreds of final-band
observations remain even at 180 bouts, so the result is not produced merely by
the complete disappearance of the mature lower tail.

The secondary smooth weighting `prior/(prior+60)` reduces the unrestricted
final step from +66.06 to approximately +28.08 rating points. It therefore
shows that maturity composition affects the magnitude of the observed curve.
It does not remove or reverse the anomaly.

### Literal-chii view

The exact-chii curve is much noisier. Among supported lower-tail adjacent chii,
the reversal proportion is:

| Minimum prior rated bouts | Supported lower-tail chii | Reversal proportion | Largest reversal |
|---:|---:|---:|---:|
| 0 | 248 | 53.0% | 37.43 |
| 30 | 185 | 51.6% | 67.40 |
| 60 | 141 | 50.7% | 71.98 |
| 120 | 77 | 51.3% | 89.00 |
| 180 | 46 | 55.6% | 123.46 |

The absolute number of reversals falls because progressively fewer chii retain
the required support. The proportion does not improve consistently, and the
largest observed reversal grows. This diagnostic does not support a claim
that mature-only literal chii recover a smooth lower-tail ordering.

### Stage 3 answer

> Controlling for rating maturity does not remove the lower-tail anomaly.
> Maturity composition changes its magnitude, but the upturn persists under
> every declared threshold and under smooth support weighting.

## Overall interpretation

The proposed explanation required a joint pattern:

```text
low position -> low exposure
low exposure -> continuing initialisation sensitivity
maturity control -> attenuation of the anomalous rating curve
```

The first link is strongly observed. The second is observed for centred rating
states and mostly observed for forecasts, subject to the deepest-band
qualification. The third link fails: the structural upturn persists.

The defensible conclusion is therefore:

> Rapid lower-tail turnover produces a population with much less accumulated
> evidence, and entrant initialisation leaves a longer imprint on those rating
> states. That maturity composition is relevant to interpretation, but it is
> not a sufficient explanation of the Jd100-related rating anomaly.

Other mechanisms remain live, including schedule connectivity, fixed-point or
normalisation feedback, changing ability, and the institutional composition of
the deepest ranks. This experiment does not select among them.

## Uncertainty and limitations

The primary results are descriptive counts, quantiles and coupled differences.
No row-wise confidence interval is reported because rikishi-basho observations
are repeated and strongly dependent. Consequently, the career-cluster
bootstrap specified for any later interval estimate was not needed for these
point summaries.

Further limitations are:

- the adopted prior was derived from the broad period being replayed;
- boundary incumbents have unknown pre-1989 support;
- position and support remain associated even in the two-dimensional displays;
- maturity thresholds and the smooth weighting rule are declared descriptive
  choices, not discovered laws;
- Jd100 and normalized position 0.8395 are comparison points, not causal
  boundaries; and
- the analysis establishes counterfactual model sensitivity, not true ability
  or the unique correctness of either initialisation policy.

## Artifacts

The declared run contains:

- `findings.md`: compact generated staged answers;
- `rikishi_basho_maturity.csv`: the complete start-of-basho audit ledger;
- `position_support_summary.csv` and `position_support_survival.csv`;
- `jd100_support_summary.csv`;
- `coupled_rating_disagreement.csv`;
- `coupled_forecast_disagreement.csv`;
- `initialisation_sensitivity_summary.csv`;
- `chii_means_by_maturity.csv` and `position_means_by_maturity.csv`;
- `chii_reversals_by_maturity.csv`;
- three responsive Plotly HTML reports; and
- `manifest.json` with the experimental contracts, source hashes, counts and
  clean Git identity.

The implementation is verified by the repository test suite, including an
exact bout-by-bout comparison with `B_k` and `B_kP`. At completion, all 201
tests passed.

