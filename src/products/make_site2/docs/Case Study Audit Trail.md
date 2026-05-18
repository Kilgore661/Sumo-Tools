# make_site2 Case Study Audit Trail

This document consolidates the case-study trail for the first `make_site2`
migration experiments. The original per-case notes are preserved in
`docs/archive/`.

## Working Partition

| Nav item | Page id | Grammar | PA shape | Filter scope | Artifact rendering | Notes | Migration risk |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| 7.1 Basho Results | `basho_results_browser` | G1 | One table PA: Basho Results table | Contents-level filters: basho/date, division, previous context, ratings, nu chii | Indexed table from BRB index and selected payload | Table notes only, shown when relevant table columns/groups are visible | First reference slice; must remove iframe and avoid copied page HTML |
| Division Stability | `division_stability` | G1 | One chart PA: Division Stability chart | No filters in first slice | Grouped line chart over `persistence.csv` | None for initial model | First chart slice; must prove charts do not reintroduce shell behavior |
| Standings by Wins | `standings_by_wins` | G1 | One table PA: Standings by Wins table | Contents-level filters: view, number of basho, active/current, division | Table over selected standings CSV | Table notes only | First non-indexed table slice; replaces old `TableAppView` path |
| Career Length | `career_length` | G2b | Branch-selected contents: Chart branch or Table branch | Branch-local filters: chart type for Chart; active/all for Table | One selected branch PA: chart or Longest table | Table notes only when Table branch is selected | Replaces original G2; branch-selected, not simultaneous PAs |
| Finish by Chii | `finish_by_chii` | G1 | One public chart PA: Finish by Chii threshold chart | Contents-level filters: division, direction, chii | Bar chart over top/bottom threshold CSVs | Scope note only in prototype | Current public item is standalone HTML; producer has extra outputs not automatically public-facing |

## Grammar Summary

G1 is the ordinary case:

```text
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA+ . Note*
PA -> Title . Artifact
```

G2b is the branch-selected pressure case:

```text
ContentPanel -> Heading . Contents
Contents -> BranchSelector . Branch+ . Note*
Branch -> FilterSection . PA
```

The important G2b invariant is that only the selected branch contributes a
visible artefact.

## Case 1: BRB First Slice

The first executable vertical slice was:

```text
7.1 Basho Results / Basho Results Browser
direct ContentPanel rendering
no iframe
no copied standalone HTML
```

Build command:

```powershell
python -m src.products.make_site2 --output files\output\make_site2
```

Generated output included:

```text
files/output/make_site2/
  index.html
  manifest-index.json
  manifests/basho_results_browser.json
  runtime/make_site2.css
  runtime/make_site2.js
  data/basho_results_index.json
  data/by-basho/*.csv
```

What was proven:

- `index.html` contains no `iframe`.
- Navigation selects BRB by loading a manifest/envelope, not by assigning `frame.src`.
- The ContentPanel renders the page heading, contents-level filters, one indexed table PA, and table notes.
- The BRB index loads from `data/basho_results_index.json`.
- The selected basho payload loads from `data/by-basho/*.csv`.
- Filters update the rendered table.
- URL state records selected filters and sort state.
- Table-header sorting works.
- Notes are filtered by visible table features.

Browser check:

```text
title: Basho Results
table: Makuuchi Results (Day 6) for May 2026
rows: 42
filters: basho_date, division, previous_context, rating_context, nu_chii
iframe count: 0
```

Model lesson:

```text
make_site PA manifest Option -> make_site2 content envelope Filter
```

The old implementation term `Option` should not leak into the public
`make_site2` model.

Formatting lesson:

BRB is not only a raw table renderer. The Kirishima May 2026 case showed that
`previous_result` must append `previous_rank_level_movement` for the Result
column. For that column only, each sanyaku rank is considered a rank level, so
Kirishima's previous result must render as:

```text
12-3 YS ↑
```

Remaining gaps:

- builder copies all BRB payload CSV files rather than supporting a payload mode such as latest-only;
- runtime is BRB-first rather than a clean generic table runtime plus BRB adapter;
- envelope is hand-built from the existing manifest rather than generated through stable model classes;
- CSS is usable but provisional;
- loading and error states are minimal;
- `previous_delta` and `previous_equelo` exist in the manifest but are not yet exposed by filters;
- filter grouping is still flat;
- URL state is adequate but not yet a documented contract;
- automated tests do not yet cover the shell.

