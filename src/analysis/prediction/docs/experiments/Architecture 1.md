# Architecture 1: Basic Elo Predictive Behaviour

## Status

Accepted design for `Proposal 1.md`.

## Purpose

Implement Proposal 1 as a pipeline of explicit transformations over the
existing `History` domain model. The implementation owns Basic Elo prediction
and evaluation. It does not depend on Expt1, Expt3, clean Elo or Equelo.

Those earlier analyses are evidence about possible data and modelling traps,
not runtime dependencies.

## Pipeline

```text
History
  -> RatedBoutSelection
  -> ForecastLedger
  -> ScoredForecasts
  -> BashoLossSeries
  -> RollingLossSeries + CumulativeLossSeries
  -> PointwiseUncertainty
  -> PersistedTables
  -> ResponsivePlotlyChart
```

## Source package

```text
src/analysis/prediction/
  __main__.py
  definition.py
  bouts.py
  basic_elo.py
  experiment.py
  scoring.py
  series.py
  uncertainty.py
  output.py
  charts.py
  run.py
```

## Experiment definition

Proposal 1 has one immutable definition:

```text
epoch = 1989/01
q = 400
k = 35
b = 1500
reference probability = 0.5
rolling windows = 6, 12, 24 basho
bootstrap interval = pointwise 95%
```

The canonical run also carries an explicit inclusive final basho and an
explicit History source. Model parameters are not CLI options.

## Rated bout selection

`bouts.py` transforms `History` into an ordered tuple of rated bouts and a
selection summary.

An eligible bout has the outcome pair `{W, L}`. The transformation ignores the
decision field, so a missing kimarite does not remove an observed result.
`FS/FP` and `DRAW/DRAW` are counted but excluded.

Chronology is ordered by `Date`, `Day` and canonical `Pair`. The bout identity
is `(Date, Day, Pair)`. The first member of `Pair` is competitor A. Every
recorded probability means `P(A wins)`.

The transformation trusts the structural validity of `History`. It does not
validate torikumi, banzuke membership, dictionary domains or impossible
internal states.

Neither `Chii` nor shikona enters the rated-bout model. `RikId` and `Pair` own
identity. Human-readable chii strings and shikona may be added by a presentation
consumer but cannot drive computation.

## Basic Elo producer

`basic_elo.py` owns a persistent registry:

```text
RikId -> rating
RikId -> earlier rated-bout count
```

A previously unseen `RikId` receives 1500 immediately before its first rated
bout. Ratings remain in the registry for the full experiment. Banzuke absence,
inactivity, retirement and reappearance are not Basic Elo state transitions.

Prediction receives a contest without its outcome. Update receives the
prediction and the subsequently revealed binary outcome. This type boundary
expresses the chronological contract directly.

## Forecast ledger

`experiment.py` performs the single chronological pass and produces immutable
forecast rows containing bout identity, competitor IDs, pre-bout ratings,
prior experience counts, probability, observed outcome, rating delta and
post-bout ratings.

The forecast ledger is the boundary between rating production and evaluation.
No evaluator may reconstruct earlier predictions from later ratings.

## Evaluation

`scoring.py` adds per-bout log loss, Brier loss, the corresponding 50%
reference losses and paired loss differences.

`series.py` derives one loss row per basho, complete trailing 6-, 12- and
24-basho windows, and a cumulative series from 1989/01.

`uncertainty.py` resamples complete basho within each rolling window using a
fixed seed and writes pointwise 95% intervals for the paired mean loss
difference.

The calculation does not declare a warm-up boundary. Crossings of zero and
their sensitivity to window length are reportable observations.

## Persistence and rendering

The canonical output tree is:

```text
files/output/prediction/proposal_1/<range>/
  manifest.json
  forecast_ledger.csv
  basho_loss.csv
  rolling_loss.csv
  cumulative_loss.csv
  uncertainty.csv
  predictive_behaviour.html
  report.md
```

CSV and JSON outputs own the calculated evidence. `charts.py` renders those
models without introducing new analysis. Plotly HTML uses the CDN bundle and
responsive configuration.

## Application boundary

The reusable entry point consumes an already constructed `History`. The CLI
owns loading an explicit History zip, recording its digest, choosing the
inclusive final basho and writing outputs.

The live store may support development runs but is not the source of a
canonical reproducible report.
