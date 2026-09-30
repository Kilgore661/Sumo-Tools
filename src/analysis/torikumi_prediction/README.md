# Torikumi Prediction

This package implements the first, descriptive phase of the proposal in
[`docs/Proposal.md`](docs/Proposal.md). It extracts one directed observation
for each ranked endpoint of every scheduled regular bout and writes empirical
opponent-class distributions for all divisions.

Run the complete available History:

```text
python -m src.analysis.torikumi_prediction
```

Select a range or source explicitly:

```text
python -m src.analysis.torikumi_prediction \
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" \
  --start 1989/01 \
  --end 2026/09
```

Each run creates an immutable timestamped directory beneath
`files/output/analysis/torikumi_prediction` containing the observations, four
aggregate CSVs, diagnostics and a manifest.
