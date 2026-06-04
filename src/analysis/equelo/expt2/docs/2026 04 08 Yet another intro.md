# Methodology and Interpretation

## Overview

Equelo is an Elo-based rating system designed for historical sumo data with a changing participant pool. It addresses two structural issues that prevent meaningful comparison across eras:

1. **Entry bias** — how new competitors are initialised
2. **Population turnover** — how entry and exit affect rating levels over time

The system resolves these explicitly, yielding a single, internally consistent rating scale across the full history.

---

## Observability Model (Oracle Construction)

Equelo operates on a **cleaned oracle history**, not raw records. This is not ad hoc preprocessing; it defines the domain on which the rating system is constructed.

The model is defined on the cleaned rating universe produced by the Oracle. From
1989 onward this is the represented banzuke domain. Before 1989, when full
lower-division bout data is unavailable, the rating universe retains all
raw-banzuke sekitori and lower-division rikishi who participate in retained
sekitori-involving bouts. Competitors outside this domain (mae-zumo, and some
unobserved early lower-division banzuke positions) are not represented in the
system.

The oracle is constructed as follows:

* Pre-1958 data is excluded
* Before 1989, only bouts involving at least one sekitori are retained
* Before 1989, all raw-banzuke sekitori remain in the rating universe even if
  they have no retained bouts
* From 1989 onward, only bouts between rikishi in the modelled banzuke domain are retained
* Rank annotations are collapsed to canonical `chii` values

In particular:

> Bouts involving mae-zumo rikishi are excluded because those competitors are outside the modelled state space.

This ensures:

* all participants in a bout have defined ratings
* rating updates occur within a closed, well-defined population
* rank (`chii`) is comparable across time

All results and interpretations are conditional on this observable competition network.

---

## Elo Dynamics

Ratings evolve according to a standard Elo update rule. For a bout between competitors (A) and (B):

* Expected score:
  [
  \mathbb{E}_A = \frac{1}{1 + 10^{(r_B - r_A)/q}}
  ]

* Update:
  [
  \Delta = k(\text{chii}_A) \cdot (\text{actual}_A - \mathbb{E}_A)
  ]

* Ratings are updated symmetrically:
  [
  r_A \leftarrow r_A + \Delta, \quad r_B \leftarrow r_B - \Delta
  ]

Rating mass is conserved within each scored bout.

---

## Entry: Rank-Based Fixed-Point Prior

New competitors are assigned initial ratings via a function:
[
\mu : \text{chii} \rightarrow \mathbb{R}
]

Rather than specifying (\mu) a priori, Equelo estimates it as a **fixed point**:

1. Run the simulation with current (\mu)
2. Collect **basho-start ratings** (after entry, before bouts)
3. Aggregate by `chii` and compute mean ratings
4. Apply a uniform additive shift (see below)
5. Set this as the new (\mu)
6. Repeat until convergence

At convergence:

> The initial rating assigned to each rank equals the average rating observed at that rank at basho start.

This yields a **self-consistent entrant prior**, ensuring that entry conditions are stable and invariant across eras.

---

## Exit: Closed Active-Population Dynamics

To handle population turnover, Equelo uses a **closed active-universe model**:

* When a competitor leaves the active pool, their rating is removed
* The deviation of their rating from the active mean is redistributed uniformly across remaining active competitors

This enforces:

> The mean rating of the active population is preserved at basho boundaries.

Without this, rating levels drift due to systematic entry and exit effects.

---

## Normalisation

Elo ratings depend only on differences: adding a constant to all ratings does not change expected outcomes or updates.

Equelo uses this property to apply a **uniform additive shift** during the fixed-point iteration so that the mean rating equals a chosen baseline (b).

This:

* does not affect any model dynamics
* introduces no additional structure
* serves only to fix a convenient reference level

---

## Resulting Rating Scale

The final output assigns each rikishi a rating such that:

* ratings evolve via standard Elo dynamics
* entry conditions are rank-consistent and self-consistent
* population turnover does not induce drift
* the scale is fixed for interpretability

---

## Interpretation

### Cross-Era Comparability

Equelo defines a single rating scale spanning all eras.

> Two rikishi with the same Equelo rating have the same expected performance against the model’s competitive environment.

Because entry and exit are normalised, this implies:

> A rikishi’s expected performance depends only on their rating, not on the era in which they compete.

Equivalently:

> Two rikishi with equal ratings are interchangeable across eras in terms of expected outcomes.

---

### What the Ratings Represent

An Equelo rating measures:

> Competitive strength relative to a self-consistent, historically integrated field of competitors.

This field is defined by:

* the cleaned observable bout network
* rank structure (`chii`)
* the fixed-point entrant prior
* closed-population dynamics

---

## Scope and Assumptions

The interpretation is conditional on the modelling framework:

* Entry strength is modelled as a function of rank (`chii`)
* The Elo functional form (logistic expectation and K-policy) is assumed
* The observable competition network is defined by the oracle construction

Equelo does not model:

* physical or technical changes in the sport across eras
* causal mechanisms of performance

It provides a **consistent statistical embedding** of competitors into a single rating space.

---

## Summary

Equelo resolves the main ambiguities of historical Elo rating:

* **Observability** → explicit oracle construction
* **Entry** → fixed-point rank-based prior
* **Exit** → closed-population conservation

Together, these yield:

> A stable, interpretable, and cross-era comparable rating system for a changing competitive pool.