## Case 2: Division Stability Chart Slice

This was the first ordinary chart page:

```text
Page id: division_stability
Grammar: G1
Status: prototype
PA: Division Stability chart
Artifact: grouped line chart over persistence.csv
Notes: none
```

Build output:

```text
manifests/division_stability.json
data/division-stability/persistence.csv
data/division-stability/metadata.json
data/division-stability/page.json
```

What was proven:

- A chart page can render in the shared ContentPanel.
- The chart renders from a `make_site2` envelope rather than copied HTML.
- The shell still contains no iframe.
- Runtime dispatch by artifact kind supports both `indexed_table` and `chart`.
- The first chart renderer can consume table-shaped CSV data and group it into visible traces.

Browser check:

```text
title: Division Stability
chart title: Division Stability chart
series: 6
legend: Makuuchi, Juryo, Makushita, Sandanme, Jonidan, Jonokuchi
iframe count: 0
```

Model lesson:

An ordinary chart page does not need a different shell model from BRB. It is
still:

```text
Heading
FilterSection
PA
Notes
```

The public difference is the artifact renderer:

```text
table-shaped data -> grouped line chart
```

Remaining gaps:

- chart subtitle and explanatory metadata from `page.json` are not yet shown;
- line chart rendering is simple SVG, not yet a general chart abstraction;
- legend entries are display-only;
- default-visible provenance is represented visually by muting other series, but is not interactive;
- hover fields from provenance are not yet rendered;
- chart axes and tick density are provisional;
- renderer is still effectively a `division_stability` adapter.

## Case 3: Standings Table Slice

This was the first ordinary non-indexed table page:

```text
Page id: standings_by_wins
Grammar: G1
Status: prototype
PA: Standings by Wins table
Artifact: table over selected standings CSV
Notes: table notes only
```

Filters:

```text
metric_group_preset
current_num_basho
current_only
division
```

Build output:

```text
manifests/standings_by_wins.json
data/standings/*.csv
data/standings/*.json
data/standings/page_bundle.json
data/standings/site_config.json
```

The data sources correspond to the existing `TablePA` windows:

```text
1, 2, 3, 4, 5, 6, 12, 18, 24, 36, 60 basho
```

What was proven:

- A non-indexed table page can render inside the shared ContentPanel.
- The page uses the same G1 shape as BRB and Division Stability.
- The page renders from a `make_site2` envelope, not copied app HTML.
- Filter changes select or restrict table data.
- Table notes render below the table.
- Table sorting works through the same header-click path.
- The shell still contains no iframe.

Browser checks:

```text
title: Standings by Wins
filters: metric_group_preset, current_num_basho, current_only, division
default table: Makuuchi Standings by Average after March 2026 Basho
default rows: 42
notes: 3
iframe count: 0
```

```text
division = juryo
table: Juryo Standings by Average after March 2026 Basho
rows: 28
URL state includes division=juryo
```

Model lesson:

Ordinary table pages do not need `TableAppView` as a public site mechanism.
Compared with BRB:

- BRB is an indexed table: one index chooses a payload.
- Standings is a direct table: filters choose among declared data sources and visible table groups.

Both are still G1 table PAs.

Remaining gaps:

- table runtime is partly generic and partly a `standings_table` adapter;
- copied data includes the whole standings publisher bundle;
- controls are flat rather than grouped;
- table layout is functional but not final;
- pagination is not implemented;
- table-app-specific affordances from the old standalone app have not been audited for parity;
- URL state works but is not yet documented as a stable contract;
- no automated browser test covers filter changes or sorting.

## Case 4: Career Length Pressure Case

The original hypothesis was that Career Length was the G2 pressure case:

```text
Charts
  filter: chart = distribution | PMF | CDF | survival

Longest
  filter: active = all rikishi | active only
```

That hypothesis was wrong. The first implementation rendered two visible
artefacts at once: one chart and one table. Career Length should show exactly
one visible artefact:

```text
distribution chart
or PMF chart
or CDF chart
or survival chart
or Longest table
```

The correction is G2b: branch-selected contents.

Revised page model:

