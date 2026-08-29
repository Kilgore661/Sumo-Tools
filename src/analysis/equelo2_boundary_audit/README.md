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
