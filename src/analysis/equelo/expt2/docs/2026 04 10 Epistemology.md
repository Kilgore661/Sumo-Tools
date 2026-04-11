# Equelo: A Constrained Elo System (Epistemological Draft)

## 1) What Equelo is

Equelo is a modification of the system introduced by Arpad Elo. It preserves the core idea:

> The difference between two players’ ratings determines the expected probability of one beating the other.

Nothing in Equelo alters:

* the mapping from rating differences to expected scores
* the update mechanism based on game results

So in predictive terms, Equelo is simply Elo.

What Equelo adds is a **global constraint**:

* Fix a constant ( b )
* All new players enter with rating ( b )
* At all times, the **mean rating of the active pool is maintained at ( b )**
* When a player leaves, their net gain/loss ((q - p)) is redistributed **uniformly and additively** across the remaining players

Because this redistribution is uniform:

* Rating differences are unchanged
* Expected scores are unchanged

So the predictive structure of Elo is preserved exactly.

---

## 2) Epistemological stance

Equelo adopts the same restraint found in The Rating of Chess Players, Past and Present:

> Ratings are statistical constructs, not measurements of a metaphysical “true skill”.

The only standard that matters is:

> **Calibration** — do predicted probabilities match observed outcomes?

Equelo does not claim:

* that “skill” is a real scalar quantity
* that populations are stationary
* that eras are objectively comparable

It only claims:

> If the model is calibrated, it is adequate.

All other interpretations are optional and external.

---

## 3) What Equelo changes

Standard Elo systems (e.g. FIDE) allow:

* rating inflation and deflation
* drift in the mean
* accumulation of historical artifacts

Equelo removes this by construction:

> The mean rating is fixed at ( b ) for the active population.

This makes explicit something implicit in Elo:

* Absolute rating levels are conventional
* Only differences carry predictive meaning

---

## 4) Key properties

### (a) Invariance of differences

Uniform adjustments ensure:

* ( R_i - R_j ) is unchanged
* All predicted probabilities are unchanged

So Equelo preserves everything that matters for prediction.

---

### (b) Fixed reference level

The rating scale is anchored:

* No drift over time
* No need for ad hoc corrections (floors, periodic adjustments)

---

### (c) Separation of roles

Equelo cleanly separates:

* **Information** → rating differences
* **Convention** → choice of ( b )

---

## 5) Apparent issues and their resolution

### Issue 1: Inflation / deflation

✔ **Resolved structurally**
Equelo enforces a constant mean, eliminating drift.

---

### Issue 2: “Strength of the pool may change over time”

This is often raised but is:

> A hypothesis about the world, not a property of the rating system.

Equelo’s position:

* If such changes affect results → calibration will reveal it
* If not → irrelevant

So this is not an internal objection.

---

### Issue 3: Distribution shape may change

Response:

* Empirically, rating distributions appear stable (e.g. skewed with exponential-like tail)
* This can be treated as a **testable assumption**, not a flaw

---

### Issue 4: Selection effects (who enters/leaves)

Different narratives are possible:

* strong players leave more
* weak players leave more

Without measurement, these are speculative.

Equelo’s stance:

> Only effects that disturb calibration matter.

So again, this is external to the system.

---

### Issue 5: Meaning of the “average player”

Clarification:

* The value ( b ) is fixed
* What changes is which players occupy that rating

So:

> The *reference level is stable*, even if the population changes.

---

### Issue 6: New players starting at ( b )

This raises the question:

> When are ratings considered “stable”?

Rather than a flaw, this points to a requirement:

* Define a notion of **stabilization**
* Evaluate calibration after that point

This applies to Elo generally, not just Equelo.

---

### Issue 7: Stability / convergence

A central empirical question:

> Does the system reach a regime where ratings and predictions stabilize?

This must be tested.

---

## 6) What remains as genuine questions

After removing structural and speculative objections, the real issues are:

1. **Calibration**

   * Do predicted probabilities match observed results?

2. **Stabilization**

   * Does the system reach a usable steady regime?

3. **Distribution stability**

   * Is the rating distribution approximately invariant?

4. **Temporal consistency**

   * Does calibration hold across time?

These are all **empirical questions**, not philosophical ones.

---

## 7) Cross-era comparison

Equelo removes a known obstacle:

* rating drift across time

So:

> Any remaining difficulty in comparing eras is not caused by the rating system.

Within this framework:

* If calibration holds across periods
* And the system is stable

then:

> Cross-era comparisons are justified operationally (within the model)

No stronger claim is made.

---

## 8) Final characterisation

Equelo is best understood as:

> **Elo with an explicit mean constraint, evaluated purely by calibration after stabilization**

Its guiding principle is:

> If the model predicts well, it is sufficient.
> If it does not, it should be replaced.

All other questions—about “true skill,” population changes, or historical comparisons—are treated as **external hypotheses**, not properties of the system.

---
