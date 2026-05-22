## `build_calibration_rows()` technical specification

This specification describes the **core evaluation primitive** in `analysis/probability`, in the same style as the previous specs.

Primary source: `builder.py`, with supporting structures from `classes.py`.  

---

# 1. Function signature

```python
def build_calibration_rows(
    history: History,
    ratings: ChiiRatings,
    q: float,
    bin_width: float,
) -> list[CalibrationRow]
```

Defined in `builder.py`. 

---

# 2. Purpose

`build_calibration_rows(...)` constructs a **binned calibration dataset** comparing:

* **predicted win probabilities** (from Elo ratings), vs
* **observed win frequencies** (from historical bouts)

The output is a list of **calibration rows**, each corresponding to a probability bin, containing:

* mean predicted probability
* empirical win rate
* confidence intervals
* error metrics

---

# 3. Formal parameters

## 3.1 `history: History`

A cleaned historical dataset (typically oracle-processed).

### Meaning

Provides the full set of observed bouts used for evaluation.

### Required structure

For each `Date`:

* `basho_state.banzuke`: mapping `RikId → Chii`
* `basho_state.summary[day]`: daily bout results

### Role in the function

Defines:

* which bouts are evaluated
* which `Chii` labels are assigned to competitors
* the observed outcomes against which predictions are compared 

---

## 3.2 `ratings: ChiiRatings`

Type alias:

```python
ChiiRatings = dict[Chii, float]
```

### Meaning

A mapping from rank (`Chii`) to rating, typically produced by Expt2.

### Role in the function

Provides the **input model** used to generate predicted probabilities:

[
p = \frac{1}{1 + 10^{(r_2 - r_1)/q}}
]

where `r1 = ratings[c1]`, `r2 = ratings[c2]`. 

---

## 3.3 `q: float`

### Meaning

Elo logistic scale parameter.

### Role in the function

Controls the mapping from rating differences to predicted probabilities via:

```python
1 / (1 + 10 ** ((r2 - r1) / q))
```

This must match (or be consistent with) the `q` used during model estimation to ensure coherent evaluation. 

---

## 3.4 `bin_width: float`

### Meaning

Width of probability bins in the interval ([0,1]).

Example:

* `0.05` → bins like `[0.00–0.05), [0.05–0.10), …`

### Constraints

Must satisfy:
[
0 < \text{bin_width} \le 1
]

### Role in the function

Determines the resolution of the calibration curve:

* smaller width → finer bins, higher variance
* larger width → coarser bins, lower variance

---

# 4. Output

## 4.1 Return type

```python
list[CalibrationRow]
```

Each `CalibrationRow` contains:

```python
@dataclass(frozen=True)
class CalibrationRow:
    p_bin_lo: float
    p_bin_hi: float
    n_obs: int
    n_wins_c1: int
    n_losses_c1: int
    mean_predicted: float
    observed_win_rate: float
    ci95_lower: float
    ci95_upper: float
    abs_error: float
    sq_error: float
```

Defined in `classes.py`. 

---

## 4.2 Output meaning

Each row corresponds to a **probability bin** and summarises:

* **Predictions**
  
  * mean predicted probability in the bin

* **Observations**
  
  * number of observations (`n_obs`)
  * empirical win rate

* **Uncertainty**
  
  * 95% Wilson confidence interval

* **Error metrics**
  
  * absolute error
  * squared error

---

# 5. Execution semantics

The function performs the following steps:

---

## 5.1 Initialise bin accumulator

```python
bins = CalibrationBins(bin_width)
```

This object:

* partitions ([0,1]) into fixed-width bins
* accumulates counts and sums per bin 

---

## 5.2 Iterate over all bouts

For each:

* `date` in sorted history
* `day` in sorted basho days
* `bout` in daily results

---

## 5.3 Apply inclusion rules

A bout is **skipped** if:

* `decision` is `"fusen"` or `"blank"`
* either rikishi is not present in the banzuke mapping 

---

## 5.4 Map competitors to canonical `Chii`

For each valid bout:

* extract raw `Chii` for both rikishi
* reorder them into canonical order:

```python
c1, c2 = (lower ordinal, higher ordinal)
```

This ensures:

* consistent orientation of prediction
* `c1` is always the “reference competitor” 

---

## 5.5 Compute prediction and outcome

### Predicted probability

[
p = P(c1 \text{ beats } c2)
]

using the Elo logistic formula. 

### Observed outcome

[
y =
\begin{cases}
1 & \text{if winner has } Chii = c1 \
0 & \text{otherwise}
\end{cases}
]

---

## 5.6 Record observation

```python
bins.record(predicted_probability=p, outcome=y)
```

This:

* assigns the observation to a bin
* increments counts and sums for that bin 

---

## 5.7 Finalise bins

After all bouts:

```python
return bins.to_rows()
```

Each bin produces a `CalibrationRow` with:

* mean predicted probability
* observed win rate
* Wilson 95% CI
* error metrics 

---

# 6. Statistical interpretation

The function estimates, for each bin:

[
\mathbb{E}[Y \mid p \in \text{bin}] \quad \text{vs} \quad \mathbb{E}[p \mid p \in \text{bin}]
]

Perfect calibration would satisfy:

[
\text{observed_win_rate} \approx \text{mean_predicted}
]

Deviations measure miscalibration.

---

# 7. Preconditions

### 7.1 Consistent `Chii` domain

All `Chii` values appearing in `history` must be present in `ratings`.

Otherwise:

* `ratings[c1]` or `ratings[c2]` will fail

### 7.2 Matching collapse regime

The function assumes:

* full `Chii` (annotation-level) representation

This is enforced at CLI level (probability module rejects mismatched runs). 

### 7.3 Valid bin width

`bin_width ∈ (0,1]` or a `ValueError` is raised. 

---

# 8. Invariants

### 8.1 Bounded probabilities

All predicted probabilities are clamped to ([0,1]) before binning. 

### 8.2 Deterministic canonical ordering

Every bout is evaluated in a consistent orientation (`c1` vs `c2`). 

### 8.3 One record per valid bout

Each valid bout contributes exactly one `(p, y)` observation.

---

# 9. Postconditions

After execution:

* Each returned row corresponds to one non-empty probability bin

* Total observations equal the number of valid bouts processed

* Each row contains:
  
  * empirical frequency estimate
  * predicted mean
  * uncertainty estimate
  * error metrics

---

# 10. Relationship to the overall system

`build_calibration_rows(...)` sits at the end of the pipeline:

```
Expt1 → generates dynamics
Expt2 → estimates Chii-level ratings (mu)
Probability module → evaluates calibration
```

More concretely:

```
ratings (from Expt2)
    + history
    ↓
build_calibration_rows   ← THIS FUNCTION
    ↓
calibration_summary
    ↓
CSV / metrics
```

---

# 11. Concise functional description

`build_calibration_rows(...)` maps a **rank-based Elo model** and a **set of observed bouts** into a **binned calibration dataset**, by:

* computing Elo-implied win probabilities,
* aligning them with actual outcomes,
* aggregating into probability bins,
* and producing summary statistics that quantify calibration error and uncertainty.
