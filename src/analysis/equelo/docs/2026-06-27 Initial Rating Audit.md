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

`aggregate_by_chii` observes basho-start ratings by chii and averages those
observations. `normalise` currently applies the mean adjustment used by the
implementation.

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
