# P1-WL Evaluation: Findings

## Conclusion

P1-WL passes the tests proposed for the missing-kimarite correction.

It preserves the reason for using an informed entrant prior, does not perform
materially differently from same-History P1 as an initializer, and slightly
improves aggregate forecast loss when propagated through exact Elo-89. The
older informed prior remains better for new entrants, as it was when P1 was
adopted; P1-WL therefore preserves rather than resolves the accepted P1
trade-off.

The downstream effect is small but not zero. Forecast probabilities differ by
0.31 percentage points on average and by at most 4.23 points. Historical
basho-end ratings differ by 7.65 points on average after aligning the two
rating origins, with a maximum of 42.73. At the final represented basho the
top 30 retain exactly the same order, although their absolute ratings are
about 18--23 points higher under P1-WL. Adoption therefore requires a normal
regeneration of dependent Elo-89 and site artifacts; it is not a one-file
substitution whose existing outputs remain valid.

On the evidence considered here, these effects are acceptable consequences
of making bout eligibility agree with the claimed evidence model: a known
binary W/L result is rating evidence even when its kimarite is absent.

## Adopted run

The adopted evidence is in
[`output/p1-wl-evaluation-2026-10-25-v2`](output/p1-wl-evaluation-2026-10-25-v2).
It was produced by `src.validation.kimarite.p1_wl_evaluation` in 155.259
seconds. The manifest binds all inputs and parameters. In particular:

- selected interval: `1989-01` through `2026-09`;
- represented binary W/L bouts: 581,634;
- History SHA-256:
  `afddcc2a77aa237d539073008bf46414989eb766cad8b281cf719963141793ca`;
- q: 400;
- bootstrap: 2,000 deterministic basho-block resamples; and
- exact Elo-89 controls: common bout domain, K configuration, lifecycle and
  population-mean policy.

The causal contrast is P1-WL minus the same-History P1 fitted alongside it.
The published P1 is retained as a separate reference. Its difference from
same-History P1 is source/refit drift and must not be attributed to the
kimarite rule.

## Test A: value as an initializer

All six candidates forecast the same 581,634 bouts without Elo-89 population
adjustment.

| Initialisation model | Log loss | Brier loss | ECE |
|---|---:|---:|---:|
| Equal, constant K (`B`) | 0.682522 | 0.244574 | 0.018960 |
| Equal, divisional K (`B_k`) | 0.681792 | 0.244246 | 0.013475 |
| Older informed prior | **0.676749** | **0.241872** | **0.013397** |
| Published P1 | 0.677112 | 0.241982 | 0.014395 |
| Same-History P1 | 0.677110 | 0.241981 | 0.014427 |
| P1-WL | 0.677088 | 0.241961 | 0.014588 |

Paired candidate-minus-comparator log-loss differences were:

| Comparator | Difference | 95% basho-block interval | Interpretation |
|---|---:|---:|---|
| `B` | -0.005433 | [-0.006241, -0.004684] | P1-WL clearly better |
| `B_k` | -0.004703 | [-0.005531, -0.003927] | P1-WL clearly better |
| Older informed prior | +0.000339 | [+0.000120, +0.000558] | Older prior remains better |
| Published P1 | -0.000023 | [-0.000057, +0.000011] | No detectable difference |
| Same-History P1 | -0.000022 | [-0.000055, +0.000014] | No detectable difference |

P1-WL therefore retains the established benefit over equal initialisation and
comfortably passes the historical non-inferiority gate against Basic Elo. Its
difference from P1 is numerically tiny and uncertain.

The previously accepted weakness is also retained. For new entrants the
older prior beats P1-WL by 0.004517 log-loss units (95% interval 0.000376 to
0.009976); under 30 career bouts it beats P1-WL by 0.002595 (0.001311 to
0.003947). The reason for accepting P1 was not that it maximised this
retrospective score. It removed the older prior's construction pathology while
preserving most of the predictive value of informed initialisation. P1-WL has
the same standing.

## Test B: exact Elo-89

| Prior | Log loss | Brier loss | ECE |
|---|---:|---:|---:|
| Published P1 | 0.675436 | 0.241267 | **0.014513** |
| Same-History P1 | 0.675430 | 0.241263 | 0.014556 |
| P1-WL | **0.675290** | **0.241185** | 0.014968 |

