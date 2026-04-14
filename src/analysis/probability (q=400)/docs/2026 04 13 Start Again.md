# Technical Status Report (Draft)

## 1. Objective

We evaluate an Elo-style rating model for sumo, in which bout outcomes are predicted as a function of the rating difference between rikishi. The objective is to assess the model’s calibration and predictive performance against historical data.

---

## 2. Data Characteristics

The dataset comprises approximately 630,000 bouts spanning 1958–2026.

Due to the scheduling of matches (torikumi) in sumo, most bouts occur between rikishi of similar rank (chii). It follows that, in any numerical rating system, bouts are not uniformly distributed across rating differences.

In practice:

* The distribution of rating differences is highly concentrated around zero.
* Large rating differences occur infrequently.
* Predicted probabilities are correspondingly concentrated near 0.5, with relatively few observations in the tails.

This structure is a property of the competition format rather than of the model.

---

## 3. Estimation of Calibration

Calibration is assessed by comparing predicted win probabilities with observed win frequencies, aggregated into bins.

Observed win rates are empirical estimates and are therefore subject to sampling variability. The variance of these estimates depends on the number of observations per bin, with low-frequency bins exhibiting high variance.

Consequently:

* Estimates in high-support regions are relatively stable and interpretable.
* Estimates in low-support regions, particularly in the tails, are noisy and unstable.

---

## 4. Restriction to High-Support Regions

To obtain meaningful calibration estimates, we restrict attention to bins with sufficient observational support.

In this analysis, we use a working threshold corresponding to a standard error of approximately 0.02 (roughly n ≥ 500 in the worst case). This is a modelling choice, and the extent to which the results depend on it is not yet clear.

The purpose of this restriction is to limit attention to regions where observed deviations between predicted and empirical probabilities are not dominated by sampling noise.

Under this restriction:

* The retained bins account for the majority of observations.
* The effective evaluation domain corresponds to near-even matchups.
* Regions with large rating differences are largely excluded due to insufficient support.

---

## 5. Preliminary Observations

Within the high-support region:

* The model exhibits reasonable calibration.
* Systematic deviations between predicted and observed probabilities are small at the level of resolution considered.
* Results are stable under changes in binning, although sensitivity to the support threshold has not yet been fully explored.

Outside this region:

* Apparent deviations are larger but highly unstable.
* These are consistent with sampling variability rather than clearly attributable to model behaviour.

---

## 6. Current Position

At this stage:

* The model captures meaningful predictive signal in the data.
* Calibration can be assessed with confidence only within a restricted, high-support region.
* Conclusions about model performance outside this region are limited by data sparsity.

Further work is required to:

* assess sensitivity to the support threshold,
* explore alternative aggregation schemes, and
* investigate model behaviour in low-frequency regimes.

---

## 7. Choice of Probability Scale (q)

In the Elo formulation, predicted win probabilities are derived from rating differences via a logistic function parameterised by a scale parameter ( q ):

[
p = \frac{1}{1 + 10^{-\Delta / q}}
]

where ( \Delta ) is the rating difference.

The parameter ( q ) controls the mapping from rating difference to probability:

* Smaller ( q ) produces steeper mappings (more extreme probabilities).
* Larger ( q ) produces flatter mappings (probabilities closer to 0.5).

---

### 7.1 Empirical Behaviour

We evaluated model performance across a range of ( q ) values, holding other parameters fixed.

The principal observations are:

* Predictive performance (as measured by Brier score) improves as ( q ) increases from conventional values (e.g. 400) up to approximately ( q \approx 800\text{–}900 ).
* Improvements are primarily driven by reductions in calibration error (reliability).
* The model’s resolution (ability to distinguish outcomes) remains broadly stable across this range.

Beyond this region, improvements are small and the objective function appears relatively flat.

---

### 7.2 Interpretation

The results indicate that, for this dataset and modelling setup:

* Conventional Elo scaling (e.g. ( q = 400 )) produces predictions that are systematically overconfident.
* A larger ( q ) yields better-calibrated probabilities without materially reducing discrimination.

This suggests that the effective relationship between rating differences and outcome probabilities in this setting is flatter than that implied by standard Elo parameterisations.

---

### 7.3 Interaction with Data Structure

The effect of ( q ) must be interpreted in the context of the data distribution described in Section 2.

In particular:

* Most observations occur at relatively small rating differences.
* Large rating differences are both rare and weakly supported.

As a result:

* The relevant operating range of ( \Delta / q ) is limited.
* Even relatively large values of ( q ) do not imply that predictions collapse to 0.5 across the observed data.

