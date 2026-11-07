# Entrant Prior Mapping Optimisation

## Status

**TBD research proposal.** No optimisation experiment has been specified or
run, and no replacement for P89 is proposed by this document.

## Matter arising

P89's literal source was constructed by starting from a constant
chii-to-rating map and repeatedly replaying history to generate another map.
The algorithm has the form of a fixed-point iteration because it was
originally expected that the limiting self-consistent map might be the best
answer. Later evidence does not support that interpretation. Moving closer to
numerical convergence eventually worsened log loss and Brier loss and
destabilised sparsely supported cells.

The retained early iterate is therefore better understood as one useful point
found along one structured path through mapping space. Nothing establishes
that this path, or the selected point on it, is the best way to construct
first ratings.

This raises the research question:

> Can a declared modern optimisation or statistical estimation method find a
> chii-to-first-rating mapping which improves predictive performance and
> stability over P89 without sacrificing reproducibility or interpretability?

## Why this is a separate investigation

The current P89 artifact is fitted, frozen and operationally verified. An
optimisation study would reopen how its literal mapping is constructed. It
must not be performed implicitly inside an ordinary Elo-89 replay or website
build.

The exercise is also larger than choosing a new epsilon. An epsilon comparison
selects another point on the existing iterative trajectory. This matter asks
whether a different search path or estimator should be used at all.

## Candidate approaches

The investigation may consider, but should not assume the superiority of:

- regularised direct optimisation of literal- or paired-chii values;
- partial pooling across adjacent ranks, divisions, sides or rank families;
- hierarchical frequentist models;
- hierarchical Bayesian models with explicit posterior uncertainty;
- gradient-based optimisation where the replay and objective can be made
  differentiable or supplied with reliable derivatives;
- derivative-free or black-box optimisation;
- random, quasi-random or low-discrepancy exploration of constrained maps;
- monotone or softly monotone models; and
- models using information in addition to chii, provided the resulting
  first-rating rule remains available when it is applied.

The first experiment need not implement every family. It should compare a
small number of clearly motivated approaches against strong baselines.

## The object being optimised

Before implementation, the proposal must declare the parameterisation. At
least three choices are materially different:

1. one free parameter for every literal chii;
2. one free parameter for every paired P89 consumer key; or
3. a lower-dimensional function of rank, division, side, family and support.

The current two-stage construction fits literal cells and then aggregates
them. Directly optimising the paired table would answer a different question.
The experiment must not compare these parameterisations as though they differ
only computationally.

The proposal must also identify the coordinate constraint. Elo probabilities
depend on rating differences, so optimisation requires a declared location
anchor. That technical identification choice is distinct from Elo-89's
production policy of maintaining the active-population mean.

## Objective functions

Predictive selection should use proper scoring rules. At minimum report:

- mean log loss;
- mean Brier loss;
- calibration diagnostics;
- results by rating maturity and entrant experience; and
- uncertainty for material differences, using an appropriate temporal or
  basho-block resampling scheme.

No single aggregate score is sufficient. A candidate which obtains a tiny
global gain by producing extreme or unstable values in sparse cells may be a
poor first-rating policy.

The study should therefore also report:

- the distribution and range of mapping values;
- support attached to each value;
- local reversals and division-boundary discontinuities;
- sensitivity to small changes in the fitting sample;
- stability across optimisation seeds or initial states;
- differences from constant initialisation and P89; and
- effects on complete Elo-89 replay invariants and artifacts.

## Preventing information leakage and overfitting

The largest risk is optimising hundreds of mapping values against the same
history on which they are judged. That would turn historical outcomes into a
high-dimensional lookup table and could improve in-sample scores without
improving first ratings for later entrants.

A credible design must separate fitting, tuning and evaluation. Preferred
options include:

- rolling-origin evaluation with each fitted map using only information
  available before its evaluation period;
- a temporal development period followed by a untouched final period; or
- nested temporal validation if regularisation strength and model family are
  selected from the data.

Random bout-level splits are inappropriate where later career results can
leak information about earlier first ratings. The split must respect
chronology and the unit at which the map is fitted.

The current retrospective P89 evidence remains a baseline, not permission to
use the evaluation period during optimisation.

## Required baselines

At minimum, compare every candidate with:

1. constant first ratings;
2. official frozen P89;
3. nearby candidates on the retained iterative trajectory, including the
   epsilon-10, epsilon-8.5 and epsilon-8 regions where feasible; and
4. a simple regularised rank curve or partial-pooling model which prevents a
   sophisticated optimiser from being credited merely for adding shrinkage.

All baselines must use the same eligible bouts, chronology, K schedule,
population policy and forecast-before-update protocol unless the experiment
explicitly identifies a factorial comparison.

## Face validity and interpretation

P89 was partly accepted because its broad mapping looked plausible. That
informal screen should not be replaced by an optimiser whose output is
accepted solely because one score is smaller.

The proposal should define an inspectable plausibility audit before viewing
candidate results. Possible diagnostics include broad rank ordering, extreme
values, support-conditioned deviations, discontinuities, stability and the
upper-rank sequence. These are diagnostic constraints and modelling
judgements, not observations of true ability.

If a method produces a less intuitive map but reliably better out-of-sample
probabilities, the conflict should be reported rather than silently resolved
in favour of either appearance or prediction.

## Suggested experimental sequence

1. Freeze the exact History, bout policy, Elo-89 contract and P89 baseline.
2. Choose a temporal fitting, tuning and evaluation design.
3. Implement a low-dimensional regularised baseline.
4. Implement one literal- or paired-map optimisation method.
5. Record every candidate, parameter, seed and input identity.
6. Evaluate proper scores, calibration, stability and plausibility without
   changing the declared selection rule.
7. Run the selected candidate through a complete Elo-89 replay and dependent
   site build.
8. Publish findings whether or not a candidate improves on P89.

## Reproducibility requirements

Any implementation should write an immutable run directory containing:

- a manifest with source revision and all input hashes;
- the exact fitting, tuning and evaluation periods;
- the parameterisation and coordinate constraint;
- optimiser name, version, settings, stopping rule and random seeds;
- every retained candidate map;
- predictive and plausibility diagnostics;
- the selected map, if any, with its selection rule; and
- sufficient intermediate state to distinguish optimisation failure from a
  negative empirical result.

The experiment must not overwrite
`src/analysis/equelo_prior_aggregation/results/priors.csv`.

## Decision boundary

Completion of an optimisation run does not promote a new prior. Replacing P89
would require a separate decision which addresses:

- out-of-sample predictive evidence;
- uncertainty and practical size of any improvement;
- behaviour in sparse and historically changing chii;
- interpretability and operational complexity;
- complete replay and site-build verification;
- artifact identity and source-controlled persistence; and
- corresponding changes to the expert account.

Until that decision is made, P89 remains the official Elo-89 first-rating
table.

## Non-goals of this proposal

This document does not:

- select an optimiser or statistical model;
- declare log loss or Brier loss the sole project objective;
- refit or replace P89;
- change Elo-89 mean preservation, K, q, chronology or bout eligibility;
- claim that a numerically optimal mapping measures true ability; or
- require that a future mapping be monotone.
