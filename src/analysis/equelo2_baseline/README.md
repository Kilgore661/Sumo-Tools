# Equelo2 Full-History Baseline

## Purpose

This package performs the first Tranche 2 baseline described in the Elo/Equelo
story. It runs one chronological rating world from January 1958 using the
frozen Elo-89 entrant prior, then runs a separate Elo-89 reference world from
January 1989 over the same later bouts.

The purpose of the historical extension is to put pre-1989 and modern rikishi
on one continuous rating scale, permitting comparisons such as Taiho with
Hakuho. It is not intended to improve post-1988 ratings or forecasts. The
post-1988 reference comparison checks that incorporating the incomplete earlier
record does not materially damage Elo-89; a favourable difference is incidental
and is not the intended benefit of the extension.

This is an experiment, not yet the selected Equelo2 model.
It is a retrospective diagnostic: the adopted Elo-89 prior was estimated using
post-1988 information and is therefore future-informed when applied in 1958.

## Fixed contract

- `q = 400`;
- the established divisional-`k` configuration;
- the frozen canonical P1 Elo-89 entrant prior, paired from its literal
  east/west chii by the same unweighted rule as the Tranche 1 predictive gate;
- historical-only chii use the nearest represented chii above in the same
  division (`M19` therefore receives `M18`'s rating);
- the active population is the complete represented banzuke;
- a common shift before and after each basho preserves the exact population
  mean implied by applying Elo-89 priors to the January 1989 banzuke;
- every represented W/L result is rated, irrespective of kimarite;
- fusen, non-binary outcomes and results with an off-banzuke participant are
  excluded and reported;
- no missing result is inferred;
- in the full-history candidate, ratings persist across gaps in results and
  are archived while a rikishi is absent from the represented banzuke;
- the post-1988 control uses Elo-89's exact departure behavior: a rating is
  discarded on departure and the rikishi receives the chii prior if they
  later reappear.

The package reads `History` directly. It deliberately does not reuse the
legacy pre-1989 oracle, which retains only bouts involving a sekitori, or the
legacy replay rule that treats a blank kimarite as an unrated result.

Absence from a represented banzuke is not necessarily permanent departure.
The source contains hundreds of ranked gap-and-return careers, normally through
`Bg` and `Mz`, nine historical `Kg`/`Mz` returns, the ambiguous Muraishi sequence
`Jk8e, ??, ??, Mz, Jk4w`, and Sokokurai's exceptional direct restoration from
`M16e` to `M15w`. The lifecycle audit and terminology are recorded in story
document 17. The baseline's archive-and-restore behavior is a candidate policy,
not an inference that the administrative categories are equivalent.

The Elo-89 artifact is not modified. Historical completion is written to the
experiment output as a separate derived map.

The default source artifact is
`files/output/analysis/equelo_bkp1/prior.csv`.

## Rating observation convention

Published Equelo2 ratings and career records use the processed `end` phase:
after all eligible bouts in the basho and the end-of-basho population
normalisation. Start-state data needed internally for replay and forecast
reproduction is not a rating observation and must not be used for published
ratings or records.

## Full run

With the live store running:

```powershell
python -m src.analysis.equelo2_baseline
```

The default interval is `1958/01` through `2026/07`, matching the retained
Elo-89 comparison endpoint. The live store is preferred; if unavailable, the
same History-zip fallback used by the bout-completeness audit is used.

An explicit History zip can be supplied for a reproducible run:

```powershell
python -m src.analysis.equelo2_baseline `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip"
```

Default output is:

```text
files/output/analysis/equelo2_baseline/full_history_1958_01_to_2026_07/
```

The principal files are:

- `findings.md` and `manifest.json`;
- `completed_prior.csv`;
- `1988_11_ratings.csv` and `1989_01_handover.csv`;
- `chii_rating_summary.csv`;
- `score_summary.csv` and `post_1988_score_difference.csv`;
- bout-level forecast and rating-comparison ledgers;
- the population-adjustment and exclusion ledgers.

`rating_ledger.csv` records both the display-form `chii` and its authoritative
integer `chii_ordinal` on every start and end row. Filtering the candidate run
to the last basho and `phase=end` gives the active population's latest
processed ratings; selecting each rikishi's final end row gives last recorded
career ratings.
