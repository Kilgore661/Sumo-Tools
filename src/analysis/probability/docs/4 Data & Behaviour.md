# **4. Data & Behaviour**

---

## 1. Overview

This document describes the structure of the data on which Expt3 operates, and how that structure constrains what can be inferred from evaluation.

The focus is on:

* the distribution of predicted probabilities
* the distribution of match imbalance
* the degree of statistical support across the probability range

No claims about model performance are made here; those are addressed in *Results & Findings.md*.

---

## 2. Distribution of predicted probabilities

### 2.1 Summary statistics

Across **633,625 bouts**, predicted probabilities have the following characteristics:

| Statistic | Value  |
| --------- | ------ |
| Mean      | 0.502  |
| Median    | 0.500  |
| Std dev   | 0.0808 |
| Min       | 0.0127 |
| Max       | 0.981  |

---

### 2.2 Quantiles

| Quantile | 1%    | 5%    | 10%   | 25%   | 50%   | 75%   | 90%   | 95%   | 99%   |
| -------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| p        | 0.276 | 0.371 | 0.413 | 0.464 | 0.500 | 0.539 | 0.591 | 0.635 | 0.740 |

---

### 2.3 Distribution (horizontal histogram)

| Range     | <0.20 | 0.20–0.30 | 0.30–0.35 | 0.35–0.40 | 0.40–0.45 | 0.45–0.50 | 0.50–0.55 | 0.55–0.60 | 0.60–0.65 | 0.65–0.70 | ≥0.70 |
| --------- | ----- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | ----- |
| Share (%) | 0.259 | 1.26      | 2.06      | 4.43      | 11.2      | 29.6      | 30.8      | 11.6      | 4.70      | 2.15      | 1.85  |

---

### 2.4 Observations

* The distribution is **tightly concentrated around 0.5**

* Approximately:

  * **60.4%** of observations lie in [0.45, 0.55]
  * **83.3%** lie in [0.40, 0.60]
  * **92.4%** lie in [0.35, 0.65]

* The distribution is **approximately symmetric** about 0.5

* It exhibits a **single central peak spanning 0.45–0.55**, split across adjacent bins

* Extreme probabilities are rare:

  * p < 0.20 accounts for **0.26%**
  * p > 0.80 accounts for **0.37%**

---

## 3. Distribution of match imbalance

Match imbalance is expressed as:

```text
|Δ| = |r1 - r2|
```

### 3.1 Summary statistics

| Statistic | Value |
| --------- | ----- |
| Mean      | 85.6  |
| Median    | 55.6  |
| P75       | 112.9 |
| P90       | 200.1 |
| P95       | 270.7 |
| P99       | 455.5 |

---

### 3.2 Observations

* Most bouts occur between competitors with **moderate rating differences**
* Large mismatches occur but are relatively rare
* The distribution has a **long right tail**, reflecting occasional uneven matchups

---

## 4. Data support across the probability range

### 4.1 Central region

From the distribution:

```text
0.35 ≤ p ≤ 0.75
```

contains approximately:

```text
609,890 observations (~96% of all bouts)
```

---

### 4.2 Tail regions

The extremes of the probability range are sparsely populated:

* 0.01 ≤ p ≤ 0.15: 690 observations
* 0.87 ≤ p ≤ 0.98: 709 observations

Combined:

```text
~0.2% of all observations
```

---

### 4.3 Implications for inference

* Regions with many observations provide **stable statistical estimates**
* Regions with few observations are subject to **high variance**

Therefore:

> **The ability to assess model behaviour depends strongly on the distribution of data across the probability range.**

---

## 5. Summary

The key structural features of the data are:

* Predicted probabilities are **highly concentrated near 0.5**
* The distribution is **approximately symmetric with a strong central peak**
* The vast majority of observations lie in **0.35 ≤ p ≤ 0.75**
* Tail regions are **extremely sparse**

These features define the **effective domain** over which model behaviour can be meaningfully evaluated.
