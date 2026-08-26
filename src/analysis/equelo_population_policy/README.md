# Equelo normalisation-policy experiments

The package now proceeds in two stages. The first isolates the suspect
post-iteration chii-map recentering while leaving the legacy Elo replay
untouched. Only after that baseline is credible should the second stage compare
population-normalisation policies.

## Stage 1: chii-map recentering

The old recentering adds one common shift to every chii. The isolated sweep
allocates the same total correction mass using `support(chii) ** alpha` for
`alpha = 0, 0.25, 0.5, 1` and records both:

- the difference changes caused by each individual recentering step;
- the difference between the eventual fixed-point maps.

Run it with:

```powershell
python -m src.analysis.equelo_population_policy
```

Artifacts are written beneath
`files/output/analysis/equelo_population_policy/recentering/`.

Render any recentering sweep as a responsive Plotly chart with:

```powershell
python -m src.analysis.equelo_population_policy.chart_recentering `
  --input files/output/analysis/equelo_population_policy/recentering/prior_comparison.csv
```

### Retrospective predictive gate

The `alpha=1` result can be consumed as a candidate prior inside the exact
`q=400` forecast/update contract used by the established Elo model-selection
comparison:

```powershell
python -m src.analysis.equelo_population_policy.predict_candidate `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07
```

The producer pairs east/west values by an unweighted mean, uses the minimum
paired value for the unranked fallback, and writes a separate comparison under
`files/output/analysis/equelo_population_policy/prediction_q400/`. It does not
alter or overwrite the canonical four-model comparison.

## Stage 2: population policy

This package is the reproducible Tranche 1 comparison between otherwise
identical post-1988 Equelo replays:

- `legacy_departure`: the old Expt2 rule, which redistributes a departing
  rikishi's deviation from the active mean over the survivors;
- `equal_share`: a clean-Elo-style rule, which restores one target active mean
  after the current population is formed and again after its bouts;
- `support_0_25`, `support_0_5`, and `support_1`: the same rule, but distribute
  the population-boundary correction using `support(chii) ** alpha`. These
  preserve the mean while deliberately allowing rating differences to change.
  The small post-bout unequal-K correction remains uniform.

Both variants use the same history, bout semantics, divisional K policy,
chii-based fixed-point aggregation and unweighted post-iteration map
recentering. No production rating code is changed.

The provisional population-policy sweep remains available with:

```powershell
python -m src.analysis.equelo_population_policy.run
```

The controlled comparison using the canonical q=400, alpha=1 BKP1 prior is:

```powershell
python -m src.analysis.equelo_population_policy.run_bkp1_population `
  --start 1989 --end 2026 --zip
```

It first holds the canonical prior fixed to isolate the population operator,
then independently solves each policy's fixed point with the same q=400,
alpha=1 map recentering. Two controls isolate the two possible sources of
drift: legacy departure handling plus only a dual-`k` correction, and
whole-population turnover correction without the dual-`k` correction.

Its artifacts are written beneath
`files/output/analysis/equelo_population_policy/bkp1_q400/`:

- `manifest.json` records the parameters;
- `summary.json` and `findings.md` give headline comparisons;
- `iterations.csv` records fixed-point convergence;
- `prior_comparison.csv` compares the solved chii maps;
- `basho_adjustments.csv` records the final replay under each solved map;
- `one_shot_basho_adjustments.csv` holds the controlled replay in which all
  policies use the canonical BKP1 prior.

The one-shot comparison isolates the population rule. The independently solved
fixed points show its feedback through the chii prior. The default ten-point
tolerance is intentionally the same practical scale used by the recovered
historical support-weighting experiments; convergence at that tolerance does
not make a low-support prior trustworthy.

### Exact predictive comparison

Hold canonical P1 fixed and compare no population adjustment, actual Expt2
departure redistribution, and whole-population mean preservation on the exact
B-family forecast domain with:

```powershell
python -m src.analysis.equelo_population_policy.predict_population_policy `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07
```

This also includes the old informed-prior `B_kP` as a benchmark. Outputs are
written beneath
`files/output/analysis/equelo_population_policy/prediction_bkp1_population_q400/`.
