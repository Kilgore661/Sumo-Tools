Yes. The main enumeration doc is [Project Map.md](<X:\Sumo\Sumo-Tools\docs\Project Map.md:58>). The earlier, simpler list is in [2026 05 03 Presentation Layer.md](<X:\Sumo\Sumo-Tools\src\analysis\docs\2026 05 03 Presentation Layer.md:103>).

Right now the `site` package only deploys/integrates:

- `Standings`
- `Banzuke Compare`

The HTML artefacts that look like plausible stress-test candidates but are not yet in the site shell are:

- `files/output/misc/finish_by_chii_1958_2026.html`
- `files/output/misc/finish_by_chii_1978_1980.html`
- `files/output/banzuke_division_era_chart.html`
- `files/output/rank_era_chart.html`
- `files/output/first_app.html`
- `files/output/division_churn.html`
- `files/output/probability/matchups/observed_sideless_matchup_traces.html`
- `files/output/probability/matchups/equelo_sideless_matchup_traces.html`
- `files/output/persistence/division_persistence (...) .html` pages, but these were explicitly marked not-first-pick / low readiness.

Also present but probably **not** good nav stress-test candidates:

- `files/output/current standings/*.html`: lots of old per-basho current-standings pages; likely superseded by the standings tool.
- `files/output/HTML results/**/*.html`: raw downloaded/source-ish results pages; Project Map marks this as internal.
- `files/output/banzuke warnings.html` and `file-format weirdness.html`: diagnostics/internal.
- lots of `files/output/Equelo.../*.html`: research records, mostly not current public-surface candidates.
