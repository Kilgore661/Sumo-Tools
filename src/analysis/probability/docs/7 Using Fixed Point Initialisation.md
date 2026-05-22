# Initialisation Experiments for Expt3c

## 1. Purpose

This document describes a series of experiments aimed at improving upon the **baseline case** for Expt3c, in which all entrant ratings are initialised to a constant value.

The goal is practical rather than theoretical:

> Can we obtain better probabilistic predictions (as measured by Brier score and binned MAE) by using more informative initial ratings?

In particular, we consider whether ratings derived from Expt2, either directly or after scaling, can improve performance.

This document records:

* what was done
* what was observed
* how key quantities were obtained
* what conclusions can reasonably be drawn

Traceability is prioritised over brevity. Where possible, results are tied to commands, files, or explicitly identified as reported.

---

## 2. Background

### 2.1 Expt3c

Expt3c produces bout-level win probabilities using:

* a rating system (Elo-style)
* a logistic link function with parameter **q**
* entrant initial ratings

In this document, **q = 900** is fixed throughout.

The key point is:

> **Expt3c is a function of initial ratings.**

---

### 2.2 Expt2

Expt2 produces a set of ratings derived independently from Expt3.

The relevant property for this document is:

> Expt2 ratings converge to a distribution centred on **b = 1500**, but with substantial spread.

These ratings define the **fixed-point case**.

---

## 3. Candidate Initialisations

We consider three cases.

### 3.1 Baseline case (constant)

All entrants initialised to the same value:

```text
r = 1500
```

---

### 3.2 Fixed-point case (Expt2)

Initial ratings taken directly from Expt2 output.

This preserves ordering but introduces large dispersion.

---

### 3.3 Scaled fixed-point case

Initial ratings transformed as:

```text
r' = μ + α (r − μ)
```

where:

* μ = mean of Expt2 ratings
* α ∈ [0,1]

This preserves ordering while controlling spread.

---

## 4. Evaluation Setup

### 4.1 Metrics

Primary metrics:

* **Raw Brier score** (lower is better)
* **Binned MAE** (lower is better)

Rationale:

* Brier measures overall probabilistic accuracy
* MAE measures calibration (bin-based)

Other Brier components (skill, reliability, resolution) are not analysed in detail here.

> **TBD:** systematic analysis of Brier decomposition.

---

### 4.2 Parameters

The experiments depend on many parameters, including:

* q (fixed at 900)
* K policy (divisional)
* entrant policy
* alpha (for scaled case)
* bin width (0.02)
* evaluation years (1958–2026)
* simulation mode (closed)

Only a subset of these were varied.

---

### 4.3 Traceability note

Results come from three sources:

* **console output**
* **file output** (relative to `analysis/Equelo/`)
* **reported values** (no retained artefact)

Preference order:

```text
file > console > reported
```

---

## 5. Results

### 5.1 Baseline case

```text
Source: console

Command:
  py -m src.analysis.probability.expt3c --q 900

Observed:
  Raw Brier score ≈ 0.244153
  Calibration MAE (binned) ≈ 0.004764
```

This serves as the reference.

---

### 5.2 Fixed-point case

```text
Source: console

Command:
  py -m src.analysis.probability.expt3c --entrant-policy expt2_example --q 900

Observed:
  Raw Brier score ≈ 0.246206
  Calibration MAE (binned) ≈ 0.011168
```

Observation:

* significantly worse Brier
* significantly worse MAE

Conclusion:

> Raw Expt2 initialisation is too dispersed.

---

### 5.3 Scaled fixed-point case

Varying α yields substantial changes.

Example:

```text
Source: console

Command:
  py -m src.analysis.probability.expt3c --entrant-policy expt2_scaled --expt2-alpha 0.5

Observed:
  Raw Brier score ≈ 0.244652
  Calibration MAE (binned) ≈ 0.005470
```

This already improves dramatically over the fixed-point case.

---

## 6. Alpha Sweep

### 6.1 Coarse sweep

```text
Source: console

Command:
  py -m src.analysis.probability.expt3c_alpha_sweep \
    --alpha-start 0 --alpha-end 1 --alpha-step 0.05 \
    --q 900 --objective raw_brier
```

