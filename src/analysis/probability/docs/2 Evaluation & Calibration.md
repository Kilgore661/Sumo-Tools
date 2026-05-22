# **2. Evaluation & Calibration.md**

---

## 1. Overview

This document defines how the output of the generation stage is evaluated.

Given a sequence of bout-level observations:

```text
(predicted probability, outcome)
```

the goal is to assess whether the system satisfies the core requirement:

> Predicted probabilities should be empirically well-calibrated 

Evaluation is performed using:

* **calibration analysis** (via binning)
* **proper scoring rules** (Brier score)

---

## 2. Input data

The input to evaluation is a sequence of records of the form:

```text id="d5pdgd"
(predicted: float, outcome: int)
```

where:

* `predicted ∈ (0, 1)` is the model’s estimated probability that rikishi 1 wins
* `outcome ∈ {0, 1}` is the realised result

Each record corresponds to one scored bout, generated as described in *Model & Generation.md*.

---

## 3. Calibration construction

### 3.1 Binning

Calibration is assessed by grouping predictions into fixed-width probability bins.

This is implemented via:

* `CalibrationBins` 

Given a bin width `w`, the interval `[0, 1]` is partitioned into bins:

```text id="3g5ijy"
[0, w), [w, 2w), ..., [1-w, 1]
```

Each observation is assigned to a bin based on its predicted probability.

---

### 3.2 Per-bin statistics

For each bin, the following quantities are computed:

* `n_obs` — number of observations
* `mean_predicted` — average predicted probability
* `observed_win_rate` — fraction of outcomes equal to 1
* `abs_error = |observed - predicted|`
* `sq_error = (observed - predicted)^2`

These are aggregated into `CalibrationRow` objects 

---

### 3.3 Interpretation

Each bin provides a local calibration check:

```text id="d9bhq9"
mean_predicted ≈ observed_win_rate
```

Deviations indicate miscalibration in that probability region.

---

## 4. Metrics

### 4.1 Calibration error

Calibration error is measured by aggregating per-bin errors.

#### Mean Absolute Error (MAE)

```text id="qj1k6x"
MAE = Σ (n_obs × abs_error) / total_obs
```

#### Root Mean Squared Error (RMSE)

```text id="1x0bsl"
RMSE = sqrt( Σ (n_obs × sq_error) / total_obs )
```

These quantify how closely predicted probabilities match observed frequencies.

---

### 4.2 Brier score (raw)

The Brier score is computed directly over individual observations:

```text id="kh8u7j"
Brier = mean( (predicted - outcome)^2 )
```

This is implemented in:

* `summarise_brier_raw(...)` 

It measures overall probabilistic accuracy without binning.

---

### 4.3 Brier score (binned)

A binned version of the Brier score is also computed using calibration rows:

* `summarise_brier_binned(...)` 

This yields a decomposition:

```text id="b51m3n"
Brier = reliability - resolution + uncertainty
```

where:

* **reliability** — calibration error
* **resolution** — ability to distinguish outcomes
* **uncertainty** — variance of the base rate

---

### 4.4 Baseline and skill

A baseline predictor is defined using the overall win rate:

```text id="d0bt2k"
baseline = mean(outcome)
```

The corresponding baseline Brier score is:

```text id="k3jzmh"
mean( (baseline - outcome)^2 )
```

The **Brier skill score** is:

```text id="7m64p9"
1 - (Brier / baseline_Brier)
```

This measures improvement over a constant predictor.

---

## 5. Summary of outputs

Evaluation produces:

### Calibration rows

* one row per probability bin
* used for inspection and plotting

### Aggregate metrics

* MAE
* RMSE
* Brier score (raw and binned)
* Brier decomposition components
* Brier skill score

These outputs form the basis for interpreting model performance.

---

## 6. Summary

Evaluation proceeds as follows:

```text id="x7l7dr"
(predicted, outcome)
    ↓
bin into probability ranges
    ↓
compare predicted vs observed
    ↓
compute aggregate metrics
```

This provides both:

* a **local view** (via calibration bins)
* a **global view** (via scoring rules)

of how well the model satisfies the requirement of empirical calibration.
