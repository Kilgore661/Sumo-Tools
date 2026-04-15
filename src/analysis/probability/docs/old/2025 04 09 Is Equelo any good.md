Once you have

* (p(c_1 \text{ beats } c_2)): observed win probability
* (q(c_1 \text{ beats } c_2)): Equelo-implied win probability

for collapsed ranks (c_1,c_2), there are several sensible ways to compare them.

The main choice is what you want to penalise:

* raw probability error
* directional disagreement
* bad fit in rare vs common matchups
* statistical implausibility given sample size

## 1. Pointwise error metrics

These compare (p) and (q) directly cell by cell.

### Absolute error

[
|p-q|
]

Simple and interpretable.

Aggregate versions:
[
\text{MAE}=\frac{1}{|C|}\sum_{(c_1,c_2)\in C}|p(c_1,c_2)-q(c_1,c_2)|
]

This is usually the cleanest first metric.

### Squared error

[
(p-q)^2
]

Aggregate:
[
\text{MSE}=\frac{1}{|C|}\sum (p-q)^2
]

or RMSE:
[
\text{RMSE}=\sqrt{\text{MSE}}
]

This penalises big misses more heavily than MAE.

### Maximum error

[
\max_{(c_1,c_2)\in C}|p-q|
]

Useful if you care about worst-case discrepancy.

---

## 2. Weighted versions

Some rank pairings occur very often, others barely at all. Usually you do not want a 2-bout cell to count as much as a 500-bout cell.

Let (n(c_1,c_2)) be the number of observed bouts in that cell.

### Weighted MAE

[
\frac{\sum n(c_1,c_2),|p-q|}{\sum n(c_1,c_2)}
]

### Weighted MSE / RMSE

[
\frac{\sum n(c_1,c_2),(p-q)^2}{\sum n(c_1,c_2)}
]

These are often more meaningful than unweighted versions.

A good practical pair is:

* unweighted MAE, to assess fit across the rank grid
* weighted RMSE, to assess fit where the data actually are

---

## 3. Likelihood-based metrics

These treat (q) as a probabilistic model for the observed wins/losses.

If in cell ((c_1,c_2)) you observe (w) wins for (c_1) out of (n) bouts, then the binomial log-likelihood under (q) is

[
\ell = w\log q + (n-w)\log(1-q)
]

Summed over cells, this gives a global score.

This is very natural statistically, because it uses the observed counts directly rather than reducing first to (p=w/n).

Equivalent loss form: **cross-entropy** or **negative log-likelihood**.

This is often the best metric if your real question is:

> how well does Equelo explain the observed rank-v-rank outcomes?

---

## 4. Brier-type scores

For each cell, with observed proportion (p) and model probability (q), use

[
(p-q)^2
]

which looks like MSE, but interpreted as a probability calibration score.

If you go back to individual bouts rather than aggregated cells, the usual Brier score is

[
\frac1N\sum_i (y_i-q_i)^2
]

with (y_i\in{0,1}).

That is often preferable if you can compute model probability bout by bout.

---

## 5. Deviance / goodness-of-fit against binomial noise

Because (p) itself is noisy, especially in sparse cells, you may want not just “how far apart are (p) and (q)?” but

> is the discrepancy larger than one would expect from sampling variation?

For each cell, compare observed wins (w) out of (n) against expected (nq). Natural summaries include:

### Pearson residual

[
\frac{w-nq}{\sqrt{nq(1-q)}}
]

### Standardised difference in proportions

[
\frac{p-q}{\sqrt{q(1-q)/n}}
]

These let you spot cells where the model is genuinely off, not merely noisy.

A global version is Pearson chi-square:
[
\sum \frac{(w-nq)^2}{nq(1-q)}
]

though this needs care when (q) is near 0 or 1.

---

## 6. Rank-order / monotonic agreement metrics

Sometimes you care less about exact probabilities and more about whether the model gets the ordering right.

For example:

* if (q(c_1,c_2)>0.5), does (p(c_1,c_2)>0.5)?
* if one pairing is easier than another under the data, does the model rank them likewise?

Possible metrics:

* sign agreement of (p-0.5) and (q-0.5)
* correlation between (p) and (q)
* Spearman correlation on cells

These are weaker than calibration metrics, but useful as supplementary checks.

---

## 7. Symmetry-consistent metrics

Since
[
p(c_2 \text{ beats } c_1)=1-p(c_1 \text{ beats } c_2)
]
and similarly for (q), you may want to avoid double-counting both directions.

So define your comparison domain on ordered pairs with, say, (\operatorname{ord}(c_1)<\operatorname{ord}(c_2)), and store just one probability per unordered pairing.

That makes summaries cleaner.

---

## 8. Visual diagnostics

Not a metric, but very useful.

### Calibration scatter

Plot (p) against (q), one point per pairing, optionally sized by (n).

Perfect fit lies on the line (y=x).

### Heatmap of residuals

Plot
[
p(c_1,c_2)-q(c_1,c_2)
]
over the rank-pair grid.

This is often the fastest way to see where the system systematically misses.

---

## What I would recommend first

For a first pass, I would use four summaries:

1. **Weighted MAE**
   [
   \frac{\sum n|p-q|}{\sum n}
   ]

2. **Weighted RMSE**
   [
   \sqrt{\frac{\sum n(p-q)^2}{\sum n}}
   ]

3. **Binomial log-likelihood** or negative log-likelihood, using counts directly

4. **Residual heatmap**
   for structure

That gives you:

* interpretability
* robustness to sparse cells
* a proper probabilistic score
* a visual diagnostic

---

## One subtle point

If (p) is computed from the same data used to fit Equelo, then this is a **fit assessment**, not a true out-of-sample validation.

That is still useful. It tells you how well the fitted Equelo surface reproduces the observed rank-v-rank surface.

Later, if you want a stricter test, you could compare on held-out eras or held-out basho.

---

## Bottom line

The main choices are:

* **MAE / RMSE** if you want direct probability discrepancy
* **weighted versions** if you want common matchups to matter more
* **log-likelihood / cross-entropy** if you want the most statistically principled score
* **standardised residuals** if you want to know where discrepancies are bigger than sampling noise

My default recommendation would be:

> use weighted MAE for interpretability, and binomial log-likelihood for principled model comparison.

