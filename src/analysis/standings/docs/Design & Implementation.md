# GSSWD - Design and Implementation Notes (Temporary Working Document)

## Status

Informal technical companion to the current specification.

This document records how the standings page is presently designed and implemented, together with known partial solutions and likely future design directions.

It is descriptive rather than normative.

---

# 1. Architecture Overview

The application currently follows a static-publication model.

## Offline responsibilities

Python tooling prepares published standings artefacts from historical sumo data.

These artefacts contain precomputed standings metrics for supported retrospective basho windows.

## Browser responsibilities

The browser currently handles:

* loading published artefacts
* user control interaction
* filtering rows
* sorting rows
* recalculating visible positions where required
* rendering tables
* rendering titles and notes
* switching table views

The browser does **not** compute standings metrics from raw bout history.

---

# 2. Publication Layer

## Current shape

The publication process emits browser-consumable datasets for each supported basho window.

These are currently backed by Python modules in the standings toolchain.

Each supported window has:

* one CSV data file
* one JSON sidecar file

The publication layer also writes a shared `site_config.json` file.

## Browser-facing files

The browser currently expects:

* `site_config.json`
* `multiple basho standings view (...).csv`
* `multiple basho standings view (...).json`

The CSV contains row data.

The per-window JSON sidecar contains reporting-period metadata.

The shared `site_config.json` contains discovery and default-selection metadata.

## Practical note

The browser can therefore remain lightweight and responsive because expensive historical calculations are already complete.

The browser must not recompute core standings metrics from raw bout history. It loads, filters, sorts, computes visible display positions, and renders precomputed fields.

---

# 3. Published Data Contract

The published CSV now contains more fields than the main table currently displays.

This is intentional.

Some fields are part of the current browser-facing contract:

* `rikishi_id`
* `shikona`
* `chii`
* `chii_ordinal`
* `is_current`
* `credited_wins`
* `selected_average_credited_wins`
* `selected_expected_bout_count`
* `win_percent`

These fields are used directly for identity display, activity filtering, division filtering, visible metrics, sorting, and ranking.

Other published fields are present for diagnostics, future variants, or analytical reuse:

* fought-vs-credited win fields
* selected-vs-containing basho counts
* expected-vs-available bout counts
* selected and containing averages
* standard deviation fields
* SEM fields
* CI95 half-width fields

These fields should not be treated as current public UI requirements merely because they are published.

They do, however, form part of the practical data shape emitted by the publisher.

## Per-window sidecar JSON

Each per-window sidecar JSON file describes the reporting window represented by the matching CSV.

It currently contains:

* `anchor_date`
* `direction`
* `num_basho`
* `effective_start_date`
* `effective_end_date`

The browser uses this metadata to label the selected reporting period.

## Site config JSON

`site_config.json` is the browser's discovery/configuration file.

It currently contains:

* `anchor_token`
* `direction`
* `supported_num_basho`
* `default_num_basho`
* `default_division`

Changing supported windows, the anchor token, direction, or default selections should be understood as a publication/configuration change rather than an HTML-template edit.

---

# 4. Publication and Deployment Path

The current publisher performs both data publication and deployment preparation.

Typical flow:

1. `publisher.py` loads history.
2. It resolves the current anchor basho.
3. It creates a timestamped run directory under `files/output/standings/publisher/runs/`.
4. It writes `site_config.json` for the run.
5. It writes one CSV and one JSON sidecar for each supported basho window.
6. It refreshes the latest-data directory used for deployment.
7. It copies static files and latest data to the local web root.

When `publisher.py` is run as `__main__`, it also invokes the remote deployment helper.

## Static files

The static browser shell is currently made from:

* `index.html`
* `standings.css`
* `standings.js.txt`

These files are copied alongside the generated data files.

## Latest data

The timestamped run output records each publisher run.

The latest-data directory is the deployment source for the current published state.

This keeps historical run artefacts separate from the files served by the browser.

## Local deployment

Local deployment copies static files and latest CSV/JSON data into the configured local web root.

This supports manual browser inspection without requiring a live server-side computation system.

## Remote deployment

Remote deployment uploads:

* static browser files to the remote standings root
* current CSV/JSON data files to the remote `data` directory

The current remote target is `/var/www/html/standings`.

Remote deployment requires the `MY_SFTP_PASS` environment variable to be set.

No deployment password should be stored in source.

---

# 5. Front-End Structure

The current page is a conventional static web page composed of:

* HTML template
* CSS stylesheet
* JavaScript behaviour layer

## HTML role

The HTML serves two purposes:

1. live application shell
2. editable template for future WYSIWYG/manual refinement

Therefore some default/demo content has intentionally been retained.

