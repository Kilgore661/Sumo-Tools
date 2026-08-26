# BKP1 q=400 entrant-prior producer

This package is the maintained candidate copy of the fixed-point prior
producer. It leaves the legacy Equelo/Expt2 implementation and its `q=900`
artifacts untouched.

The model contract fixes:

- `q = 400`;
- support-proportional (`alpha = 1`) post-iteration recentering;
- the declared divisional-`k` configuration;
- the legacy departure redistribution during this controlled stage; and
- annotation-only chii collapse over the 1989-onward complete record.

There is deliberately no `--q` or `--alpha` option. Run it with:

```powershell
python -m src.analysis.equelo_bkp1 --start 1989 --end 2026 --zip
```

Artifacts are written under `files/output/analysis/equelo_bkp1/`.

Run its retrospective `q=400` predictive gate with:

```powershell
python -m src.analysis.equelo_population_policy.predict_candidate `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07 `
  --candidate-prior files/output/analysis/equelo_bkp1/prior.csv `
  --output files/output/analysis/equelo_bkp1/prediction_q400
```
