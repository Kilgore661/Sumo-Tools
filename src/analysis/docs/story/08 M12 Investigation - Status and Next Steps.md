# The M12 Investigation: Status and Next Steps

## Decision

The draft accounts of Elo and Equelo will not yet be turned into finished
documentation.

There are unanswered questions about Elo, but none currently appears to be a
show-stopper for explaining the system. Elo has been described many times from
different perspectives, and its basic construction is straightforward in
principle.

Equelo is in a different position. Its three headline changes can be described,
but one known feature of the resulting ratings is not yet understood well
enough for a finished account: the lower-maegashira initial-rating curve stops
falling at about M12 or M13 and then rises. We call this the *M12 problem*.

The non-monotonicity is not automatically a defect. Equelo ratings are not
chii, and there is no theorem requiring them to be a monotone transformation
of chii. The show-stopper is therefore not merely that the curve is surprising.
It is that we do not yet know how much of the surprise comes from sumo and its
changing banzuke, and how much comes from Equelo's fixed-point construction,
normalisation and support policies. A finished account should not imply an
explanation that has not been established.

The next work is therefore an investigation of the M12 problem rather than
further polishing of the Equelo prose.

## The current production result

The maintained fixed-supported initial-rating map contains the following
east-side values:

| Chii | Initial rating | Basho-start support | Source |
|---|---:|---:|---|
| M12e | 1921 | 410 | Direct estimate |
| M13e | 1932 | 385 | Direct estimate |
| M14e | 1942 | 324 | Direct estimate |
| M15e | 1950 | 255 | Direct estimate |
| M16e | 1980 | 182 | Direct estimate |
| M17e | 2011 | 77 | Direct estimate |

The west-side values show broadly the same rise. M17w and M18 do not meet the
current support threshold and are completed from M17e, but M12 through M17e
are directly estimated. The supported-domain policy has therefore removed the
most extreme unsupported values without removing the M12--M17 pattern.

Sources:

- [production master map](../../../../files/output/Equelo/fixed_supported/master_chii_initial_rating_map.csv);
- [production solver statistics](../../../../files/output/Equelo/fixed_supported/solver_runs/rfsc_min_app_60/2026-07-28_12-13-47/rfsc_min_app_60_combined_final_with_stats.csv);
- [fixed-supported design](../../equelo/docs/Fixed%20Supported%20Design.md).

The falling support is conspicuous, but it does not by itself prove that low
support causes the rising ratings. It gives us a specific relationship to
test.

## The Jk73 precedent

An earlier raw fixed-point implementation could assign a deep Jonokuchi chii
such as Jk73w an initial rating of about 3000 or more. This was not treated as a
discovery about the strength of a Jk73w rikishi. It was an underidentification
failure.

The fixed-point calculation works schematically as follows:

```text
C_next = normalise(aggregate_by_chii(simulate(history, C)))
```

A well-supported chii has many basho-start observations, most of which are
ratings carried into the basho after earlier results. A very rare chii may
instead have only one or a few observations, many of them entrant ratings
supplied directly by the previous iteration's map. The solver can then learn
mainly from its own previous prior rather than from independent bout history.

The production repair directly estimates only chii with at least 60 collapsed
appearances and completes the rest from the nearest supported chii. This
prevents the spectacular Jk73-style outputs. It is a defensible protection,
but it is a policy response rather than a complete theory of the failure.

Sources:

- [Fixed Supported Requirements](../../equelo/docs/Fixed%20Supported%20Requirements.md);
- [Initial Rating Audit](../../equelo/docs/2026-06-27%20Initial%20Rating%20Audit.md);
- [Lower-Rank Problems in Equelo](../../equelo/docs/equelo%20docs/lower_rank_problems.md).

## The proposed common mechanism

The natural suspicion is that the M12 problem is a milder version of the Jk73
problem. There is abundant evidence at M1--M12, followed by progressively less
evidence at M13--M17. Perhaps low-support lower-maegashira buckets are affected
by the same fixed-point feedback and repeated normalisation that overwhelmed
the genuine signal at rare Jonokuchi chii.