Thus, the empirical preference for larger ( q ) values does not correspond to a “coin-flip” model, but rather to a rescaling of probabilities within the range where the data are concentrated.

---

### 7.4 Current Position

At this stage:

* Values of ( q ) in the range ( 700 \text{–} 900 ) provide the best empirical performance under the current evaluation framework.
* The objective function is relatively flat in this region, and the choice is therefore not sharply identified.
* The interaction between ( q ), rating dynamics, and calibration warrants further investigation.

In particular, it remains to be established:

* whether the optimal ( q ) is robust to alternative evaluation criteria, and
* to what extent the observed behaviour reflects properties of the data versus properties of the model.

---

## 7.5 Role of ( q ) in the Model

The parameter ( q ) affects the model in two distinct but coupled ways:

1. **Probability mapping (link function)**
2. **Rating dynamics (update mechanism)**

These effects should be considered separately.

---

### 7.5.1 Effect on Probability Mapping

The most direct role of ( q ) is in the mapping from rating difference to predicted probability:

[
p = \frac{1}{1 + 10^{-\Delta / q}}
]

This determines how rating differences are interpreted probabilistically:

* Smaller ( q ):
  
  * Steeper mapping
  * Larger deviations from 0.5 for a given ( \Delta )
  * More extreme predictions

* Larger ( q ):
  
  * Flatter mapping
  * Smaller deviations from 0.5
  * More conservative predictions

Holding ratings fixed, increasing ( q ) reduces overconfidence and tends to improve calibration if the original mapping is too steep.

---

### 7.5.2 Effect on Rating Updates

In the Elo framework, the same probability function is used in the update rule. For a bout between rikishi ( A ) and ( B ), the rating update is:

[
R_A' = R_A + K \cdot (S_A - p_A)
]

where:

* ( S_A \in {0,1} ) is the observed outcome
* ( p_A ) is the expected probability computed using ( q )

Thus, ( q ) affects not only the reported probability but also the *magnitude and direction of rating updates*.

Specifically:

* Larger ( q ) produces probabilities closer to 0.5
* Therefore, the term ( (S_A - p_A) ) is typically larger in magnitude
* This leads to larger average updates for a given ( K )

Conversely:

* Smaller ( q ) produces more extreme probabilities
* The model is more “confident”
* Updates are smaller on average when outcomes align with expectations

---

### 7.5.3 Interaction with Rating Scale

Because ( q ) influences update magnitudes, it also affects the long-run distribution of ratings.

In particular:

* Larger ( q ) tends to:
  
  * Increase volatility of updates
  * Potentially widen the distribution of ratings

* Smaller ( q ) tends to:
  
  * Reduce update magnitudes
  * Compress the rating distribution

As a result, ( q ) influences the scale of ( \Delta ) itself, not just its interpretation.

---

### 7.5.4 Coupling Between Mapping and Dynamics

The two roles of ( q ) are tightly coupled:

* ( q ) determines how rating differences are converted into probabilities
* The same probabilities determine how ratings evolve
* The evolving ratings determine future rating differences

Thus, changing ( q ) affects:

* instantaneous predictions
* update sizes
* long-run rating distribution
* future predictions

This feedback loop means that:

> Changing ( q ) is not equivalent to rescaling probabilities post hoc; it changes the entire model behaviour.

---

### 7.5.5 Implications for Interpretation

The empirical finding that larger values of ( q ) improve predictive performance can therefore be interpreted in multiple ways:

1. **Link misspecification**
   
   * The logistic mapping is too steep for the observed relationship
   * Increasing ( q ) corrects this

2. **Dynamic compensation**
   
   * The update mechanism (e.g. choice of ( K )) may produce rating differences that are too large relative to observed outcome probabilities
   * Increasing ( q ) counteracts this by flattening the mapping

3. **Joint scaling issue**
   
   * The combination of ( K ), ( q ), and the data structure determines an equilibrium scale
   * The optimal ( q ) reflects this joint configuration rather than a property of the link function alone

These interpretations are not mutually exclusive.

---

### 7.5.6 Consequences for Model Evaluation

Because ( q ) affects both mapping and dynamics:

* Optimising ( q ) using predictive metrics (e.g. Brier score) identifies the best-performing **combined system**, not just the best link function.
* Comparisons across ( q ) values implicitly compare different rating systems, not just different probability calibrations.

This complicates interpretation:

* Improvements in performance may arise from:
  
  * better calibration of probabilities,
  * more appropriate rating spread, or
  * both.

---

### 7.5.7 Current Position

At this stage:

