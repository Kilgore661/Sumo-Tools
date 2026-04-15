# Expt3

## Overview

**Expt3 is a ratings-based probability generator and evaluator.**

It uses *Equelo* — an Elo-like rating process — to generate pre-bout win probabilities and evaluates those probabilities against observed outcomes.

The purpose of Expt3 is:

> **To assess how well a simple Elo-style system produces calibrated probabilities.**

---

## Core idea

Expt3 operates as a single, self-contained process:

1. **Ratings are generated dynamically**

   * Ratings evolve over time using an Elo-like update rule
   * New entrants are assigned a **constant initial rating**

2. **Probabilities are produced**

   * For each bout, a win probability is computed from the rating difference using a logistic function

3. **Probabilities are evaluated**

   * Predictions are compared to actual outcomes

---

## Evaluation

The result of Expt3 is an evaluation of the generated probabilities.

### 1. Calibration

* Predicted probabilities are grouped into bins
* Observed win rates are compared to predicted probabilities

Reported as:

* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)
* Calibration tables (CSV output)

---

### 2. Brier score

* Measures overall probabilistic accuracy

Includes:

* Raw Brier score
* Baseline Brier score
* Brier skill score

---

## Entry point

### `expt3c.py`

This is the **maintained entry point** for Expt3.

It:

* runs the full rating and prediction process
* generates bout-level probabilities
* computes calibration and Brier metrics
* writes calibration output

---

## Running Expt3

Expt3 is run via the module entry point:

```bash
py -m src.analysis.equelo.expt3.expt3c
```

Typical arguments include:

* `--start`, `--end` — date range for historical data
* `--q` — logistic scale parameter
* `--k-policy`, `--k-value` — Elo update configuration
* `--b` — baseline rating for entrant initialisation

Example:

```bash
py -m src.analysis.equelo.expt3.expt3c \
    --start 1958 \
    --end 2025 \
    --q 850
```

The exact parameter set depends on the experiment being run.

---

## Outputs

Expt3 produces:

### Calibration data (CSV)

* probability bins
* observed win rates
* per-bin error measures

### Summary metrics (console output)

* calibration MAE and RMSE
* Brier score and skill
* base rate and observation counts

Outputs are written under:

```
files/output/Equelo/
```

These artefacts are intended for:

* calibration plots
* comparison across runs
* further analysis

---

## Initialisation

Expt3 uses:

> **constant initialisation of entrant ratings**

This is the default and preferred approach.

An alternative initialisation based on Expt2 outputs is included in the code as an example of how different initialisation strategies could be implemented. This is not part of the core method and is retained only as a reference.

---

## Summary

Expt3 is a focused experiment:

* **Generate** probabilities from an Elo-like rating system
* **Evaluate** them using calibration and Brier metrics

No external inputs or prior rating systems are required.

---

## Further documentation

For more detail, see:

* **0. Requirements.md** — purpose, constraints, and success criteria
* **1. Model & Generation.md** — how ratings and probabilities are produced
* **2. Evaluation & Calibration.md** — how predictions are evaluated
* **3. Reporting.md** — what outputs are produced

---

## 🧠 Notes

* The system is intentionally minimal
* Results should be interpreted in terms of probabilistic calibration, not ranking quality
* The focus is on behaviour of the model, not completeness of representation

