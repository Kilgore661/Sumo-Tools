# Equelo: a conceptually minimal modification of the Elo rating system

## Introduction

Elo’s rating system is elegant, but in a changing population it exhibits **rating inflation and deflation**, preventing meaningful comparison across eras.

This problem is well known. In practice, sequential updates combined with variation in the player pool cause the overall rating level to drift over time, so that ratings from different periods are not directly comparable.

---

## What we built

We introduce **Equelo**, a conceptually minimal modification of the Elo rating system.

The central idea is to retain Elo’s difference-based probabilistic structure, while enforcing **global consistency across all observed results** under a fixed-mean constraint.

The resulting system:

* assigns scalar ratings
* models outcomes via a logistic function of rating differences
* interprets ratings purely through relative differences

At the same time:

> **The rating scale is drift-free by construction: the global mean is fixed, so inflation and deflation cannot occur.**

Ratings are determined jointly rather than sequentially, producing a single, time-stable scale.

Despite this change, the system remains Elo-like in behaviour:

* predictions depend only on rating differences
* global shifts do not affect probabilities
* no additional features or covariates are introduced

---

## What this allows

Because the rating scale is anchored, **ratings are directly comparable across eras**.

Concretely:

* a given rating has the same probabilistic meaning regardless of when it is observed
* rating differences correspond to the same expected win probabilities across time
* competitors from different periods can be placed on a common scale of expected performance

This should be understood in probabilistic terms:

> a higher rating implies a higher expected win probability against comparable opposition.

It does not imply that competitors are interchangeable across eras, but that they occupy comparable positions within a common, calibrated rating scale.

---

## What we claim

> **Equelo yields robust, well-calibrated win probabilities (~1–2% error) for sumo match outcomes across data regimes.**

More concretely:

* In high-density regions of the data, predicted probabilities match observed win frequencies to within ~1% on average
* Across all matchups, calibration error is ~2%
* These results are stable across:

  * different historical slices (modern vs full history)
  * different data inclusion rules (e.g. missing lower-tier results)
  * different estimation pipelines

---

## How we evaluate the claim

We evaluate the model purely as a **probabilistic predictor**.

For each bout:

* compute the predicted win probability from ratings
* compare against the observed outcome

We then:

* group predictions into probability bins
* compute empirical win frequencies per bin
* measure calibration error using:

  * mean absolute error (MAE)
  * root mean squared error (RMSE)

This directly tests whether:

> *events predicted with probability (p) occur with frequency (p)*

---

## Results (summary)

Across multiple runs:

* **Core calibration (well-sampled bins):**

  * MAE ≈ 0.011

* **Overall calibration:**

  * MAE ≈ 0.018–0.019

These values are consistent across:

* full historical data
* modern-era-only data
* reduced datasets with missing lower-tier matches

---

## Why this supports the claim

### 1. Calibration is directly measured

The evaluation tests probabilistic correctness, not just ranking quality. The model produces probabilities that match observed frequencies to within ~1–2%.

---

### 2. Results are stable across data regimes

Substantial changes to the input data (including removal of large portions of historical matches) do not materially change calibration metrics.

This indicates:

* the model is not sensitive to noisy or incomplete subsets
* the learned probability structure is stable

---

### 3. Performance is achieved without additional model complexity

Equelo uses:

* no per-rikishi parameters
* no temporal dynamics
* no covariates

Despite this, it achieves strong calibration, suggesting that:

* the core Elo-style structure captures most of the predictive signal

---

## What we are not claiming

We do not claim:

* that the model captures all aspects of sumo performance
* that the ratings are uniquely determined or interpretable beyond prediction
* that more complex models would not improve accuracy

The claim is limited to:

> **Equelo provides a well-calibrated probabilistic model of match outcomes.**

---

## Summary

Equelo shows that a conceptually minimal, Elo-style system can produce **accurate and stable win probabilities** for sumo, even when trained on noisy and incomplete data. By anchoring the rating scale, it also provides a **common basis for comparing competitors across eras**, something standard Elo systems cannot reliably do.