Against same-History P1, P1-WL improves mean log loss by 0.000140 (95%
interval 0.000100 to 0.000180 in the favourable direction) and Brier loss by
0.000077 (0.000060 to 0.000094). Aggregate ECE worsens by 0.000412. The point
estimates therefore favour P1-WL on the two proper scoring rules but not on
this binned calibration summary.

The gain is concentrated at lower experience. P1-WL improves log loss for
under-30, 30--59, 60--119 and 120--239 career-bout groups. The differences
reverse for 360--479 and 480-plus. This is not anomalous for an initialization
change: it has its strongest legitimate influence early and a very small
residual influence after long propagation. The new-entrant-only estimate is
favourable but its interval includes zero.

The first divergent forecast is the first relevant Day 1 bout in `1989-01`:
rikishi 2 at `Sd41e` against rikishi 1346 at `Sd40w`. Both have zero earlier
rated bouts. The bout identity and order are unchanged; only their rank-based
initial ratings differ. This confirms the expected causal path.

### Forecast-probability scale

Across all bouts, the absolute probability difference has:

| Measure | Value |
|---|---:|
| Mean | 0.003107 |
| RMS | 0.004308 |
| Median | 0.002244 |
| 90th percentile | 0.006931 |
| 99th percentile | 0.013862 |
| Maximum | 0.042348 |

The largest differences occur early in the interval and among inexperienced
lower-division rikishi, as expected from the location of the 33,521 newly
eligible observations.

### Rating-state scale

P1-WL's preserved target mean is 3.193960 points higher than P1's. Raw
differences are the publication consequence and are retained in the outputs;
mean-aligned differences diagnose changes in competitive separation.

At basho end across 160,778 common date/rikishi states:

| Measure | Raw | Mean-aligned |
|---|---:|---:|
| Mean absolute difference | 7.357 | 7.651 |
| RMS difference | 10.655 | 10.165 |
| Median absolute difference | 4.908 | 6.257 |
| 90th percentile | 17.510 | 15.180 |
| 99th percentile | 37.733 | 34.540 |
| Maximum | 45.922 | 42.728 |

The raw mean absolute difference falls from 12.890 in `1989-01` to 5.162 in
`2026-09`, but does not disappear. The initialisation rule continually affects
new and returning active rikishi, and Elo propagation preserves some relative
differences. This is why the result cannot be described simply as a harmless
3.19-point translation.

Source/refit drift is much smaller: same-History P1 versus published P1 has a
mean absolute basho-end difference of 0.251 and a maximum of 1.700. The
reported P1-WL effects are therefore not an artefact of refitting the control
against a newer source snapshot.

### Publication-facing scale

At `2026-09`, 272 of 593 active rikishi move at least one place in the complete
rating ordering, with a maximum movement of ten places. These are mostly
dense lower portions of the table. The leading 30 retain exactly the same
order. Their ratings rise by roughly 18--23 points; the maximum current rating
difference is 22.827.

For historical peaks, 4,376 of 4,558 complete-table positions change, because
small rating changes reorder a dense all-rikishi list. The top six are
unchanged; the first change swaps positions seven and eight. Of 4,558
rikishi, 133 (2.9%) acquire a different peak date or day. No rating threshold
or milestone rule was found in the current site producer, so there is no
separate threshold-crossing criterion to test.

These publication changes are visible in exact numbers but do not change the
overall shape or leading current ordering. A candidate site rebuild remains a
sensible visual confirmation when the corrected prior is promoted.

## Decision supported by this evidence

The tests support adopting the positive binary-W/L eligibility rule and the
P1-WL prior generated from it. They do not support describing the numerical
effect as literally insignificant or retaining old dependent artifacts.

The implementation step should:

1. make the canonical P1 producer positively select represented binary W/L
   results without requiring kimarite;
2. promote a newly generated prior with full source provenance;
3. regenerate exact Elo-89 and all dependent publication artifacts; and
4. build and inspect a candidate site before replacing the published site.

That implementation is a separate action. This evaluation changed no
canonical P1, production Elo-89 or site artifact.

## Scope limits

This remains retrospective internal-coherence evidence. P1 and P1-WL are
both fitted using the history on which they are evaluated. The test supports
the semantic repair and shows its consequences; it is not an out-of-sample
claim that P1-WL is an optimal entrant model.

The experiment also deliberately holds the current lifecycle rule fixed.
Reinitialising a rikishi after absence and using off-banzuke results remain
separate Matters Arising and are not endorsed by this run.
