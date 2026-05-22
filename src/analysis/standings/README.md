# Standings

The Standings tool produces a static browser page for rolling professional sumo
standings.

Its current user-facing product is **Grand Sumo Standings by Wins Digest**
(GSSWD). The practical question it answers is:

> Who has performed best over a recent rolling period?

The tool is deliberately split into two parts:

- Python code computes and publishes standings data offline.
- A static browser page loads that published data and lets users filter, sort,
  switch views, and inspect the results.

The browser does not compute standings from raw bout history.

## Current Product

The current public page supports:

- selecting a retrospective basho window
- filtering by division
- showing current rikishi only, or all rikishi in the selected window
- switching between Standard, Percentages, and Combined views
- sorting visible columns
- shareable URL state

The current published metric regime is:

- wins are credited wins, including fusensho
- average is credited wins divided by the selected number of basho
- bouts are expected bouts over the selected period
- win percentage is credited wins divided by expected bouts

The default publication settings are currently defined in `publisher.py` and
`files/site_config.json`. At the time of writing, the default browser view is
six basho, Makuuchi, current rikishi only, sorted by average wins.

## What This Is Not

The current product is not a general-purpose historical query engine. It does
not currently expose:

- arbitrary custom date ranges
- user-defined formulas
- selectable win-policy variants
- opponent-strength adjustment
- prediction or forecasting
- advanced statistical dashboards

Some fields in the published CSVs originated during exploratory analysis before
the current product requirements settled. Relative to the current specification,
those fields are diagnostic or latent fields rather than active UI
requirements. They may support future features, but their presence alone should
not be read as a product decision to expose those features.

Examples include fought-vs-credited win fields, selected-vs-containing basho
fields, available-vs-expected bout fields, standard deviations, SEMs, and CI95
half-widths.

## Architecture

The current architecture is a static publication pipeline.

1. Load historical sumo data.
2. Resolve the anchor basho and selected retrospective windows.
3. Compute multiple-basho standings in Python.
4. Derive display fields such as shikona, chii, averages, expected bouts, and
   win percentage.
5. Write one CSV and one JSON sidecar for each supported window.
6. Write `site_config.json` for browser discovery and defaults.
7. Copy static HTML/CSS/JS and current data into a web root.

This keeps hosting simple: the deployed page is just static files plus
precomputed data.

## Main Files

- `multiple_basho.py` contains the core multiple-basho standings aggregation.
- `multiple_basho_view.py` derives display-oriented metrics from the core
  result.
- `multiple_basho_main.py` is a command-line entry point for ad hoc engine
  output.
- `publisher.py` builds the browser-consumable static data set.
- `publisher_reports.py` defines publisher output paths and metadata writers.
- `deploy.py` uploads the static site and data to the remote standings root.
- `files/index.html` is the browser page shell.
- `files/standings.css` is the browser stylesheet.
- `files/standings.js` is the browser behaviour layer.
- `files/site_config.json` is a checked-in sample/current browser config.

## Published Data Contract

The browser expects:

- `site_config.json`
- one CSV per supported basho window
- one JSON sidecar per supported basho window

Current browser-facing fields include:

- `rikishi_id`
- `shikona`
- `chii`
- `chii_ordinal`
- `is_current`
- `credited_wins`
- `selected_average_credited_wins`
- `selected_expected_bout_count`
- `win_percent`

The browser uses these for identity display, filtering, sorting, visible ranking,
and table rendering.

The per-window sidecar JSON provides reporting-period metadata:

- `anchor_date`
- `direction`
- `num_basho`
- `effective_start_date`
- `effective_end_date`

The shared `site_config.json` provides browser discovery and defaults:

- `anchor_token`
- `direction`
- `supported_num_basho`
- `default_num_basho`
- `default_division`

## Browser Behaviour

The browser loads one precomputed CSV/JSON pair at a time. It then:

- filters rows by activity and division
- sorts rows client-side
- computes visible competition positions after filtering
- renders the selected view
- updates sort indicators and notes
- maintains URL state for shareable views

Displayed positions are computed over the currently displayed rows. Filtering by
division or activity changes the comparison population and therefore changes the
displayed positions.

## Running

For ad hoc engine output:

```powershell
python -m src.analysis.standings.multiple_basho_main --date 2026/03 --direction BACKWARDS --num-basho 6 --wins all
```

For the static browser publisher:

```powershell
python -m src.analysis.standings.publisher
```

Be careful with the publisher command: when `publisher.py` is run as a script,
it performs the publisher run and then invokes remote upload via `deploy.py`.
Remote deployment requires `GEOLOCATION` to be set.

The publisher currently also copies static files and latest data to the local
web root configured in `publisher.py`.

## Documentation Map

- `docs/Requirements.md` describes the product need and scope.
- `docs/Specification.md` defines the intended externally visible behaviour.
- `docs/Design & Implementation.md` describes the current implementation.
- `docs/Rationale.md` records why the product and architecture are shaped this
  way.
- `docs/UI Feature Impact Taxonomy.md` is a decision aid for future features.
- `docs/variant_publisher.md` is a draft proposal, not current behaviour.

When docs and code appear to disagree, treat `docs/Specification.md` as the
current statement of intended public behaviour, and `docs/Design &
Implementation.md` as the best guide to current implementation state.

## State of Play

The tool has a working static-publication shape and a browser page with useful
controls. The main caution is that the code and CSV output contain traces of
exploratory analytical work that are broader than the current product surface.

That exploratory surplus is not automatically bad. It is useful context and may
become future capability. But it should not be mistaken for current product
requirements.
