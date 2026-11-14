# Proposal: Public San'yaku Prospects Artifact

## Status

Implemented as the 1989+ production analysis and public
`Research > Age > Prospects` artifact for make_site89.

This proposal covers:

1. the new canonical `analysis.prospects` calculation and data bundle;
2. the thin site89 publication adapter; and
3. the interactive public artifact.

The existing 1958+ `analysis.greatness.sanyaku_prospects` implementation is a
legacy research source. It remains runnable but is not a dependency of the new
production path.

## Architectural decision

The public artifact follows make_site89's established single-History policy.
Both rating and non-rating production use the selected History beginning at
`1989/01`, even where an individual non-rating analysis could use earlier
records.

The intended flow is:

```text
selected 1989+ production History
  + bios
  + exact basho calendar
  + cutoff career status
             |
             v
analysis.prospects
  - eligible population
  - lifecycle outcomes and censoring
  - rank/age cohorts
  - probabilities and support
  - complete career trajectories
             |
             v
analysis.site89.prospects
  - validate the prospects bundle
  - compact and group fields for browser lookup
  - write site-facing JSON and diagnostics
             |
             v
make_site89 bundle validation and static publication
             |
             v
browser selection and Plotly rendering only
```

The calculation is owned by a new package:

```text
src/analysis/prospects/
```

The site-facing adapter is a module in the existing package:

```text
src/analysis/site89/prospects.py
```

It should not need a Python subpackage because it performs publication packing,
not analysis. The richer browser implementation may justify a JavaScript
subpackage such as `ui/charts/prospects/`.

## Why the production analysis begins in 1989

make_site2 belongs to the earlier 1958+/Equelo publication era. make_site89 was
created with a coherent post-1988 History and Elo-89 production chain. Its
model-independent artifacts also use that selected History: Division
Persistence, career records and similar pages do not silently choose a longer
scope merely because their calculations do not require ratings.

Prospects follows the same policy. This is a production-coherence decision,
not a claim that pre-1989 data are useless or that January 1989 is an intrinsic
boundary for age and promotion analysis.

The existing full-history greatness analysis remains valuable exploratory
work. It must not, however, become an exceptional second History source hidden
inside the current site bundle.

The governing context is recorded in:

- `src/products/make_site89/README.md`;
- `src/products/make_site89/docs/Implementation Plan.md`; and
- `src/products/make_site89/docs/Production Documentation Strategy.md`.

## Relationship to the legacy greatness package

`analysis.greatness.sanyaku_prospects` currently implements the required
population, lifecycle, probability and trajectory concepts over the 1958+
History. It must remain unchanged as a reproducible legacy analysis, apart from
documentation identifying its status.

The new production package should begin as a deliberate fork of the relevant
greatness code. It must not import greatness-specific modules. This prevents a
legacy package from becoming a hidden production dependency and allows the
1989+ population contract to evolve independently.

Copied code must be reviewed and tested rather than treated as correct merely
because it came from greatness. A short package note should record the source
package and the commit from which the fork was made.

The new package may continue to import genuinely shared infrastructure and
domain APIs, including `History`, `BioStore`, the basho calendar and public age
utilities. Only the prospects-specific analytical implementation is forked.

Update `src/analysis/greatness/README.md` to state that the package is legacy
full-history research and is outside the make_site89 production chain. It may
be reconsidered if the project later adopts a systematic multi-epoch
production design.

## Public question

For each selected rikishi, how did the historical proportion of comparable
rikishi who eventually reached san'yaku change as he moved through the banzuke
and grew older?

For a pre-san'yaku appearance, the plotted value is:

\[
P(S \mid D, R, A, \text{no previous san'yaku}),
\]

where:

- `S` is first eventual attainment of Komusubi, Sekiwake, Ozeki or Yokozuna;
- `D` is `M`, `J`, `Ms`, `Sd`, `Jd` or `Jk`;
- `R` is rank number, with east and west pooled; and
- `A` is completed age on the exact civil date of Day 1.

The chart uses continuous exact age for position on the age axis. Cohort lookup
continues to use completed integer age.

The value is an observed proportion among resolved historical cohort members.
It becomes a prospect estimate only when generalised to another comparable
rikishi. It is not a personalised model of ability.

## Production population

The January 1989 banzuke is supporting boundary data. A rikishi already present
on that banzuke has an unknown earlier career and is excluded from the
complete-record population. A rikishi first appearing after the boundary may
be eligible.

An eligible trajectory requires:

- a first represented ranked appearance after `1989/01`;
- a usable exact birth date;
- consistent exact Day 1 dates for every contributing basho; and
- at least one eligible pre-san'yaku rank-state observation.

The existing lifecycle policy is forked and revalidated:

- first later san'yaku is success;
- known retirement without san'yaku is failure;
- activity at the cutoff is right-censored;
- missing or contradictory cutoff evidence is unknown; and
- `Mz`, `Bg`, `Kg` and `Sj` are administrative statuses, not formal chii.

The cutoff must be the same latest represented basho used by the site89
production History.

## Canonical `analysis.prospects` bundle

The package writes to:

```text
files/output/analysis/prospects
```

It owns complete, publication-neutral outputs, including:

```text
population_summary.csv
population_exclusions.csv
basho_date_coverage.csv
rank_state_observations.csv
probability_by_rank_state_age.csv
career_trajectory_points.csv
manifest.json
```

It may retain debut- and division-state outputs if they remain useful, but the
public artifact depends on the rank-state and trajectory contracts above.

### Rank-state observations

Retain one row for every eligible pre-san'yaku banzuke appearance. Each row
contains identity, shikona, basho, exact start date, completed and continuous
age, division, rank number, display chii, first-san'yaku event metadata,
lifecycle outcome, evidence and follow-up.

### Probability cells

Group observations by `(division, rank_number, completed_age)`. Repeated
appearances by the same rikishi remain separate observation counts but that
rikishi counts only once toward the cell outcome proportion.

For each cell retain:

- raw banzuke observations;
- unique rikishi;
- success, failure, right-censored and unknown counts;
- resolved count;
- resolved probability;
- lower and upper censoring bounds;
- support tier; and
- analysis cutoff.

A cell with no resolved rikishi has a blank resolved probability. It must not
be represented as zero.

### Complete career trajectories

`career_trajectory_points.csv` contains all chartable rikishi, not only IDs
requested at the command line. Every eligible pre-san'yaku appearance supplies
one ordinary point. First san'yaku supplies exactly one terminal attainment
point at 100%.

Each point contains:

```text
rikishi_id
shikona
basho
date
age
exact_age
division
rank_number
chii
point_kind
probability
cohort_observations
cohort_rikishi
cohort_success
cohort_failure
cohort_unresolved
cohort_resolved
support_tier
```

Every ordinary point is a validated lookup into the canonical probability
table. The trajectory producer must not independently recalculate a
probability.

If a rikishi never reaches san'yaku, the trajectory ends at his last
represented pre-san'yaku appearance. It does not receive an artificial 0%
retirement point. No post-san'yaku points are emitted.

### Standalone compatibility

The production package may retain the legacy CLI convenience of generating
standalone HTML for requested rikishi. Requested IDs control only which HTML
files are rendered; they do not control the contents of the canonical all-
rikishi trajectory CSV.

Cached rendering filters the canonical trajectory points rather than rebuilding
them through a second analytical path.

## Support presentation

Support is unique resolved rikishi in a `(division, rank_number, age)` cell,
not repeated banzuke observations.

The inherited descriptive tiers remain:

| Unique resolved rikishi | Presentation |
|---:|---|
| 20 or more | supported; green marker |
| 10--19 | low support; amber marker |
| 1--9 | very low support; red marker |
| 0 | undefined probability; chart gap |

These thresholds are presentation policy, not uncertainty intervals. Because
the 1989+ eligible population is smaller than the legacy 1958+ population, the
new run is expected to contain more low-support cells. The first production
run must measure this rather than silently carrying over the legacy support
claims.

## Legacy comparison

The first completed 1989+ run should produce a one-off validation comparison
against the existing 1958+ greatness bundle. Compare at least:

- eligible rikishi and observation counts;
- probability-cell counts;
- resolved-support distribution;
- coverage of actual trajectory observations by support tier; and
- differences in probabilities for shared `(division, rank, age)` cells.

The purpose is to understand the consequences of the new boundary and detect
implementation errors. Agreement is not required: the populations are
deliberately different. The legacy bundle is a comparison source, not a
production dependency.

## Site-facing producer

Add:

```text
src/analysis/site89/prospects.py
```

It consumes the explicit `analysis.prospects` bundle produced during the same
site89 build. The site89 orchestrator passes the bundle root; the adapter must
not discover a global greatness output.

The adapter may:

- validate the prospects manifest and required files;
- require matching History start and cutoff values;
- verify row reconciliation and probability ranges;
- create a deterministic rikishi selector index;
- compact repeated field names using declared column arrays;
- group points by rikishi ID; and
- write publication diagnostics.

It may not:

- build the eligible population;
- classify careers or outcomes;
- calculate ages, probabilities, censoring bounds or support tiers;
- infer first san'yaku attainment; or
- read the legacy greatness bundle.

### Site contract

Write:

```text
age/prospects/data/trajectory_master.json
age/prospects/data/trajectory_master_report.json
```

The master contract contains:

```text
schema_version
source
columns
rikishi
points_by_rikishi
```

`rikishi` contains selector metadata including ID, display shikona, first
basho and last plotted basho. `points_by_rikishi` maps IDs to compact arrays
whose fields are declared by `columns`.

The adapter may use a separate compact cohort table referenced by points if
measurement shows a material size reduction. That is lossless publication
packing, not analysis.

The report contains rikishi count, point count, attainment count, maximum
points per career, raw JSON bytes and gzip bytes. If one master payload proves
too large, prefer a modest number of indexed shards over thousands of one-file-
per-rikishi payloads.

## Public artifact

The page identity is:

```text
page id: prospects
navigation: Research > Age > Prospects
route: age/prospects
title: San'yaku Prospects
```

Use a specialised interactive renderer, provisionally:

```text
renderer: prospects
```

It should reuse or extract the Rikishi History selector behavior rather than
create a separate convention. Shared behavior may include search, add/remove,
URL serialization, stable per-rikishi colours and strict legend isolation.
Prospect-specific trace construction remains separate.

## Interaction

### Rikishi selection

- Start with no selected rikishi and show the searchable add control.
- Add and remove rikishi one at a time.
- Search by shikona or numeric rikishi ID.
- Retain selections while changing the x-axis.
- Serialize selected IDs using the existing `rikishi` URL key.
- A normal legend click toggles one rikishi.
- A legend double-click always shows only that rikishi; double-clicking an
  already isolated rikishi must not restore all traces.
- Removing a rikishi removes his line and support markers.

Do not prevent comparisons between different eras within the represented
1989+ period.

### X-axis

Provide:

```text
Age (default)
Date
```

Age uses continuous exact age on Day 1 and is the primary comparison view. It
aligns careers by a conditioning variable.

Date uses exact civil Day 1. With several rikishi it aligns contemporaries and
shows how their prospects diverged in calendar time. Non-overlapping careers
appear separately across the union of their dates. Date is an observation
axis, not another predictor.

Use URL state:

```text
x=age
x=date
```

### Y-axis and traces

- The y-axis is historical probability of eventual san'yaku attainment from
  0% to 100%.
- Each selected rikishi has one stable line identity and colour.
- Undefined probabilities remain gaps with `connectgaps = false`.
- Ordinary points receive green, amber or red support markers.
- Support-marker overlays do not create extra rikishi legend entries.
- First san'yaku is a gold star at 100%, without an on-chart text label.
- Careers without san'yaku simply end; there is no artificial zero.

Hover text includes:

- shikona and rikishi ID;
- basho and exact Day 1;
- exact and completed age;
- chii;
- probability;
- success, failure, resolved and unresolved unique-rikishi counts;
- raw observation count; and
- support description.

## Interpretation shown on the page

The page must state that:

- values are historical matched-cohort proportions, not personalised forecasts
  of ability;
- cohorts use division, rank number and completed age;
- east/west and rank annotations do not create separate cohorts;
- age and rank are the predictors; date is an alternative display axis;
- unresolved careers are excluded from the resolved proportion but retained in
  audit counts and censoring bounds;
- support is unique resolved rikishi;
- results use the completed 1989+ supporting record, including information not
  necessarily available at the plotted historical date;
- January 1989 incumbents are excluded because their careers began before the
  represented production boundary; and
- first san'yaku attainment, once, is the adopted minimal endpoint.

## Production integration

Prospects is a derived-data producer, so downloading new results is not by
itself sufficient to update the artifact. The next normal live-store-first
production build must recalculate it. No separate manual Prospects command is
required in the production workflow.

The normal `.\_boot89.ps1` sequence must therefore be:

1. refresh or select the live input data in the established way;
2. have `src.analysis.site89` load the selected 1989+ History once;
3. run `analysis.prospects` against that History and the corresponding bios
   and basho calendar;
4. run `analysis.site89.prospects` against the newly completed canonical
   Prospects bundle;
5. include and validate its site-facing outputs in
   `files/output/analysis/site89_bundle`; and
6. only then allow `make_site89` to assemble the static site.

This rebuild is required after new results because they may resolve previously
censored careers, add observations, change existing cohort probabilities and
extend active trajectories. The first implementation may rebuild the complete
Prospects bundle; incremental recomputation is not required.

The Prospects manifest must identify enough inputs to detect a mismatched or
old run: at minimum the History start and cutoff basho, History source identity
or fingerprint, and the identities or fingerprints of the bio and exact basho
calendar inputs. The site89 adapter and bundle validation must reject outputs
that do not match the inputs of the current orchestration run.

The presentation-only commands retain their existing meanings:

- `python -m src.products.make_site89 --build-only` assembles an already
  produced site89 bundle and does not recalculate Prospects; and
- `.\_boot89.ps1 --no-build` deploys the existing static tree without
  refreshing inputs or recalculating Prospects.

Consequently, neither command is the route for publishing newly downloaded
results. The normal `.\_boot89.ps1` run (or its `--build-only` form, which
still runs production but omits deployment) is the supported refresh path.

Implementation must:

1. create and test the independent `analysis.prospects` package;
2. wire it into `src.analysis.site89` so its bundle is rebuilt from the same
   selected History on every normal production run;
3. add the thin `analysis.site89.prospects` adapter;
4. add adapter outputs to the site89 manifest and validation contract;
5. add the promoted page and artifact declaration;
6. add `Prospects` under the existing `Age` research navigation category;
7. add the specialised browser renderer and shared selection behavior;
8. update the greatness README to mark the old package as legacy; and
9. record the one-off comparison with the legacy full-history run.

Production must fail if the prospects bundle is absent, stale, built from a
different History scope or cutoff, or has an unsupported schema. It must not
fall back to greatness or silently recalculate from another History.

## Validation

### Canonical analysis

Tests must demonstrate that:

1. January 1989 occupants are supporting-boundary exclusions;
2. eligible later entrants have complete represented records and exact birth
   dates;
3. every eligible pre-san'yaku appearance creates one ordinary trajectory
   point;
4. repeated appearances count once per rikishi in a probability cell but
   remain separate observation and trajectory rows;
5. every ordinary point agrees with its canonical probability cell;
6. exact age and date use the validated basho calendar;
7. undefined probabilities remain blank;
8. support uses unique resolved rikishi;
9. first san'yaku creates one terminal 100% event;
10. no post-san'yaku or artificial retirement points appear; and
11. requested standalone charts filter the complete canonical points.

### Site adapter

Tests must demonstrate that:

1. packing is deterministic and lossless for declared fields;
2. the selector index has one entry per trajectory-bearing rikishi;
3. point, event and rikishi counts reconcile with the prospects bundle;
4. start, cutoff and source identity match the site production History;
5. stale or unsupported inputs fail explicitly;
6. output paths and bundle declarations agree; and
7. size diagnostics describe the actual payload.

### Browser artifact

Tests must demonstrate that:

1. rikishi can be added, removed and found by ID or shikona;
2. Age is the default x-axis and Date is optional;
3. changing axes preserves selection and trace visibility;
4. multiple careers use the union of their ages or dates;
5. support colours and the attainment star are correct;
6. gaps are neither converted to zero nor connected;
7. strict legend double-click isolation is stable;
8. URL state restores selected rikishi and axis; and
9. page, navigation, runtime manifest and bundle integration are complete.

An opt-in real-data smoke test should build the production prospects bundle,
pack it for the site and verify attainment, non-attainment and active/censored
examples. It must remain outside the normal unit-test suite.

## Non-goals

This artifact does not add:

- a 1958+ production exception;
- imports from the legacy greatness implementation;
- smoothing or minimum-support suppression;
- confidence or credible intervals;
- individual performance, recent results, injury or heya predictors;
- entry-route conditioning;
- east/west-specific probabilities;
- leave-one-rikishi-out estimates;
- rolling estimates using only information available at each plotted date;
- post-san'yaku persistence or repeated attainment; or
- automatic reconciliation of different historical epochs.

Those are separate analytical or production questions and must not be
introduced by the site adapter or browser.