* The observed improvement in performance with larger ( q ) is a robust empirical finding.
* The mechanism underlying this improvement is not yet fully disentangled.

Further work is required to separate:

* the effect of ( q ) on the probability mapping, and
* its effect on rating dynamics and scale.

One possible approach would be:

* fix a rating trajectory (generated under a given ( q )), and
* evaluate alternative mappings applied post hoc

to isolate the link function from the dynamics.

---

# Summary

The parameter ( q ) is not a simple scaling constant. It is a structural parameter that jointly determines:

* how rating differences are interpreted, and
* how ratings evolve over time.

As a result, empirical tuning of ( q ) reflects properties of the entire modelling system rather than of the probability mapping in isolation.

The next step is to design an experiment that separates:

* **link effect**: how `q` maps rating differences to probabilities
* **dynamic effect**: how `q` changes the rating trajectory itself

Right now your Expt3 sweep changes both at once.

# Proposed experiment design

## Goal

Estimate how much of the improvement from raising `q` comes from:

1. better probability mapping for a *fixed* rating history
2. better rating dynamics producing a different rating history

## Core idea

Split the problem into two layers.

### Layer A: dynamics

Run the simulator once with some chosen `q_sim`, and record all pre-bout rating differences:

[
\Delta_t = r_{1,t}^{\text{before}} - r_{2,t}^{\text{before}}
]

### Layer B: link

Holding those (\Delta_t) fixed, evaluate many alternative values `q_link` using:

[
p_t(q_{\text{link}})=\frac{1}{1+10^{-\Delta_t/q_{\text{link}}}}
]

against the same observed outcomes (y_t).

That gives you a **post hoc link sweep**.

---

# Why this helps

Your current sweep answers:

> What is the best full Elo system if I set `q = ...` everywhere?

The new sweep answers:

> Given a fixed rating trajectory, what is the best probability mapping?

So you can compare:

* **full sweep optimum** over `q`
* **link-only sweep optimum** given fixed ratings

If they are similar, then the main issue is the probability link.

If they differ a lot, then dynamics are doing substantial work.

---

# Concrete experiment matrix

I would run three related experiments.

## Experiment 1: full-system sweep

You have already done this.

For each `q_full`:

* simulate with `q_full`
* evaluate with the same `q_full`

Output:

* raw Brier
* skill
* reliability
* resolution

This is your baseline.

---

## Experiment 2: link-only sweep on fixed trajectories

Pick a small set of simulation scales, for example:

* `q_sim = 400`
* `q_sim = 600`
* `q_sim = 850`

For each one:

1. run Expt3 once

2. save raw bout-level rows with:
   
   * `delta`
   * `outcome`

Then for a grid of `q_link` values, recompute only:

[
p = \frac{1}{1+10^{-\Delta/q_{\text{link}}}}
]

and evaluate Brier without rerunning simulation.

This gives curves like:

* best `q_link` for ratings generated under `q_sim = 400`
* best `q_link` for ratings generated under `q_sim = 600`
* best `q_link` for ratings generated under `q_sim = 850`

### Interpretation

If all three prefer similar `q_link`, then there is a fairly stable best link scale.

If they prefer very different `q_link`, then the dynamics and link are tightly entangled.

---

## Experiment 3: link calibration after normalization of delta scale

This is optional, but useful.

For each `q_sim`, compute summary stats of the resulting delta distribution:

* mean of `|delta|`
* sd of `delta`
* selected quantiles

Then compare whether higher `q_sim` is simply changing the *scale* of the delta distribution.

This helps answer:

> Is large optimal `q` just compensating for large generated rating gaps?

---

# What to record

For each bout in the fixed-trajectory files, keep:

* `date`
* `day`
* `rikishi1`
* `rikishi2`
* `r1_before`
* `r2_before`
* `delta = r1_before - r2_before`
* `outcome`

That is enough to do any post hoc link experiment later.

You do **not** need to store predicted probability in the fixed-trajectory file, because that can be recomputed for any `q_link`.

---

# Minimal implementation plan

You already have most of this.

## Step 1

Extend Expt3 so the raw bout CSV is easy to write and reuse.

You already added `delta`, so that part is basically done.

## Step 2

Write a new module, something like:

```text
src/analysis/probability/expt3_link_sweep.py
```

It should:

* read a bout-level CSV from Expt3

* ignore any stored `predicted`

* for each `q_link`:
  
  * compute predicted from `delta`
  * compute raw Brier, baseline Brier, skill

* write a CSV of results

This will be very fast because no history load or simulation is needed.

## Step 3

Generate fixed-trajectory files for a few `q_sim` values:

