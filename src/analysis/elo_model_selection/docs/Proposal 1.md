# Proposal 1: Controlled Post-1988 Elo Model Comparison

## Status

The controlled retrospective comparison is implemented and the declared
1989/01--2026/07 run has been made. Its findings and the subsequent
model-selection discussion are recorded in
[Results 1: Controlled Retrospective Comparison](Results%201.md).
Prospective validation remains separate future work.

## Objective

Run one controlled, reproducible comparison of the definitive Basic Elo model
`B` with the three models obtained by changing entrant initialisation,
the `k` policy, or both.

The experiment has two purposes:

1. establish whether each model contains predictive information beyond an
   independent 50--50 account of outcomes; and
2. determine whether each modification improves upon `B`, or is at least
   non-inferior under a declared practical threshold.

The result will support selection of a post-1988 successor `B'`. It will not
by itself define full-history Equelo.

## Why a controlled comparison is required

Earlier experiments changed several properties at once: epoch, `q`, `k`,
initialisation, normalisation, eligible bouts and sometimes the purpose of the
model. They demonstrate that predictive signal exists and that initialisation
can help or harm, but they cannot cleanly attribute a difference to the two
policies now under consideration.

This proposal fixes the prediction problem and varies only:

- constant versus divisional `k`; and
- constant versus informed entrant initialisation.

That two-by-two design permits direct estimation of the two policy effects and
their interaction.

## Models

All four models use:

```text
epoch = 1989/01
q = 400
identity = RikId
rating persistence = permanent within a run
chronology = forecast before result update
eligible result = W/L, irrespective of kimarite
excluded result = FS/FP or draw
```

The cells are:

| Model | `k` | Entrant initialisation |
|---|---|---|
| `B` | constant 35 | one common value |
| `B_k` | divisional policy | one common value |
| `B_P` | constant 35 | prior policy `P` |
| `B_kP` | divisional policy | prior policy `P` |

The common constant rating is an arbitrary origin. For the prior models,
common translation is also immaterial only when all entrants and fallbacks are
translated consistently.

### Divisional `k`

The initial proposed policy is the existing configuration in:

```text
files/input/elo_fide.json
```

Before the first declared run, the implementation must freeze and report:

- the exact file hash;
- the `k` assigned to every division/rank region;
- whether each participant receives his own pre-bout `k`;
- the treatment of cross-policy and cross-division bouts; and
- the resulting non-zero-sum behaviour when the two participants have
  different update rates.

No result may be labelled `B_k` merely because it invokes an older simulator
whose other policies differ from this proposal.

### Prior policy `P`

The intended source is the adopted, east/west-paired contextual entrant-prior
construction documented by the story workspace. The experiment tests a prior
*policy*, not merely one final artifact learned through 2026.

Two matters must be resolved and recorded before the declared run:

`P` is the exact adopted paired artifact. The implementation does not rescale,
smooth or recenter it. The same values are used by `B_P` and `B_kP`, so prior
choice is not confounded with `k` policy. The source path and hash are recorded.

The one known unranked History case cannot be looked up by chii. It receives
the weakest value in the adopted table and `k=35`; this fallback is explicit in
the ledger, manifest and report.

Because the artifact was constructed from the broad period being scored, its
results are future-informed. This is an interpretation boundary, not something
the implementation attempts to disguise by constructing a different `P`.

## Work products

The first implementation produces:

1. one canonical bout selection shared by all models;
2. one combined immutable pre-bout forecast ledger containing all four models;
3. a manifest containing source hashes, model parameters, prior provenance,
   eligibility counts and artifact semantics;
4. paired log-loss and Brier-loss comparisons;
5. paired uncertainty intervals using basho-level blocks;
6. all-bout, sekitori, sub-sekitori and entrant-experience summaries;
7. the factorial contrasts attributable to `k`, the prior and their
   interaction;
8. machine-readable CSV summaries; and
9. a reader-auditable Markdown report.

Every forecast ledger will include at least:

```text
basho, day, bout identity
rikishi identities and pre-bout chii/division
ratings before the bout
k values used
initialisation source
predicted probability
observed result
log loss and Brier loss
ratings after the update
```

## Retrospective diagnostic

Run all four models across the complete 1989/01--2026/07 record, using the
final adopted prior after its rating-scale treatment has been declared.

This stage will:

- verify that the four implementations share the same bout domain;
- reveal gross improvements, regressions and interactions;
- reproduce `B`'s established scores;
- expose initialization-gap and subgroup behaviour; and
- provide useful debugging evidence.

Because the final prior uses information from the period being scored, this
stage is in-sample. Its results are labelled *retrospective diagnostic* and
must not select `B'` on their own.

Prospective validation is a later proposal. Testing the exact adopted artifact
requires genuinely later results. Rebuilding priors at historical cutoffs
would instead test the construction policy, not this adopted artifact.

## Evaluation populations

The primary population is every common eligible bout in the declared period.

Required secondary populations are:

- both participants sekitori;
- both participants sub-sekitori;
- cross-boundary bouts;
- bouts grouped by each participant's prior rated-bout experience; and
- bouts involving a newly initialised rikishi.

The experience views are important because initialisation should have its
largest effect early in a rating history, whereas divisional `k` can continue
to affect established ratings. Aggregate scores alone may conceal that
difference.

## Metrics

### Primary metric

Mean pre-bout log loss, evaluated as paired differences on exactly the same
bouts.

Log loss is primary because it is a proper scoring rule and strongly penalises
confident errors.

### Secondary metrics

