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
python -m src.analysis.greatness.sanyaku_prospects
```

The default run uses the live History, parsed bios, downloaded daily-result
pages, the first represented basho as the supporting boundary, and writes to:

```text
files/output/analysis/greatness/sanyaku_prospects
```

The output bundle contains atomic cohort observations, debut and state
probabilities, population and exclusion audits, exact basho-date coverage,
outcome counts, and a manifest. Ages are completed years on the exact civil
date of Day 1 parsed from the downloaded results pages.

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
right-censored; unresolved disappearances remain unknown.

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

### Future work

Two natural extensions have been identified but are not part of the current
producer:

- stratify debut probability by entry route where the data can support a
  reliable classification; and
- chart an individual rikishi's matched state probability over time as his age
  or division changes, with debut-probability markers at first division
  appearances.

The latter would show the trajectory of historical age-and-division cohort
prospects, not a personalised model of the rikishi's ability.

The full specification and caveats are in
`docs/Proposal - Division and Age as Predictors of Sanyaku Attainment.md`.

## Exploratory modules

The older modules in this package retain useful exploratory calculations:

- `yusho_chii_distribution.py`;
- `eligible_rikishi.py`;
- `sanyaku_age_distribution.py`;
- `sanyaku_transition_probability.py`.

They are not substitutes for the audited `sanyaku_prospects` bundle.
