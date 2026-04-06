# **Problem Statement: The 1989 Observability Cliff and Rating Initialisation**

## 1. Context

We model competitive strength in historical sumo using an Elo-based system in which ratings evolve through sequential bout outcomes.

The system is **path-dependent**: ratings at any time reflect both current performance and prior history. As a result, how competitors are initialised when they first appear in the dataset has a material impact on the evolution of ratings.

---

## 2. The Observability Cliff

The historical dataset exhibits a structural discontinuity around 1989:

* A large number of rikishi appear in the data at once.
* These rikishi are not new competitors; rather, their results become newly observable.
* Prior to this point, their competitive history is effectively latent.

This produces what we term the **1989 observability cliff**:

> A sudden expansion of the observable population, without corresponding prior rating information.

---

## 3. Consequences of Flat Initialisation

Under standard Elo practice, any competitor without prior history is initialised at a baseline rating ( b ).

Applied at the observability cliff, this implies:

* Hundreds of already-active rikishi are assigned identical ratings at entry.
* The rating distribution is artificially compressed.
* The mean and structure of ratings are perturbed.
* The system requires a substantial period to re-equilibrate.

Empirically, this manifests as a visible discontinuity (the “cliff”) in time series of aggregate statistics such as the mean rating.

---

## 4. Available Structure at Entry

Although individual rating histories are unavailable at the point of entry, each rikishi is associated with a **rank (chii / ordinal)**.

This rank encodes structured information about competitive standing and provides a potential proxy for expected strength.

---

## 5. Objective

The objective is to improve rating initialisation in the presence of partial observability, in order to:

* Reduce artificial transients caused by flat initialisation
* Mitigate distortions introduced by large-scale observability changes (e.g. 1989)
* Improve cross-era comparability of ratings

Specifically, we seek to:

> **Estimate a mapping from rank (ordinal) to a typical rating, and use this mapping to initialise competitors whose prior rating history is unavailable.**

---

## 6. Self-Consistency Requirement

The rank-based initialisation should be consistent with the Elo dynamics under which ratings evolve.

That is:

* When ratings are initialised using the rank-based mapping
* and the historical sequence of bouts is simulated
* the resulting relationship between rank and rating should reproduce the same mapping (up to an additive constant)

This defines a **self-consistent prior** for rank-based initialisation.

---

## 7. Scope

This approach:

* Uses rank as a proxy for expected strength under missing information
* Does **not** assume that rank is determined by rating
* Does **not** attempt to model promotion or ranking dynamics

It is concerned solely with improving initialisation under partial observability.

---

# **Method (Draft): Estimating and Applying Rank-Based Initialisation**

We consider two complementary approaches for estimating a rank-to-rating mapping.

---

## **Method A: Whole-History Fixed-Point Estimation**

### Overview

Estimate a mapping from ordinal to rating using the entire historical dataset via fixed-point iteration.

### Procedure

1. **Initialisation**
   
   * Assign all entrants the baseline rating ( b )

2. **Simulation**
   
   * Run the Elo model over the full historical dataset

3. **Aggregation**
   
   * For each ordinal, compute the average rating of rikishi observed at that ordinal

4. **Normalisation**
   
   * Apply a uniform shift so that the mapping satisfies a chosen anchoring condition (e.g. mean equals ( b ))

5. **Update**
   
   * Use the resulting ordinal-to-rating mapping as the initialisation rule for the next iteration

6. **Iteration**
   
   * Repeat steps 2–5 until convergence (changes in the mapping fall below a threshold)

### Interpretation

The fixed point represents a **self-consistent rank prior** under the full historical process.

---

## **Method B: Post-1989 Calibration and Full-History Application**

### Overview

Use the post-1989 era, where observability is more complete, to estimate a rank-based prior, then apply this prior to the full historical dataset.

### Procedure

1. **Calibration Phase (Post-1989)**
   
   * Restrict the dataset to post-1989 basho
   * Estimate an ordinal-to-rating mapping using Method A (or a single-pass aggregation if preferred)

2. **Initialisation of Full History**
   
   * Use the calibrated mapping to initialise all entrants in the full dataset, including pre-1989 and observability-cliff entrants

3. **Full Simulation**
   
   * Run the Elo model over the entire historical dataset using this initialisation

4. **Optional Refinement**
   
   * Optionally perform further fixed-point iterations over the full dataset, starting from the calibrated mapping

### Interpretation

This method treats the post-1989 era as a **calibration regime**, providing a more reliable estimate of the rank-strength relationship, which is then applied to earlier periods.

---

## **Comparison and Evaluation**

The two methods can be compared along several dimensions:

* Presence and magnitude of the 1989 cliff
* Stability of mean rating over time
* Sensitivity to initialisation
* Consistency of ordinal-to-rating mappings
* Cross-era comparability

Agreement between methods (up to a uniform shift) would support the robustness of the inferred mapping. Divergence would indicate sensitivity to data completeness and modelling assumptions.

---

## **Final Note**

In both methods, absolute rating levels are determined only up to an additive constant. Any normalisation step is therefore a choice of reference level, not a change to the underlying model dynamics.
