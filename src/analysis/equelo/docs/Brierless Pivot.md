# Equelo Experiment Proposal: FP vs Brier vs Sanitised Ratings

## Purpose

Investigate whether the unexpectedly large gap between:

- current high live Equelo ratings (e.g. Yokozuna near 3000), and
- published “Typical Equelo Ratings” (e.g. Yokozuna ≈ 2555)

is primarily caused by:

1. the Brier compression/scaling step, or
2. the later cleaning/smoothing/sanitisation process.

The experiment is intended to clarify the semantic meaning of the published ratings and determine whether they retain an approximate fixed-point/equilibrium interpretation.

---

# Current Understanding

The current conceptual pipeline appears to be:

```text
Raw historical data
    +
constant initialisation
    ↓ iterative simulation
FP
    ↓ alpha shrinkage / Brier optimisation
Brier
    ↓ cleaning + smoothing + landmark extraction
Sanitised
    ↓ selective display
Published
```

Where:

- `FP` is the converged Expt2 fixed-point mapping `Chii → rating`
- `Brier` is the alpha-compressed mapping used operationally by fixed_v1
- `Sanitised` is the cleaned/smoothed interpretive mapping
- `Published` is the subset displayed publicly on the web site

---

# Background Assumptions

## Fixed-point property

If Elo updates depend only on rating differences, then:

- adding a constant offset to all ratings preserves the simulation dynamics,
- but multiplicative compression of rating differences does not.

Therefore:

- FP is expected to be approximately self-consistent under simulation,
- Brier is not guaranteed to be.

More precisely:

```text
aggregate(simulate(FP)) ≈ FP
```

where aggregation refers to the Expt2 basho-start aggregation operator.

---

# Main Hypothesis

The primary source of divergence between:

- published “Typical Equelo Ratings”, and
- modern live day-end ratings

may be the Brier compression step rather than the later smoothing/sanitisation step.

---

# Proposed Experiment

## Step 1 — Remove Brier Compression

Run the historical simulation pipeline using:

```text
initialiser = FP
```

instead of:

```text
initialiser = Brier
```

That is:

- use the raw Expt2 fixed-point mapping directly,
- skip the alpha-compression step.

---

## Step 2 — Apply Existing Cleaning/Smoothing

Apply the existing cleaning/smoothing/sanitisation pipeline unchanged.

This should produce:

```text
Sanitised(FP)
```

which is the sanitised interpretation of the raw fixed-point mapping.

---

## Step 3 — Quantify Smoothing Distortion

Measure the change induced by the sanitisation process.

Specifically compare:

```text
FP → Sanitised(FP)
```

Questions:

- How much do ratings move?
- Is smoothing mostly local?
- Are changes small for major ranks?
- Are sparse/odd ranks the main source of adjustment?
- Does monotonic enforcement significantly alter the upper ranks?

This stage determines whether sanitisation itself materially changes the meaning of the ratings.

---

## Step 4 — Re-simulate Using Sanitised(FP)

Use:

```text
initialiser = Sanitised(FP)
```

and run the historical simulation again.

Then:

- sample the resulting simulated ratings,
- aggregate by Chii/rank group,
- compare the observed values back to `Sanitised(FP)`.

Questions:

- Do simulated Yokozuna ratings remain close to sanitised Yokozuna values?
- Are upper-rank distributions centered near the sanitised ratings?
- Does the sanitised mapping behave approximately like a stable equilibrium?
- Or does simulation drift substantially away from the sanitised interpretation?

---

# Expected Outcomes

## Possibility A — Sanitised(FP) remains approximately stable

This would suggest:

- smoothing is mostly cosmetic/interpretable,
- the published ratings still retain an equilibrium interpretation,
- the major distortion was introduced by Brier compression.

---

## Possibility B — Sanitised(FP) drifts substantially

This would suggest:

- smoothing materially changes the dynamics,
- published ratings are interpretive landmarks rather than equilibrium quantities,
- the public explanatory layer has diverged from the simulation layer.

---

# Important Conceptual Distinction

The experiment distinguishes three different optimisation targets:

| Layer | Optimisation Target |
|---|---|
| FP | self-consistency |
| Brier | predictive calibration |
| Sanitised | human interpretability |

The purpose of the experiment is to determine whether the interpretability layer can still preserve approximate equilibrium semantics without the Brier compression step.

---

# Proposed fixed_v2 Experimental Structure

A new package will be introduced:

```text
analysis/equelo/fixed_v2/
```

The intent is exploratory at first, but with the possibility that the resulting ratings become the eventual “definitive” Equelo interpretation.

The primary entry point will be:

```text
fixed_v2.__main__
```

conceptually:

```text
python -m analysis.equelo.fixed_v2
```

This will act as the experimental application/orchestrator.

---

# Initial fixed_v2 Workflow

The first-stage pipeline should be:

```text
load config
    ↓
load FP ratings
    ↓
load Brier ratings
    ↓
verify smoothing/cleaning compatibility
    ↓
apply cleaning/smoothing to FP
apply cleaning/smoothing to Brier
    ↓
write comparison CSV
```

---

# Configuration

The application should import configuration from a shared/configurable source.

The initial requirement is simply:

- locate the FP ratings,
- locate the Brier ratings,
- locate output paths.

At this stage the exact configuration mechanism is intentionally deferred.

---

# Structural Assumption To Verify

The current cleaning/smoothing pipeline was designed for Brier ratings.

However, conceptually there should be no structural difference between:

```text
FP : Chii → rating
```

and:

```text
Brier : Chii → rating
```

Therefore the cleaning/smoothing code should theoretically be reusable unchanged.

This assumption must be verified first.

Questions:

- Does the smoothing pipeline assume compressed values?
- Does it assume monotonicity?
- Does it depend on specific rank filtering already performed upstream?
- Does it assume specific rating ranges?
- Does it depend only on the mapping structure itself?

---

# Output 1 — Comparison CSV

The first output artifact should be a CSV with columns:

```text
chii_ordinal,
fp_rating,
brier_rating,
fp_sanitised_rating,
brier_sanitised_rating
```

Purpose:

- inspect the effects of Brier compression,
- inspect the effects of smoothing,
- compare FP-derived and Brier-derived sanitised curves,
- support manual spreadsheet inspection before further automation.

At this stage:

- manual review is preferred,
- statistical analysis can be added later if necessary.

---

# Deferred Stages

Only after manual inspection of the CSV should further simulation work proceed.

Potential later stages:

## Re-simulation Using Sanitised(FP)

```text
initialiser = Sanitised(FP)
```

Then:

- run the simulator,
- sample resulting ratings,
- compare sampled values back to the sanitised curve.

---

## Optional Fixed-point Iteration

Possibly:

```text
Sanitised(FP)
    → simulate
    → aggregate
    → sanitise
    → repeat
```

Current expectation:

- interesting theoretically,
- probably not operationally useful.

The main immediate objective is understanding the relationship between:

- FP,
- Brier,
- sanitisation,
- and modern live ratings.

