# Prior Aggregation

> **Continuation, 8 November 2026:** The support-weighting policy decided
> here is unchanged. P89 has since been rebuilt from the selected
> epsilon-8.5 / iteration-20 literal source. The currently installed paired
> table has SHA-256
> `31ba2ea5430fb6a117b80290e78570cbbb160875febb6af14664a6c64ec93cdf`.
> The hashes and values below identify the original epsilon-10 aggregation
> decision and remain part of its audit trail.

## Status

Concluded on 6 November 2026. P1-prime-WL (`P1'-WL`) is accepted as the
official successor Elo-89 entrant prior. The strict production loader has
been installed and a complete candidate Elo-89 replay and site build have
been verified against the frozen artifact.

## Question

How should side-specific literal-chii ratings and support be aggregated into
the paired prior consumed by Elo-89?

The legacy consumer mapped literal cells to paired rank keys and gave every
cell equal weight. For numbered sanyaku families this gave low-support overflow
positions such as K2 the same total influence as K1. It also ignored material
support differences between east and west cells. The resulting legacy P1 and
P1-WL paired priors both placed K1 below M1.

## Evidence

The generic experiment under
[`src/analysis/equelo_prior_aggregation`](../../../../analysis/equelo_prior_aggregation/README.md)
compared three post-fit aggregation policies for the same-history P1 and the
accepted P1-WL literal fits:

1. legacy unweighted aggregation;
2. direct support-weighted aggregation of every mapped literal cell; and
3. canonical-sanyaku aggregation using only numbered slot 1.

The support-weighted rule is generic. East and west retain their individual
support. Every numbered position present for Y, O, S, and K maps to the
canonical family consumer key, with no hard-coded maximum position number.

The retained run is:

```text
files/output/analysis/equelo_prior_aggregation/2026-11-06-run-001/
```

Its headline comparison was:

| Prior | K1 | M1 | K1 minus M1 |
|---|---:|---:|---:|
| P1 legacy | 2213.254912 | 2257.998577 | -44.743664 |
| P1-prime | 2279.037975 | 2257.998577 | +21.039399 |
| P1-WL legacy | 2258.522898 | 2301.520015 | -42.997117 |
| P1-prime-WL | 2323.047889 | 2301.520015 | +21.527874 |

The same support-weighting policy raised all four sanyaku family aggregates in
both source fits. P1-prime established that the inversion was an aggregation
problem already present in P1; it was not caused by the missing-kimarite
eligibility correction.

## Decision

Adopt P1-prime-WL as the official successor entrant prior.

Its construction is:

```text
accepted P1-WL literal ratings and support
    -> map each literal cell to the paired consumer key
    -> sum(rating * support) / sum(support) within each key
    -> frozen P1-prime-WL paired prior
```

This decision combines two previously separate corrections in their logical
order:

1. P1 to P1-prime corrects the arbitrary unweighted aggregation policy.
2. P1-prime to P1-prime-WL retains the accepted rule that represented binary
   W/L bouts remain eligible when kimarite is missing.

P1-prime is retained as the controlled aggregation comparator. It is not the
selected production successor. The canonical-sanyaku alternative is also not
selected.

## Exact artifact identity

The accepted candidate is the subset of `paired_priors.csv` satisfying:

```text
source = p1-wl
candidate = P1-prime-WL
policy = support_weighted
```

The retained identities are:

| Artifact | SHA-256 |
|---|---|
| Accepted literal P1-WL source | `6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486` |
| Aggregation manifest | `9cb1b01680a2e6de61b3ac50c6944e9390338a370ae1df3cd927165e953364d9` |
| Auditable paired-priors table | `9710a37c5b50a7891f8cde7dc45fea6fcb66e44c02e69929b6f5ac02a60c8a2c` |
| Comparison table | `8aa75142270e07e6f3f0f03e96f69a56d27448f634f2602144af3cb6e12e9bbe` |
| Generated findings | `83f273970a9071d1f3ad20843f963684314ced45f88411a215bceafbb7e5dc27` |

The selected 484 rows are now persisted on their own at:

```text
src/analysis/equelo_prior_aggregation/results/priors.csv
```

That strict `rank_pair,ordinal,rating` file has SHA-256
`41430ce50f61bf2769ee7b37e4c964d5ecd00e78fe554a9790a869ad35955d38`.

The combined experimental table remains the audit artifact. The standalone
`results/priors.csv` is the frozen strict input selected for production.

## Production consequence

The Elo-89 producer now loads the persisted paired file strictly and records
its path and SHA-256 identity. A complete candidate replay through 2026/09 and
the dependent `make_site89` build succeeded without changing replay
mathematics or bout eligibility. Public typical-rating and provenance wording
now describes the artifact as P1-prime-WL rather than as a simple east/west
average.

The verified candidate outputs are:

```text
files/output/analysis/site89_bundle_p1_prime_wl/
files/output/make_site89_p1_prime_wl/
```

The replay retained the `1989/01` through `2026/09` history interval, 581,634
rated bouts, 3,034 excluded fusen and 3 other excluded outcomes. These are
candidate verification artifacts; this record does not claim that the
ordinary deployment path has been published.
