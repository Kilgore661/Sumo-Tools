# Prediction Analysis

`analysis/prediction` owns the chronological framework for testing the
predictive behaviour of Elo-family rating producers. It begins with Basic Elo
and deliberately does not depend on Equelo, `equelo/expt1`, `expt3` or
`clean_elo`.

The first experiment asks what can meaningfully be said about the pre-bout
probabilities produced by Basic Elo with q=400 and constant k=35. It is a
predict-then-update experiment, not an attempt to estimate rikishi ability from
chii or select a preferred Elo variant.

## Research documents

- [`docs/A Defence of Elo for Sumo.md`](docs/A%20Defence%20of%20Elo%20for%20Sumo.md)
  is the working structure for the eventual reader-facing argument.
- [`docs/experiments/Aims.md`](docs/experiments/Aims.md) records the wider
  research programme.
- [`docs/experiments/Proposal 1.md`](docs/experiments/Proposal%201.md)
  specifies the fixed first experiment.
- [`docs/experiments/Architecture 1.md`](docs/experiments/Architecture%201.md)
  records its implemented architecture and data boundaries.
- [`docs/experiments/Proposal 2.md`](docs/experiments/Proposal%202.md)
  specifies the sekitori-only evaluation of the unchanged Proposal 1 forecasts.
- [`docs/experiments/Proposal 2b.md`](docs/experiments/Proposal%202b.md)
  specifies the complementary sub-sekitori evaluation.
- [`docs/experiments/Proposal 3.md`](docs/experiments/Proposal%203.md)
  specifies the retrospective trailing-10 Chii initialization diagnostic.
- [`docs/experiments/Proposal 4.md`](docs/experiments/Proposal%204.md)
  specifies the proof-of-concept randomized Chii-prior placebo experiment.
- [`docs/experiments/Proposal 5.md`](docs/experiments/Proposal%205.md)
  specifies the deterministic division-only initialization experiment.
- [`docs/experiments/Proposal 6.md`](docs/experiments/Proposal%206.md)
  specifies the fair-coin bookmaker null for the probability-staked betting
  interpretation.
- [`docs/experiments/Findings.md`](docs/experiments/Findings.md) consolidates
  the empirical findings, limitations and unresolved questions from the
  completed experiments.
- [`docs/experiments/Proposed next steps.md`](docs/experiments/Proposed%20next%20steps.md)
  records the proposed follow-on sequence: sekitori-only evaluation first,
  followed by chii-based initialization, a randomized-prior placebo,
  deterministic division-only initialization, constant update-rate
  sensitivity, the 1958–1988 sekitori regime, and chii-dependent update rates.

Proposal 1 remains the baseline when later experiments are added. Follow-on
ideas do not retrospectively alter its definition.

## Proposal 1 definition

```text
epoch = 1989/01
q = 400
k = 35
initial rating = equal 1500
eligible result = W/L, irrespective of kimarite
excluded result = FS/FP or DRAW/DRAW
reference probability = 50%
rolling windows = 6, 12 and 24 basho
uncertainty = pointwise 95% basho-block bootstrap
```

The equality of the initial ratings is an externally imposed initial
condition. The common value 1500 is arbitrary because translating all ratings
by the same constant changes no predicted probability.

Ratings are keyed by stable `RikId` and persist for the complete pass. Banzuke
absence, retirement and reappearance do not reset them. Chii and shikona do not
reach the Proposal 1 prediction producer; chii strings and shikona are display
values rather than computational identities.

Every forecast is recorded before its bout result updates the ratings. The
immutable forecast ledger is the boundary between prediction production and
evaluation, so later ratings cannot be used to reconstruct earlier forecasts.

## Implementation

The package is organized as explicit transformations:

```text
History
  -> eligible chronological bouts
  -> Basic Elo pre-bout forecasts
  -> scored forecast ledger
  -> basho, rolling and cumulative loss series
  -> pointwise uncertainty
  -> CSV, JSON, Markdown and responsive Plotly HTML
```

The principal reusable entry point is:

```python
run_proposal_1(
    history: History,
    definition: Proposal1Definition,
) -> Proposal1Result
```

The chart renderer writes plain HTML using Plotly's CDN bundle and responsive
configuration. It does not require the Plotly Python package. An internet
connection is required when opening the HTML so that the browser can load the
CDN bundle.

## Reproduce the canonical run

Supply an explicit annotated History zip and inclusive final basho:

```powershell
python -m src.analysis.prediction `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --end 2026/07
```

Model parameters are intentionally not command-line options for Proposal 1.
The command records the source path and SHA-256 digest in the manifest.

Outputs are written beneath:

```text
files/output/prediction/proposal_1/proposal_1_1989_01_to_<end>/
  manifest.json
  forecast_ledger.csv
  basho_loss.csv
  rolling_loss.csv
  cumulative_loss.csv
  uncertainty.csv
  predictive_behaviour.html
  report.md
```

Generated bulk data is not source code and should not be committed unless the
repository policy changes.

## Reproduce the sekitori-only evaluation

```powershell
python -m src.analysis.prediction.sekitori_cli `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --end 2026/07
```

This command runs the same all-bout rating pass, then evaluates only forecasts
for which both participants are sekitori on the basho banzuke. All other bouts
still update ratings. Outputs are written beneath:

```text
files/output/prediction/sekitori_only/sekitori_only_1989_01_to_<end>/
```

The 1989/01–2026/07 run evaluates 106,905 two-sekitori bouts. Mean log loss is
0.674671, a 2.7% reduction from the 50% reference and a larger improvement than
the 1.5% all-bout reduction. Mean Brier loss is 0.241227, a 3.5% reduction from
the reference. The first complete rolling windows are below the neutral
forecast; their pointwise intervals first lie wholly below zero between
1990/09 and 1993/09, depending on window length.

