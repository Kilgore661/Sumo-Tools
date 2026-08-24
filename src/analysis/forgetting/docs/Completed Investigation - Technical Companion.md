# Completed Investigation: Technical Companion

## Purpose

This companion is the reconstruction guide for the fixed-skill forgetting
study. The [Completed Investigation](Completed%20Investigation%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md)
contains the argument and conclusion. The [Proposal](Proposal%201%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md)
contains the design history and claim boundary. This document identifies the
code, commands, run artifacts, schemas, and extraction rules needed to inspect
or reproduce the work.

Paths are relative to the repository root unless stated otherwise.

## 1. Code map

All implementation code is under:

```text
src/analysis/forgetting/toy/
```

| File | Responsibility |
|---|---|
| `model.py` | Declares the population, latent skills, `Q`, `K`, and standard initial maps. |
| `elo.py` | Expected-score calculation and replay of a persisted history from arbitrary initial ratings. |
| `history.py` | Round-robin pair construction, seeded schedule and outcome generation, CSV persistence, reload, and hashing. |
| `metrics.py` | Centred state distance, all-pair forecast distance, truth-relative metrics, persistent landmarks, and integrated disagreement. |
| `experiment.py` | Original single-history development experiment. |
| `outputs.py` | Development CSV, manifest, Markdown, and Plotly HTML outputs. |
| `true_start_ensemble.py` | Standalone replicated `T0` baseline and signed-error cancellation diagnostic. |
| `constant_start_ensemble.py` | General paired ensemble engine for `TC`, `TI`, and arbitrary named initial maps. |
| `inverted_start_ensemble.py` | Thin `TI` command-line entry point. |
| `random_start_ensemble.py` | Reproducible `TR01`--`TRNN` map generator and batch orchestrator. |
| `results_table.py` | Discovers selected model-runs and creates the rectangular results CSV. |
| `report_identity.py` | Adds manifest-derived run identity blocks to HTML reports. |

Automated tests are in:

```text
tests/test_forgetting_toy.py
```

The test suite covers deterministic generation and replay, common paired
outcomes, translation invariance, zero-sum preservation, metric behaviour,
output contracts, ensemble aggregation, TC/TI initialization, random-map
reproducibility, batch progress, and results-table extraction.

## 2. Declared world

The default `ToyWorld` has:

```text
player_count = 10
latent_gap = 40
latent_skills = 180, 140, 100, 60, 20, -20, -60, -100, -140, -180
Q = 400
K = 5
pairs_per_event = 45
bouts_per_player_per_event = 9
```

The latent probability that player `i` beats player `j` is:

\[
p_{ij}=\frac{1}{1+10^{(S_j-S_i)/Q}}.
\]

The displayed-rating updater uses the same functional form with current
ratings and applies the zero-sum update with `K=5`.

## 3. Seed and coupling contract

The canonical history master seed is 1. The ensemble runner creates a local
`random.Random(1)` instance and derives one recorded 64-bit seed per replicate.
Each replicate seed generates a schedule seed and an outcome seed. The complete
ordered history is generated independently of initialization.

Within a paired comparison, `T0` and the alternative replay the exact same
history object. Their schedules and Boolean outcomes can therefore be compared
row for row. Between replicates, histories are independently seeded.

The random-initialization batch has a separate map master seed, also 1 in the
completed run. Each map receives a derived 64-bit map seed. Raw player ratings
are drawn independently from Uniform[-360, 360], then translated to mean zero.
Every random map is tested against the same history master seed 1. Different
map seeds do not constitute fresh history banks.

## 4. Run inventory

### 4.1 Standalone T0 baseline

Canonical-size T0:

```text
files/output/analysis/forgetting/toy/true_start_ensemble/
    20260822_132803_development_seed1/
```

Configuration: 800 replicates, 500 events, seed 1. The historical manifest
labels this run `development`, although it supplies the canonical-size T0 row.
The report identity block and results-table support columns disambiguate it.

Larger overnight T0:

```text
files/output/analysis/forgetting/toy/true_start_ensemble/
    20260822_230000_development_seed1/
```

Configuration: 3,200 replicates, 2,000 events, seed 1. Total simulated bouts:
288,000,000. Recorded runtime: approximately 18,309 seconds.

### 4.2 TC and TI

TC:

```text
files/output/analysis/forgetting/toy/constant_start_ensemble/
    20260822_154839_canonical_seed1/
```

TI:

```text
files/output/analysis/forgetting/toy/inverted_start_ensemble/
    20260822_201355_canonical_seed1/
```

Both contain 800 paired replicates, 500 events, history master seed 1, and a
25-event persistence rule.

### 4.3 Random batch

Batch root:

```text
files/output/analysis/forgetting/toy/random_start_ensemble/
    20260822_204617_batch_seed1/
```

The batch root contains:

```text
manifest.json
random_initialisations.csv
model_summary.csv
summary_report.md
summary_report.html
```

Each `TRNN` directory contains one timestamped canonical child run. For
example:

```text
TR01/20260822_204617_canonical_seed1/
TR02/20260822_205312_canonical_seed1/
...
TR10/20260822_214817_canonical_seed1/
```

Every child is a complete standalone-model and paired-`T0` experiment, not
merely a row in the batch summary.

### 4.4 Results table

Current table:

```text
files/output/analysis/forgetting/toy/results_table/results_seed1.csv
```

It has 14 rows: T0 at 800 by 500, T0 at 3,200 by 2,000, TC, TI, and ten random
models at 800 by 500. The earlier
`results_800x500_seed1.csv` is superseded.

## 5. Commands

Run the canonical-size T0 baseline:

```powershell
python -m src.analysis.forgetting.toy.true_start_ensemble --runs 800 --events 500 --seed 1
```

Run TC with canonical defaults:

```powershell
python -m src.analysis.forgetting.toy.constant_start_ensemble
```

Run TI with canonical defaults:

```powershell
python -m src.analysis.forgetting.toy.inverted_start_ensemble
```

Run ten reproducible random initializations:

```powershell
python -m src.analysis.forgetting.toy.random_start_ensemble --maps 10
```

Generate the current results table:

```powershell
python -m src.analysis.forgetting.toy.results_table
```

Select protocols explicitly if required:

```powershell
python -m src.analysis.forgetting.toy.results_table --protocol 800x500 --protocol 3200x2000
```

Run the tests:

```powershell
python -m pytest -q
```

Instructions for scheduling large T0 runs are retained in [Running overnight
true-start batches](Running%20overnight%20true-start%20batches.md).

## 6. Per-run artifacts

Standalone T0 directories contain:

```text
manifest.json
replicate_seeds.csv
replicate_event_metrics.csv
event_summary.csv
final_player_mean_errors.csv
final_mean_error_progress.csv
report.md
report.html
```

Alternative-model directories contain:

```text
manifest.json
replicate_seeds.csv
replicate_event_metrics.csv
event_summary.csv
replicate_forgetting_landmarks.csv
forgetting_summary.csv
<model>_final_player_mean_errors.csv
<model>_final_mean_error_progress.csv
<model>_report.md
<model>_report.html
paired_report.md
paired_report.html
```

The standalone report is Output 1 and describes that model relative to latent
skill. The paired report is Output 2 and measures initialization forgetting
relative to `T0`.

Every current HTML report begins with a manifest-derived run identity block.
It shows the experiment, filename, run ID, role/status, timestamps, world,
ensemble configuration, and initialization vectors. Existing reports were
retrofitted; future report generation adds the block automatically.

## 7. Metric columns

### 7.1 Standalone T0 event summary

Important `event_summary.csv` columns include:

```text
event
state_mean, state_median, state_standard_deviation
state_q05, state_q25, state_q75, state_q95
probability_mean, probability_median, probability_standard_deviation
probability_q05, probability_q25, probability_q75, probability_q95
adjacent_inversion_run_fraction
all_pair_inversion_mean
```

Truth-relative RMSE is calculated within each replicate before aggregation.
Calculating RMSE from the ensemble-mean rating vector would incorrectly permit
signed errors from different histories to cancel.

### 7.2 Alternative event summary

The historical internal field prefix for the alternative is `t_prime`, even
when the public model name is TC, TI, or TRNN. Important column families are:

```text
true_state_mean, true_probability_mean
t_prime_state_mean/median/q05/q95
t_prime_probability_mean/median/q05/q95
paired_state_mean/median/q05/q95
paired_probability_mean/median/q05/q95
paired_fraction_mean/median/q05/q95
```

The public reports and new filenames use T0/TC/TI/TRNN terminology. The first
historical TC canonical directory predates that rename and contains files such
as `t_prime_report.html`; its manifest and report identity block establish that
it is TC.

### 7.3 Forgetting landmarks

`replicate_forgetting_landmarks.csv` contains one row per replicate and target.
Important columns are:

