# Elo-89 entrant-prior aggregation

## Status

Implemented and accepted on 6 November 2026. The selected 484-row paired
entrant prior is denoted **P89** (\(P_{89}\)) and is persisted at:

```text
src/analysis/equelo_prior_aggregation/results/priors.csv
```

Its SHA-256 is
`41430ce50f61bf2769ee7b37e4c964d5ecd00e78fe554a9790a869ad35955d38`.
Elo-89 loads that file strictly and does not repeat the aggregation during
replay.

## Purpose

The fixed-point producer estimates ratings and support for literal banzuke
cells. Elo-89 consumes one side-free value for each paired rank key. This
package defines and audits the conversion between those representations.

The accepted rule is direct support weighting. For consumer key \(g\), with
literal cells \(i\), ratings \(r_i\), and observed support \(n_i\):

\[
P_{89}(g)=
\frac{\sum_{i\in g}n_i r_i}{\sum_{i\in g}n_i}.
\]

East and west retain their individual support. Every numbered position
present for Y, O, S and K maps to the canonical family consumer key. There is
no hard-coded maximum slot number. Other ranks map to their ordinary paired
key after side and annotation removal.

## Why support weighting?

The consumer key represents the pooled observations mapped to that rank.
Giving every literal cell one equal vote would make the answer depend on how
the cells happened to be subdivided and would give a rare cell the same
influence as a heavily observed one. Support weighting instead calculates the
mean rating of the represented observations in the pool.

This is a modelling choice, not a theorem that support count is the uniquely
optimal statistical weight. A hierarchical or uncertainty-weighted entrant
model remains a possible successor. The accepted rule is transparent,
generic, reproducible, and avoids discarding supported cells.

For the retained source, K2 supplied only 35 of 485 Komusubi observations.
Equal-cell averaging allowed that rare cell to exert the same influence as
K1 and placed the paired Komusubi value below M1. Under P89:

| Rank | Rating |
|---|---:|
| K1 | 2323.047889 |
| M1 | 2301.520015 |

The rule was applied to the whole table, not tuned only to change this pair.
The complete map is broadly ordered but is not forced to be perfectly
monotone.

## Evidence boundary

The aggregation experiment compared:

1. equal weighting of mapped cells;
2. direct support weighting of every mapped cell; and
3. retaining only canonical sanyaku slot 1.

Direct support weighting was selected because it pools all represented
observations without giving arbitrary cell boundaries equal influence. The
canonical-slot policy would discard supported observations.

P89 inherits a tested predictive lineage. The canonical P1 source passed the
existing predictive gate, and the matched P1-WL replay produced nearly the
same rating structure with slightly better aggregate log and Brier loss. The
aggregation experiment then compared the post-fit pooling rules and selected
support weighting because it represents the underlying observations more
defensibly; it was not selected on a claim of improved prediction.

The resulting P89 map has been loaded through a complete Elo-89 replay and
dependent `make_site89` build. Those checks establish artifact integrity,
schema enforcement, replay compatibility and unchanged bout counts. What has
not been isolated is the incremental predictive effect of replacing the
legacy aggregation of P1-WL with support weighting. This is narrower than
saying that P89 or its fitted source was never predictively checked.

## Reproduction

Run the retained aggregation package with a new output directory:

```powershell
python -m src.analysis.equelo_prior_aggregation --output <new-output-directory>
```

The run writes auditable candidate, constituent, comparison, findings and
manifest artifacts. It refuses to overwrite an existing output directory.
The source-controlled `results/priors.csv` changes only through an explicit
promotion decision.

## Reproducibility boundary

The package begins with a qualifying, already-fitted literal prior whose rows
contain rating and support. It ends with candidate paired values and their
derivation record. It does not:

- decide bout eligibility;
- perform literal-prior fixed-point fitting;
- run the production Elo-89 replay;
- deploy the website;
- impose monotonic smoothing; or
- establish that P89 is timeless or uniquely optimal.

The fixed-point source, aggregation rule, source identities, support totals,
software revision and output hashes together identify a fitted release.
