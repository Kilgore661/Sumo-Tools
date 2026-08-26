# Equelo Restart: From B Prime to Full History

## Status

Restart proposal retained for its recovered project history. Its immediate
next-action plan has been superseded: Tranche 1 is complete in
[Tranche 1: Population Normalisation Policy](15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md),
and the current restart point is recorded in
[Handoff After Tranche 1](16%20Handoff%20After%20Tranche%201.md).

This document recovers the shortest current route through the Elo and Equelo
work. It does not define the next production Equelo, adopt a pre-1989
completion policy or prescribe a normalisation rule. Its purpose is to identify
the next bounded analytical work without reopening questions that have already
been settled well enough to proceed.

The current model authorities remain:

- [The M12 Problem](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md);
- [Initial Rating Policy](10%20Initial%20Rating%20Policy.md);
- [Elo-family Model Lineage and Analysis Triage](12%20Elo-family%20Model%20Lineage%20and%20Analysis%20Triage.md); and
- [Results 1: Controlled Retrospective Comparison](../../elo_model_selection/docs/Results%201.md).

This restart note reconciles their chronology and proposes the next tranche.

## 1. The recovered project story

The project began with the represented sumo record, the `History`. The first
question was deliberately broad: what useful and interesting facts could be
derived from it? Analyses produced records, comparisons and exhibits, and a
static website became the natural way to present selected findings.

Elo introduced a different kind of question. Before choosing parameters, the
project had to decide what population and evidence an Elo rating would describe.
The represented bout record is sufficiently complete across the banzuke only
from 1989 onward. From 1958 through 1988 it is sufficiently complete for
sekitori, but not for the full lower-banzuke population. Ordinary all-banzuke
Elo therefore has a natural post-1988 scope.

Within that scope, two familiar problems became central:

1. an open and changing population can move the active rating scale; and
2. equal initial ratings give new or newly observed rikishi an artificial
   adjustment period.

The first Equelo work addressed scale drift with a population-normalisation
policy. The second used fixed-point iteration to seek self-consistent entrant
initial ratings by chii. Expt2 established an empirically stable fixed point
under its declared simulation, aggregation and anchoring rules.

The larger conceptual leap was to combine the incomplete pre-1989 record with
the complete post-1988 record. The January 1989 population is not a new
population: most rikishi represented then were also present in November 1988.
The original Equelo construction exploited that continuity. Although parts of
the combination were ad hoc, the combined calculation also reached a stable
fixed point and avoided the conspicuous scale drift that had motivated
normalisation.

The resulting ratings looked broadly plausible. Their typical chii curve was
largely ordered, had a striking and satisfying rise at yokozuna, and was useful
enough to place in the website as a way of exploring both the ratings and their
possible audiences.

The lower-maegashira reversal then became the M12 problem. The public-facing
`Typical Equelo Ratings` presentation implicitly treated the curve as more
authoritative and monotone than the evidence justified. Investigating that
problem led back through ordinary Elo, entrant initialisation, support,
normalisation, changing division depth, boundary-relative representations and
loosely connected divisional populations.

That investigation produced useful evidence, but it also obscured the main
route. Much of the work concerned Elo-like model choices rather than the
distinctive full-history Equelo problem.

## 2. What has now been settled well enough

### 2.1 Basic Elo has a precise project definition

The definitive baseline \(B\) is no longer an informal reference to Elo in
general. It is the declared post-1988 model with:

```text
history = represented results from 1989/01 onward
q = 400
k = constant 35
initialisation = one common rating
chronology = forecast before update
identity = RikId
rating persistence = permanent within the run
eligible result = represented W/L, irrespective of kimarite
```

### 2.2 The M12 problem is closed as a blocker

Ratings are not chii. Exact literal-chii monotonicity is neither a necessary
property of ratings learned from bouts nor a decisive validity test.

Chii remains relevant evidence. It is an institutional ordering, can inform an
entrant prior and may help where earlier bout evidence is absent. But an
empirical or fixed-point chii curve is conditional on the represented history,
banzuke structure and modelling policy. It is not a measurement of timeless
ability attached to each literal rank.

The project has therefore retained the small remaining reversal in the adopted
post-1988 prior rather than fitting it away merely to obtain a perfectly smooth
public curve.

### 2.3 The informed entrant prior has a defined role

The adopted \(P\) is an entrant prior intended to shorten the initialisation
gap. It is not a rating assigned permanently by chii and it is not a claim that
the chosen values are uniquely true.