```bash
py -m src.analysis.probability.expt3 --q 400 --bout-output ...\expt3_bouts_q400.csv
py -m src.analysis.probability.expt3 --q 600 --bout-output ...\expt3_bouts_q600.csv
py -m src.analysis.probability.expt3 --q 850 --bout-output ...\expt3_bouts_q850.csv
```

## Step 4

Run the link-only sweep over each file.

---

# What outcomes would mean

## Case A: best `q_link` is always around 850

Then most of the issue is link scaling.

## Case B: best `q_link` varies a lot with `q_sim`

Then the rating dynamics are changing the meaning of rating differences, and `q` is not just a link parameter in practice.

## Case C: even at best `q_link`, residual structure remains large and smooth

Then you have stronger evidence against the logistic family itself.

---

# Strong version of the experiment

If you want the cleanest possible decomposition, use this 2x2 comparison:

For chosen values like 400 and 850, evaluate:

* simulate at 400, evaluate with 400
* simulate at 400, evaluate with 850
* simulate at 850, evaluate with 400
* simulate at 850, evaluate with 850

That gives a very readable table:

| rating dynamics | probability link | Brier |
| --------------- | ----------------:| -----:|
| 400             | 400              | ...   |
| 400             | 850              | ...   |
| 850             | 400              | ...   |
| 850             | 850              | ...   |

This is probably the single most informative design.

---

# Recommendation

I would do this next:

1. Generate bout-level files for `q_sim = 400, 600, 850`
2. Build a fast `expt3_link_sweep.py`
3. Compare best `q_link` across those fixed trajectories
4. Optionally make the 2x2 table first as a quick read

That will tell you whether “high q” is mostly:

* a better link,
* a better simulator scale,
* or both.

---

## 8. Findings on the Role of ( q )

To investigate the role of the probability scale parameter ( q ), we decomposed its effect into:

* **rating dynamics** (via simulation with a given ( q_{\text{sim}} )), and
* **probability mapping** (via post hoc evaluation using a potentially different ( q_{\text{link}} )).

This was implemented by:

1. Generating fixed rating trajectories under selected values of ( q_{\text{sim}} ).
2. Re-evaluating those trajectories using alternative values of ( q_{\text{link}} ).
3. Comparing predictive performance across combinations of ( (q_{\text{sim}}, q_{\text{link}}) ).

---

### 8.1 Summary of Results

A 2×2 comparison using ( q \in {400, 850} ) yields:

* ( (q_{\text{sim}}, q_{\text{link}}) = (400, 400) ): baseline system
* ( (400, 850) ): improved performance
* ( (850, 850) ): best observed performance
* ( (850, 400) ): substantially degraded performance

---

### 8.2 Key Observations

1. **Link scaling alone improves performance**
   
   For a fixed rating trajectory, replacing ( q = 400 ) with ( q = 850 ) improves predictive accuracy. This indicates that the standard Elo mapping is too steep for this setting.

2. **Rating dynamics also matter**
   
   Even with the same probability mapping, trajectories generated with larger ( q ) perform better. This indicates that ( q ) affects not only calibration but also the structure of the rating system itself.

3. **Consistency between dynamics and mapping is critical**
   
   The combination ( (q_{\text{sim}}, q_{\text{link}}) = (850, 400) ) performs significantly worse than all other configurations.
   
   This demonstrates that:
   
   * ratings generated under one scale cannot be reliably interpreted under another, and
   * the model requires internal consistency between rating evolution and probability mapping.

---

### 8.3 Interpretation

These results indicate that ( q ) should not be interpreted solely as a parameter of the probability mapping.

Instead, ( q ) defines a **joint scale** governing both:

* how rating differences are generated, and
* how those differences are interpreted probabilistically.

The optimal value of ( q ) therefore reflects a **self-consistent equilibrium** between rating dynamics and probability calibration.

---

### 8.4 Current Conclusion

The empirical results support the following:

* Conventional Elo scaling (e.g. ( q = 400 )) is too steep for this dataset.

* A flatter scale (e.g. ( q \approx 800\text{–}900 )) provides better calibration without reducing discrimination.

* The improvement arises from both:
  
  * improved probability mapping, and
  * more appropriate rating dynamics.

Further work is required to determine whether this reflects:

* properties of the data (e.g. matchup structure),
* properties of the update rule (e.g. interaction with ( K )), or
* a more general limitation of standard Elo parameterisation.

---

# 🧠 Why this section works

* It **answers the original experiment question**
* It clearly separates **evidence → interpretation**
* It avoids over-claiming
* It sets up the next phase naturally; i.e. what is the relationship between k
  and q?
