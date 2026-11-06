# Appendix: Research and Implementation Guide

## Purpose

The expert account is a synthesis, not a self-contained archive of every
derivation, experiment and implementation decision. The complete project is
[open source](https://github.com/Kilgore661/Sumo-Tools). This appendix points
to the work which defines the current model, supports the principal empirical
claims and records important qualifications.

The guide is deliberately selective. Superseded development notes and the
broader drafting record are archived separately and do not define the current
model.

Research results remain attached to the model, data snapshot and comparison
declared in their source. A result obtained for an earlier prior or an earlier
end date is not silently treated as a new experiment on the final contract.
Where such work still supports a retained policy, that limitation is stated
below.

## The exact Elo-89 contract

The prose specification is [Chapter 9](09%20The%20Exact%20Elo-89%20Model.md).
The production implementation is divided as follows:

- [`model.py`](../../analysis/elo89/model.py) defines the Elo-89 run state and
  recorded observations;
- [`replay.py`](../../analysis/elo89/replay.py) implements the chronological
  recurrence, population shifts, forecasts and bout updates;
- [`producer.py`](../../analysis/elo89/producer.py) binds the accepted prior,
  (K) schedule and input history to the replay;
- [`config.py`](../../analysis/elo89/config.py) identifies the accepted P1-WL
  fitting boundary and immutable run;
- [`output.py`](../../analysis/elo89/output.py) writes the reproducible rating
  artifacts and their manifest; and
- [`bouts.py`](../../analysis/prediction/bouts.py) supplies the common eligible-
  bout selection used by the analyses.

The exact divisional (K) schedule is stored in
[`elo_fide.json`](../../../files/input/elo_fide.json). A standard production
bundle records the resolved inputs and outputs in its generated
[`manifest.json`](../../../files/output/analysis/site89_bundle/sources/elo89/manifest.json).
Files beneath `files/output` are generated locally and are not tracked by Git.

## The January 1989 data boundary

The earlier [bout-data completeness investigation](../../analysis/docs/story/17%20Pre-1989%20Bout-Data%20Completeness%20and%20Rating%20Persistence.md)
establishes that pre-1989 lower-division coverage is substantial but
incomplete. Its lifecycle discussion belongs to an earlier stage of the work
and should not be read as the present Elo-89 contract.

The later [1989--1998 bout-data completeness audit](../../../docs/1989-1998%20Bout-Data%20Completeness%20Audit.md)
rechecks the first ten years of the Elo-89 period at bout level. All sixty
basho contained opponent-paired lower-division results; fifty-nine matched the
corresponding career-result symbols exactly, and the remaining case contained
all seven daily bouts despite anomalous career symbols. This supports the
account's direct statement that the required banzuke and bout record is
available from January 1989.

The separate [Mae-zumo data audit](../../../docs/Mae-zumo%20%28Mz%29%20Data%20Semantics%20and%20Audit.md)
records why incomplete Mz--Mz detail is not the same question as completeness
for bouts between rikishi on the banzuke.

## Ordinary Elo and the interpretation of a rating

The conceptual background used in Chapters 2--7 is developed in:

- [Strength, Purpose and Model Bias](../../analysis/docs/2026%2009%2011%20Strength,%20Purpose%20and%20Model%20Bias%20-%20Lab%20Note.md);
- [Chii and the Measurement of Strength](../../analysis/docs/2026%2009%2026%20Chii%20and%20the%20Measurement%20of%20Strength.md);
- [What It Means to Test a Sumo Model](../../../docs/What%20It%20Means%20to%20Test%20a%20Sumo%20Model.md); and
- the [standard Elo account for a STEM reader](../../analysis/docs/story/06%20Draft%20Standard%20Elo%20Account%20for%20the%20STEM%20Reader.md).

These sources explain why a rating is a model state rather than a direct
observation, why different purposes can justify different summaries, and why
predictive evidence does not by itself establish a unique meaning of
“strength”.

## (q), divisional (K), and the initial model comparison

The [Basic Elo predictive investigation](../../analysis/prediction/docs/experiments/Findings.md)
examines the (q=400) baseline, forecast-before-update protocol, calibration
and rating-maturity effects.

The [controlled retrospective model comparison](../../analysis/elo_model_selection/docs/Results%201.md)
compares constant and divisional (K), and equal and informed
initialisation, over the same eligible bouts. It supports the general use of
divisional (K) and informed initialisation. It does not establish that the
exact 10/15/25/35 schedule is optimal, and it predates the final P1-WL
artifact. The current schedule is therefore partly an empirically supported
policy and partly a retained modelling judgement.

## P1-WL first ratings

The current production account is the
[P1-WL README](../../analysis/elo89/prior/README.md). It identifies the
accepted immutable fitted run, explains the conversion from side-specific
chii values to rank-pair values and points to the exact paired CSV written by
the standard Elo-89 replay.

The principal supporting investigations are:

- [P1-WL prior comparison](../elo89-expert-account/Matters%20Arising/Kimarite/P1-WL%20Prior%20Comparison%20-%20Findings.md),
  which measures the effect of admitting every eligible W/L result regardless
  of whether kimarite is recorded;
- [P1-WL evaluation](../elo89-expert-account/Matters%20Arising/Kimarite/P1-WL%20Evaluation/Findings.md),
  which evaluates the corrected prior both as an initialiser and inside the
  complete Elo-89 calculation; and
- [the rejected tighter fit](../elo89-expert-account/Matters%20Arising/Kimarite/P1-WL%20Evaluation/P1WL3%20Findings.md),
  which shows why numerical convergence alone is not an acceptance criterion
  for the unsmoothed literal-chii map.

The fitting implementation is in
[`src.analysis.elo89.prior`](../../analysis/elo89/prior/producer.py). The
accepted side-specific fitted artifact is generated at:

```text
files/output/analysis/elo89/prior/2026-09/run-001/prior.csv
```

The exact paired values consumed by the standard site-data replay are in the
generated [paired prior CSV](../../../files/output/analysis/site89_bundle/sources/elo89/prior.csv).

The retained table is empirical and unsmoothed. It is not constrained to be
monotone with chii. The investigations above discuss sparse-cell instability
and reject an extreme tighter fit, but they do not constitute a dedicated
evaluation of monotonicity or of a monotone or smoothed alternative.

## Population anchoring and normalisation

The retained population policy was selected in the
[Tranche 1 normalisation account](../../analysis/docs/story/15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md).
That work compares population policies while holding the declared fitted
inputs fixed and explains why a longitudinal coordinate requires an explicit
open-population rule.

Later work separates three questions which should not be conflated:

- the [normalisation contribution investigation](../../analysis/elo89_normalisation/docs/Normalisation%20Investigation.md)
  measures how common shifts contribute to reported individual changes;
- the [signed findings](../../analysis/elo89_normalisation/docs/Signed%20Findings.md)
  retain the direction of those contributions; and
- the [per-chii drift findings](../../analysis/elo89_normalisation/docs/Per-Chii%20Drift%20Findings.md)
  show that preserving one global mean does not make ratings stationary at
  every chii or prove absolute cross-era equivalence.

The production recurrence is in
[`replay.py`](../../analysis/elo89/replay.py). The diagnostic accounting code
is in [`accounting.py`](../../analysis/elo89_normalisation/accounting.py).

## Chii as evidence and baseline

The [chii prediction findings](../../analysis/chii_prediction/docs/Findings.md)
measure how often the stronger chii wins on the declared historical snapshot.
This is a descriptive favourite-selection baseline, not a fitted probability
model and not a matched demonstration that chii is better or worse than
Elo-89.

The measurement and interpretation issues are developed more broadly in
[Chii and the Measurement of Strength](../../analysis/docs/2026%2009%2026%20Chii%20and%20the%20Measurement%20of%20Strength.md).

## Connectivity, selective schedules, and toy evidence

The [Toy Elo research guide](../../analysis/toy_elo/README.md) collects the
controlled work on incomplete comparison graphs, division-like populations
and sparse bridges. These experiments demonstrate mechanisms and failure
modes under their declared artificial conditions. They do not establish the
size of the same effects in the historical sumo network.

The production account therefore treats connectivity and selective scheduling
as qualifications on interpretation, not as measured corrections silently
applied to the ratings.

## What has and has not been compared

The main retained empirical comparisons are:

| Question | Principal record | Scope qualification |
| --- | --- | --- |
| Does chronological Basic Elo contain information beyond 50--50? | [Basic Elo findings](../../analysis/prediction/docs/experiments/Findings.md) | Retrospective, beginning January 1989 |
| Constant or divisional (K); equal or informed initialisation? | [Model-selection results](../../analysis/elo_model_selection/docs/Results%201.md) | Earlier fitted prior; supports policies rather than every final numerical choice |
| Does P1-WL retain useful informed initialisation? | [P1-WL evaluation](../elo89-expert-account/Matters%20Arising/Kimarite/P1-WL%20Evaluation/Findings.md) | Retrospective within its fitting history |
| No population adjustment or whole-population preservation? | [Normalisation policy](../../analysis/docs/story/15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md) | Comparison conditional on the fixed inputs used there |
| How large are normalisation contributions? | [Normalisation investigation](../../analysis/elo89_normalisation/docs/Normalisation%20Investigation.md) | Diagnostic rather than a new model-selection gate |
| Does a fixed mean stabilise every chii? | [Per-chii drift findings](../../analysis/elo89_normalisation/docs/Per-Chii%20Drift%20Findings.md) | Descriptive historical audit |
| How often does the stronger chii win? | [Chii findings](../../analysis/chii_prediction/docs/Findings.md) | Favourite accuracy, not a probability comparison |

No comparable completed experiment in the repository establishes superiority
over a Glicko-like uncertainty model, a dynamic Bayesian paired-comparison
model, a fitted probabilistic chii model or a model with persistent matchup
effects. The current evidence is also primarily retrospective. Those absences
are limitations, not evidence that the untested alternatives would win.

## Production and publication artifacts

The standard site-data build is implemented by
[`site89/producer.py`](../../analysis/site89/producer.py). It writes the Elo-89
run beneath `sources/elo89` and records the files used by the website in the
bundle manifest. The website build and its data boundary are described in the
[implementation plan](../../products/make_site89/docs/Implementation%20Plan.md).

The generated artifacts needed to reproduce or audit a particular published
release include:

- the site-bundle manifest;
- the Elo-89 run manifest;
- the paired P1-WL CSV and its source hash;
- the exact (K) configuration;
- the input-history identity and final basho;
- the bout ledger containing pre-update forecasts; and
- the basho-start, day-end and normalised basho-end rating states.

Generated files are intentionally outside source control. A published release
must therefore preserve or distribute the relevant bundle rather than rely on
the repository alone to recreate a past data snapshot.

