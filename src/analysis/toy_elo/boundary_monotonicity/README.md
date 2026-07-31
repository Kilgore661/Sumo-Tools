# Boundary Monotonicity

This package tests a possible explanation for the lower-makuuchi Elo upturn
observed by `analysis.clean_elo`.

The controlled question is:

> If latent skill declines strictly through a fixed top division, can an
> evidence-shaped Makuuchi-Juryo comparison graph nevertheless make recovered
> Elo ratings turn upward near the lower boundary?

The experiment runs two scenarios:

1. `evidence_bridge` uses the Makuuchi-Juryo bridge profile produced by
   `toy_elo.matchup`.
2. `rank_local_control` uses the same fixed skills and rank-local within-
   division scheduler but removes every interdivision bridge bout.

Both scenarios have a fixed population, fixed monotonically declining latent
skills, constant k, and outcomes sampled from the same logistic family used by
the Elo updater.

## Boundary groups

The default 42-player top division is reduced to seven two-player groups at
its lower boundary. These are BP4-like no-side groups ordered from
`top_bottom_7` through `top_bottom_1`. They are boundary coordinates rather
than claims that the fixed toy positions are literally M12 through M18.

For each scenario the package reports:

- final ensemble-mean rating and hidden skill by boundary group;
- approximate 95% intervals for each group mean;
- a non-increasing isotonic fit;
- the endpoint reversal from the first to last boundary group;
- the largest later-minus-earlier reversal anywhere in the seven groups;
- bootstrap intervals for those ensemble statistics;
- the proportion of independent simulated histories with any reversal;
- the proportion whose endpoint is at least as flat as the historical
  boundary endpoint;
- the proportion whose maximum local reversal is at least as large as the
  historical boundary reversal.

The historical targets come from the 1989+ `clean_elo.boundary_rating_probe`.
Across `top_bottom_7` through `top_bottom_1`, it found:

```text
historical endpoint difference = -9.31
historical maximum reversal    = +14.32
historical Elo q               = 900
```

Both are scaled by `toy q / historical q`. With toy q 400, the defaults are:

```text
scaled endpoint target = -4.14
scaled maximum target  = +6.36
```

Unlike the earlier literal M12-M18 comparison, these targets use the same
paired boundary-distance coordinate as the toy experiment.

## Run

First generate the empirical bridge profile if it is not already present:

```powershell
python -m src.analysis.toy_elo.matchup
```

Then run:

```powershell
python -m src.analysis.toy_elo.boundary_monotonicity
```

For a quick smoke run:

```powershell
python -m src.analysis.toy_elo.boundary_monotonicity `
  --events 5 --runs 10 --bootstrap-samples 100
```

Outputs are written to a UTC timestamped directory beneath:

```text
files/output/analysis/toy_elo/boundary_monotonicity
```

The files are:

- `scenario_summary.csv`;
- `boundary_groups.csv`;
- `run_reversals.csv`;
- `profile.csv`;
- `manifest.json`.

## First 500-event result

The first default-sized run used:

```text
profile period       = 1989/01 through 2026/07
events               = 500
independent runs     = 100
days per event       = 15
bootstrap samples    = 5,000
seed                 = 1
```

Its output is:

```text
files/output/analysis/toy_elo/boundary_monotonicity/
  2026-07-29_13-47-38/
```

The evidence scheduler produced a mean 9.6355 bridge bouts per run-event. It
processed 25,960,587 bouts, compared with 26,250,000 in the fully paired
rank-local control.

The hidden skill difference from `top_bottom_7` to `top_bottom_1` is
\(-480\). The recovered ensemble endpoint differences were:

| Scenario | Endpoint difference | Hidden gap recovered |
|---|---:|---:|
| Rank-local control | -465.44 | 97.0% |
| Evidence bridge | -312.39 | 65.1% |
| Historical boundary endpoint, scaled by q | -4.14 | almost flat |

The rank-local control therefore recovered almost all of the intended
boundary gradient. The evidence bridge compressed that gradient by about 153
points relative to the control, but did not reverse it.

Every successive evidence-bridge group difference remained negative:

```text
-52.4, -50.4, -59.4, -47.1, -48.3, -54.7
```

The ensemble curve was completely non-increasing, so its isotonic fit made no
adjustment. Its bootstrap 95% interval for the endpoint difference was
approximately:

```text
-315.87 to -308.98
```

Of the 100 independent evidence-bridge histories:

- 98 were completely monotonic across all seven groups;
- two contained a small local reversal;
- those maximum reversals were 9.62 and 3.66 points;
- none had an endpoint as flat as the -4.14 historical target;
- one reached the +6.36 scaled historical maximum-reversal target.

All 100 rank-local control histories had no local reversal.

The original run manifest and `scenario_summary.csv` used the then-provisional
literal M12-M18 target of +60.52. Those target-rate columns are superseded by
the boundary-aligned rescoring above; the simulated ratings and ensemble
statistics themselves are unchanged.

The result is:

> Evidence-shaped interdivisional scheduling produces substantial compression
> of lower-boundary Elo differences, but its expected boundary gradient
> remains far steeper than the nearly flat historical boundary-relative
> curve.

This rejects only the simple schedule-only explanation represented by this
model. It does not rule out comparison-graph effects involving mechanisms
that the scheduler omits, particularly record-dependent opponent selection,
rank movement, population selection, and changing ability.

The result is conditional on the 500-event endpoint. The experiment has not
yet demonstrated that the boundary statistics are stable across event counts.

## Interpretation

The ensemble mean asks whether the simplified scheduler causes a systematic
boundary distortion. The per-run rates ask how often stochastic Elo histories
produce a reversal even when the expected curve remains monotonic.

If the evidence scenario exhibits substantially more or larger reversals than
the rank-local control, the comparison graph supplies a possible mechanism
for the historical pattern. If neither scenario reproduces the historical
effect, the next explanations include population selection, changing skills,
record-dependent torikumi, banzuke structure, and differences between what
chii and Elo summarize.

The controls do not have exactly the same bout count. With an odd number of
bridge bouts on a day, the evidence scheduler leaves one otherwise unpaired
player in each division; the no-bridge control can pair both even-sized
divisions completely. `scenario_summary.csv` therefore reports total and
mean bout counts explicitly. The comparison diagnoses the complete scheduling
mechanisms rather than isolating bridge connectivity while holding every
player's degree fixed.

This is not a historical sumo simulator. Players do not move between ranks or
divisions, and the scheduler omits records, days, absences, promotion,
demotion, stable constraints, and human torikumi judgement.
