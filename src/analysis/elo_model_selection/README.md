# Elo Model Selection

## Status

New analysis package. The research position and first proposal are documented;
the comparison code has not yet been implemented.

## Purpose

This package owns a new, controlled tranche of work for selecting the
post-1988 Elo-like model that should precede the next full-history Equelo
construction.

The project already has a definitive Basic Elo baseline, denoted by `B`:

```text
history = represented results from 1989/01 onward
q = 400
k = constant 35
initialisation = the same rating for every newly encountered rikishi
forecast chronology = predict before processing the result
rating identity = RikId
rating persistence = permanent
```

Existing work establishes that this model contains predictive information not
present in an independent 50--50 account of bout outcomes. Across the
1989/01--2026/07 record it reduced mean log loss by about 1.5% and mean Brier
loss by about 2.2% relative to a neutral forecast. A separate complete-history
fair-coin experiment strongly rejected the corresponding independent 50--50
null.

That result answers a question about `B`. It does not determine whether
divisional `k`, informed entrant priors, or their combination improve upon
`B`.

## Models under consideration

The tranche will compare a two-by-two family while holding `q=400` and the
post-1988 prediction problem fixed:

| Model | `k` policy | Entrant initialisation |
|---|---|---|
| `B` | constant 35 | constant |
| `B_k` | divisional | constant |
| `B_P` | constant 35 | informed prior `P` |
| `B_kP` | divisional | informed prior `P` |

These names describe experimental cells, not four promised production models.
The model eventually selected from this work is denoted by `B'`. Until the
comparison is complete, `B'` is an unfilled role rather than a definition.

The order of the subscripts is not intended to say that applying a `k` policy
and applying a prior are sequential operations. The table is a factorial
design: it permits the effect of each choice, and any interaction between
them, to be examined without changing unrelated parts of the model.

## Agreed research questions

For every model `C` in the table, ask:

> Does `C` contain predictive information beyond independent 50--50
> outcomes?

This has already been answered for `B`, but the new package must reproduce
the result on its own frozen comparison domain.

For each modified model `C` in `{B_k, B_P, B_kP}`, also ask:

> Does `C` predict better than `B`, or is it at least no worse under a
> declared non-inferiority rule?

The first question is a basic admissibility test for a rating model intended
to represent ability. The second is the model-selection question. A model can
beat 50--50 while still being worse than `B`.

Direct comparison among the three modified models will identify whether the
`k` policy, the prior, or their interaction accounts for any improvement or
loss.

## Why this is a new tranche

The repository contains valuable predictive and probability experiments, but
they do not collectively form this controlled comparison.

- `analysis/prediction` supplies the canonical `B` experiment and several
  retrospective constant-`k` initialisation diagnostics.
- Earlier exact-chii and division-only priors were compared with `B`, but
  they are not the recently adopted contextual prior and they use future
  outcomes from the period they score.
- The canonical prediction work has not compared constant and divisional `k`.
- The older probability and fixed-v1 work used materially different models,
  including `q=850` or `q=900`, divisional `k`, closed-mode
  normalisation, fixed-point or scaled priors, a 1958 epoch and differing bout
  eligibility.
- The recently adopted contextual prior was itself constructed in a
  `q=900`, divisional-`k`, closed simulation. It has not been evaluated in
  the canonical `q=400` prediction design.

Those experiments motivate this work, expose likely failure modes and provide
reusable machinery. Their results must not be combined as though they were the
four cells of one experiment.

## Relationship to Equelo

This package does not define Equelo.

Its job is to select `B'` using the sufficiently complete post-1988 record:

```text
B -> {B_k, B_P, B_kP} -> B'
```

The next Equelo will then be constructed by extending the selected `B'` to
the incomplete 1958--1988 history. That later construction will need its own
predictive comparison with an appropriate ordinary-Elo model.

Doing the post-1988 comparison first gives the later investigation diagnostic
power. If `B'` is worse than `B`, the problem lies in divisional `k`, the
prior or their interaction. If `B'` is sound but full-history Equelo later
performs worse, attention can turn to the historical extension,
normalisation, eligibility or another Equelo-specific policy.

## Interpretation boundary

The adopted final post-1988 prior artifact was learned from the same broad
history on which a retrospective run would score it. Such a run can be a
useful diagnostic, but it cannot establish prospective predictive power.

The decisive comparison must prevent results under evaluation from influencing
the prior used to predict them. It must also settle how a prior derived on a
`q=900` rating scale is represented in a model whose `q` is fixed at 400.
Neither raw reuse nor a scale conversion may be left implicit.

## Research and model success

The research tranche succeeds if it provides a reproducible, leakage-aware and
like-for-like answer, even if every proposed modification fails. A negative
result is useful model-selection evidence.

A modified model succeeds as a candidate only if it:

1. contains predictive information beyond 50--50;
2. is superior or non-inferior to `B` under the predeclared primary rule;
3. does not obtain its result through future-data leakage; and
4. has no important population-specific regression concealed by the aggregate
   result.

The numerical decision rule, paired uncertainty procedure and subgroup
guardrails are proposed in
[Proposal 1: Controlled Post-1988 Elo Model Comparison](docs/Proposal%201.md).

## Boundaries

This package will not:

- reopen the general search over `q`;
- seek ratings that reproduce chii monotonically;
- treat the chosen model as a causal or uniquely true account of ability;
- define the pre-1989 completion policy;
- overwrite the current fixed-supported Equelo artifacts; or
- migrate website consumers.

Those are separate questions. The package's immediate output is evidence for
choosing `B'`, not a new production rating series.
