# Evidence and Source Map

## Detailed inventory

The initial repository review is recorded in
[Elo Documentation Rummage](../2026%2008%2014%20Elo%20Documentation%20Rummage.md).
It identifies the Markdown and HTML material about Elo, Equelo and the related
experiments.

This note is the shorter map for constructing the eventual account.

## Current public-facing explanations

- [Elo Ratings](../../../products/make_site2/prose/Elo%20Ratings.html) is the
  clearest existing introduction to ordinary Elo and its immediate historical
  sumo problems.
- [Equelo Ratings](../../../products/make_site2/prose/Equelo%20Ratings.html) is
  existing site prose and should be reviewed against the structure in this
  folder.
- [Equelo Assumptions](../../../products/make_site2/prose/Equelo%20Assumptions.html)
  records assumptions currently exposed to readers.
- [What Is an Equelo Rating?](../../../../docs/What%20is%20an%20Equelo%20Rating.md)
  is the project-level account of interpretation and limits.

## Basic Elo predictive evidence

- [Prediction README](../../prediction/README.md) maps the chronological Basic
  Elo experiments.
- [Findings](../../prediction/docs/experiments/Findings.md) consolidates the
  measured results, population differences and initialisation experiments.
- [A Defence of Elo for Sumo (Sketch)](../../prediction/docs/A%20Defence%20of%20Elo%20for%20Sumo%20%28Sketch%29.md)
  gives the narrowest reader-facing claim currently supported.

These sources support a modest aggregate predictive claim. They do not
establish true strength, universal parameter choices or predictive validity for
Equelo.

## Probability and calibration

- [Probability README](../../probability/README.md) maps the probability
  experiments.
- [Results and Findings](../../probability/docs/5%20Results%20%26%20Findings.md)
  records the current calibration results and their supported regions.
- [Using Fixed Point Initialisation](../../probability/docs/7%20Using%20Fixed%20Point%20Initialisation.md)
  is relevant to the predictive effect of Equelo-like entrant ratings.

## Elo behaviour and incomplete comparisons

- [Toy Elo README](../../toy_elo/README.md) maps the controlled comparison-graph
  experiments.
- [What Ratings Might Say About Grand Sumo](../../toy_elo/docs/What%20Ratings%20Might%20Say%20About%20Grand%20Sumo.md)
  supplies the most important interpretive guardrails.
- [Boundary Monotonicity](../../toy_elo/boundary_monotonicity/README.md) tests a
  scheduling explanation for the lower-Makuuchi anomaly.
- [Elo Bottom Line 2](../2026%2008%2010%20Elo%20Bottom%20Line%202.html) explains
  continuing fixed-`k` fluctuation and the limits of the available theoretical
  bound.

## Equelo mechanics and unresolved behaviour

- [Equelo README](../../equelo/README.md) identifies the current production
  model and access contract.
- [Fixed Supported Requirements](../../equelo/docs/Fixed%20Supported%20Requirements.md)
  and [Fixed Supported Design](../../equelo/docs/Fixed%20Supported%20Design.md)
  define the maintained construction.
- [Initial Rating Audit](../../equelo/docs/2026-06-27%20Initial%20Rating%20Audit.md)
  records support and completion concerns.
- [Lower-Rank Problems](../../equelo/docs/equelo%20docs/lower_rank_problems.md)
  gives the clearest account of churn, sparse support and pathological tail
  behaviour.

These documents describe current production and the failure that motivated its
support policy. They do not define the adopted next entrant-prior policy.

## Contextual initial-rating policy

- [The M12 Problem: Consolidated Research Record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md)
  records the chronology, evidence, interpretation and decision that closed the
  M12 issue as a documentation blocker.
- [M12 Experiment Catalogue](09%20M12%20Experiment%20Catalogue.md) records the
  commands, matched artifacts and headline results for the literal, boundary,
  dual-boundary and lower-banzuke experiments.
- [Initial Rating Policy](10%20Initial%20Rating%20Policy.md) is the normative
  decision for the adopted 1989-onward paired entrant priors.
- [Fixed-Boundary Equelo](../../equelo/fixed_boundary/README.md) defines the
  contextual Makuuchi--Juryo source experiment.
- [Continuous Lower-Banzuke Equelo](../../equelo/fixed_lower_banzuke/README.md)
  defines the second contextual source experiment.
- [Initial-Rating Reconciliation](../../equelo/smoothing/README.md) defines the
  persisted merge and pairing producers.

The policy is adopted but not yet the map used by current production Equelo.
Its source fixed points are experimental evidence; the final reconciliation is
a declared construction rather than the direct fixed point of one simulation.

## Clean Elo and chii disagreement

- [Clean Elo README](../../clean_elo/README.md) records the negative result and
  the limits of interpretation.
- [Rating Probe Findings](../../clean_elo/docs/Rating%20Probe%20Findings.md)
  contains the detailed monotonicity and boundary-alignment findings.

These sources are central to explaining why neither agreement nor disagreement
between a rating system and chii should be treated as self-interpreting.

## Historical material

The older dated planning notes and archived site prose are useful for tracing
the development of the ideas, but should not be used as authority where newer
specifications or findings exist. The detailed rummage document identifies
those files and their current evidential status.