This is not a newly invented explanation. The June 2026 initial-rating audit
identifies mean normalisation as its main suspect, explicitly connects the
historical low-rank blow-up with M13--M17 appearing too high relative to M12,
and proposes normalisation by chii frequency or observation weight. It asks for
three things that have not yet been brought to a conclusion:

1. separate each chii's evidence-driven movement from the common
   normalisation adjustment;
2. prototype a support-weighted alternative;
3. compare the current fixed point with a corresponding calculation without
   mean preservation.

Diagnostic artifacts containing observation counts, carried and
entrant-initialised observations, raw movement and normalisation shifts do
exist. No findings document completes the proposed comparison, and the current
code contains no support-weighted normaliser. The common-mechanism hypothesis
therefore remains plausible but untested.

## Evidence against a single-cause explanation

Later Clean Elo work reproduced the literal M12--M18 rise without an iterative
chii-prior calculation. That run used a constant entrant rating, persistent
ordinary Elo updates, divisional `k` and uniform end-of-basho mean restoration.
Its mean start-of-basho ratings rose from approximately 1927 at M12 to 1991 at
M16 and 2032 at M17.

This means that normalisation inside the iterative prior calculation cannot be
the sole cause of the M12 problem.

The Clean Elo investigation then regrouped the same observations by distance
from the actual lower edge of Makuuchi. Literal rank labels are not stable
boundary coordinates: an M16 may be the bottom pair in one basho, while an M18
may occupy that structural position in another. The number of sanyaku and
maegashira slots changes over time, so M12 and M18 draw observations from
different selections of basho and different positions relative to Juryo.

After boundary alignment, the broad endpoint reversal disappeared. The group
nearest Juryo had a mean 9.31 points below the group seven pairs above it, and
the naive monotonicity test did not reject a monotone relationship
(`p = 0.552`). Small local reversals remained, but the evidence no longer
supported the claim that the bottom of Makuuchi was systematically stronger
than the ranks above it.

Source: [Clean Elo Rating Probe Findings](../../clean_elo/docs/Rating%20Probe%20Findings.md).

This result establishes that historically variable banzuke structure explains
an important part of the apparent problem. It does not exonerate every Equelo
mechanism. Clean Elo still uses population-level normalisation, and the
fixed-point construction may amplify a pattern that already exists in the
historical grouping.

## Two different normalisations

The investigation must keep two operations separate.

### Population normalisation

When a rikishi departs, Equelo distributes the resulting rating-mass difference
uniformly among the active survivors. This is intended to preserve the active
mean. It preserves differences among those survivors at that moment, but later
entry and results mean that its complete historical effect is not necessarily
just a harmless change of origin.

This operation may interact with churn because lower ranks contain more new
and short-career rikishi.

### Fixed-point map normalisation

After basho-start ratings have been averaged by chii, the current normaliser
calculates the unweighted mean of those chii averages and adds one common shift
to every chii so that the mean equals the chosen base. Every represented chii
therefore has the same weight when the shift is calculated, regardless of
whether it has hundreds of observations or only one.

The common additive shift does not itself change differences within that
iteration. A Jk73 value cannot overtake a yokozuna merely because both receive
the same addition. The extreme result also requires underidentification and
self-referential feedback: the rare bucket retains too much of its own prior
while well-connected buckets are repeatedly disciplined by bout evidence.
Normalisation anchors that process, but calling the common shift the complete
cause would be too strong.

The implementation is in
[normalise.py](../../equelo/expt2/normalise.py), while the observation counts
are calculated separately in
[aggregate.py](../../equelo/expt2/aggregate.py).

## What support-weighted normalisation might mean

There are at least two materially different proposals.

### A support-weighted centre followed by a common shift

Instead of finding the unweighted mean of the chii averages, find their mean
weighted by basho-start observations or another support measure. Then add the
resulting common shift to every chii.

This stops rare chii having the same influence as common chii when the origin
of the scale is selected. It continues to preserve all rating differences at
that iteration. Precisely because it preserves those differences, it should
not be expected by itself to remove a stable M12--M17 inversion or a relative
Jk73 blow-up. Testing this is nevertheless useful as an invariance check.

### Different adjustments according to support

Alternatively, distribute the required correction unevenly, so that
well-supported chii absorb more of it and weakly supported chii receive less.
This could prevent a rare chii receiving the full repeated adjustment.

