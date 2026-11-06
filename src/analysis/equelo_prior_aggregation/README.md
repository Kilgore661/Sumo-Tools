# Equelo Prior Aggregation

## Status

Implemented as a retained, post-fit aggregation experiment. The experiment
compares policies only and does not alter Elo-89 production. On 6 November
2026, the project accepted the support-weighted P1-WL result, P1-prime-WL, as
the official successor entrant prior. Canonical installation, replay, and
dependent artifact regeneration remain separate implementation work.

## Purpose

This package will investigate how a side-specific literal-chii entrant prior is
converted into root-chii values. It is a generic prior-aggregation experiment,
independent of the Kimarite matter and of any particular prior candidate.

The experiment applies the candidate aggregation policies to both P1 and
P1-WL. In this document, the support-weighted result derived from P1 is called
**P1-prime** (`P1'`), and the support-weighted result derived from P1-WL is
called **P1-prime-WL** (`P1'-WL`). P1-prime remains a comparator. P1-prime-WL
is the accepted official successor prior.

## Motivation

The current prior consumer removes annotations, collapses numbered sanyaku
positions to their root rank family, and takes an unweighted mean of every
rating in the resulting group. For an ordinary numbered rank such as M1, that
means:

```text
M1 = mean(M1e, M1w)
```

For Komusubi, however, it gives K1 and the much lower-support K2 cells equal
influence:

```text
K = mean(K1e, K1w, K2e, K2w)
```

In the examined P1-WL table, K2 supplied only 35 of 485 Komusubi observations
but received half of the unweighted aggregate. The resulting root K rating was
below M1, whereas both a support-weighted K and a canonical-K1-only K were
above M1. The same aggregation issue was already present in P1; P1-WL merely
made it conspicuous.

Support may also differ materially between east and west at the same numbered
rank. The support-weighted candidate therefore uses one rule for every literal
cell; it does not preserve an intermediate unweighted east/west average.

Two logically separate corrections are therefore in view:

1. **Aggregation correction (`P1` to `P1'`)**: retain the P1 literal fit but
   replace equal weighting across all literal cells, including east and west,
   with support-weighted aggregation.
2. **Bout-eligibility correction (`P1'` to `P1'-WL`)**: use the P1-WL literal
   fit, which includes represented binary win/loss bouts even when kimarite is
   missing, and apply the same support-weighted aggregation policy.

`P1'-WL` is not made by adding bouts directly to the already-aggregated `P1'`
table. The broader WL-eligible history produces its own literal ratings and
supports; those fitted values are then aggregated under the same policy.

## Experimental questions

The experiment should answer:

1. How do alternative post-fit aggregation policies change each root-chii
   prior, especially root K relative to M1?
2. How sensitive are the results to low-support numbered sanyaku overflow
   cells?
3. Does support weighting repair the pre-existing P1 aggregation problem to
   produce a coherent P1-prime candidate?
4. What additional change results when the same aggregation policy is applied
   to the WL-eligible literal fit to produce P1-prime-WL?
5. Which policy is sufficiently explicit, auditable, and reproducible for
   possible later Elo-89 adjudication?

Grouping and weighting must remain separate decisions. Mapping K2 to root K
does not by itself determine how much influence K2 should have on K.

## Candidate policies

Every run must select a policy explicitly. Existing unweighted experiments
must remain reproducible.

1. **Legacy unweighted aggregation**: every literal rating mapped to a root
   chii receives equal weight.
2. **Support-weighted aggregation**: every literal rating mapped to a paired
   chii is weighted by its own recorded support. Thus `M1e` and `M1w` are
   support-weighted into `M1`, while every numbered and sided `Y`, `O`, `S`, or
   `K` cell is support-weighted into its canonical family key (`Y1`, `O1`,
   `S1`, or `K1`). Numbered sanyaku slots are discovered from the input; there
   is no fixed upper slot number.
3. **Canonical-sanyaku aggregation**: ordinary numbered ranks average their
   available east/west values, while Y, O, S, and K use only canonical `1`
   slots.

## Minimum comparison matrix

| Literal source fit | Legacy unweighted | Support-weighted | Canonical sanyaku |
|---|---:|---:|---:|
| P1 eligibility | P1 | P1-prime (`P1'`) | required comparator |
| WL eligibility | P1-WL | P1-prime-WL (`P1'-WL`) | required comparator |

