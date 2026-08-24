# Forgetting

This package studies how an Elo process loses sensitivity to its initial
ratings.

The central question is not whether fixed-`K` ratings eventually stop moving.
They do not. It is:

> If two otherwise identical Elo processes start from different rating maps,
> how long does their initialization continue to make a material difference?

That question cannot be answered from one rating trajectory alone. A single
run can show departure from its initial state, continuing fluctuation, and
error relative to known latent skill. It cannot show whether the current state
would have been different under another initialization. Forgetting is therefore
a counterfactual, coupled-process property.

The first true-start toy run has a deliberately narrower role. It establishes
the natural behaviour of fixed-`K` Elo when displayed ratings initially equal
known latent skills. The first measurement of forgetting begins only when a
flat-start process replays the exact same bouts and outcomes.

The programme begins in synthetic worlds where latent skill is known. Later
work may introduce changing skill, entry, retirement, imperfect chii signals,
and finally historical sumo replay. Predictive usefulness is a separate model-
evaluation question and is not part of the definition of forgetting.

## Relationship to earlier work

`src/analysis/toy_elo` established controlled fixed-skill Elo experiments and
exposed the difficulty of describing fixed-`K` ratings as converged. Historical
work under `toy_elo.normative` also developed a useful true-start versus
flat-start comparison and distinguished initial-condition catch-up from
stationarity.

`forgetting` is an intellectual continuation of that work, but it has a
separate experimental contract. Its principal object is the decay of
disagreement between coupled Elo processes, rather than convergence of a
rating path to fixed latent ratings.

`src/analysis/prediction` contains the chronological historical replay and
initialization comparisons most likely to support a later historical phase.

## Package layout

Proposals and research notes belong in:

```text
src/analysis/forgetting/docs/
```

The completed fixed-skill study is documented from three perspectives:

- `docs/Completed Investigation - README.md` is the reading guide;
- `docs/Completed Investigation - Forgetting in a Fixed-Skill Toy World.md`
  is the end-to-end account and conclusion;
- `docs/Completed Investigation - Technical Companion.md` is the
  reconstruction and audit guide.

Future experiment code should use subpackages that identify the experimental
world or responsibility clearly. The output path mirrors the package path
below `forgetting` beneath the project's standard `files/output/analysis`
root.
For example:

```text
code:    src/analysis/forgetting/toy/coupled/
output:  files/output/analysis/forgetting/toy/coupled/
```

Thus the default output folder for code in
`src/analysis/forgetting/x/y` is:

```text
files/output/analysis/forgetting/x/y
```

Individual runs may create timestamped or otherwise uniquely named audit
directories beneath their default output folder.

## Current proposal

The first experiment is specified in:

```text
docs/Proposal 1 - Forgetting in a Fixed-Skill Toy World.md
```

## Implemented first experiment

The first fixed-skill true-start versus flat-start development experiment is
implemented in:

```text
src/analysis/forgetting/toy/
```

Run it from the repository root with:

```powershell
python -m src.analysis.forgetting.toy
```

The command:

1. generates and persists one seeded complete-round-robin history;
2. reloads that exact history;
3. replays it from true latent skills and from flat ratings;
4. measures centred rating-state and all-pair forecast disagreement;
5. writes provisional fractional and absolute forgetting landmarks;
6. writes auditable CSV, JSON, Markdown, and standalone HTML artifacts beneath
   `files/output/analysis/forgetting/toy/`.

The current development command performs both the true-start baseline and the
flat-start replay in one invocation. Conceptually and in future reporting,
these remain separate stages:

```text
Stage 1: true start alone
         describes natural fixed-K fluctuation
         does not measure forgetting

Stage 2: flat start replays the identical persisted history
         coupled disagreement measures initialization memory
```

Useful development overrides include:

```powershell
python -m src.analysis.forgetting.toy --events 500 --seed 1 --persistence-events 25
```

Focused verification is in `tests/test_forgetting_toy.py`.

### Aggregate the true-start baseline

Run independent true-start histories and aggregate each run's truth-relative
errors with:

```powershell
python -m src.analysis.forgetting.toy.true_start_ensemble --runs 800 --events 500 --seed 1
```

This command calculates RMSE separately within every run before reporting the
mean, median, standard deviation, and 5th, 25th, 75th, and 95th percentiles by
event. It does not calculate RMSE from ensemble-mean ratings. The command prints
progress and total wall-clock run time, and writes beneath:

```text
files/output/analysis/forgetting/toy/true_start_ensemble/
```

Instructions for sizing and scheduling large overnight batches are in:

```text
docs/Running overnight true-start batches.md
```

### Run the constant-start ensemble and paired comparison

The toy-model family uses `T0` for the true latent-strength initialization,
`TC` for constant-midpoint initialization, and `TI` for inverted latent-strength
initialization. `TC` starts all ten displayed ratings at zero. Run it with:

```powershell
python -m src.analysis.forgetting.toy.constant_start_ensemble
```

The defaults freeze the canonical protocol at 800 replicates, 500 events,
master seed 1, and a 25-event persistence requirement. Corresponding `T0` and
`TC` runs replay identical histories within every replicate. The command
writes two conceptually separate outputs beneath:

```text
files/output/analysis/forgetting/toy/constant_start_ensemble/
```

`tc_report.html` is Output 1. It describes `TC` alone through its truth-relative
rating-state and probability errors. `paired_report.html` is Output 2. It
compares `T0` with `TC` and reports the decay of initialization
memory and the distribution of persistent forgetting landmarks.

Run the inverted model, `TI`, against `T0` with:

```powershell
python -m src.analysis.forgetting.toy.inverted_start_ensemble
```

Its outputs use the same two-report contract beneath
`files/output/analysis/forgetting/toy/inverted_start_ensemble/`, with
`ti_report.html` for TI alone and `paired_report.html` for T0 versus TI.

### Run reproducible random initializations

The random-start batch tester generates a CLI-selected number of maps and
compares each one separately with `T0`:

```powershell
python -m src.analysis.forgetting.toy.random_start_ensemble --maps 10
```

The defaults retain the canonical 800-replicate, 500-event protocol. For every
map, ten raw ratings are independently drawn from Uniform[-360, 360] using map
master seed 1 and are then centred to population mean zero. The same history
master seed and therefore the same history ensemble is used for every model.
Use `--half-range`, `--map-seed`, or `--history-seed` to change those choices.

The batch is written beneath
`files/output/analysis/forgetting/toy/random_start_ensemble/`. Each random model
(`TR01`, `TR02`, and so on) has its own folder containing Output 1 and its paired
`T0` comparison. The batch root contains the generated maps, a model summary,
an HTML summary report, and a manifest that is updated after every completed
model. Console progress identifies both the current model and the number of
completed random models.

### Build the model-results table

Extract the agreed descriptive result for every canonical 800-replicate,
500-event, seed-1 model and the 3200-replicate, 2000-event overnight T0 run
with:

```powershell
python -m src.analysis.forgetting.toy.results_table
```

The command discovers the latest matching run for each requested model and
protocol and writes one ordinary CSV row per model-run to:

```text
files/output/analysis/forgetting/toy/results_table/results_seed1.csv
```

The table records replicate and event counts before the eight result columns:
TRMSE settled level, settling event and 5th--95th percentile width; the
corresponding three PRMSE values; and cancellation RMSE at the final included
replicate together with that replicate count. By default, event levels and
widths are terminal-100 medians and settling requires 25 consecutive points
within 5%. Use repeated `--protocol REPLICATESxEVENTS` options to select other
run sizes.
