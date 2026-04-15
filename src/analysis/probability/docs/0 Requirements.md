# Requirements

## 1. Objective

The purpose of this package is to explore whether a simple rating-based system can produce meaningful win probabilities for sumo bouts.

Given historical bout data, the system should assign ratings to rikishi and use those ratings to generate pre-bout probabilities of victory.

The focus is not on ranking per se, but on the **quality of the resulting probabilities**.

---

## 2. Core requirement

The central requirement is:

> The system should produce probabilities that are **empirically well-calibrated**.

That is, over a large number of bouts:

> Events predicted with probability *p* should occur with frequency close to *p*.

This requirement defines what it means for the model to be “good” in this context.

---

## 3. Constraints

The system is intentionally simple. In particular:

* Ratings are scalar values assigned to each rikishi
* Predictions depend only on **differences in ratings**
* No additional features or covariates are used
* Bouts are processed sequentially in historical order
* New entrants are assigned a **constant initial rating**

These constraints are not incidental — they define the scope of the experiment.

---

## 4. Non-goals

The system is not intended to:

* provide a definitive model of sumo performance
* capture all factors influencing bout outcomes
* ensure comparability of ratings across eras
* control or correct for rating drift

It is also not intended to explore alternative initialisation strategies beyond what is required to run the experiment.

---

## 5. Success criteria

Performance is assessed using standard probabilistic evaluation methods.

In particular, we are interested in:

* **Calibration error**, measured by comparing predicted probabilities with observed frequencies
* **Brier score**, as a measure of overall probabilistic accuracy
* Stability of these metrics across different subsets of the data

The system is considered successful to the extent that it produces:

* low calibration error
* reasonable Brier scores
* consistent behaviour across data regimes

---

## 6. Interpretation

This is an exploratory system.

The aim is not to prove that the model is “correct”, but to determine:

> whether a minimal, rating-based approach is sufficient to produce useful probabilistic predictions in this setting.
