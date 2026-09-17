# Per-chii rating drift: findings and verification

Completed 12 September 2026 against the saved production Elo89 run covering
January 1989–July 2026: 224 represented basho and 160,185 rikishi/basho
observations. The matching annotated History ZIP supplies metadata and
validates the saved run; the model was not replayed.

## Findings for the Elo89 account

Preserving the population mean does not produce stationary ratings at every
chii. There are substantial historical movements, and several upper ranks
rise early in the run and fall later. A single slope can obscure that shape.

For example, post-basho M1 period means are approximately 2,293 in 1989–1993,
2,512 in 2004–2008 and 2,452 in the partial 2024–2026 period. Its full-history
slope is +42.2 points per decade, compared with −8.2 from January 2000 onward.
The first-to-last period change is +158.6 points; the largest period separation
is 218.9. These describe different aspects of the same series.

Y1 gives a stronger example of a rise and subsequent fall: its period mean
goes from 2,515 in 1989–1993 to 2,939 in 2009–2013 and then 2,633 in 2024–2026.
Its largest period separation is 423.5 points. Occupant concentration matters
when reading that series: Hakuho accounts for 22.1% of its occupant observations.
This is context, not a causal decomposition.

Of 489 numbered groups, 382 meet the presentation rule of at least 60 basho
spanning ten years. Their full-history post-basho slopes range from −104.5
to +92.3 points per decade: 49 positive and 333 negative. Those counts weight
groups equally, not wrestlers, and are not significance findings. The strongest
positive slope belongs to Y2, supported by only 61 basho with long gaps; some
strong negative slopes belong to deep Jonidan positions that disappear later.
Their coverage is essential to interpreting these extremes.

Among jointly eligible groups, slope signs differ from the primary full-run
post-basho result for:

- 4 of 382 groups when using basho-start ratings;
- 10 of 374 groups after excluding the first 12 represented basho;
- 38 of 346 groups when restricting to January 2000 onward.

The overall population means still reconcile to their fixed target at both
endpoints. Rank-specific movements, changing population composition and a fixed
global mean coexist. The results do not identify algorithmic inflation or
establish absolute ability comparisons across eras, and do not in themselves
require a change to the accepted model.

## Outputs and reproduction

The detailed [report](../../../../files/output/analysis/elo89_normalisation/chii_drift/report.md)
includes familiar ranks, extremes, period support, frequent occupants and
population context. The [offline explorer](../../../../files/output/analysis/elo89_normalisation/chii_drift/charts.html)
shows both endpoints, raw and rolling series, every group, sensitivity summaries,
period means, population quantiles, division means/counts/depth and selected
contemporaneous group gaps. Keep its `chart_data` directory beside it.

```powershell
python -m src.analysis.elo89_normalisation.chii_drift `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip"
```

Without `--history-zip`, the command uses the published live store and exits if
none is available. It never silently substitutes a ZIP. Actual analytical dates
come from the saved run, not the ZIP filename. The generated manifest records
input hashes, the represented History fingerprint, settings, implementation
hashes and the exact output file list. Existing contribution-study outputs
remain outside this study's separate output directory.

Display conventions are explicit: lines break at missing represented basho
and calendar gaps over four months; a rolling mean requires six observations
within 12 represented basho. Lower-support groups remain available but are not
ranked by slope alongside eligible groups. First/last contrasts refer to each
series' supported periods. Literal chii preserve side and annotations; numbered
and title summaries are separate. No prior reference line is used because its
production grouping can differ from these groups.

## Verification

- All 11 new contract tests pass, including fixed-mean divergence, reversals,
  irregular dates, equal-basho weighting, missing periods, rolling support,
  title grouping, returning membership, duplicate positions, eligibility and
  additive-shift invariance. The 16 existing normalisation tests also pass.
- The existing input validator reconciles active membership, chii, eligible
  bouts, adjustment counts and both endpoint means against matching History.
  The saved prior is validated and hashed. Input hashes are checked again
  after publication.
- An independent output audit compared all 160,185 observations against both
  source snapshot files and reconstructed all numbered per-basho means/counts.
- An independent covariance calculation reproduced all 8,910 trend rows,
  including the three date selections, and repeated the calculation after a
  10,000-point additive shift. Maximum slope discrepancy was below 1.3e-10
  points per decade.
- Offline browser checks exercised grouping, search, rank selection, sorting,
  endpoints, historical selections and every population panel. Desktop and
  mobile renders were inspected; there were no browser errors or page overflow.

The repository virtual environment referenced a missing Python installation
in this session. Verification used the available bundled Python with NumPy
and pandas. No model, prior, website build or deployment was changed.

## Next

The author should review these findings before resuming the normalisation
account. The evidence supports explaining temporal movement and its limits;
it does not resolve its causes.
