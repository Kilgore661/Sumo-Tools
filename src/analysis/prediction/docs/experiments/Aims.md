
# Aims: Test Elo Win-Probability Models on Historical Sumo Results

## Status

Umbrella research aims.

This document records the wider programme from which numbered, narrower
proposals follow. A numbered proposal may deliberately address only part of
these aims. Completing such a proposal does not imply that the whole programme
has been completed.

## Objective

Build a reproducible system for testing how accurately Elo models predict professional sumo bout winners.

Because sumo bouts have binary outcomes and no draws, an Elo expected score can be interpreted directly as a predicted win probability:

\[
P(A\text{ wins})=
\frac{1}{1+10^{(R_B-R_A)/q}}
\]

Evaluate a family of models of the form:

\[
\operatorname{Elo}(q,\;K\text{-policy},\;b\text{-policy})
\]

and determine which specification produces the best chronologically out-of-sample win probabilities.

Do not merely identify how often the higher-rated rikishi wins. Evaluate the quality and calibration of the complete probability predictions.

## Initial repository and data investigation

Before implementing anything:

1. Inspect the repository structure and relevant documentation.
2. Locate the authoritative chronological bout dataset.
3. Locate any existing Elo implementation, rating outputs, tests and analytical conventions.
4. Establish the exact meanings already assigned to \(q\), \(K\) and \(b\).
5. Identify fields for date, basho, day, rikishi identity, winner, rank, division, absence and bout status.
6. Report any ambiguity that could materially affect the experiment.
7. Preserve existing behaviour and unrelated user changes.

Reuse reliable existing rating and data-loading code where practical. Keep the testing framework separate enough that it cannot accidentally use ratings calculated with future results.

## Model definition

For every eligible bout between rikishi \(A\) and \(B\), use their ratings immediately before the bout to calculate:

\[
p_A=\frac{1}{1+10^{(R_B-R_A)/q}}
\]

After recording the prediction and observing result \(S_A\in\{0,1\}\), update:

\[
R_A' = R_A + K_A(S_A-p_A)
\]

\[
R_B' = R_B + K_B((1-S_A)-(1-p_A))
\]

Permit \(K_A\) and \(K_B\) to be supplied by a configurable \(K\)-policy.

The framework must support at least:

- constant \(K\);
- \(K\) varying by current rating;
- \(K\) varying by experience or number of rated bouts;
- existing repository-specific \(K\)-policies, if present.

The \(b\)-policy determines a rikishi’s initial rating. Support at least:

- one constant initial rating for every entrant;
- an initial rating derived from an available prior estimate;
- existing repository-specific initialization policies.

Any prior estimate must use only information that existed before the rikishi’s first included bout. Record exactly which variables it uses.

## Parameter identifiability

Investigate rating-scale invariance before interpreting \(q\), \(K\) or \(b\) as independently meaningful.

Rescaling all rating differences, \(q\), \(K\), and initial-rating differences can produce equivalent predictions. Detect or explain equivalent parameterizations and avoid presenting duplicate models as substantively different.

If necessary, fix \(q\) to a conventional value such as 400 and optimize dimensionless quantities such as \(K/q\), or impose another explicit normalization. Prediction quality—not the arbitrary numerical rating scale—is the target.

## Test model

Implement a test interface conceptually equivalent to:

\[
\operatorname{Test}
(\text{prefix},\operatorname{Elo}(q,K,b),\text{metric})
\]

Let the eligible bouts, ordered chronologically, be:

\[
D=(d_1,\ldots,d_N)
\]

For a prefix proportion \(p\):

\[
m=\lfloor pN\rfloor
\]

Use \(d_1,\ldots,d_m\) as the initial training or warm-up prefix. Use later bouts for forward prediction.

For each evaluated bout:

1. Read ratings based solely on earlier results.
2. calculate and store the win probability before reading the result;
3. score the prediction;
4. reveal the result;
5. update the ratings before predicting subsequent bouts.

Updating after each evaluated bout is expected: this is an online, prequential evaluation. A bout must never influence its own prediction or any earlier prediction.

Make the prefix configurable. Test multiple sensible prefix values to determine whether conclusions depend heavily on the warm-up period.

## Model selection and final evaluation

Do not select a model and estimate its final performance on the same observations.

Use chronological sections:

1. **Training/warm-up:** establish ratings and fit parameters where necessary.
2. **Validation:** compare model specifications and select the best.
3. **Final test:** evaluate the chosen specification on a later, untouched period.

Alternatively, supplement this with expanding-window or walk-forward validation.

All splits must be chronological. Do not randomly divide individual bouts across training and test sets.

If the historical period is too short for a credible three-way split, explain the limitation and use nested walk-forward evaluation.

## Primary and secondary metrics

Use mean log loss as the primary selection metric:

\[
-\frac{1}{n}\sum_i
[y_i\log(p_i)+(1-y_i)\log(1-p_i)]
\]

Also report:

