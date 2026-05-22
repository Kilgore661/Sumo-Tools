# Division Stability Chart Slice Experiment

## Purpose

This experiment adds the first ordinary chart page to `make_site2`.

The goal is to test whether G1 also covers chart PAs:

```text
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA+ . Note*
PA -> Title . Artifact
```

For this slice, `FilterSection` is empty.

## Page

```text
Page id: division_stability
Grammar: G1
Status: prototype
PA: Division Stability chart
Artifact: grouped line chart over persistence.csv
Notes: none
```

## Build Output

The builder now emits:

```text
manifests/division_stability.json
data/division-stability/persistence.csv
data/division-stability/metadata.json
data/division-stability/page.json
```

The page is selected from the same `index.html` shell as BRB.

## What Was Proven

- A chart page can render in the shared ContentPanel.
- The chart renders from a `make_site2` envelope rather than copied HTML.
- The shell still contains no iframe.
- The runtime can dispatch by artifact kind:
  - `indexed_table` for BRB;
  - `chart` for Division Stability.
- The first chart renderer can consume table-shaped CSV data and group it into
  visible traces.

Browser check:

```text
title: Division Stability
chart title: Division Stability chart
series: 6
legend: Makuuchi, Juryo, Makushita, Sandanme, Jonidan, Jonokuchi
iframe count: 0
```

## Model Notes

This case confirms that an ordinary chart page does not need a different shell
model from BRB.

It is still:

```text
Heading
FilterSection
PA
Notes
```

The public difference is the artifact rendering:

```text
table-shaped data -> grouped line chart
```

## Remaining Gaps

This is a successful chart slice, but not yet a finished chart runtime.

Known gaps:

- chart subtitle and explanatory metadata from `page.json` are not yet shown;
- line chart rendering is simple SVG, not yet a general chart abstraction;
- legend entries are display-only;
- default-visible provenance is represented visually by muting other series,
  but not yet interactive;
- hover fields from provenance are not yet rendered;
- chart axes and tick density are provisional;
- this renderer is still effectively a `division_stability` adapter.

## Next Experiment

Move to an ordinary table page.

Preferred target:

```text
standings_by_wins
```

Reason:

- it is currently a `TableAppView` in the old shell;
- it already has a `TablePA` manifest;
- migrating it proves a non-indexed table can render directly without copied
  standalone table-app HTML.
