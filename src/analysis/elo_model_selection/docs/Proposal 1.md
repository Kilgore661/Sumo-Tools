# Proposal 1: Controlled Post-1988 Elo Model Comparison

## Status

Proposed design for review. No comparison code has yet been implemented and no
candidate model has been selected.

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

1. **Rating scale.** The adopted source maps were produced with `q=900`,
   divisional `k` and closed-mode normalisation. This experiment fixes
   `q=400`. The implementation must either rebuild the prior within the
   declared model scale or apply a mathematically explicit transformation.
   Raw reuse is not an unstated default.
2. **Training boundary.** A prior used for held-out prediction must be
   constructed without any result from the evaluation period. The final
   through-2026 artifact may be used in a labelled retrospective diagnostic,
   but not in the decisive validation.

The same frozen prior must be used by `B_P` and `B_kP` within each
validation fold. Otherwise prior choice would be confounded with `k` policy.
Coverage, unsupported chii, Mae-zumo, missing chii and fallback behaviour must
be identical and explicitly manifested.

## Work products

The code will produce:

1. a canonical prepared-bout ledger shared by all models;
2. one immutable pre-bout forecast ledger per model and validation fold;
3. a manifest containing source hashes, model parameters, prior provenance,
   eligibility counts and software version;
4. paired per-bout log-loss and Brier-loss differences;
5. cumulative and rolling summaries by basho;
6. paired uncertainty intervals using basho-level blocks;
7. all-bout, sekitori, sub-sekitori and entrant-experience summaries;
8. the factorial contrasts attributable to `k`, the prior and their
   interaction;
9. a machine-readable decision summary; and
10. a reader-auditable Markdown report and charts.

Every forecast ledger will include at least:

```text
basho, day, bout identity
rikishi identities and pre-bout chii/division
ratings before the bout
k values used
initialisation source and prior-training cutoff
predicted probability
observed result
log loss and Brier loss
ratings after the update
```

## Two analysis stages

### Stage 1: retrospective diagnostic

Run all four models across the complete 1989/01--2026/07 record, using the
final adopted prior after its rating-scale treatment has been declared.

This stage will:

- verify that the four implementations share the same bout domain;
- reveal gross improvements, regressions and interactions;
- reproduce `B`'s established scores;
- expose initialization-gap and subgroup behaviour; and
- provide useful debugging evidence.

Because the final prior uses information from the period being scored, this
stage is in-sample. Its results must be labelled *retrospective diagnostic* and
must not select `B'` on their own.

### Stage 2: temporal validation

The decisive evaluation will use expanding historical training prefixes and
later untouched evaluation blocks. For each fold:

1. construct `P` using only results at or before the training cutoff;
2. rerun each model through the training prefix to establish its state;
3. freeze the trained prior for the following evaluation block;
4. predict and update chronologically through that block; and
5. discard and reconstruct state at the next fold so no later result reaches
   an earlier forecast.

The proposed folds are:

| Training results through | Evaluation block |
|---|---|
| 2000/11 | 2001/01--2006/11 |
| 2006/11 | 2007/01--2012/11 |
| 2012/11 | 2013/01--2018/11 |
| 2018/11 | 2019/01--2024/11 |
| 2024/11 | 2025/01--2026/07 |

These dates are part of the proposal, not yet an adopted design. Before code is
run for a declared result, they should be checked against prior support,
historical coverage and the desire not to choose cutoffs after seeing scores.
Any revision must be documented before comparative output is inspected.

If the adopted prior construction cannot produce a supported map from an early
training prefix, that is a finding about the policy. The code must fail or use
a predeclared fallback; it must not silently borrow later evidence.

## Evaluation populations

The primary population is every common eligible bout in the held-out blocks.

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
- cumulative loss by time; and
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

If the independent fair-coin simulation is repeated for a modified model, the
entire training and prediction procedure must be rebuilt within each simulated
history. Reusing historical trained priors inside a fair-coin history would not
represent the declared null.

## Proposed success criteria

There are separate criteria for the research tranche and for a candidate
model.

### Research success

The tranche succeeds if:

- all four models are exactly specified and reproducible;
- the same eligible held-out bouts are compared;
- no evaluation result influences a training prior or earlier forecast;
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

where `L` is mean held-out log loss and `L(50) = log(2)`.

Model `C` contains predictive information under the primary rule when the
one-sided 95% upper confidence bound for `D(C,50)` is below zero. Brier loss
against 0.25 supplies a required secondary check. Material disagreement
between the two proper scores must be explained rather than averaged away.

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
`B`'s held-out log-loss advantage over the neutral forecast:

```text
delta(log) = 0.05 * (L(50) - L(B))
```

A modified model is non-inferior when the one-sided 95% upper confidence bound
for `D(C,B)` is below `delta(log)`. The same construction will be reported
for Brier loss using 5% of `B`'s held-out Brier advantage over 0.25.

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

A model is eligible for selection only if it passes the predictive-information
criterion and is superior or non-inferior to `B` on the primary held-out
comparison.

Among eligible models, the proposed selection rule is:

1. prefer the model with the lowest held-out mean log loss;
2. use Brier loss, calibration and subgroup results to identify meaningful
   trade-offs rather than silently override log loss;
3. prefer the simpler model when predictive differences are practically
   negligible; and
4. retain `B` if no modification clears the declared gate.

Selection of `B'` must be recorded as a decision with the full report and
manifest, not inferred later from whichever artifact entered production.

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
- future-result isolation;
- constant-rating translation invariance;
- prior training-cutoff enforcement;
- deterministic prior and fallback lookup;
- correct per-rikishi divisional `k` selection;
- cross-division update behaviour;
- paired score arithmetic;
- fold reconstruction and boundary dates;
- deterministic uncertainty under a fixed seed; and
- manifest hashes and parameter completeness.

At least one deliberately leaky fixture must fail, demonstrating that the
training boundary is enforced rather than merely documented.

## Deliverables

The first implementation tranche is complete when it provides:

1. the shared model and experiment definitions;
2. the four forecast producers or one parameterised producer proving the four
   contracts;
3. retrospective diagnostic output;
4. temporal-validation output;
5. paired uncertainty and factorial comparisons;
6. automated verification;
7. a consolidated findings document; and
8. a decision record selecting `B'` or retaining `B`.

No Equelo or website artifact should be changed as part of this proposal.
- reproduce `B`'s established scores;
