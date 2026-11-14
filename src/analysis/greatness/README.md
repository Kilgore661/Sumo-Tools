# Greatness analysis

This package contains analyses concerned with championship achievement,
progression to san'yaku, and related proxies for sustained prominence.

## San'yaku prospects

The production analysis is `sanyaku_prospects`. It estimates two distinct
eventual-attainment probabilities:

1. reaching san'yaku after first appearing in division/rank group `D` at age
   `A`;
2. reaching san'yaku after being observed in `D` at age `A`, without previously
   having reached san'yaku.

The first, division-debut probability, is the primary result. It answers the
original question about what age implies when a new Maegashira appears. The
second, division-state probability, is a secondary updating measure: it asks
what the historical prognosis is for a rikishi at his current division and age
after his career has continued without san'yaku attainment. It allows the
assessment to change as he ages or changes division, but it is not a substitute
for the debut result.

Run it with:

```powershell
python -m src.analysis.greatness.sanyaku_prospects --rebuild
```

`--rebuild` performs the complete historical calculation and is intentionally
opt-in. Without it, the CLI renders requested charts from the existing
rank-state CSV bundle and does not load History or recompute probabilities.

The default run uses the live History, parsed bios, downloaded daily-result
pages, the first represented basho as the supporting boundary, and writes to:

```text
files/output/analysis/greatness/sanyaku_prospects
```

The output bundle contains atomic cohort observations, debut and state
probabilities, basho-level rank-state observations and probabilities,
population and exclusion audits, exact basho-date coverage, outcome counts,
and a manifest. Ages are completed years on the exact civil date of Day 1
parsed from the downloaded results pages.

### Exact-age date provenance

The canonical History key identifies a basho only by year and month. That is
not precise enough for completed age: a birthday can fall between the start of
the labelled month and the tournament, and some basho begin in the preceding
calendar month.

To avoid that error, the current producer reads the exact civil date embedded
in each downloaded daily-results HTML page. It derives Day 1 by subtracting
`day - 1`, checks that every available page for the basho implies the same Day
1, and persists the evidence in `basho_date_coverage.csv`. Production fails if
any represented basho lacks a consistent exact start date.

This is a transitional source path, not the desired final ownership boundary.
Properly, the infrastructure parser should construct and persist a first-class
basho calendar (or an equivalent core structure) while parsing the downloaded
pages. Greatness and other analyses should consume that persisted calendar and
should not need to inspect raw HTML. `DailyResults.calendar_date` and compatible
serialization have been added as a step toward that design, but existing live
and archived histories predate the field and have not yet been rebuilt with it.

San'yaku means Komusubi, Sekiwake, Ozeki, or Yokozuna. `M` means Maegashira
only. Known retirement without later san'yaku is failure; active careers are
right-censored. Activity at the cutoff is checked in both ranked History and
the dated career rows on the downloaded rikishi page. This matters because
Maezumo (`Mz`) and the non-ranking statuses `Bg`, `Kg`, and `Sj` are not formal
banzuke positions and therefore do not appear in History. A rikishi absent
from both sources at the cutoff is treated as retired. Missing, invalid,
unrecognised, or contradictory source evidence remains `unknown`, and the
atomic CSV records the exact `outcome_evidence` used.

The adopted minimal notion of greatness is reaching san'yaku at least once.
Only first attainment matters: later returns to san'yaku do not create further
events or increase the success value. Persistence in san'yaku, measured by
cumulative basho, consecutive tenure, or repeated entries, is a valid stronger
notion of greatness but is not the outcome used in this experiment.

### Interpreting division-debut probability

The principal debut results are Maegashira and Juryo. Their age curves answer
the motivating scouting question directly: the Maegashira curve suggests age
27 as a useful descriptive boundary, while the corresponding Juryo boundary is
about age 26.

Makushita and the lower divisions require a different interpretation. Their
debut-age curves mix ordinary young recruits with university, qualified
amateur, foreign, and tsukedashi entry routes. The secondary peaks around ages
22--23 are therefore structured cohort effects, not evidence that age has
ceased to matter. Makushita remains potentially useful if entry route is added
as a parameter. Sandanme, Jonidan, and Jonokuchi debut probabilities are best
treated as exploratory recruitment-pathway results rather than simple age
curves. Division-state probability remains relevant to the practical question
of a rikishi's prospects from his current position. In particular, it can
update the cohort prognosis for an existing rikishi as his age or division
changes after debut.

Here, division debut means first represented appearance in each division. It
is not necessarily the rikishi's professional debut division, and the same
rikishi can contribute a debut observation as he first appears in several
successive divisions. The current calculation also does not classify whether
a first appearance was reached from below, by direct entry, or from above.
Entry route is a possible future cohort axis, not part of the present output.

### Career prospect charts

The same producer can render a rikishi's whole pre-san'yaku career as a Plotly
HTML chart. Supply one or more IDs:

```powershell
python -m src.analysis.greatness.sanyaku_prospects `
  --chart-rikishi-id 12320 `
  --chart-rikishi-id 12226
```

This fast path requires an existing bundle produced by at least one
`--rebuild`. To refresh the underlying analysis and produce charts in the same
run, combine the options:

```powershell
python -m src.analysis.greatness.sanyaku_prospects --rebuild `
  --chart-rikishi-id 12320
```

Each pre-san'yaku banzuke appearance supplies one point at the rikishi's exact
age. Its probability
is selected by division, rank number, and completed age; east and west are
pooled. First san'yaku attainment adds a terminal 100% point with a special
marker. A career without san'yaku simply ends without an artificial 0% point.
The proportion counts each rikishi once within a rank-age cell, while the raw
banzuke-observation count is retained separately. The HTML uses pinned CDN
Plotly and retains basho date, rank, completed age, unique cohort counts, and
observation count in hover data. The title states the question directly: the
historical probability of eventually attaining san'yaku, given rank and age.

Support is measured by unique resolved rikishi. Points with 20 or more are
solid green, 10--19 are solid amber for low support, and 1--9 are solid red for
very low support. A cell with no resolved rikishi remains a gap. These are
presentation categories, not formal confidence intervals.

These charts show trajectories of historical matched-cohort proportions,
not personalised ability models or estimates necessarily available at the
time. Formal uncertainty intervals remain deferred.

The specifications and caveats are in:

- `docs/Proposal - Division and Age as Predictors of Sanyaku Attainment.md`;
- `docs/Proposal - Career Sanyaku Prospect Charts.md`.

## Exploratory modules

The older modules in this package retain useful exploratory calculations:

- `yusho_chii_distribution.py`;
- `eligible_rikishi.py`;
- `sanyaku_age_distribution.py`;
- `sanyaku_transition_probability.py`.

They are not substitutes for the audited `sanyaku_prospects` bundle.
