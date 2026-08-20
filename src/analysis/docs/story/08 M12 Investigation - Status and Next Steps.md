# The M12 Problem: Consolidated Research Record

## Purpose and navigation

This is the canonical entry point for project work on the *M12 problem*: the
rise in experimentally derived initial ratings towards the lower end of
Makuuchi. It consolidates the question, the successive explanations considered,
the evidence obtained, where the investigation stopped, and the decision that
now governs entrant initial ratings.

Read this document for the reasoning and conclusion. Use the two companion
documents for implementation work:

- [M12 Experiment Catalogue](09%20M12%20Experiment%20Catalogue.md) records the
  code, commands, parameters, artifacts and headline results needed to reproduce
  the investigation.
- [Initial Rating Policy](10%20Initial%20Rating%20Policy.md) is the concise
  normative decision for the post-1988 paired initial ratings and their scope.

Earlier notes remain useful as sources, but they are not current decision
documents. If an earlier note conflicts with this record or the policy, this
record and the policy take precedence.

## Decision

The M12 investigation is closed as a blocker to the Equelo documentation.
There is no established model that both explains and removes every
non-monotonicity, and it is not clear that such a model exists. Further attempts
to account for each local reversal are unlikely to improve the rating product.

Monotonicity is desirable for entrant initialisation, but it is not a required
property of ratings learned from results. Banzuke rank is a capacity-constrained
assignment as well as a rough ordering of ability. Changes in division size
move rikishi across the Makuuchi--Juryo and Juryo--Makushita boundaries and
change the opponents they are likely to face. Consequently, a timeless
empirical answer to "what rating belongs to chii c?" is not uniquely identified
by the available history.

The adopted position is therefore:

1. The experimental fixed-point curves are evidence about plausible scale and
   spacing, not definitive estimates of intrinsic ability at each chii.
2. The post-1988 M/J and continuous lower-banzuke results are aligned, merged
   over Juryo and combined into east/west rank pairs.
3. The resulting paired curve is already sensible for shortening the entrant
   initialisation gap. Smoothing would be a reasonable way to require exact
   monotonicity, but exact monotonicity is not necessary for this purpose.
4. The project therefore chooses not to smooth. The tiny M/J reversal is
   retained as a documented feature rather than concealed or fitted away.
5. This decision applies only to chii represented in the post-1988 scope.
   Completing pre-1989-only ranks would be a separate policy and artifact.
6. Once bouts are observed, ratings are intended to be driven by performance
   rather than by the entrant prior.

Public documentation must say that the initial ratings are sensible priors
informed by historical experiments. It must not describe the chosen numbers
as uniquely estimated truths. The retained experimental outputs show both the
evidential basis and the constructive choices.

The documentation work may now resume. Predictive validation remains required,
but the existence of non-monotone experimental estimates is no longer a
show-stopper.

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

## The earlier common-mechanism hypothesis

The initial suspicion was that the M12 problem might be a milder version of the
Jk73 problem. There is abundant evidence at M1--M12, followed by progressively
less evidence at M13--M17. Perhaps low-support lower-maegashira buckets were
affected by the same fixed-point feedback and repeated normalisation that
overwhelmed the genuine signal at rare Jonokuchi chii.

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
code contains no support-weighted normaliser.

The later Clean Elo and boundary results mean that this should no longer be the
primary M12 hypothesis. Fixed-point normalisation may amplify the literal-rank
pattern, but it cannot be its sole cause, and historically variable banzuke
structure explains an important part of the apparent reversal. The Jk73
support/normalisation failure remains a real historical failure, but the
supported-domain and nearest-supported completion policies now control it.

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

### Model-conditional finding: divisional K is a boundary confounder

Every Clean Elo, fixed-supported and contextual-boundary result cited here was
obtained under the maintained divisional K policy:

| Rank region | K |
|---|---:|
| Yokozuna through Komusubi | 10 |
| Maegashira | 15 |
| Juryo | 25 |
| Makushita and below | 35 |

K therefore changes at exactly the Makuuchi--Juryo and Juryo--Makushita
boundaries whose irregularities this investigation studies. Each rikishi is
updated using the K belonging to that rikishi's current chii. In a
cross-division bout the two competitors can consequently use different K
values, so the bout need not transfer equal numbers of rating points in each
direction. Closed-population mean restoration controls the overall scale but
does not prove that these local K discontinuities are irrelevant to the fitted
shape.

