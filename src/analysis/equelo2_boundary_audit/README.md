# Equelo2 January-1989 Boundary Audit

This package compares two rating states for the same event: the start of the
January 1989 basho, before any January bouts. It uses only rikishi represented
in both November 1988 and January 1989:

- the rating carried by the full-history replay after the November results and
  January population normalisation;
- the fresh Elo-89 rating assigned from the January chii.

It writes a matched rikishi table, overall and divisional summaries, the two
rating maps at literal January chii, the corresponding canonical Elo-89
side-paired view, and the largest individual differences.

It also performs a directional tenure-cohort sanity check. Career tenure starts
with the first represented proper chii (Jk or above), not an administrative
`Mz`, `Bg` or `Kg` appearance. Nested 0, 1, 2, 3, 5 and 10-year cohorts are
reported. The declared primary comparison is five years against zero years;
both mean absolute and RMS rating difference must decrease for it to pass.
Within-division metrics are retained where at least ten rikishi remain.

Finally, it derives the one-pass chii map implied by the complete 1958-onward
replay. This is not a full-history fixed-point calculation. For every
annotation-free literal chii, the code averages all basho-start ratings across
the replay, applies the canonical support-proportional recentering once at
`MODEL_BASE = 1517`, and then applies the same unweighted east/west pairing used
to consume P1. Common-domain literal and paired maps are compared with P1;
historical-only ranks are reported separately.

## Retained result

The start-state comparison contains 741 matched incumbents. Historical and
fresh Elo-89 ratings have Pearson correlation `0.9340` and Spearman correlation
`0.8817`, but the near-zero mean difference conceals systematic divisional
offsets and a mean absolute difference of `68.401` points.

The declared five-year tenure check does not pass its absolute-difference
criterion: MAE increases from `68.401` to `75.505` points and RMS difference
from `89.631` to `99.332` points. Rank agreement is mixed but more favourable:
Spearman correlation rises from `0.8817` to `0.9048`, while Pearson changes
from `0.9340` to `0.9310`.

The division-controlled result is not a uniform failure. At five years, MAE
and RMS difference both improve in Makuuchi, Juryo and Makushita. Sandanme is
roughly flat to worse, and Jonidan becomes materially worse. Tenure therefore
does increase the amount of represented evidence, but it also selects a
different mixture of divisions and career trajectories; it is not a pure
measure of rating reliability.

The retained interpretation is that numerical equality is rejected. Makuuchi
shows broad agreement in ordering, not equality of rating level: its Pearson
and Spearman correlations are `0.8815` and `0.8276`, while historical ratings
average `101.703` points above the fresh priors and have MAE `106.363` points.
This is not inherently a defect. The prior discards individual history, while
the historical rating is intended to retain it.

Canonical P1 is an entrant-initialisation policy, not a target for mature
ratings. A later propagation analysis should test whether the historical and
fresh-start replay worlds converge as they process the same post-1988 evidence.
It should not test whether final individual ratings or an end-of-basho
chii/rating map return to P1.

The one-pass full-history implied map contains 1,125 annotation-free literal
chii and 558 canonical pairs. All 484 P1 pairs occur in it; the remaining 74
pairs are historical-only. Over the common domain, the full-history map has
Pearson correlation `0.979457` and Spearman correlation `0.955111` with P1.
Mean absolute difference is `47.291` points and RMS difference `57.687` points.

The close overall shape conceals division-level shifts. Relative to P1, the
one-pass map averages `+149.273` points in Makuuchi, `+39.552` in Juryo,
`-35.350` in Makushita, `-35.783` in Sandanme, `-12.624` in Jonidan and
`-43.761` in Jonokuchi. Makushita and Sandanme retain near-perfect within-
division ordering; Jonokuchi remains the weakest division by rank correlation.

Run against the retained full-history output with:

```powershell
python -m src.analysis.equelo2_boundary_audit
```

The default output is:

```text
files/output/analysis/equelo2_boundary_audit/1989_01/
```

This is a read-only analysis of the existing handover and rating-ledger
artifacts. It does not rerun or modify either rating model.