```text
Page id: career_length
Grammar: G2b
Status: prototype
Branches:
  Chart
  Table
```

Branch selector:

```text
branch = chart | table
```

Branch-local filters:

```text
Chart:
  chart = distribution | pmf | cdf | survival

Table:
  active = all | active
```

Visible structure:

```text
ContentPanel
  Heading
  BranchSelector
    Chart | Table
  Selected Branch
    FilterSection
    PA
  Note*
    table notes only when branch = table
```

Build output:

```text
manifests/career_length.json
data/career-length/distribution.csv
data/career-length/pmf.csv
data/career-length/cdf.csv
data/career-length/survival.csv
data/career-length/longest.csv
data/career-length/metadata.json
data/career-length/page.json
```

Browser checks:

```text
branch = chart
chart = distribution
visible chart count: 1
visible table rows: 0
notes: 0
table branch filters disabled
```

```text
branch = table
visible chart count: 0
visible table rows: 50
notes: 1
chart branch filters disabled
URL: ?branch=table&chart=distribution&active=all#page=career_length
```

```text
branch = table
active = active
visible table rows: 16
URL: ?branch=table&chart=distribution&active=active#page=career_length
```

Model lesson:

The earlier G1/G2 partition was too eager to treat differing filter scopes as
different simultaneous PAs. Career Length shows another shape:

```text
Contents may choose exactly one Branch.
Each Branch owns branch-local filters and one PA.
```

This is not the same as reverting to the old flat implementation term `View`.
The model is nested:

```text
select branch
then apply branch-local filters
then render selected branch PA
```

Remaining gaps:

- chart rendering is simple SVG;
- table rendering caps Longest at 100 rows for usability;
- table sorting for Longest is not yet wired;
- chart hover behavior is not implemented;
- G2b semantics need to be merged into the main migration plan;
- automated tests should cover one-visible-artefact behavior.

## Case 5: Finish by Chii Manifest Slice

The old make_site item 5.1 is currently a `StandaloneHtmlView` over:

- `files/output/misc/finish_by_chii_1958_2026.html`
- `files/output/misc/finish_by_chii_1958_2026_top_thresholds.csv`
- `files/output/misc/finish_by_chii_1958_2026_bottom_thresholds.csv`

The producer is `src/misc/finish_by_chii.py`, with chart HTML emitted by
`src/misc/finish_by_chii_charting.py`.

First make_site2 shape:

```text
G1
  filters
    division = makuuchi | juryo
    direction = top | bottom
    chii = values from selected division
  PA
    finish_by_chii_chart
      top thresholds CSV
      bottom thresholds CSV
  notes
```

The rendered artefact is one threshold-probability chart. This matches the
existing standalone HTML. The same producer emits additional files, including
summary/average data, but producer outputs are not automatically public-facing
artefacts.

Assumptions:

- `division` is a normal shared filter.
- `direction` chooses the data source and probability semantics.
- `chii` is a data-derived filter because valid values depend on division.
- The chart renderer belongs in make_site2 runtime for now; later migration can move the manifest definition closer to the producer if this pattern repeats.

Implemented trial:

- builder emits `manifests/finish_by_chii.json`;
- builder copies threshold CSVs into `data/finish-by-chii/`;
- `finish_by_chii` is registered in navigation and `manifest-index.json`;
- runtime renders the public threshold chart directly without iframe.

Verification:

```text
default state: Makuuchi Y1e top chart, 10 bars
division switch: Juryo values populate and chart renders
direction switch: Bottom finish chart renders
console errors: none
```

## Cross-Case Lessons

- The replacement target is not a new shell around old standalone pages. It is a
  direct ContentPanel renderer driven by a manifest/envelope.
- `Option` may remain in old make_site producer code, but `make_site2` should
  expose controls as filters.
- Producer side outputs are available evidence, but not automatically page
  artefacts. The public page model decides what gets rendered.
- G1 currently covers ordinary indexed tables, ordinary direct tables, ordinary
  charts, and the first Finish by Chii slice.
- G2b is needed for branch-selected contents where exactly one branch artefact
  should be visible.
- Rendering details can still require semantic adapters, as shown by BRB
  previous-result rank-level movement.
- The runtime is intentionally still prototype quality: several renderers are
  page-specific adapters pending a more stable abstraction.