The boundary experiments changed the representation of entrant priors while
holding this K policy fixed. They therefore show what boundary-relative
representations do **within the chosen Equelo model**; they do not isolate
banzuke geometry from divisional K. The divisional policy could cause or
contribute to some of the M/J and J/Ms irregularity. No retained constant-K
sensitivity run establishes how much.

This qualification weakens a causal interpretation, not the practical
decision. A constant-K sensitivity comparison would be epistemically useful,
but a monotone entrant prior does not require proof that divisional K caused,
or did not cause, the experimental reversals.

## Revised diagnosis: the missing banzuke context

The current aggregation asks, schematically:

```text
What is the mean rating associated with literal chii c?
```

That question pools observations from banzuke with different structures. For
lower Makuuchi, the more complete question is:

```text
What rating is associated with chii c in a banzuke of structure b?
```

The relevant structure may include the size of Makuuchi, the number of sanyaku
and maegashira positions, the lowest maegashira chii, and the rikishi's
distance from the Makuuchi--Juryo boundary. Historical era may explain
additional variation, but it should first be tested separately from the actual
banzuke structure rather than used as an unexplained proxy for it.

This changes the interpretation of the M12 problem. The literal M12--M17
initial-rating curve is not yet evidence that lower chii correspond to greater
performance, nor is its shape by itself evidence that Equelo and chii measure
different things. It is first evidence that the current timeless
literal-chii-to-rating aggregation combines positions whose structural meaning
varies between basho.

The fixed-point idea remains potentially useful. It addresses the real
circularity involved in estimating entrant priors from simulations that need
entrant priors. What has not been validated is the current factorisation:

```text
LiteralChii -> InitialRating
```

This motivated testing whether the appropriate contract might instead be some
form of:

```text
(LiteralChii, BanzukeStructure) -> InitialRating
```

and how a basho-start rating observation might contribute to such a map. The
later dual-boundary experiment showed that this change alone does not supply
one definitive full-history solution.

## First context-conditioned Equelo result

An experimental producer now replaces the literal-chii key at the
Makuuchi--Juryo boundary with a signed position key derived from the complete
contemporaneous banzuke:

```text
Makuuchi: negative position from the bottom; bottommost is -1
Juryo:    position from the top minus one; J1e is 0
```

The key is assigned before the support filter is applied, so excluding an
unsupported rikishi cannot move everybody else's boundary position. Other
divisions retain the fixed-supported literal-chii key. The experiment keeps
the production `q`, divisional `k`, closed-population normalisation, map
centring and support threshold.

The relevant question concerns post-1988 Equelo. An initial implementation
mistakenly followed the production modern-then-full-history process, allowing
pre-1989 banzuke to affect the fitted map and displaying historical ranks as
low as M22. That run does not answer the intended monotonicity question.

The corrected producer defaults to 1989 onward and applies that scope before
cleaning, key assignment, support measurement, solving, process ratings and
chart aggregation. It also estimates a literal-chii control from the same
scoped history rather than comparing against the full-history production map.

A 1989--2026 run at a tighter 0.01-point convergence tolerance took 55
iterations. When the contextual priors are resolved back onto literal
maegashira chii, the east-side curve is strictly decreasing through the lowest
rank present, M18e:

| Chii | Scoped literal control | Contextual prior, mean |
|---|---:|---:|
| M12e | 1988 | 1979 |
| M13e | 1986 | 1975 |
| M14e | 1985 | 1968 |
| M15e | 1975 | 1959 |
| M16e | 1996 | 1955 |
| M17e | 2015 | 1954 |
| M18e | 2015 | 1951 |

This is evidence for the missing-context diagnosis, not a monotonicity
constraint or a finished validation. No monotone fitting or post-hoc rank
banding was applied. The result says that, for the intended post-1988 domain,
the large lower-maegashira reversal is created by the literal-chii prior
representation and disappears under the contemporaneous boundary coordinate.

The implementation and its contract are described in
[`fixed_boundary/README.md`](../../equelo/fixed_boundary/README.md). The
matched run is recorded under
`files/output/Equelo/fixed_boundary/2026-08-17_14-30-30`; its responsive Plotly
charts compare the two post-1988 curves directly.

## Two different normalisations

The research record must keep two operations separate.

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

## Outcome of the investigation

The investigation produced three useful results.

First, the supported-domain policy addresses the Jk73 failure. Chii below the
support threshold no longer estimate themselves from recycled priors; they are
completed from a nearby supported chii. The maintained public map must retain
the provenance of these completed values.

Second, the post-1988 Makuuchi--Juryo boundary coordinate removes most of the
large literal M12--M17 reversal without imposing monotonicity. This establishes
that changing banzuke structure is material to the problem.

