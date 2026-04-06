Here is a first draft for **Expt2**.

---

# **Expt2 — Estimating Basho-Start Initial Ratings by Fixed-Point Iteration**

## 1. Purpose

Expt1 examined the behaviour of an Elo system when applied to a historical record whose observable population changes over time. In particular, it identified the consequences of an inconsistent observable pool, including mean drift in the open system and the structural disturbance associated with the 1989 observability cliff.

Expt2 asks a different question:

> **Can we improve the initial ratings assigned to rikishi whose prior rating history is unavailable?**

The motivating idea is that the flat rule “assign baseline rating (b)” is artificial. It implies long burn-in periods, distorts early estimates, and handles the 1989 observability cliff badly, since many already-existing rikishi become newly observable and must otherwise all enter at the same baseline.

The proposed remedy is to estimate a **basho-start prior by ordinal**.

---

## 2. Core idea

We seek a mapping

[
\mu : \text{ordinal} \to \text{rating}
]

to be interpreted as:

> the rating to assign, at the start of a basho, to a rikishi appearing with a given ordinal when that rikishi has no prior rating in the observable system.

This mapping is not determined by Elo itself. It is an external input to the rating process. However, once such a mapping is supplied, the Elo simulation induces an implied relationship between basho-start ordinal and basho-start rating.

Expt2 proposes to estimate (\mu) by requiring **self-consistency**.

---

## 3. Fixed-point formulation

Given a current guess (\mu^{(t)}):

1. **Simulation step**
   Run the Elo history simulation using (\mu^{(t)}) as the basho-start initialisation rule for rikishi whose rating is unavailable.

2. **Aggregation step**
   Collect all **start-of-basho** observations from the simulated history.
   For each ordinal (c), compute the arithmetic mean of the observed ratings of rikishi appearing at basho start with ordinal (c).
   
   This produces a new estimate:
   
   [
   \tilde{\mu}^{(t+1)}(c)
   ]

3. **Normalisation step**
   Since Elo ratings are defined only up to an additive constant, apply a **uniform shift** to the aggregated values to fix a reference level.

4. **Update step**
   Set
   
   [
   \mu^{(t+1)} = \text{Normalise}\left(\tilde{\mu}^{(t+1)}\right)
   ]

5. **Convergence check**
   Compare (\mu^{(t+1)}) with (\mu^{(t)}).
   If the maximum absolute difference is below a chosen tolerance, terminate. Otherwise iterate.

A fixed point is therefore a mapping (\mu^*) such that, when used to initialise the historical Elo simulation, the resulting basho-start ordinal means reproduce (\mu^*) up to shift.

---

## 4. Why basho-start observations?

The target of Expt2 is a **basho-start initialisation rule**, so the relevant observations are basho-start ratings.

We therefore use only **start-of-basho** observations, not daily in-basho ratings.

This choice is deliberate:

* it matches the quantity the method is trying to estimate
* it avoids contamination from within-basho rating movement
* it avoids mixing the initialisation problem with a different descriptive question about rating during competition

Thus the object estimated in Expt2 is:

> **the expected basho-start rating associated with a given ordinal**

rather than a daily or trajectory-weighted quantity.

---

## 5. Why the arithmetic mean?

For each ordinal, the simulation produces many basho-start rating observations across many basho. Under a stable regime, these may be treated as repeated samples from an underlying distribution of basho-start ratings conditional on ordinal.

The arithmetic mean is then used as the estimator of the expected value of that distribution.

This choice is not defended merely on grounds of simplicity. It is appropriate because Expt2 aims to estimate a single representative rating for each ordinal under repeated sampling. Alternative summaries such as medians or weighted means would correspond to different target quantities and would require additional modelling assumptions.

---

## 6. Why normalisation?

The aggregation step yields ordinal means only up to an additive constant. This is because Elo depends on rating differences, not absolute level.

Accordingly, the normalisation step must be a **uniform shift only**. It may not rescale or otherwise deform the rating profile.

The old solver fixed the reference level by shifting all ordinal means so that their unweighted mean equalled (b). Expt2 may begin with the same rule, while recognising that this is an anchoring convention rather than part of the Elo dynamics themselves.

---

## 7. Two variants

Expt2 will investigate two related procedures.

### Variant A — Whole-history fixed point

Estimate the basho-start ordinal prior using the full historical dataset from the outset.

This asks whether a self-consistent prior can be obtained directly from the whole corpus.

### Variant B — Post-1989 calibration, then full-history refinement

First estimate the basho-start ordinal prior using the post-1989 period, where the observable population is comparatively consistent. Then use that estimate as the starting point for a full-history run, with optional further refinement by fixed-point iteration.

This variant is motivated by the idea that the post-1989 regime provides a cleaner calibration set, less affected by the observability cliff itself.

---

## 8. Hypothesis

The working hypothesis is:

> **A self-consistent basho-start prior by ordinal will reduce artefacts caused by flat initialisation, especially around the 1989 observability cliff, and will provide a more plausible estimate of initial ratings for rikishi whose prior rating history is unavailable.**

---

## 9. Questions to investigate

Expt2 does not assume in advance that the fixed-point approach is valid or useful. It is intended to answer at least the following questions:

1. Does the fixed-point iteration converge?
2. If so, is the resulting ordinal-to-rating mapping stable?
3. Do the whole-history and post-1989-calibrated variants converge to similar mappings, up to shift?
4. Does the learned prior reduce the visible effects of the 1989 cliff?
5. How sensitive are the results to the normalisation convention?
6. How sensitive are they to the choice of aggregation regime?
7. Does the learned prior materially change downstream ratings in plausible ways?

---

## 10. Scope and non-claims

Expt2 does **not** assume that rank is determined by rating, nor that end-of-basho rating determines next-banzuke rank.

Rank is used only as a proxy for expected strength at basho start when individual rating history is unavailable.

The goal is not to model promotion, demotion, or banzuke formation. The goal is to improve basho-start initialisation under partial observability.

---

## 11. Success criteria

Expt2 will be considered informative if it establishes some or all of the following:

* whether fixed-point estimation is computationally feasible
* whether a stable basho-start ordinal prior can be identified
* whether post-1989 calibration improves robustness
* whether the learned prior mitigates the pathologies associated with flat initialisation

Even a negative result would be useful, since it would show that the ordinal prior is not well identified or is too sensitive to modelling choices.
