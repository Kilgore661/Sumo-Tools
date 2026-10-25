# P1-WL Prior Comparison: Provisional Findings

## Purpose and status

This document records the prior-level evidence obtained after changing the P1
bout rule from decision-field eligibility to positive selection of represented
binary W/L results. It is a provisional finding, not a decision to replace the
production P1 artifact.

The question at this stage is narrow:

> What happens to the fitted P1 entrant-prior map when otherwise valid W/L
> bouts with missing kimarite are admitted consistently?

The later question—what those changes do to the complete Elo-89 replay and its
published results—has not yet been tested.

## Source and controlled comparison

The adopted run is:

[`output/p1-wl-comparison-2026-10-25-rerun`](output/p1-wl-comparison-2026-10-25-rerun)

Its important controls are:

| Item | Value |
|---|---|
| History snapshot | `files/output/Historys/1958_01 to 2026_11.zip` |
| Snapshot SHA-256 | `afddcc2a77aa237d539073008bf46414989eb766cad8b281cf719963141793ca` |
| Selected interval | `1989-01` through `2026-09` |
| Selected basho | 225 |
| Oracle preprocessing | `annotation_only` |
| P1 domain | 975 base chii cells |
| Elo expectation scale | q = 400 |
| Base | 1517 |
| Convergence threshold | maximum successive prior change below 10 |
| Maximum iterations | 200 |
| Total run time | 37.333 seconds |

The same selected and preprocessed History, K configuration, fixed-point
solver, base, convergence rule and recentring rule were used for both fits.
Only bout eligibility differed:

- **P1 control:** exclude `decision="blank"` and `decision="fusen"`;
- **P1-WL candidate:** include only results whose paired outcomes are W and L.

The control rated 548,117 of 584,671 represented observations. P1-WL rated
581,634. It admitted all 33,521 blank-kimarite W/L bouts and excluded four
observations which the legacy decision-field rule had rated despite their
outcomes not being W/L:

| Basho | Day | Outcomes | Decision |
|---|---:|---|---|
| 1994-03 | 5 | DRAW / DRAW | unclassified |
| 1999-01 | 3 | DRAW / DRAW | unclassified |
| 1999-01 | 14 | DRAW / DRAW | unclassified |
| 2016-09 | 9 | FP / FS | hansoku |

The net increase in rated observations was therefore 33,517. The four removals
are a consequence of expressing the intended evidence rule positively as
binary W/L, rather than a separate kimarite judgement.

## Run validity

Both variants converged in 18 iterations:

| Variant | Iterations | Final maximum prior change | Converged |
|---|---:|---:|---|
| P1 | 18 | 9.595 | Yes |
| P1-WL | 18 | 9.728 | Yes |

An earlier run in `output/p1-wl-comparison-2026-10-24` is explicitly marked
invalid. It bypassed canonical oracle preprocessing, retained annotation-
specific rank cells and failed to converge. It is diagnostic evidence about a
corrected validation-runner defect and must not be used in this comparison.

## Prior differences

All 975 prior cells changed, as expected from a fixed-point replay followed by
whole-map recentring. Across the complete map:

| Measure | Rating points |
|---|---:|
| Mean difference | approximately 0 |
| Mean absolute difference | 13.462 |
| RMS difference | 17.817 |
| Maximum absolute difference | 77.832 |

The near-zero mean is imposed by the common recentring rule. It does not mean
that corresponding ranks are unchanged.

The division-level results are:

| Division | Cells | Mean difference | Mean absolute difference | Maximum absolute difference |
|---|---:|---:|---:|---:|
| Makuuchi | 53 | +38.823 | 38.972 | 56.769 |
| Juryo | 28 | +37.095 | 37.095 | 41.775 |
| Makushita | 120 | +21.187 | 21.187 | 38.068 |
| Sandanme | 201 | +3.682 | 4.812 | 15.575 |
| Jonidan | 420 | -12.203 | 12.203 | 38.077 |
| Jonokuchi | 153 | -8.193 | 9.064 | 77.832 |

The overall maximum occurs at `Jk76w`, where P1-WL is 77.832 points lower.
That chii has support of one and is therefore a sparse fringe cell rather than
evidence of a broad structural change.

The largest Makuuchi change is +56.769 at `K2w`, with support of 21. This is
also a relatively rare chii. The well-supported top-Makuuchi cells generally
rise by about 40–45 points; for example, `Y1e` rises by 44.132, from 2544.008
to 2588.141, on support of 221.

Manual side-by-side inspection of plots over the complete rank domain found
the two curves visually indistinguishable at that scale. This is consistent
with the numerical result: the overall shape is retained, while relatively
smooth division-level offsets and a few sparse-cell differences remain.

## Provisional interpretation

Including the missing-kimarite W/L results changes P1 measurably, but the
prior comparison provides no sign that it changes the rank structure in a
qualitatively important way. The largest overall difference is attached to a
single-observation cell; the largest Makuuchi difference is attached to a
comparatively rare rank; and the well-supported upper-division changes are
mostly smooth shifts rather than changes in shape.

There is consequently little value at this stage in investigating individual
prior-cell differences further. The roughly 40-point upper-division shift
must not, however, be dismissed merely because two whole-domain charts look
the same. P1 is an entrant prior, so a systematic change can propagate through
the later Elo-89 population even when the prior curve retains its shape.

The supported conclusion is therefore:

> P1-WL produces a modest, smooth change to the fitted entrant-prior map and
> no evident structural anomaly. Prior-level evidence alone is insufficient
> to decide whether its downstream effect on Elo-89 is insignificant.

## Proposed next step

The next experiment should hold the complete Elo-89 replay fixed and vary only
the frozen prior artifact:

1. run the incumbent P1 control and P1-WL candidate over the same frozen
   History;
2. bind both runs to their History, K and prior fingerprints;
3. compare rating differences across time, current and peak published ratings,
   and any ordering changes in published outputs;
4. repeat the established predictive evaluation with identical bout and
   population policies; and
5. decide whether the semantically cleaner W/L rule is empirically neutral,
   beneficial or harmful enough to affect adoption.

This is a downstream consequence test, not a further search for interesting
individual P1 cells. No production artifact should be replaced until that
comparison has been completed and recorded.
