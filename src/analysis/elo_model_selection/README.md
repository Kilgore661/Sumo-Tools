# Elo Model Selection

## Status

Implemented retrospective comparison package. The declared 1989/01--2026/07
run has been made and produces the four common forecast ledgers, paired
evaluation, participant-level calibration, uncertainty, provenance and a
qualified report. The results and their current interpretation are recorded in
[Results 1: Controlled Retrospective Comparison](docs/Results%201.md).

The comparison retains `B_kP` with `q=400` as provisional `B'`, because it
wins under the predeclared primary log-loss criterion and under Brier loss.
Calibration adds nuance rather than overturning that choice: `B_kP` is
fractionally best in aggregate, while `B_k` is fractionally best when ECE is
calculated separately within rating-maturity bands and then weighted by bout
count. The two are the strongest candidates and there is not a great deal to
choose between them. `B_k` is therefore recorded as the serious alternative.

Calibration by paired prior rated-bout counts shows that the troubling
aggregate overconfidence is concentrated primarily where a rating with fewer
than 30 prior results faces a more established rating. Two immature ratings
can be well calibrated against one another, while mature pairings are much
more closely calibrated in general. Investigating `q` remains possible, but
is no longer a prerequisite for proceeding to the full-history definition of
Equelo.

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
The comparison supports `B_kP` as the provisional post-1988 successor denoted
by `B'`, with `B_k` retained as the close alternative. Further diagnostics
refine the account of their strengths and weaknesses; they are not being
treated as a prerequisite for naming the model.

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
history on which this retrospective run scores it. The historical comparison
is therefore not out-of-sample validation.

For this tranche, `P` means the exact adopted paired artifact, unchanged. It is
used without rescaling, smoothing or recentering even though its source
experiments used `q=900`. Its behaviour inside the `q=400` candidate models is
part of what the comparison measures.

This is a provenance boundary, not an objection to selecting or using the
fitted model. Using all results through the latest basho to fit a model and
then forecasting the next basho is an ordinary past-to-future application.
The retrospective calculation supplies the intended sanity check that the
adopted prior improves on constant initialisation. A later prospective
experiment may add new evidence by scoring the fixed artifact on genuinely
future results; that is distinct from reconstructing the prior at historical
cut-offs.

## Research and model success

The research tranche succeeds if it provides a reproducible, leakage-aware and
like-for-like answer, even if every proposed modification fails. A negative
result is useful model-selection evidence.

A modified model can clear the retrospective candidate criterion only if it:

1. contains predictive information beyond 50--50;
2. is superior or non-inferior to `B` under the predeclared primary rule;
3. has no important population-specific regression concealed by the aggregate
   result.

For `B_P` and `B_kP`, clearing that criterion is retrospective model-selection
evidence rather than a historical out-of-sample test. This distinction is
recorded as provenance and is not treated as a reason to reject the adopted
prior.

The numerical decision rule, paired uncertainty procedure and subgroup
guardrails are proposed in
[Proposal 1: Controlled Post-1988 Elo Model Comparison](docs/Proposal%201.md).
The completed run is summarised in
[Results 1: Controlled Retrospective Comparison](docs/Results%201.md).

## Cumulative dual-K mass diagnostic

The follow-up experiment specified in
[Proposal 2: Cumulative Dual-K Rating Mass](docs/Proposal%202%20-%20Cumulative%20Dual-K%20Rating%20Mass.md)
measures rating mass created or destroyed when the two participants use
different `k` values. It consumes the persisted model-selection forecast ledger
so that it audits the exact `B_k` and `B_kP` runs already used in the controlled
comparison.

Run it with:

```powershell
python -m src.analysis.elo_model_selection.dual_k_mass `
  --ledger "files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/forecast_ledger.csv"
```

The diagnostic reports model, K-pair and basho accounting. It does not measure
entrant/retirement inflation, infer the endpoint active-population mean or
select a normalisation policy.

## Run

```powershell
python -m src.analysis.elo_model_selection `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07
```

Outputs are written beneath `files/output/analysis/elo_model_selection/`. The
manifest hashes the History, adopted prior and divisional-`k` configuration.

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