Its current authority and domain are limited to the represented 1989-onward
chii. Historical ranks absent from that scope, including M19--M22 and J15--J24,
require a separate historical-completion decision.

### 2.4 A post-1988 successor has been selected provisionally

The controlled four-model comparison considered:

| Model | `k` policy | Entrant initialisation |
|---|---|---|
| \(B\) | constant 35 | constant |
| \(B_k\) | divisional | constant |
| \(B_P\) | constant 35 | informed prior \(P\) |
| \(B_{kP}\) | divisional | informed prior \(P\) |

\(B_{kP}\) had the lowest declared aggregate log loss, and Brier loss gave the
same ordering. Most of the improvement over \(B\) came from informed
initialisation; divisional `k` supplied a smaller additional improvement.
Calibration evidence leaves \(B_k\) as a serious alternative, and the adopted
prior was derived from the broad history being scored, so the selection is
properly described as provisional retrospective model-selection evidence.

Nevertheless, changing the selection rule after seeing the results would be
hard to defend. The current working successor is therefore:

\[
B' = B_{kP}.
\]

Some earlier story text predates this result and still describes selection of
\(B'\) as outstanding. That is documentary chronology, not a current research
blocker.

## 3. The newly clarified Equelo boundary

Divisional `k` and informed initialisation are valid Elo-family choices. They
do not by themselves define Equelo.

The shortest current lineage is:

\[
B \longrightarrow B'=B_{kP} \longrightarrow
\text{Equelo over the represented 1958--present history}.
\]

The remaining distinctive Equelo problem is therefore:

> What explicit, reproducible historical-extension policy applies \(B'\) to
> the incomplete 1958--1988 record and carries the resulting state across the
> January 1989 observability change?

This does not require Equelo to contain a novel update equation. Its distinctive
contribution may be the declared treatment of incomplete historical evidence,
population continuity, historical-only ranks and rating-scale drift.

## 4. Why a rating-mass audit comes next

It is tempting to move immediately to alternative historical prior tables. That
would leave the scale policy under-specified.

The word *inflation* currently covers several different phenomena. An open,
changing population does not guarantee monotonically rising ratings, but it can
move the mean of the active pool. The direction and size depend on who enters,
who leaves and their ratings. The selected divisional-`k` policy introduces a
separate mechanism: when two participants use different `k` values, their
updates are unequal and opposite only in sign, so a cross-division bout can
create or destroy total rating mass.

At least four contributions must therefore be distinguished:

1. **entrant composition**: ratings added when previously unrated rikishi enter
   the represented active population;
2. **departure composition**: ratings removed when rikishi leave that active
   population;
3. **bout mass change**: non-zero-sum updates caused by unequal participant
   `k` values; and
4. **observability change**: especially the large change in represented
   population at January 1989.

The object being preserved must also be named. Plausible but different objects
include:

- total rating mass among all rikishi ever encountered;
- total rating mass among the current banzuke population;
- the mean rating of the current banzuke population;
- a reference subgroup such as sekitori; and
- an externally anchored rating level.

No normalisation rule should be adopted merely because it keeps one convenient
number constant. The audit must first show what moves, why it moves and which
movement is undesirable for the intended interpretation of Equelo.

## 5. Rating-mass audit requirements

### 5.1 Purpose

The audit must describe rating-scale movement in \(B\), \(B_k\), \(B_P\) and
\(B_{kP}\) without correcting it. It is a diagnostic producer, not a new rating
model.

### 5.2 Fixed model contracts

The audit must use the exact contracts and inputs of the completed controlled
post-1988 comparison. It must not silently change `q`, `k`, \(P\), bout
eligibility, chronology, identity or history bounds.

This allows the two-by-two comparison to separate the relevant mechanisms:

- \(B\) versus \(B_P\) isolates entrant initialisation under zero-sum bouts;
- \(B\) versus \(B_k\) exposes divisional-`k` effects under constant
  initialisation; and
- \(B_P\) versus \(B_{kP}\) exposes divisional-`k` effects under \(P\).

### 5.3 Basho-level accounting

For every model and represented basho, the audit should record at least:

```text
date
active population before departures
departing rikishi count
departing rating mass and mean
active population after departures
entrant count
entrant rating mass and mean
active population after entry
rating mass before bouts
rating mass change from rated bouts
rating mass after bouts
active mean before and after each boundary
cumulative entrant, departure and bout contributions
```

The accounting identities must reconcile exactly within floating-point
tolerance. An unexplained residual is an implementation or model error, not a
category called `other`.

### 5.4 Required views

The first output should be machine-readable basho-level data. A short findings
report should then answer:

1. Does the active rating mean drift materially in each model?
2. Is the movement predominantly caused by entrants, departures or unequal-`k`
   bouts?
3. Is the movement consistently upward, consistently downward or episodic?
4. Are particular division boundaries responsible for most unequal-`k` mass
   change?
5. Does informed initialisation reduce or increase population-composition
   effects?
6. What, if anything, would a scale policy need to preserve?

Charts are useful only after the accounting table and identities are settled.

### 5.5 Explicit exclusions

The audit must not:

- apply normalisation;
- select a preferred scale correction;
- define pre-1989 priors;
- rerun the M12 search;
- judge a model by agreement with chii; or
- migrate production Equelo or website consumers.

## 6. The historical-extension tranche behind the audit

After the audit, hold \(B'\) fixed and compare a small number of full-history
constructions. The comparison should include at least:

1. \(B'\) beginning in 1989, as the no-historical-extension comparator;
2. full-history \(B'\) with no rating-mass correction;
3. full-history \(B'\) with the audit-supported correction, if the audit
   supports one; and
4. the maintained fixed-supported Equelo as a production-legacy comparator
   where a like-for-like forecast ledger can be produced.

The full-history candidates must otherwise share:

```text
q = 400
k = the selected divisional policy
entrant prior = P where P is defined
chronology = forecast before update
identity = RikId
eligible result = represented W/L irrespective of kimarite
```

The historical policies that genuinely need comparison are:

- backward use of the post-1988 prior;
- literal-rank or boundary-relative completion for historical-only ranks;
- treatment of rikishi first observed as sekitori before 1989;
- treatment of the newly observable lower-banzuke population in January 1989;
  and
- the rating-mass policy identified by the audit.

The M12 evidence makes boundary-relative completion the stronger conceptual
candidate for historically deeper Makuuchi and Juryo tails. Literal completion
is simpler and should remain a comparator rather than being rejected by
intuition alone.

## 7. The decisive historical question

The first evaluation should score identical post-1988 bouts. It should report
the whole period, but pay particular attention to the years immediately after
January 1989, when information carried from the earlier history can matter
most.

The primary question is:

> Does processing the represented 1958--1988 history improve forecasts after
> January 1989 compared with starting \(B'\) afresh in 1989?

This is the empirical heart of the next Equelo claim. If the answer is no, the
historical extension may still be interesting as a historical rating product,
but it cannot be defended as improving the post-1988 model merely because its
construction reaches a fixed point.

The use of a prior derived from the broad post-1988 history remains a provenance
qualification shared by the fitted candidates. A genuinely prospective test
can score the fixed selected model on future basho. It need not be confused
with the narrower comparison of whether carrying pre-1989 evidence into the
same fitted model adds useful information.

## 8. Decision gates

The work should proceed through explicit gates:

```text
selected post-1988 B'
  -> rating-mass audit
  -> scale-policy decision, including a decision to do nothing
  -> historical prior/completion specification
  -> controlled full-history comparison
  -> selected Equelo construction
  -> production artifacts and API migration
  -> website migration
```

Failure at a gate is informative. In particular:

- the audit may show that no material scale correction is needed;
- the historical record may add no post-1988 predictive information;
- boundary-relative completion may be indistinguishable from the simpler
  literal rule; or
- the older fixed-supported construction may remain competitive.

None of those outcomes would invalidate the useful work already completed.

## 9. Work not to reopen now

The next tranche should not wait for:

- an exactly monotone chii-to-rating curve;
- a causal explanation of every M12 reversal;
- proof of fixed-point existence or uniqueness in general;
- another general search over `q`;
- proof that divisional `k` is uniquely optimal;
- editorial consolidation of the public Elo story; or
- replacement of every older Equelo producer.

Those questions can remain documented limitations, retained evidence or later
work. They are no longer the route to the next Equelo.

## 10. Next

This proposed next step was carried out and then developed into the completed
Tranche 1 investigation. Do not restart from this section. Continue from the
[handoff](16%20Handoff%20After%20Tranche%201.md), which records the resulting
candidate model, evidence, code paths and remaining full-history work.
