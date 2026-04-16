# **6. Sensitivity & Variations**

The preceding sections treat the model configuration as fixed. This section examines the sensitivity of the results to variations in the logistic scale parameter (q) and the associated link function.

---

## **6.1 Sensitivity to q**

The main account uses a fixed value of (q), but does not justify this choice. To assess sensitivity, a sweep over (q) was performed using:

```bash
py -m src.analysis.probability.expt3_q_sweep \
  --q-start 400 \
  --q-end 2000 \
  --q-step 100
```

which writes results to:

```text
files/output/Equelo/expt3_q_sweep.csv
```

The sweep evaluates the full Expt3 simulation over:

```text
400 ≤ q ≤ 2000  (step 100)
```

with all other parameters unchanged.

Values below (q \approx 400) were not considered further, as they produce highly compressed or unstable behaviour and are not relevant to the regime of interest.

---

### Observations

Inspection of the sweep output shows:

* raw Brier is minimised at approximately:

```text
q ≈ 800
```

* calibration MAE is minimised at approximately:

```text
q ≈ 1000
```

Both metrics vary smoothly with (q), and differences in the range:

```text
800 ≤ q ≤ 1000
```

are small relative to their overall variation.

---

### Interpretation (Pareto)

These results define a small Pareto set of non-dominated values.

In this context, “favouring” a metric means that improvement in one objective cannot be achieved without degrading the other.

Within this set:

* (q \approx 800) favours Brier (discrimination)
* (q \approx 1000) favours calibration (MAE)

---

### Choice of q

Where a single value is required, we take:

```text
q = 900
```

as a representative midpoint within this Pareto set, minimising regret in either direction.

---

## **6.2 Sensitivity to link scale**

Changing (q) in the full system affects both:

* the rating dynamics
* the mapping from rating differences to probabilities

To isolate the latter, a link-only sweep was performed using:

```bash
py -m src.analysis.probability.expt3c --q 900 --bout-output foo.csv

py -m src.analysis.probability.expt3_link_sweep \
  --input foo.csv \
  --q-start 400 \
  --q-end 3000 \
  --q-step 100
```

The bout CSV contains the sequence of rating differences (`delta`) and outcomes produced by the full simulation.

For each value of (q_{\text{link}}), probabilities are recomputed as:

```text
p = 1 / (1 + 10^(-delta / q_link))
```

and evaluated using the raw Brier score.

Results are written to:

```text
files/output/Equelo/expt3_link_sweep.csv
```

---

### Observations

The sweep output shows:

* a clear minimum in raw Brier at:

```text
q_link ≈ 900
```

* smooth and monotonic degradation away from this value
* no secondary optima over the range:

```text
400 ≤ q_link ≤ 3000
```

Differences near the optimum are small (on the order of (10^{-4})).

---

### Interpretation

Because the rating trajectory is held fixed, this result isolates the role of the link function.

The observed optimum at:

```text
q_link ≈ 900
```

indicates that the mapping from rating differences to probabilities minimises raw Brier at this scale.

In particular, when the simulation is run with:

```text
q = 900
```

the resulting rating differences are most accurately interpreted using the same logistic scale.

---

### Conclusion

The link-only sweep shows that:

> **(q = 900) is internally consistent: the rating dynamics it induces are best interpreted using a logistic link of the same scale.**

Together with Section 6.1, this supports the use of (q = 900) as a representative value.