- Brier score;
- favourite-selection accuracy;
- calibration intercept and slope, if practical;
- observed win frequency within probability bins;
- sample size;
- uncertainty intervals for differences between models.

Protect log-loss calculations against numerical failure by clipping stored computational probabilities only at a very small documented epsilon. Preserve the original probabilities for reporting where possible.

Accuracy alone must not determine the winning model. A model predicting 0.51 and one predicting 0.90 make the same categorical selection but very different probabilistic claims.

## Calibration analysis

Produce a calibration table and plot. For suitable probability bins, show:

- number of predictions;
- mean predicted probability;
- observed win proportion;
- difference between predicted and observed rates;
- uncertainty interval.

Use bins that remain interpretable without producing misleadingly tiny samples. Consider equal-count bins as well as fixed-width bins.

Where useful, exploit symmetry by expressing every prediction as the higher-rated rikishi’s probability and outcome. Ensure this transformation is implemented consistently.

## Baselines

Compare Elo against at least:

- a constant 50% prediction;
- choosing the higher-ranked rikishi;
- an empirical rank-difference probability model;
- a recent-record model, if it can be defined without leakage;
- the existing production or published sumo Elo model, if one exists.

Probability-based baselines must be evaluated using the same log-loss and Brier metrics.

## Eligibility and data rules

Define and document the treatment of:

- fusensho and fusenpai;
- cancelled or missing bouts;
- non-bout administrative results;
- torinaoshi;
- missing or duplicate rikishi identifiers;
- same-day ordering;
- cross-division bouts;
- playoffs;
- pre-modern or structurally different eras;
- rikishi returning after long absences;
- name changes;
- entrants without sufficient prior information.

Default assumption: exclude walkovers and administrative outcomes from prediction scoring and rating updates because no contested bout occurred. Verify that this matches the dataset’s semantics.

Use stable rikishi identifiers rather than names wherever possible.

## Sumo-specific subgroup analysis

After selecting the principal model, report performance by relevant subgroup where sample sizes permit:

- era;
- division;
- rank band;
- rating-difference band;
- experience level;
- first tournament after absence;
- newly rated versus established rikishi;
- basho;
- playoff versus regulation bout.

These are diagnostic analyses, not opportunities to repeatedly retune the model on the final test set.

## Uncertainty and comparison

Report uncertainty around aggregate performance and model differences.

Because bouts within a basho and bouts involving the same rikishi are not fully independent, do not rely solely on an independent-bout standard error. Prefer a defensible block bootstrap, such as resampling basho, and explain its limitations.

For each candidate against the selected model, report:

- difference in mean log loss;
- difference in Brier score;
- uncertainty interval;
- whether the practical improvement is material, not merely numerically positive.

## Required outputs

Produce:

1. A reusable testing implementation.
2. Automated tests covering chronological prediction, initialization, updating and leakage prevention.
3. A machine-readable file containing one row per evaluated bout, including:

   - bout identifier and date;
   - both rikishi identifiers;
   - pre-bout ratings;
   - predicted probability;
   - actual outcome;
   - model specification;
   - dataset split;
   - per-bout log loss;
   - per-bout Brier score.

4. A model-comparison table.
5. Calibration tables and plots.
6. A concise report explaining:

   - dataset and eligibility rules;
   - model family;
   - chronological testing method;
   - parameters searched;
   - selection criterion;
   - validation results;
   - untouched final-test results;
   - uncertainty;
   - subgroup findings;
   - limitations;
   - recommended Elo specification.

7. Exact commands or documented steps needed to reproduce the results.

Save user-facing deliverables in the project’s normal output location. Avoid committing generated bulk data unless that is already repository convention.

## Verification requirements

Add tests demonstrating that:

- changing a future result cannot change an earlier prediction;
- each bout is predicted before its result updates ratings;
- chronological sorting is deterministic;
- rikishi identity survives name changes;
- excluded results neither receive predictions nor update ratings;
- the two win probabilities sum to one;
- rating changes behave correctly for wins and losses;
- equivalent scale parameterizations produce equivalent probabilities where expected;
- repeated runs with identical inputs produce identical outputs.

Run the relevant existing test suite as well as the new tests.

## Decision rule

Choose the model with the lowest validation log loss, subject to:

- no data leakage;
- acceptable calibration;
- sufficient stability across chronological folds;
- no unnecessary complexity where performance is effectively tied.

Break practically negligible ties in favour of the simpler, easier-to-explain policy.

Evaluate the selected model once on the untouched final-test period. Do not change the model after inspecting that result. If the final result motivates a new model, label that as a new exploratory cycle requiring a new future test period.

## Final research question

Answer:

> Within the family \(\operatorname{Elo}(q,K\text{-policy},b\text{-policy})\), which specification provides the best calibrated, chronologically out-of-sample probabilities of winning professional sumo bouts, and how much better is it than simple baselines and the existing Elo specification?

Lead the final response with the empirical answer, followed by the evidence, limitations and links to the implementation and report.
