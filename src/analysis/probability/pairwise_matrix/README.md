# Pairwise probability matrix

Create self-contained HTML heatmaps for every possible pairing in one division
of the current banzuke. The calculation consumes a saved Elo89 artifact set; it
does not replay or alter the rating model.

Run from the repository root:

```powershell
python -m src.analysis.probability.pairwise_matrix
```

Defaults use the latest basho in
`files/output/Historys/1958_01 to 2026_11.zip`, the accepted Elo89 artifacts in
`files/output/analysis/site89_bundle/sources/elo89`, and makuuchi. Override them
with `--history-zip`, `--ratings-root`, `--output-root`, or `--division`.

Two files are written under a dated output directory:

```text
files/output/analysis/probability/pairwise_matrix/YYYY-MM/
    makuuchi_by_rating.html
    makuuchi_by_chii.html
```

Each matrix uses rows as prospective winners and columns as opponents. Cell
colour runs from red below 50%, through neutral at 50%, to green above 50%.
Hovering a cell shows both rikishi, their chii and ratings, the rating
difference, and the row rikishi's modelled win probability.