The complementary run is:

```powershell
python -m src.analysis.prediction.sub_sekitori_cli `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --end 2026/07
```

It evaluates 469,959 two-sub-sekitori bouts. Mean log loss is 0.684398, a 1.3%
reduction from the 50% reference; mean Brier loss is 0.245379, a 1.8%
reduction. This population reproduces the long early underperformance of the
all-bout aggregate, first moving below neutral during 1999–2002 depending on
window length. Unlike sekitori performance, it continues improving after 2015
and reaches its best rolling values around 2023–2025.

## Reproduce the Chii-initialization diagnostic

```powershell
python -m src.analysis.prediction.chii_initialisation_cli `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --end 2026/07
```

The first pass retains the last ten normalized start-of-basho ratings for each
exact Chii. Their unsmoothed means, with ordered interpolation for missing
Chii, initialize the second pass. The authoritative audit table is
`chii_prior.csv`, keyed by chii ordinal; `chii_prior_observations.csv` contains
the retained observations behind every mean.

The retrospective prior slightly improves all-bout and sub-sekitori whole-epoch
loss, but worsens sekitori loss. It makes several short-window estimates
favourable much earlier without removing the long period before improvement is
persistent. Because the prior is derived from later outcomes, this is an oracle
diagnostic rather than an out-of-sample model.

## Reproduce the randomized-prior placebo

First run Proposal 3 to produce its canonical prior table, then run:

```powershell
python -m src.analysis.prediction.randomised_prior_cli `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --prior-csv "files/output/prediction/chii_initialisation/chii_initialisation_1989_01_to_2026_07/chii_prior.csv" `
  --end 2026/07
```

This applies the genuine mapping, 100 global fixed-seed permutations, and 100
within-division fixed-seed permutations of exactly the same prior values.
Equal-1500 initialization is retained as a deterministic control. During the
202 complete Elo passes the command prints the pass count, percentage, elapsed
time and ETA. It prints the total duration on completion and writes it to
`execution_time.txt` beside the other artifacts.

## Reproduce the deterministic division-only diagnostic

After Proposal 4 has produced its refined envelope, run:

```powershell
python -m src.analysis.prediction.division_initialisation_cli `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --prior-csv "files/output/prediction/chii_initialisation/chii_initialisation_1989_01_to_2026_07/chii_prior.csv" `
  --placebo-envelope-csv "files/output/prediction/randomised_chii_prior/randomised_chii_prior_1989_01_to_2026_07/cumulative_envelope.csv" `
  --end 2026/07
```

The division-only prior is the unweighted mean of all completed Proposal 3
Chii values in each actual division. The command recomputes equal, genuine
Chii and division-only passes, then compares them with Proposal 4's
within-division randomized envelope.

Over 1989/01–2026/07, division-only initialization lowers all-bout log loss
from 0.682608 to 0.677888 and sub-sekitori log loss from 0.684398 to 0.678299.
It outperforms genuine exact-Chii initialization from the first declared
horizon and lies below the complete Proposal 4 within-division ordered band at
every declared all-bout and sub-sekitori horizon. Equal initialization retains
the lowest complete-epoch sekitori log loss, ahead of division-only by
0.001057. The division values remain retrospective oracle inputs rather than
prospectively available constants.

## Run the fair-coin bookmaker null

The declared run retains Proposal 1's equal initialization and compares its
historical probability-staked profit with 2,000 complete histories in which
every bout result is an independent 50–50 draw:

```powershell
python -m src.analysis.prediction.fair_coin_null_cli `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --end 2026/07
```

For every fair-coin history the command rebuilds Elo from the simulated
results. It prints completed passes, elapsed time and ETA, then records the
total execution time. `--replicates` and `--seed` exist to support small test
runs and exact reproduction; the declared design uses their defaults of 2,000
and 20260807.

Over 1989/01–2026/07, the all-bout strategy stakes a mean £8.6096 and earns a
mean £1.2229 per represented basho, a 14.20% return on stake. The 2,000
fair-coin histories have a 95% range of -£0.0231 to £0.0233 for the same
complete-epoch mean statistic; none reaches the historical result. The
add-one one-sided Monte Carlo value is therefore 1/2,001. Sekitori and
sub-sekitori evaluations also give the same qualitative conclusion.

## Proposal 1 canonical result

The represented 1989/01–2026/07 run contains 579,426 rated W/L bouts over 224
basho. Whole-epoch Basic Elo log loss is 0.682608 against 0.693147 for the 50%
reference, a reduction of about 1.5%. Its Brier loss is 0.244614 against 0.25,
a reduction of about 2.2%.

Under the externally imposed equal-rating initial condition, the results are
consistent with Basic Elo requiring roughly a decade before its rolling point
estimates outperform the neutral predictor. Pointwise intervals provide
stronger evidence after roughly 12 to 13 years. These are descriptive
landmarks in overlapping curves, not a formally identified or universal Elo
warm-up duration.

The 50% comparator is substantively meaningful because torikumi may be formed
to produce competitive contests. Proposal 1 evaluates predictions for the
bouts actually arranged; it does not attempt to infer the torikumi formation
policy.

## Verification

Focused tests cover eligibility, blank-kimarite inclusion, chronology,
predict-before-update ordering, persistent ratings, future-result isolation,
translation invariance, bout-weighted series, deterministic uncertainty and
date-axis ordering:

```powershell
python -m pytest -q tests/test_prediction_proposal_1.py
```
