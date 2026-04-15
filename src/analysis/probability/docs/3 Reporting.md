# **3. Reporting.md**

---

## 1. Overview

This document describes the outputs produced by Expt3 and how they are presented.

Given the evaluation defined in *Evaluation & Calibration.md*, reporting is responsible for:

* exposing the data used for evaluation
* summarising key metrics
* providing artefacts suitable for inspection and further analysis

Reporting does not introduce new computations; it organises and presents the results of the evaluation stage.

---

## 2. Output types

### 2.1 Bout-level data

The most granular data produced by the system is the sequence of bout-level observations:

```text
(predicted, outcome)
```

These are constructed during simulation and used internally for evaluation.

In practice, they are represented as `BoutForecast` records 

They may optionally be written to disk, but this is not required for standard operation.

---

### 2.2 Calibration data

Calibration analysis produces a set of binned summaries:

* one row per probability bin
* aggregated statistics within each bin

These are represented as `CalibrationRow` objects 

Each row contains:

* bin boundaries
* number of observations
* mean predicted probability
* observed win rate
* error measures

This data is used to:

* inspect calibration behaviour
* construct calibration plots

---

### 2.3 Summary metrics

Evaluation produces a set of aggregate metrics, including:

* calibration MAE
* calibration RMSE
* Brier score (raw and binned)
* Brier decomposition components
* Brier skill score
* base rate and observation counts

These summarise overall model performance.

---

## 3. Output formats

### 3.1 CSV outputs

Structured outputs are written to CSV files for external analysis.

Typical outputs include:

* calibration rows (one row per probability bin)
* sweep results (e.g. varying parameters such as `q`)

These files are suitable for:

* plotting
* comparison across runs
* downstream analysis

---

### 3.2 Console summaries

Key metrics are also reported via console output during execution.

Typical summaries include:

* Brier score and skill
* calibration error metrics
* base rate
* number of observations

These provide a quick, high-level view of model performance.

---

## 4. Role of reporting

Reporting serves as the interface between evaluation and interpretation.

It provides:

* access to raw and aggregated data
* standardised summaries of model performance

It does not:

* modify the underlying data
* perform additional modelling
* introduce interpretive conclusions

Interpretation of results is handled separately.

---

## 5. Summary

Reporting exposes the outputs of the evaluation stage in a structured and usable form:

```text
evaluation results → structured data → summaries
```

This enables both:

* detailed inspection (via CSV outputs)
* quick assessment (via console summaries)

without altering the underlying evaluation logic.