- mean Brier loss;
- calibration curves and calibration error in adequately supported regions;
- favourite win rate;
- the already defined hypothetical-evens directional statistic;
- rating and forecast coverage.

Secondary metrics explain the result and detect trade-offs. They must not be
searched selectively to overturn an unfavourable primary result.

## Uncertainty

Comparisons with `B` are paired by bout. Uncertainty will be estimated by
resampling basho-level blocks rather than treating hundreds of thousands of
bouts as independent observations.

The declared report will give two-sided 95% intervals for descriptive effects
and the corresponding one-sided upper bound for superiority or
non-inferiority decisions. The random seed, replicate count and interval method
must be fixed in the manifest.

The independent fair-coin simulation is not part of this first implementation.
Any later null experiment must state how the future-informed adopted artifact
is represented and what hypothesis that simulation actually tests.

## Proposed success criteria

There are separate criteria for the research tranche and for a candidate
model.

### Research success

The tranche succeeds if:

- all four models are exactly specified and reproducible;
- the same eligible retrospective bouts are compared;
- every individual forecast precedes its bout update, while the adopted
  artifact's whole-period provenance is disclosed;
- `B`'s established qualitative advantage over 50--50 is reproduced;
- paired effects and uncertainty are reported without suppressing adverse
  subgroups; and
- the outcome supports a clear decision, including the possible decision to
  retain `B`.

A finding that every modification is worse than `B` is still a successful
experiment.

### Predictive-information criterion

For a model `C`, define

```text
D(C,50) = L(C) - L(50)
```

where `L` is mean log loss over the common scored bouts and `L(50) = log(2)`.

Model `C` clears the numerical predictive-information criterion when the
one-sided 95% upper confidence bound for `D(C,50)` is below zero. Brier loss
against 0.25 supplies a required secondary check. Material disagreement
between the two proper scores must be explained rather than averaged away.

For `B` and `B_k`, this can support an ordinary historical predictive claim.
For `B_P` and `B_kP`, it describes retrospective pre-bout scoring but is not
leakage-free predictive evidence.

### Superiority to `B`

For a modified model `C`, define the paired difference

```text
D(C,B) = L(C) - L(B)
```

Model `C` is superior to `B` when the one-sided 95% upper confidence bound
for `D(C,B)` is below zero.

### Non-inferiority to `B`

Statistical significance alone is not an adequate rule with a very large bout
count. The proposal therefore defines a provisional practical margin as 5% of
`B`'s log-loss advantage over the neutral forecast:

```text
delta(log) = 0.05 * (L(50) - L(B))
```

A modified model is non-inferior when the one-sided 95% upper confidence bound
for `D(C,B)` is below `delta(log)`. The same construction will be reported
for Brier loss using 5% of `B`'s Brier advantage over 0.25.

The 5% fraction is a proposed modelling judgement, not a statistical constant.
It must be accepted or replaced before comparative results are inspected. A
post-hoc margin chosen to rescue a preferred model is not permitted.

### Population guardrail

An all-bout success must not be described without its sekitori,
sub-sekitori, new-entrant and experience-band results. Before the declared run,
the project must decide whether the non-inferiority margin is also a hard gate
within both principal populations or whether subgroup regressions are reported
as explicit trade-offs in selecting `B'`. That judgement remains open in
this proposal because it is substantive, not merely computational.

## Selecting `B'`

A model is retrospectively eligible only if it passes the numerical
predictive-information criterion and is superior or non-inferior to `B` on the
primary comparison.

Among eligible models, the proposed selection rule is:

1. prefer the model with the lowest mean log loss in the declared comparison;
2. use Brier loss, calibration and subgroup results to identify meaningful
   trade-offs rather than silently override log loss;
3. prefer the simpler model when predictive differences are practically
   negligible; and
4. retain `B` if no modification clears the declared gate.

The retrospective result alone does not select `B'`. Any eventual selection
must state what further prospective evidence is required and be recorded with
the full report and manifest.

## Factorial interpretation

The report will include at least these paired contrasts:

| Contrast | Interpretation |
|---|---|
| `B_k - B` | divisional `k` under constant initialisation |
| `B_P - B` | informed prior under constant `k` |
| `B_kP - B_k` | informed prior under divisional `k` |
| `B_kP - B_P` | divisional `k` under informed initialisation |

The interaction is the difference of differences:

```text
(L(B_kP) - L(B_P)) - (L(B_k) - L(B))
```

This will show whether the effect of divisional `k` depends on the
initialisation policy. The same calculation can be expressed with the prior
contrasts and must agree apart from numerical noise.

## Verification requirements

Automated tests must cover:

- exact reproduction of `B`'s forecast calculation;
- common bout identity and ordering across models;
- predict-before-update chronology;
- future bout results cannot change earlier sequential forecasts once the
  prior artifact is fixed;
- constant-rating translation invariance;
- exact adopted-prior lookup without transformation;
- deterministic prior and fallback lookup;
- correct per-rikishi divisional `k` selection;
- cross-division update behaviour;
- paired score arithmetic;
- deterministic uncertainty under a fixed seed; and
- manifest hashes and parameter completeness.

## Deliverables

The first implementation tranche is complete when it provides:

1. the shared model and experiment definitions;
2. the four forecast producers or one parameterised producer proving the four
   contracts;
3. retrospective diagnostic output;
4. paired uncertainty and factorial comparisons;
5. automated verification; and
6. a consolidated findings document after the declared run.

No Equelo or website artifact should be changed as part of this proposal.
- reproduce `B`'s established scores;
