What follows is a **clean, self-contained outline of Expt2**, rewritten so that:

* it is internally coherent
* it makes no claims beyond what the method supports
* it does **not assume it is the “correct system”**
* it avoids any dependency on Expt3

---

# 🧾 Expt2 — Outline (Reframed)

---

## 1. Purpose

The purpose of Expt2 is to address a specific problem:

> How should ratings be initialised when competitors enter the observable system without prior rating history?

This arises in historical data where:

* the observable population changes over time
* competitors may appear without recorded prior results

The goal is to construct an initialisation rule that:

* is consistent with the rating dynamics
* reduces artefacts caused by arbitrary initialisation choices
* is defined entirely in terms of observable structure

---

## 2. Problem context

### 2.1 Path dependence

In an Elo-type system:

* ratings depend on prior outcomes
* initial values influence subsequent trajectories

Therefore:

> Initialisation is not neutral; it affects the entire rating history.

---

### 2.2 Partial observability

The dataset contains:

* competitors whose earlier history is unobserved
* structural discontinuities (e.g. sudden increases in observed population)

Flat initialisation (assigning all entrants the same value):

* introduces artificial compression
* creates transients while the system re-equilibrates
* may distort aggregate behaviour

---

### 2.3 Available structure

At entry, each competitor is associated with:

* an **ordinal rank (chii)**

This provides:

> A structured, observable proxy for competitive standing.

---

## 3. Objective

Construct a function:

```text
μ : chii → rating
```

to be used as:

> the rating assigned to a competitor at entry when no prior rating is available

The function should satisfy:

* internal consistency with the rating process
* stability under repeated application
* interpretability as a typical value associated with each rank

---

## 4. Core idea: self-consistency

The key requirement is:

> The initialisation rule should reproduce itself under the dynamics it induces.

Formally:

* initialise entrants using μ
* run the rating system over the historical data
* observe resulting ratings at entry points
* require that these observed values agree with μ (up to a constant shift)

This defines a **fixed-point condition**.

---

## 5. Method

### 5.1 Operator formulation

Define an operator:

```text
T = normalise ∘ aggregate ∘ simulate
```

where:

* **simulate**
  runs the rating system with current initialisation rule

* **aggregate**
  collects entry-point ratings and computes mean values by rank

* **normalise**
  applies a uniform additive shift to fix a reference level

---

### 5.2 Iterative procedure

1. Initialise μ₀ as a constant function
2. For each iteration:

   * simulate history using μₜ
   * aggregate entry-point ratings by rank
   * normalise to obtain μₜ₊₁
3. Repeat until convergence

---

### 5.3 Interpretation of the solution

A fixed point μ* satisfies:

> When used as the initialisation rule, it reproduces itself under the rating process.

Thus:

> μ*(c) represents the typical rating associated with rank c at entry.

---

## 6. Variants

Two estimation regimes are considered:

### A. Whole-history estimation

* Use the full dataset throughout
* Seeks a globally self-consistent solution

### B. Calibration + refinement

* Estimate μ using a subset of data with more complete observability
* Apply and optionally refine over the full dataset

These provide a check on robustness.

---

## 7. Empirical observations

### 7.1 Convergence

* The iterative procedure converges under tested configurations
* Convergence is stable across runs

---

### 7.2 Structure of the solution

* The mapping μ is:

  * broadly monotonic across ranks
  * smooth at coarse resolution
  * defined over a wide rating range

---

### 7.3 Local irregularities

* Deviations from monotonicity occur in:

  * sparsely populated ranks
  * boundary regions between divisions
* These are stable but not fully explained

---

### 7.4 Agreement between variants

* Different estimation regimes produce similar mappings (up to shift)
* Suggests robustness of the inferred structure

---

## 8. Interpretation

### 8.1 What the method provides

The method produces:

* a **data-derived initialisation rule**
* consistent with the rating dynamics
* grounded in observed rank structure

---

### 8.2 What it does not establish

The method does not establish:

* that the mapping is unique
* that it is optimal for any particular predictive objective
* that rank fully determines entry strength
* that observed irregularities have causal explanations

---

### 8.3 Nature of the result

The result is best understood as:

> A self-consistent statistical construction within the chosen modelling framework

It is not:

* a causal model of performance
* a complete description of ranking dynamics

---

## 9. Evaluation criteria

The usefulness of the method should be assessed empirically, for example by:

* stability of the resulting mapping
* sensitivity to modelling choices
* impact on downstream rating behaviour
* reduction of observable artefacts (e.g. entry-related discontinuities)

No single criterion is assumed to be decisive.

---

## 10. Scope and limitations

### Included

* rank as a proxy for expected strength at entry
* Elo-type rating dynamics

### Excluded

* modelling of promotion or ranking processes
* causal interpretation of rank-performance relationships
* external validation beyond observed outcomes

---

## 11. Summary

Expt2 defines a method for constructing an initialisation rule by rank based on a self-consistency condition.

The method:

* is well-defined and computationally feasible
* produces stable and interpretable results
* incorporates available structural information at entry

Its role is:

> To provide a principled alternative to flat initialisation under partial observability

without asserting that it is uniquely correct or universally optimal.

---

## 🔚 Closing note

This version does three important things:

* Keeps the **mathematical core intact**
* Removes the **“this is the system” overreach**
* Leaves space for **external evaluation (which Section 7 now provides)**
