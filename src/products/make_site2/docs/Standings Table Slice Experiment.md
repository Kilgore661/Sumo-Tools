# Standings Table Slice Experiment

## Purpose

This experiment adds the first ordinary non-indexed table page to `make_site2`.

The target is:

```text
standings_by_wins
```

This page is useful because the old site registers it as a `TableAppView`.
Migrating it proves that a table page can render through the `make_site2`
ContentPanel and PA model without copied standalone table-app HTML.

## Page

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

## Build Output

The builder now emits:

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

## What Was Proven

- A non-indexed table page can render inside the shared ContentPanel.
- The page uses the same G1 shape as BRB and Division Stability.
- The page renders from a `make_site2` envelope, not copied app HTML.
- Filter changes select or restrict table data.
- Table notes render below the table.
- Table sorting works through the same header-click path.
- The shell still contains no iframe.

Browser check:

```text
title: Standings by Wins
filters: metric_group_preset, current_num_basho, current_only, division
default table: Makuuchi Standings by Average after March 2026 Basho
default rows: 42
notes: 3
iframe count: 0
```

Filter check:

```text
division = juryo
table: Juryo Standings by Average after March 2026 Basho
rows: 28
URL state includes division=juryo
```

## Model Notes

This case confirms that ordinary table pages do not need `TableAppView` as a
public site mechanism.

The page shape remains:

```text
ContentPanel
  Heading
  Contents
    FilterSection
    PA
      Table artifact
    Note*
```

Compared with BRB:

- BRB is an indexed table: one index chooses a payload.
- Standings is a direct table: filters choose among declared data sources and
  visible table groups.

Both are still G1 table PAs.

## Remaining Gaps

This is a successful ordinary table slice, but still provisional.

Known gaps:

- the table runtime is partly generic and partly `standings_table` adapter;
- copied data includes the whole standings publisher bundle;
- controls are flat rather than grouped;
- table layout is functional but not final;
- pagination is not implemented;
- table-app-specific affordances from the old standalone app have not been
  audited for parity;
- URL state works but is not yet documented as a stable contract;
- no automated browser test covers filter changes or sorting.

## Next Experiment

Move to the G2 pressure case:

```text
career_length
```

The goal is to stop treating Career Length as five selectable views and instead
represent it as two PAs:

```text
Charts
  filter: chart = distribution | PMF | CDF | survival

Longest
  filter: active = all rikishi | active only
```

This should test whether `make_site2` can represent PA-specific filters without
reviving `PASet` as the target model.
