# **1. Model & Generation**

---

## 1. Overview

This document describes how Expt3 generates pre-bout win probabilities from historical sumo data.

It addresses the question:

> Given the constraints in , how are probabilities produced?

The system proceeds by:

1. maintaining ratings for all active rikishi
2. converting rating differences into win probabilities
3. recording those probabilities alongside realised bout outcomes

The output of this process is a sequence of bout-level observations of the form:

```text
(predicted probability, realised outcome)
```

These observations are the sole input to the evaluation stage.

---

## 2. The Equelo model

Expt3 uses **Equelo**, an Elo-like rating model implemented via the Expt1 simulation engine.

The simulator API and full update mechanics are defined in:

*

Only the aspects required for probability generation are described here.

---

### 2.1 Ratings

Each rikishi is assigned a scalar rating.

* Ratings evolve over time as bouts are processed
* At any point, each active rikishi has a current rating
* Ratings are only meaningful **relative to one another**

New entrants are initialised at a constant baseline rating `b`.

---

### 2.2 Rating updates (Elo-like)

For each scored bout:

1. An expected score is computed from the two pre-bout ratings
2. The realised outcome is compared to this expectation
3. Both ratings are updated symmetrically

In standard Elo form:

```text
expected = f(r1, r2, q)
delta = k * (actual - expected)

r1 ← r1 + delta
r2 ← r2 - delta
```

Where:

* `q` is the logistic scale parameter
* `k` is the update factor (constant or rank-dependent)

Full details are given in the Expt1 simulator documentation.

---

### 2.3 Probability model

The predicted probability that rikishi 1 defeats rikishi 2 is given by:

```text
p = 1 / (1 + 10^((r2 - r1)/q))
```

This is the standard Elo logistic link function.

Equivalently, in terms of the rating difference:

```text
delta = r1 - r2
p = 1 / (1 + 10^(-delta/q))
```

This mapping is implemented directly in the simulation via:

```python
p = expect(r1_before, r2_before, q)
```



---

## 3. Execution over history

### 3.1 Sequential processing

The system processes bouts in chronological order using the Expt1 simulator:

```python
simulate(
    history=...,
    params=...,
    entrant_initialiser=...,
    mode=...,
    observer=...,
)
```



At each bout:

* ratings are taken **before** the bout
* a probability is computed
* the outcome is observed
* ratings are updated

This ensures that all predictions are strictly **pre-bout**.

---

### 3.2 Entrant initialisation

When a rikishi appears without a prior rating:

* they are assigned a constant initial rating `b`

This is the default and intended Expt3 configuration.

Alternative initialisation policies exist in the code but are not part of the core model.

---

### 3.3 Inclusion of bouts

Only **scored bouts** are included.

In particular:

* bouts with outcomes `"fusen"` or `"blank"` are ignored

This is enforced during simulation:

```python
def on_ignored_bout(...):
    return None
```



---

## 4. Generated data (interface to evaluation)

### 4.1 Output structure

For each scored bout, the system records a `BoutForecast`:

```python
BoutForecast(
    date,
    day,
    rikishi1,
    rikishi2,
    r1_before,
    r2_before,
    delta,
    predicted,
    outcome,
)
```



---

### 4.2 Core fields

The essential fields for evaluation are:

* `predicted` — the pre-bout win probability for rikishi 1
* `outcome` — the realised result (1 = win for rikishi 1, 0 = loss)

Additionally:

* `delta = r1_before - r2_before`
* `r1_before`, `r2_before` — ratings used to generate the prediction

---

### 4.3 Semantics

Each row represents a single probabilistic prediction:

```text
predicted = P(rikishi1 wins | ratings before bout)
outcome   = realised result of the bout
```

Crucially:

* `predicted` is computed **before** the bout
* `outcome` is observed **after** the bout
* ratings are updated only **after both are recorded**

---

### 4.4 Invariants

Across all rows:

* `0 < predicted < 1`
* `outcome ∈ {0, 1}`
* each row is independent given the evolving rating state
* the sequence is ordered in time

---

## 5. Summary

The generation process can be summarised as:

```text
ratings → delta → probability → outcome → record
```

That is:

1. take current ratings
2. compute their difference
3. convert to a probability
4. observe the bout outcome
5. record (predicted, outcome)

The result is a dataset of probabilistic predictions suitable for calibration and scoring analysis.