Unlike a common shift, however, this changes rating differences. It is not
merely a different way of choosing the origin of the Elo scale; it is a
support-based regularisation rule. That may be the right idea, but it needs an
explicit justification, formula and falsifiable evaluation. It must not be
introduced simply because it makes the curve look more like the expected chii
order.

A more explicit regularisation could combine the direct chii estimate with a
pooled or neighbouring estimate according to support. The maintained
nearest-supported completion rule already embodies a coarse version of this
principle for chii below the threshold.

## Proposed investigation

The first analysis should use the complete-results period beginning in 1989.
This avoids mixing the M12 question immediately with the incomplete historical
coverage below sekitori. The combined 1958+ calculation should follow as a
sensitivity check.

### 1. Reproduce and describe the baseline

- Reproduce the maintained fixed-supported result with recorded provenance.
- Report M1--M18 in both literal-chii and boundary-relative coordinates.
- Record appearances, distinct rikishi, entrant-initialised observations and
  carried-rating observations for every directly estimated chii.
- Trace the raw aggregate, common shift and resulting value at every iteration
  for M12--M18 and selected well- and weakly-supported controls.

### 2. Isolate the two normalisation operations

Run otherwise matched fixed-point calculations with:

1. current departure redistribution and current map centring;
2. no departure redistribution, with outputs aligned afterwards by a single
   common shift for comparison;
3. current departure redistribution and a support-weighted map centre followed
   by a common shift.

The third variant is expected to leave relative ratings unchanged if the
translation-invariance reasoning applies cleanly. If it does not, that would
identify an implementation or changing-domain interaction requiring
explanation.

### 3. Prototype support regularisation separately

Pre-specify one or more genuinely differential support rules. For each rule,
state:

- which support measure is used;
- why that measure represents independent evidence;
- how the rule treats entrant-initialised and carried observations;
- what happens as support approaches zero or becomes very large;
- whether any full-history support calculation introduces information from the
  future into the prior.

Compare each result with the baseline, not only for monotonicity but also for
rating differences, early-career behaviour, convergence, stability across
support thresholds and eventual predictive performance.

### 4. Repeat the boundary analysis within Equelo

The Clean Elo result should not simply be assumed to transfer to Equelo.
Calculate the Equelo curve directly by distance from the actual
Makuuchi--Juryo boundary. Determine how much of the literal M12--M18 rise
disappears under this coordinate and how much remains.

### 5. Check the Jk73 connection directly

Use deliberately low or absent support thresholds in an experimental output
area to reproduce the old failure. For representative sparse chii, trace how
much of each iteration comes from carried bout evidence, the previous entrant
prior, population normalisation and map centring. Then apply the candidate
support rules and see whether the mechanism changes in the predicted way.

## Decision rules

The aim is to understand the result, not to manufacture monotonicity.

- If boundary alignment accounts for the lower-maegashira rise and the
  normalisation variants do not materially change relative values, retain the
  model and explain why literal chii are an unstable coordinate in this range.
- If a current normalisation operation materially amplifies the rise, decide
  whether its intended scale-stability benefit justifies that distortion or
  whether the operation should be revised.
- If support regularisation removes the Jk73 failure and improves stability
  under independently stated criteria, it may replace the threshold/completion
  patch even if the final curve is not perfectly monotone.
- If a proposed rule merely forces the expected banzuke shape without an
  independent rationale, reject it.
- If a residual non-monotonicity remains after the mechanisms are understood,
  report it. Equelo is not chii, and disagreement is not by itself an error.

## Completion condition for the documentation

The Equelo draft can become a finished construction account when we can say,
with evidence, which of the following is true:

1. the M12 pattern is primarily a consequence of grouping historically
   variable literal ranks;
2. it is materially amplified by population normalisation, fixed-point
   normalisation or low-support feedback;
3. it survives those controls and is a reproducible property of what this
   particular rating model extracts from the historical population;
4. it is a mixture of these effects, with their contributions described.

The answer need not make Equelo monotone. It must make the behaviour
understandable enough that the finished documentation can distinguish an
observed result, a modelling consequence and an unresolved limitation.
