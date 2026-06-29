# Initial Rating Audit

## Status

Working note from 2026-06-27.

This note records the current shared understanding of the Equelo initial-rating
process and the next audit questions. It is intentionally narrower than the
existing fixed-supported design notes.

## Core Model

There is one simulation algorithm:

```text
R = S_H(C)
```

where:

* `H` is a history;
* `C` is an initial-rating map or function for every chii needed by entrants in
  `H`;
* `R` is the rating history produced by simulating `H` from `C`.

The fixed-point construction wraps this simulator:

```text
C_next = normalise(aggregate_by_chii(S_H(C)))
```

`aggregate_by_chii` means: put basho-start rikishi ratings into bins labelled
by chii, then take the arithmetic mean of each bin. `normalise` currently
applies the mean adjustment used by the implementation.

## Current Status: Modern Data

The post-1989 history is the significant modern population of bout results
because it is complete across the banzuke. It is therefore the cleanest place to
understand the model before trying to understand the combined 1958+ solve.

The current model for modern ratings is coherent:

* simulate post-1989 bouts;
* use mean preservation to avoid rating inflation;
* bin basho-start rikishi ratings by chii;
* average each chii bin;
* iterate this process as a fixed-point solver so that initial ratings are not
  chosen arbitrarily.

The unsatisfactory feature of this population is that not every chii has the
same support. The current model is systemically monotonic from Y1e down to about
Jd100w, apart from known local irregularities. Below that, the behaviour is not
monotonic in the intended direction:

* Jd101e to roughly Jd210w rises as rank number increases;
* Jk1 to roughly Jk77e also rises as rank number increases, after an initial
  drop at Jk1.

The leading hypothesis is that the model fails in these ranges because support
is low, churn is high, or both. This is not yet understood well enough to carry
the same model confidently into the combined pre/post-1989 solve.

Possible treatments for the bottom range:

1. Ignore results from Jd101e down when deriving rank priors, on the basis that
   support is too low or churn is too high.
2. Include those ranks in the output, but fill their initial ratings from
   curated values rather than directly from the fixed-point estimate.
3. Include them using model-generated values, then explain any resulting
   irregularities. This is methodologically suspect unless the explanation can
   be made close to principled rather than hand-waving.

Open questions:

* How should churn be measured, and is it noticeably higher from Jd101e down?
* If curated values are used, where do they come from? One candidate is curve
  interpolation from the well-behaved part of the ranking.
* Can any model-generated treatment of the bottom range be justified by a
  principled argument rather than by convenience?

The likely next investigation is to branch from the point where the Highest
Equelo artifact revealed the anomaly and study the modern solver in isolation.

## Current Production Factorisation

The current fixed-supported path first solves the modern-data fixed point:

```text
C_modern* = fixed_point(H_1989+, constant)
```

This is the cleanest self-contained result because 1989 onward is the closest
thing in the project to complete banzuke-wise data.

The code then uses that modern fixed point as the seed for a longer-history
fixed-point solve:

```text
C_full* = fixed_point(H_1958+, seed = C_modern*)
```

Thus the first full-history simulation is already informed by the modern
fixed point. The process does not first run a separate sekitori-only fixed
point.

## Provisional Classification

The concern is not whether the simulator can run. A raw simulation can run from
a constant initial rating. The concern is which transforms are epistemological
and which are outcome-shaping.

Currently agreed:

* The pre-1989/post-1989 data split is epistemological: it reflects what the
  source contains.
* Ignoring `fusen` and `blank` bouts is ordinary Elo logic: no fought bout, no
  rating change.
* The pre-1958 guard is probably irrelevant defensive code if no such data
  exists.
* Landmark smoothing is out of scope for this audit.

## Main Suspect

The most promising lead is mean normalisation.

The current normalisation shifts every chii in the solved map by the same
additive amount. Ultra-low-support chii can therefore accumulate mean
adjustments rather than evidence from bouts. This may explain the historical
low-rank blow-up, and may also be related to shapes such as M13-M17 appearing
too high relative to M12.

There is a second, related failure mode even if normalisation is restricted to
chii that exist in a given basho. A one-observation chii is still updated by the
fixed-point loop from its own previous output: if it starts at 1517, produces an
observed mean of 1520, then receives a normalisation bump to 1525, the next
iteration starts from 1525 and can repeat the same structural update. This is
not merely a placeholder problem; it is a low-support feedback problem in the
fixed-point construction.

The supported-domain threshold may be a symptom patch for this effect rather
than the underlying principle. The Jk73w-style extreme rating appears to have
motivated excluding low-support chii rather than revisiting how mean adjustment
is distributed.

Candidate alternative:

```text
normalise by chii frequency or observation weight
```

That is, preserve the rating scale by attaching the correction to where the data
actually has mass, instead of treating every chii as equally supported.

## Open Question: Chii Aggregation

The second important audit area is chii aggregation/collapse.

We need to verify exactly what the fixed-supported path currently does with:

* annotations;
* east/west distinctions;
* sanyaku overflow or multiple same-rank cases.

The desired epistemological stance is: remove or collapse distinctions only
when the rank meaning is not understood or not epistemically supportable.
Collapsing merely because the distinctions are inconvenient for the code is not
good science.

## Open Question: Monotonicity

There are at least two different kinds of monotonicity issue.

Pointwise data noise is a local empirical irregularity: for example, one exact
east/west chii may sit slightly above its neighbour because the rikishi who
occupied that chii happened to do well. This should be measured, but it is not
necessarily evidence of a broken model.

Systemic monotonicity failure is a coherent rank band being out of place. The
M12 dip/M13-M17 rise is one example. Another suspected example is the modern
no-normalisation bottom-division curve: roughly monotone down to deep Jonidan,
then rising through Jonokuchi, dipping at Jk1, and rising again toward the last
Jk rating. The current intuition is that this may be connected to churn and
division persistence rather than ordinary pointwise noise. Existing division
persistence work should be revisited before designing a repair.

A third possible source of systemic behaviour is historical rank-domain
mismatch. The working assumption had been that post-1989 data contains more
chii, but pre-1989 Makuuchi and Juryo had long tails for a sustained period,
with Makuuchi extending into roughly M22/M23 and Juryo into roughly J24. These
historical chii may affect the full-history fixed point in ways that are not
captured by a simple pre/post-1989 completeness story. A similar question may
apply near the bottom of the modern banzuke, especially below Jd100 and in
Jonokuchi beyond the stable core, though Jonokuchi may require separate
treatment because of entry churn.

## Next Work

1. Audit the current normalisation rule:
   * reproduce how the per-iteration shift accumulates;
   * compare high-support and low-support chii;
   * inspect whether the suspicious ranks are mostly evidence-driven or
     shift-driven.

2. Prototype a weighted normalisation rule:
   * use basho-start observation counts or chii occurrence frequency as weights;
   * compare against current fixed-supported outputs;
   * check whether low-support blow-ups and M12/M13-M17 inversions improve
     without arbitrary support thresholds.

3. Audit chii aggregation:
   * list the exact collapse rules used by fixed-supported;
   * classify each as epistemological, pragmatic, or outcome-shaping;
   * identify any rule that should become a configurable experiment rather than
     a hidden assumption.

4. Run the paired fixed-point experiment:
   * solve the post-1989 fixed point with mean preservation;
   * solve the same post-1989 fixed point without mean preservation;
   * compare monotonicity violations and scale drift, so the effect of
     rank-calibrated initial ratings can be separated from the effect of the
     stationarity convention.
