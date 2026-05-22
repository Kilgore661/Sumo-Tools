# **5. Results & Findings**

---

## 1. Overview

This document presents the results of applying Expt3 over historical sumo data and evaluates whether the generated probabilities satisfy the requirements defined in *0. Requirements.md*.

In particular, we assess:

* overall probabilistic accuracy
* empirical calibration
* the range over which calibration can be reliably evaluated

---

## 2. Experimental setup

The evaluation covers the period:

```text
1958–2026
```

with the following configuration:

* **Mode:** closed
* **Entrant policy:** constant initialisation
* **K-factor policy:** divisional
* **K configuration:** `files\input\elo_fide.json`
* **Baseline rating (b):** 1500
* **Logistic scale (q):** 850

A total of:

```text
633,625 bouts
```

are included.

The empirical base rate is:

```text
0.501841
```

---

## 3. Overall predictive performance

At the bout level:

* **Raw Brier score:** 0.244140
* **Baseline Brier score:** 0.249997
* **Brier skill score:** 0.023426

The baseline corresponds to assigning the same probability to every bout equal to the empirical base rate (~0.502).

The model therefore reduces the Brier score by:

```text
0.00586  (≈ 2.34% relative improvement)
```

indicating a consistent improvement over the baseline predictor.

---

## 4. Calibration results

Using the evaluation framework defined in *Evaluation & Calibration.md*:

* **Number of bins:** 50 (width = 0.02)

Binned calibration metrics:

* **MAE:** 0.00510  (≈ 0.51%)
* **RMSE:** 0.00761 (≈ 0.76%)

Brier decomposition:

* **Reliability:** 0.000058
* **Resolution:** 0.005883
* **Uncertainty:** 0.249997

---

### Observations

* The **low reliability term** indicates that predicted probabilities closely match observed frequencies
* The **positive resolution term** indicates that the model produces meaningful variation in predicted probabilities

---

## 5. Definition of adequacy

Calibration can only be meaningfully assessed in regions with sufficient data.

Two criteria are used:

---

### 5.1 Support criterion

A bin is considered to have adequate support if:

```text
standard error ≤ 0.02
```

This corresponds to an uncertainty of approximately:

```text
±2 percentage points
```

in the observed win rate within a bin.

---

### 5.2 Error criterion

A bin is considered well-calibrated if:

```text
|observed − predicted| ≤ 0.025
```

i.e. calibration error is within ±2.5 percentage points.

---

### 5.3 Adequate region

Applying these criteria yields:

---

#### Inadequate-support regions

* 0.01 ≤ p ≤ 0.15 (690 observations)
* 0.87 ≤ p ≤ 0.98 (709 observations)

These regions contain insufficient data for reliable evaluation.

---

#### Central adequate region

```text
0.35 ≤ p ≤ 0.75
```

* **Bins:** 21
* **Observations:** 609,890 (~96% of all bouts)
* **Maximum absolute calibration error:** 0.023130

Corresponding rating difference range:

```text
−227.84 ≤ Δ ≤ 404.31
```

---

## 6. Interpretation

Within the region where sufficient data are available:

* Typical calibration error (MAE ≈ **0.51%**) is small
* Statistical resolution is approximately **±2%**
* Predicted probabilities span a substantially wider range (~0.35–0.75)

Thus, calibration error is small relative to:

* the statistical resolution of the data
* the variation in predicted probabilities
* the inherent uncertainty of individual bout outcomes

---

### Implications

* Predicted probabilities closely match observed frequencies
* The model provides **informative variation**, not just noise around the base rate
* Calibration is reliable over the range in which the model is most frequently applied

---

### Limits

* Tail regions contain very few observations (~0.2% of data)
* Calibration cannot be reliably assessed in these regions
* Apparent behaviour in the tails should not be over-interpreted

---

## 7. Conclusion

Across the majority of observed bouts:

> **Predicted probabilities are well calibrated within the resolution of the data.**

In particular:

* Calibration error is small (≈ 0.5%)
* Evaluation uncertainty is larger (≈ 2%)
* The model improves consistently over a baseline predictor

Therefore:

> **The rating-based approach produces meaningful and empirically grounded win probabilities over the region in which it is most frequently applied.**