---

# 6. JavaScript State Model

The current browser logic uses an explicit state object.

Typical state includes:

* selected number of basho
* selected division
* selected sort key
* sort direction
* selected view mode
* selected activity filter

This has proven preferable to scattered implicit DOM state.

---

# 7. Rendering Pipeline

The current browser behaviour is increasingly organised around a render cycle.

Typical flow:

1. read current state
2. load current dataset
3. filter rows
4. sort rows
5. compute visible ranking positions
6. render titles / headings
7. render table body
8. update notes / view-dependent elements

A single top-level render path is preferred over many partial refresh functions.

---

# 8. View Mode Implementation

## Current modes

* Standard
* Percentages
* Combined

## Present implementation style

Originally implemented as column visibility toggling.

Later development moved toward mode-specific row rendering.

This is an improvement because the three modes increasingly represent different table grammars rather than one table with hidden columns.

## Likely future direction

Treat each mode as a purpose-specific renderer sharing common data/state.

---

# 9. Sorting Model

## Current behaviour

User-clickable sortable headers reorder rows client-side.

Sort direction toggles on repeated selection of the same key.

## Current known refinement

If a view change hides the active sort key, sort should revert to default.

This has been identified as required behaviour and may still need hardening depending on current code version.

---

# 10. Position Computation

The browser currently computes displayed positions over the currently visible rows after filtering.

This replaced earlier dependence on backend ranking fields that reflected all rows rather than filtered rows.

This was a major semantic improvement.

## Competition ranking

Equal values may share positions.

Example:

1, 2, 2, 4

---

# 11. Identity Display

Displayed shikona and chii are currently sourced from the most recent basho within the reporting period in which the rikishi appears.

This is an implementation method used to realise the specification concept of end-of-period identity.

Alternative sourcing rules are possible but not currently preferred.

---

# 12. Division Filtering

Current filtering uses displayed division identity derived from the displayed chii.

This is simple and understandable.

More historically strict interpretations were considered but deferred.

---

# 13. CSS / Presentation Layer

## Current principles

* compact dense data-table presentation
* readable but subdued row-number styling
* visual separator between Average and Win % blocks in Combined mode
* conservative colour palette
* desktop-first usability

## Known tuning area

Spacing remains iterative and may be further refined.

---

# 14. Notes System

## Current implementation

Notes are presently embedded in page markup.

Some notes can be shown or hidden by selected view.

Some table headers can show a small notes popover that links to the relevant note.

## Likely future direction

A structured notes model may later be desirable, where notes are:

* tagged by relevance
* mode-specific
* generated from configuration

Not currently necessary.

---

# 15. URL State

The browser supports query-string state for shareable and navigable views.

Current URL state may include:

* selected basho count
* selected division
* selected view mode
* selected activity filter
* sort column
* sort identifier
* sort direction

Invalid URL state is rejected and the page falls back to defaults.

The URL feature is presentation-layer behaviour. It does not change the published data contract.

---

# 16. Current Technical Debt / Legacy Effects

The project evolved through iterative exploration rather than top-down design.

As a result, some legacy artefacts may still exist:

* terminology drift in code/comments
* historical helper fields no longer semantically primary
* mixed rendering styles
* earlier assumptions preserved in places

This is expected and manageable.

---

# 17. Known Design Tensions

## Simplicity vs Power

Casual users prefer simple rankings.

Advanced users want richer metrics.

View modes are the current compromise.

## Static publishing vs flexibility

Static artefacts keep operations simple.

However, some future features may favour richer runtime behaviour.

## Uniform tables vs purpose-specific tables

Uniform structure simplifies code.

Purpose-specific views better match user intent.

Current direction favours purpose-specific views.

---

# 18. Deferred Ideas

## Automatic ellipsis rows

Rejected/deferred for now.

## Advanced / Expert options panel

Possible future enhancement.

## Alternate win policies

Likely future feature.

## Additional metrics

Possible if justified.

---

# 19. Recommended Next Engineering Steps

1. Verify sort fallback across all view transitions.
2. Simplify view renderers into explicit per-mode logic.
3. Review CSS spacing and visual hierarchy.
4. Remove obsolete backend ranking assumptions.
5. Consolidate comments and internal terminology.
6. Consider a formal schema/check for published CSV and JSON artefacts.

---

# 20. Longer-Term Possible Refactor

If feature scope expands materially:

* formal data contract
* clearer separation of publisher vs browser layers
* componentised UI rendering
* dedicated notes/config system
* stronger automated regression checks

Not presently required.

---

# 21. Governing Principle

The current implementation is intentionally pragmatic.

Where the specification and existing code diverge, code should evolve toward the specification rather than the reverse.