Observed behaviour:

* Raw Brier increases monotonically with α
* Best Brier at α = 0 (baseline)

---

### 6.2 MAE behaviour

From similar sweeps:

* MAE decreases from α = 0
* reaches minimum near α ≈ 0.55
* then increases

---

### 6.3 Refinement

The α range was progressively refined:

```text
Source: reported (no retained artefact)

Method:
  repeated runs of expt3c_alpha_sweep with narrower ranges and smaller step sizes
```

Example refined run:

```text
Command:
  py -m src.analysis.probability.expt3c_alpha_sweep \
    --alpha-start 0.5481 --alpha-end 0.549 \
    --alpha-step 0.00000045 --q 900
```

---

### 6.4 Best observed value

```text
Source: file

Path:
  files/output/Equelo/expt3_alpha_sweep.csv

Row:
  alpha = 0.54875745
  raw_brier = 0.244095973240272
  calibration_mae_binned = 0.00353845909456409
```

---

### 6.5 Interpretation of precision

The minimum lies within:

```text
α ≈ 0.548757 ± O(10⁻⁶)
```

This corresponds to:

* ~1 part in 10⁶ of the interval [0,1]

However:

* the objective is affected by bin transitions
* neighbouring values differ at ~10⁻⁶ scale

Conclusion:

> the exact value is not meaningful beyond this precision.

---

## 7. Trade-offs

### 7.1 Global behaviour

* α = 0:

  * best Brier
  * worst MAE

* α ≈ 0.55:

  * best MAE
  * slightly worse Brier

* α = 1:

  * worst of both

---

### 7.2 Magnitude

Total Brier change:

```text
≈ 0.0024 over α ∈ [0,1]
```

Interpretation:

> Brier degrades monotonically but modestly.

---

### 7.3 Local behaviour

Near the MAE minimum:

* MAE decreases slightly
* Brier increases slightly
* all other metrics effectively constant

Conclusion:

> Local optimisation affects calibration only, not underlying predictive performance.

---

## 8. Interpretation

### 8.1 What we have learned

* Expt2 ratings contain useful ordering information
* but are too dispersed
* scaling recovers useful structure

---

### 8.2 Key result

> There exists an interior α (~0.55) that substantially improves MAE while only modestly degrading Brier.

---

## 9. Why this is a serviceable model

The combination:

* Expt3c dynamics
* logistic link (q = 900)
* scaled fixed-point initialisation

produces:

* stable probabilities
* good calibration (MAE)
* acceptable Brier performance

Conclusion:

> This is a **serviceable model** for predicting bout outcomes.

---

## 10. Why this is not a causal model

### 10.1 Parameter fitting

* α is chosen empirically
* depends on evaluation metric

---

### 10.2 Metric dependence

* MAE and Brier prefer different α
* no single “true” optimum

---

### 10.3 Binning effects

* MAE depends on arbitrary bin structure
* introduces discontinuities

---

### 10.4 Data reuse

* tuning and evaluation use same data
* no out-of-sample validation

---

### 10.5 Structural limitation

* single scalar rating
* no contextual or interaction effects

---

### 10.6 Summary

> The model fits observed data but does not explain underlying mechanisms.

---

## 11. Practical conclusion

If the goal is:

### A. Serviceable prediction

> The model is adequate and usable.

### B. Mechanistic explanation

> The model is insufficient.

---

## 12. Issues and TBD

### 12.1 Brier decomposition

* reliability / resolution not fully analysed

### 12.2 Bin width sensitivity

* results depend on bin choice

### 12.3 Parameter interactions

* α and q may interact

### 12.4 Traceability gaps

* intermediate runs not preserved
* outputs overwritten

### 12.5 Reproducibility

* results reproducible in principle, not directly from stored artefacts

---

## 13. Final statement

> A model based on Expt3c with scaled fixed-point initialisation is a reasonable and defensible candidate for predicting bout outcomes. It performs well empirically and its behaviour is understood. However, it is the result of parameter tuning and does not constitute a causal or mechanistic account of the underlying process.
