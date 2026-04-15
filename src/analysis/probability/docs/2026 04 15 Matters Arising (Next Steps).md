I’ll organise what you’ve already said into **candidate experiments**, each with a clear question.

---

# 1) “Is chii an efficient encoding of outcomes?”

### Core idea you’ve been circling:

> Does the institutional ranking preserve the same predictive information as ratings?

### Clean question:

> How well does **chii alone** predict bout outcomes compared to ratings?

### Minimal experiment:

* Build: `P(win | chii)`
* Compare vs: `P(win | rating)`
* Evaluate with the same pipeline (Brier, calibration)

### Interpretation:

* If similar → chii is efficient
* If worse → chii is lossy
* If better → institution adds extra information

---

# 2) “What does chii throw away?”

This is the *residual* version of (1), and more interesting.

### Core idea:

> Even if chii works, does it discard useful structure?

### Clean question:

> Does rating still improve predictions **after conditioning on chii**?

### Form:

```text
P(win | chii, rating) vs P(win | chii)
```

### Interpretation:

* If rating adds nothing → chii is sufficient
* If rating helps → chii compresses too aggressively

---

# 3) “Where does the institution disagree with outcomes?”

This connects to your “bias / conservatism” idea.

### Core idea:

> Differences between rating and chii are not noise—they’re institutional decisions

### Clean question:

> Where are the largest systematic discrepancies between rating-implied and chii-implied strength?

### You’d look for:

* persistent under-ranked rikishi
* persistent over-ranked rikishi
* asymmetries (e.g. promotions vs demotions)

This is less about prediction, more about **diagnosis of the system**.

---

# 4) “Is chii a discretisation of rating?”

This is your *commutative diagram* idea, made testable.

### Core idea:

> Rank = coarse partition of a continuous ability scale

### Clean question:

> Do rank boundaries correspond to stable thresholds in rating space?

### What to check:

* distribution of ratings within each rank
* overlap between adjacent ranks
* stability of those boundaries over time

### Interpretation:

* clean separation → rank ≈ discretised rating
* heavy overlap → rank is doing something else

---

# 5) “Does the institution smooth volatility?”

This comes directly from your “flash in the pan” intuition.

### Core idea:

> Chii may deliberately resist short-term fluctuations

### Clean question:

> Do ratings react faster to performance changes than chii?

### What to compare:

* rate of change in rating vs rank movement
* lag between performance streaks and promotions

### Interpretation:

* lag → institutional conservatism
* alignment → reactive system

---

# 6) “Are ratings actually adding anything?”

This is the meta-question you landed on.

### Core idea:

> Ratings might just be a re-expression of chii

### Clean question:

> Is there predictive information in ratings that is not already in chii?

This is really just (2), but it’s the philosophical version.

---

# How these relate (important)

These are not separate projects—they form a **coherent ladder**:

1. **Prediction comparison** → (1)
2. **Information test** → (2)
3. **Structural interpretation** → (4)
4. **Behavioural diagnosis** → (3) + (5)

---

# What I’d recommend (without jumping ahead too much)

If you want clarity and momentum:

* Start with **(1) + (2)**
  → they anchor everything in measurable terms

Then:

* Use **(4)** to interpret structure
* Use **(3)/(5)** to explain deviations

---

# The key shift in your thinking

Originally:

> “Do ratings work?”

Now:

> “What is the relationship between institutional ranking and outcome-derived ability?”

That’s a much stronger and more interesting space.

---

If you want next step, we can take one of these and:

* define the exact minimal implementation
* and, crucially, what result would actually *surprise you*

That’s usually the fastest way to avoid building something trivial.

---

Grand Plan
==========

## Draft statement

### Position

The aim of this work is not to determine what the “correct” ranking of rikishi *should* be.

Instead, the goal is to construct a **fully specified, outcome-only baseline** against which institutional rankings can be compared.

This baseline is:

* derived solely from observed bout outcomes
* deterministic and reproducible
* free from discretionary judgement or narrative considerations

It represents:

> *what the ranking would look like if it were driven only by results, under a transparent rule*

The official banzuke (chii), by contrast, is understood as:

* a structured, institutionally produced ranking
* influenced by outcomes, but also by additional factors
  (e.g. stability, expectations, precedent, and implicit judgement)

The central stance is therefore:

> Any difference between the two systems reflects the presence of **non-outcome-based considerations** in the institutional process.

This is not treated as an error, but as something to be **made visible and measurable**.

---

### Questions

On this basis, the work aims to address questions of the following kind:

* **Information efficiency**

  * How well does chii predict outcomes compared to an outcome-only system?
  * Does it preserve the same predictive information, or compress it?

* **Sufficiency**

  * Does chii fully capture the information contained in outcomes?
  * Or do outcome-based ratings retain predictive power beyond rank?

* **Structure**

  * Can chii be understood as a discretisation of a continuous ability scale?
  * Do rank boundaries correspond to stable thresholds in that scale?

* **Dynamics**

  * How does the institutional system respond to changes in performance?
  * Does it systematically lag, smooth, or resist volatility?

* **Deviation**

  * Where do the largest discrepancies between outcome-based and institutional rankings occur?
  * Are these random, or do they follow identifiable patterns?

These questions are descriptive rather than normative:

> the aim is to understand what the system *does*, not what it *ought to do*

---

### Why this is workable

The feasibility of this approach rests on the results of the initial experiment.

That experiment shows that:

* A simple rating-based system can generate **well-calibrated probabilities**
* Calibration holds over the region where the data provide reliable support
* The system yields a consistent, if modest, improvement over a naive baseline 

This establishes that:

> an outcome-only mapping from past bouts to probabilistic predictions is empirically coherent

As a result:

* The rating system can be treated as a **valid reference representation of outcome-implied structure**
* It is not arbitrary, and its outputs have measurable meaning

Therefore:

> comparisons between this system and the institutional ranking are grounded in a common empirical framework

---

### Interpretation

The purpose of the subsequent experiments is not to replace the banzuke with an algorithm.

Rather, it is to:

> provide a transparent point of comparison that allows institutional decisions to be examined in relation to outcomes alone

In this sense, the work is epistemological:

* it seeks to clarify what can be inferred from data
* and what must come from additional judgement

---

## Closing line (optional tone-setting)

> The intention is not to eliminate judgement, but to make its effects legible.