This matrix separates the aggregation-policy contrast (columns) from the
bout-eligibility contrast (rows). Producing both weighted candidates is
necessary to show that the aggregation defect belongs to P1 and predates the
missing-kimarite correction. The experiment compares these candidates; it does
not by itself promote either one.

## Input contract

Each literal source table must provide at least:

```text
chii
rating
support
```

Missing support must not silently become unit support. Each input must be
identified by its path and cryptographic hash, rather than by treating a moving
filename as canonical.

## Running the experiment

From the repository root:

```powershell
python -m src.analysis.equelo_prior_aggregation --output <new-output-directory>
```

The defaults select the retained same-History P1 literal fit and the accepted
P1-WL literal fit. Alternative qualifying sources may be supplied explicitly.
The runner refuses to overwrite an existing output directory. By default it
also materialises the accepted P1-prime-WL rows at the fixed repository path:

```text
src/analysis/equelo_prior_aggregation/results/priors.csv
```

An identical existing `priors.csv` is accepted, making reproduction
idempotent. If a run derives different content, it refuses to replace the
persisted official prior silently.

## Retained run

The first retained run is:

```text
files/output/analysis/equelo_prior_aggregation/2026-11-06-run-001/
```

Its headline result is:

| Source/candidate | K1 | M1 | K1 minus M1 |
|---|---:|---:|---:|
| P1 (legacy) | 2213.254912 | 2257.998577 | -44.743664 |
| P1-prime (support-weighted) | 2279.037975 | 2257.998577 | +21.039399 |
| P1-WL (legacy) | 2258.522898 | 2301.520015 | -42.997117 |
| P1-prime-WL (support-weighted) | 2323.047889 | 2301.520015 | +21.527874 |

Support weighting therefore removes the K1-below-M1 inversion in both source
fits.

## Decision

P1-prime-WL is accepted as the official successor to P1-WL. The selected rows
in `paired_priors.csv` are exactly those with:

```text
source = p1-wl
candidate = P1-prime-WL
policy = support_weighted
```

The formal decision and artifact identities are recorded in the Elo-89
validation matter at
[`Prior Aggregation/README.md`](../../validation/elo89-expert-account/Matters%20Arising/Prior%20Aggregation/README.md).
Acceptance does not make the experimental runner a production dependency.
Production must consume a frozen paired prior through a strict loader and must
record the frozen prior and derivation-manifest hashes.

The accepted standalone table is
[`results/priors.csv`](results/priors.csv), with SHA-256
`41430ce50f61bf2769ee7b37e4c964d5ecd00e78fe554a9790a869ad35955d38`.
It contains 484 rows in the strict schema `rank_pair,ordinal,rating` and no
experimental comparator columns.

## Output contract

A run retains outputs without overwriting existing artifacts:

```text
files/output/analysis/equelo_prior_aggregation/<run-id>/
    manifest.json
    paired_priors.csv
    comparison.csv
    findings.md
```

The accepted P1-prime-WL result is the deliberate exception to the normal
`files/output` boundary. It is persisted in the repository at:

```text
src/analysis/equelo_prior_aggregation/results/priors.csv
```

The manifest should record source identities, grouping and weighting policies,
formulas, row counts, support totals, software revision, and output hashes. The
paired-priors table should retain enough constituent detail to audit a root
value such as K.

## Reproducibility boundary

The experiment begins with qualifying, already-fitted literal prior tables and
their recorded support. It ends with candidate paired root-chii priors,
comparisons, findings, and a derivation manifest. It does not own source-prior
fitting, Elo-89 replay, or site-data generation.

The P1 and P1-WL literal source fits are fixed inputs. This experiment must not
attribute the P1-to-P1-prime difference to bout eligibility, or the
P1-prime-to-P1-prime-WL difference to aggregation: the former is the
aggregation-policy contrast, while the latter is the WL-eligibility contrast
under a common aggregation policy.

The accepted integration boundary is a frozen, already-aggregated paired prior
plus its derivation manifest. Production should load that artifact strictly;
it should not calculate weighted means dynamically.

## Non-goals

The initial package will not:

- refit P1 or P1-WL;
- decide bout eligibility;
- modify the Kimarite package or its retained findings;
- change the accepted Elo-89 prior or replay;
- overwrite existing artifacts;
- assume exact monotonicity with chii is required;
- equate chii order with rating order.

## Implementation state

The package contains a command-line runner, strict literal-prior loading,
generic policy aggregation, retained artifact generation, focused tests, and
one retained run. The accepted P1-prime-WL table is persisted under `results`;
this package does not yet install it in the Elo-89 replay.