```text
replicate, seed
kind, target, tolerance
first_event, first_global_bout
recrossed, later_fraction_below, remaining_events
right_censored
```

`forgetting_summary.csv` aggregates those rows and reports replicate count,
observed/right-censored counts, observed fraction, mean/median/5th/95th first
events, and recrossed fraction.

For a first event `e` and persistence 25, the code has observed events `e`
through `e+24` at or below the target. Thus event 87 is the assigned first
qualifying event but cannot be confirmed until event 111.

## 8. Results-table extraction contract

The CSV columns are:

```text
model
replicates
events
trmse_level
trmse_settling_event
trmse_spread_q05_q95
prmse_level
prmse_settling_event
prmse_spread_q05_q95
cancel_level
cancel_replicates
```

For TRMSE and PRMSE:

1. Select the final 100 event rows.
2. Set `level` to the median of the ensemble-mean metric over that tail.
3. At every event calculate `q95 - q05`.
4. Set `spread` to the median width over the final 100 events.
5. Set `settling_event` to the first event beginning 25 consecutive rows in
   which both the mean and width are within 5% of their terminal values.
6. Return an empty settling coordinate if no qualifying window exists.

This rule deliberately includes stabilization of the percentile width. It can
therefore return a later event than visual inspection of the mean curve alone.
It is a deterministic chart-summary rule, not a definition of forgetting.

For cancellation:

1. Read the final row of `<model>_final_mean_error_progress.csv`.
2. Record its `mean_rating_error_rmse` as `cancel_level`.
3. Record its `replicate_count` as `cancel_replicates`.

No tail median, tolerance, persistence window, or cancellation settling time
is used.

By default, `results_table.py` discovers the latest seed-1 run for each model
under protocols 800 by 500 and 3,200 by 2,000. Only T0 currently exists under
the larger protocol. Repeated `--protocol` options override the default
protocol list.

## 9. Key numerical reconstruction checks

The following values are useful for checking that the intended artifacts have
been loaded:

```text
T0 800x500:
  TRMSE level/event/width = 19.415781 / 23 / 15.067152
  PRMSE level/event/width = 0.0345492 / 22 / 0.0270172
  cancellation endpoint  = 1.136736 at 800

T0 3200x2000:
  TRMSE level/event/width = 19.379420 / 23 / 15.221557
  PRMSE level/event/width = 0.0344490 / 21 / 0.0272248
  cancellation endpoint  = 0.783108 at 3200

TC strict paired tolerance:
  median first event = 70
  latest first event = 74

TI strict paired tolerance:
  median first event = 80
  latest first event = 87

Random strict paired tolerance:
  median first-event range = 73--81
  latest first-event range = 76--87
```

At event 500, the model-summary rows for random starts report paired state
means on the order of `1e-8` and paired probability means on the order of
`1e-11`. If values are materially larger, the wrong event or output family has
probably been selected.

## 10. Interpretation safeguards

The following distinctions should be maintained in any future use:

- A standalone truth-relative settling event is not a forgetting time.
- A paired tolerance first event is assigned to the start of its persistence
  window, not the event at which the window becomes knowable.
- Equality of terminal aggregate summaries corroborates forgetting but does
  not establish it without paired history-by-history distances.
- Non-zero TRMSE after forgetting is expected with fixed `K`.
- Cancellation is an ensemble-support diagnostic and need not be monotone.
- The larger T0 run contains no alternative initialization and therefore adds
  no direct paired forgetting evidence.
- `Canonical` means the standard reproducible configuration, not a predictive
  holdout or formal proof.
- Ten random maps broaden empirical coverage but do not establish a theorem
  for arbitrary initial maps.

## 11. Minimal reconstruction workflow

To review the completed study without rerunning the expensive simulations:

1. Open `results_seed1.csv` and verify that it contains 14 rows.
2. Open the T0, TC, TI, and random-batch HTML reports; check the run identity
   block before interpreting a chart.
3. Use each alternative's `forgetting_summary.csv` for medians and quantiles.
4. Use `replicate_forgetting_landmarks.csv` when maxima, censoring, or
   replicate-level assertions are required.
5. Use `event_summary.csv` for selected-event paired distances and standalone
   levels or widths.
6. Use the final signed-error progress row for cancellation endpoints.
7. Run the automated tests before changing code or regenerating reports.

This workflow preserves the distinction between the concise results table and
the paired evidence on which the forgetting conclusion rests.

