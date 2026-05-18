# BRB First Slice Experiment

## Purpose

This experiment creates the first executable `make_site2` vertical slice:

```text
7.1 Basho Results / Basho Results Browser
direct ContentPanel rendering
no iframe
no copied standalone HTML
```

The goal is not full site parity. The goal is to prove that a promoted page can
render from a `make_site2` content envelope inside one static shell.

## Build Command

```powershell
python -m src.products.make_site2 --output files\output\make_site2
```

Generated output:

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

## What Was Proven

- `index.html` contains no `iframe`.
- Navigation selects BRB by loading a manifest/envelope, not by assigning
  `frame.src`.
- The ContentPanel renders:
  - page heading;
  - contents-level filters;
  - one indexed table PA;
  - table notes.
- The BRB index loads from `data/basho_results_index.json`.
- The selected basho payload loads from `data/by-basho/*.csv`.
- Filters update the rendered table.
- URL state records the selected filters and sort state.
- Table-header sorting works.
- Notes are filtered by visible table features.

Browser check used the May 2026 default payload:

```text
title: Basho Results
table: Makuuchi Results (Day 6) for May 2026
rows: 42
filters: basho_date, division, previous_context, rating_context, nu_chii
iframe count: 0
```

## Current Envelope Shape

The generated BRB manifest uses the provisional `make_site2` envelope:

```json
{
  "page": {
    "id": "basho_results_browser",
    "title": "Basho Results",
    "summary": "Historical and current basho results by division.",
    "status": "promoted"
  },
  "contentPanel": {
    "heading": {},
    "contents": {
      "grammar": "G1",
      "filters": [],
      "pas": [],
      "notes": []
    }
  }
}
```

For BRB:

```text
ContentPanel
  Heading: Basho Results
  Contents
    FilterSection
      basho_date
      division
      previous_context
      rating_context
      nu_chii
    PA
      Basho Results table
    Note*
      table-specific notes
```

This confirms BRB as a G1 page.

## Vocabulary Boundary

The current source manifest still comes from `make_site` and uses the
implementation term `Option`.

At the `make_site2` envelope boundary, those controls are emitted as
`filters`.

This is intentionally transitional:

```text
make_site PA manifest Option -> make_site2 content envelope Filter
```

The old term should not leak into the public `make_site2` model.

## Formatting Lesson

BRB is not only a raw table renderer.

The payload contains several fields that must be interpreted together for
public table cells. The first concrete example was Kirishima in May 2026:

```text
previous_result: 12-3 YS
previous_rank_level_movement: ↑
```

In the old `make_site` runtime, the `previous_result` cell appends the
rank-level movement marker:

```text
12-3 YS ↑
```

This matters because, for that column only, each sanyaku rank is treated as a
rank level. Kirishima moved from sekiwake to ozeki, so the marker is relevant
even though both ranks are in Makuuchi.

The first `make_site2` runtime missed this because it rendered only the raw
`previous_result` field. The runtime now has a BRB-specific formatter for
`previous_result`.

Conclusion:

```text
Artifact rendering metadata is not enough by itself.
Some table columns require semantic cell formatters.
```

## Remaining BRB Gaps

This slice is successful, but not yet reference quality.

Known gaps:

- the builder copies all BRB payload CSV files rather than supporting a payload
  mode such as latest-only;
- the runtime is BRB-first rather than a clean generic table runtime plus BRB
  adapter;
- the envelope is hand-built from the existing manifest rather than generated
  through stable model classes;
- CSS is usable but provisional;
- loading and error states are minimal;
- `previous_delta` and `previous_equelo` exist in the manifest but are not yet
  exposed by filters;
- filter grouping is still flat;
- URL state is adequate but not yet a documented contract;
- automated tests do not yet cover the shell.

## Next Experiment

Move to one ordinary chart page.

Preferred candidates:

```text
division_stability
makuuchi_rank_by_era
win_probability_by_standing
```

The purpose is to verify that G1 covers chart PAs without reintroducing an
iframe, copied HTML, or page-specific shell behavior.