Third, the independently successful M/J and J/Ms maps cannot be reconciled over
Juryo by one common additive shift. Their residual disagreement changes
systematically from the top to the bottom of the division. A position-dependent
correction would amount to fitting another merge curve, so a joint geometric
model was tried instead.

Fourth, that joint M/J and J/Ms boundary experiment does not yield one timeless
monotone solution. The tightly converged 1958--2026 run makes the paired M/J
transition fall in the expected direction, but the Juryo curve rises from
about J10 and the J14--Ms1 transition rises by about eight points. Tightening
the convergence tolerance from 1 to 0.01 changes the level slightly but not
this shape. The result is therefore not an epsilon-1 stopping artefact. It
remains conditional on the divisional K policy and cannot establish that the
remaining boundary reversal is caused by banzuke structure alone.

The natural interpretation is that changes in banzuke capacity alter both rank
labels and the bout network. Expanding Makuuchi moves upper-Juryo rikishi into
new maegashira positions; the resulting Juryo vacancies draw in Makushita
rikishi. Those moves also change opponent selection. A single boundary index
captures some of this context but not the entire coupled institutional change.

These findings are sufficient to reject a uniquely estimated timeless
chii-to-rating table. They are not sufficient to justify further model
complexity, and such complexity is not required to choose useful entrant
priors. In particular, they do not identify the separate causal contributions
of banzuke geometry, opponent selection, population handling and the K-policy.

## Smoothing alternative considered

Smoothing remains a reasonable way to turn the experimental estimates into
entrant priors. The fixed-v1 `v5` work already constructed a curated, strictly
monotone curve for public rating landmarks, and the current fixed-supported
landmark producer applies that machinery to the maintained master map.

That curve is not currently used to initialise entrants. It deletes selected
historical ranks, masks the M12--Ms2 bridge and other chosen support, clamps the
remaining values into a strictly decreasing sequence, and uses a monotone cubic
to fill the gaps. It is therefore a valuable implementation precedent but not
the unsmoothed paired policy adopted here. Its curation choices also need to
be tested rather than inherited without review.

The v5-style curve remains a useful comparator and implementation precedent.
It is not, however, necessary merely because smoothing is defensible. The
paired contextual post-1988 curve is already sensible for shortening the
initialisation gap, and its very small M/J reversal can be exposed and
discussed. The project therefore chose not to smooth the retained values. The
[experiment catalogue](09%20M12%20Experiment%20Catalogue.md) records the
alternative curve's exact policy and sources.

## Decision rules

- Exact monotonicity is not a requirement of either entrant priors or learned
  Equelo ratings. Broad agreement with chii order remains desirable.
- Retain the paired post-1988 contextual values without further smoothing.
  Preserve their source estimates, alignment, merge weights and pairing rule.
- Do not claim that the adopted number for a chii is uniquely determined by
  history.
- Do not silently extend the post-1988 construction to pre-1989-only chii.
  Historical completion is a separate policy, artifact and account.
- Do not final-normalise the retained post-1988 artifact. Its mean depends on
  whether literal sides or rank pairs form the averaging domain. A future
  consumer that mixes rating origins must define, record and test its own
  uniform anchoring shift without overwriting the retained priors.
- Do not add a more complicated banzuke-context model unless it improves an
  independently stated criterion such as prospective prediction, calibration,
  early-career behaviour or stability.
- Compare Basic Elo and Equelo on the same history, eligible bouts, chronology,
  populations and scoring rules. Fit or select priors using training data only,
  then evaluate on later bouts.
- Prefer log loss and Brier loss, accompanied by calibration and results through
  time, over accuracy alone.
- Treat material sensitivity to reasonable alternative monotone priors as
  evidence against the maintained choice. Insensitivity is evidence that the
  exact starting values are not carrying the result.

## Completion condition for the documentation

The construction account may proceed once it accurately describes:

1. initial ratings as useful entrant priors rather than unique empirical chii
   values;
2. the method and provenance of the retained unsmoothed paired curve;
3. its post-1988 scope and the separation of any historical completion policy;
4. the distinction between convergence of the experimental fixed point and
   validation of the adopted priors; and
5. the limitation created by historically variable banzuke structure.

The construction account must also make clear that these findings were
obtained with divisional K, whose discontinuities coincide with M/J and J/Ms,
and that no constant-K control has isolated its contribution.

Predictive claims require the separate prospective comparison with Basic Elo.
The construction prose need not wait for a complete causal explanation of the
remaining experimental non-monotonicity, but it must not imply that such an
explanation has been established.
