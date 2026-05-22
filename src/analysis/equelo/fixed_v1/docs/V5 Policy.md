# V5 Policy

## Status

Emerging policy note.

This note records the current interpretation of the fixed-v1 v5 curve for
public-site rating landmarks and chii-like labels.

## 1. What v5 Is

The v5 curve is a curated, strictly monotone rating-landmark curve derived from
the fixed-v1 entrant initial ratings.

It is not the raw fixed-v1 rating series and it is not an observed historical
fact.  It is a deterministic public interpretation layer for questions such as:

```text
roughly what rating corresponds to this rank label?
```

## 2. Domain

The v5 curve is defined on a curated chii domain.

The current lower bound is `Jd100w`.  Historical or rare slots deleted from the
v5 domain are not represented.  Annotated chii are not represented directly.

Consumers should derive exact support from `InitialRatingCurve.v5()` rather
than duplicating the domain by hand.

## 3. Exact Chii

For a side-bearing, annotation-free chii inside the v5 domain:

```text
v5(M3e) = direct lookup of M3e in InitialRatingCurve.v5()
```

If the exact chii is not in the v5 domain, the consumer must use an explicit
policy rather than falling through silently.

## 4. Annotations

For v5 landmark purposes, annotations are ignored:

```text
v5(M3eHD) = v5(M3e)
```

This is a chosen public interpretation, not a claim that the annotation has no
historical meaning.

## 5. Numbered Sanyaku Slots

For v5 landmark purposes, `Y`, `O`, `S`, and `K` are treated as rank-family
landmarks.  Numbered slots beyond `1` collapse to the canonical `1` slot while
preserving side:

```text
v5(O3e) = v5(O1e)
v5(S2w) = v5(S1w)
v5(K2e) = v5(K1e)
```

This is canonicalisation by rank family, not nearest-rank approximation.

## 6. Sideless Numbered Labels

For labels such as `M3`, `S2`, or `J1`, the existing policy is to average the
available side-bearing v5 ratings:

```text
v5(M3) = average(v5(M3e), v5(M3w))
```

The implementation should record the support used, for example the number of
side ratings and the side-specific values.  This is already the pattern used by
the sideless matchup trace code.

If sanyaku canonicalisation is in effect, apply it before sideless aggregation:

```text
v5(S2) = average(v5(S1e), v5(S1w))
```

## 7. Rank-Family Labels

Labels such as `S`, `K`, `M`, or `J` are aggregate labels, not exact chii.

For `Y`, `O`, `S`, and `K`, the public landmark interpretation should aggregate
only the canonical `1` slots:

```text
v5(S) = average(v5(S1e), v5(S1w))
```

For wider families such as `M`, `J`, `Ms`, `Sd`, or `Jd`, no single default
meaning is currently fixed.  Possible meanings include an unweighted average
over the v5 domain, a selected headline slot such as `M1` or `J1`, or a
context-weighted average.  Consumers must name the policy they use.

## 8. Contextual Aggregates

Some pages may ask for a context-specific rating for a chii-like label, using
only the chii present in that page or weighting by observations.

That is a different operation from the static v5 landmark curve.  Such pages
must document their support and weighting policy.

## 9. Public Wording

Public pages should avoid implying that v5 ratings reveal the true rating of a
rank title.  Prefer wording such as:

```text
rating landmark
rough guide
approximate rank equivalent
```

The policy is a useful interpretation layer, not a claim about rank essence.
