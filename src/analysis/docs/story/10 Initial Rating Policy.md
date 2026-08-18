# Initial Rating Policy

## Status

This is the normative project decision produced by the M12 investigation. It
governs the next smoothing and validation work. It does not yet record a
generated production curve; that artifact remains to be built.

For the reasoning, see the
[consolidated research record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md).
For reproduction details, see the
[experiment catalogue](09%20M12%20Experiment%20Catalogue.md).

## Purpose of initial ratings

Initial ratings are entrant priors. Their purpose is to reduce arbitrary
initialisation and the adjustment gap before bout evidence accumulates. They
are not claims that each chii has one timeless intrinsic rating.

The exact prior values need to be sensible, ordered, stable and practically
useful. Ratings after entry are allowed to disagree with chii and need not be
monotone with respect to it.

## Adopted policy

1. The maintained chii-based entrant-prior curve will be monotone: a worse
   chii must not receive a higher starting rating.
2. Monotonicity is imposed as transparent ordinal regularisation, not reported
   as a finding of the fixed-point experiments.
3. The empirical source curve, support, smoothing method and resulting curve
   must be retained together with provenance.
4. Support-weighted non-increasing isotonic regression is the preferred first
   implementation. It provides the closest reproducible monotone curve to the
   source estimates under the declared weights.
5. Any manual adjustment must be exceptional, explicit, justified and recorded
   alongside the unadjusted isotonic result.
6. Unsupported chii must not independently participate in the solve. Their
   values must be supplied by a declared completion rule with provenance.
7. The final curve must be put on the declared Equelo scale by an explicit
   common anchoring operation that does not disturb monotonicity.

## Decisions still required by the smoothing implementation

Before generating the maintained curve, the implementation record must state:

- which experimental curve is the source target;
- the history period used to estimate it;
- whether east and west are fitted separately, strictly ordered, or first
  combined into rank pairs;
- the exact support weight used by isotonic regression;
- how sanyaku and lower-division annotations are collapsed;
- where the supported domain ends;
- the completion rule beyond that domain; and
- the scale anchor applied after fitting.

These are implementation choices, not reasons to reopen the search for a
perfect explanatory model of the M12 curve.

## Existing implementation precedent

The repository already contains a curated monotone `v5` landmark curve in
`fixed_v1.initial_rating`, reused by `fixed_supported.landmarks` for public
“Typical Equelo Values”. It is not the maintained entrant initialiser.

Task C must treat that curve as an explicit comparator. Reusable lookup and
monotone-interpolation code may be retained, but the existing rank deletions,
manual masks and one-sided downward clamp must not silently become the new
operational policy. At minimum, compare:

1. the existing v5-style curated curve;
2. the preferred support-weighted isotonic fit; and
3. one reasonable sensitivity alternative, such as equal-weight isotonic
   fitting or a different declared support transform.

## Validation contract

The maintained curve is acceptable only if the resulting Equelo system is
practically adequate.

The principal comparison must:

- compare Basic Elo and Equelo over the same eligible bouts and chronology;
- make every forecast before applying the corresponding result;
- derive or select entrant priors using training information only;
- evaluate on a later held-out period;
- report log loss, Brier loss, calibration and accuracy;
- report all-bout, sekitori and sub-sekitori results;
- show performance through time rather than only one epoch average; and
- test reasonable alternative monotone prior curves.

Equelo should have predictive performance at least comparable with Basic Elo.
Material sensitivity to reasonable prior alternatives counts against the
maintained curve. Insensitivity is evidence that the precise initial numbers
are not carrying the eventual result.

## Public-description boundary

Public documentation may say:

> Initial ratings are monotone priors based on banzuke position. Their scale
> was informed by experiments with historical ratings and results. Because
> banzuke structure has varied, there is no uniquely determined empirical
> rating for every chii. The chosen values provide a sensible starting scale;
> ratings thereafter respond to bout results.

Public documentation must not say or imply that:

- the raw fixed-point curve was monotone;
- history uniquely determines the adopted value at each chii;
- convergence validates the prior categories;
- the smoothing explains the M12 phenomenon; or
- predictive validity follows merely from the construction.

The public account should be written only after the predictive comparison has
established what claims the evidence supports.
