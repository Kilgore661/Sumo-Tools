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

Metrics presently supplied include:

* Wins
* Average inputs
* Bouts inputs
* Win %
* identity fields
* ordering helpers such as rank-related fields

## Practical note

The browser can therefore remain lightweight and responsive because expensive historical calculations are already complete.

---

# 3. Front-End Structure

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

# 4. JavaScript State Model

The current browser logic uses an explicit state object.

Typical state includes:

* selected number of basho
* selected division
* selected sort key
* sort direction
* selected view mode

This has proven preferable to scattered implicit DOM state.

---

# 5. Rendering Pipeline

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

# 6. View Mode Implementation

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

# 7. Sorting Model

## Current behaviour

User-clickable sortable headers reorder rows client-side.

Sort direction toggles on repeated selection of the same key.

## Current known refinement

If a view change hides the active sort key, sort should revert to default.

This has been identified as required behaviour and may still need hardening depending on current code version.

---

# 8. Position Computation

The browser currently computes displayed positions over the currently visible rows after filtering.

This replaced earlier dependence on backend ranking fields that reflected all rows rather than filtered rows.

This was a major semantic improvement.

## Competition ranking

Equal values may share positions.

Example:

1, 2, 2, 4

---

# 9. Identity Display

Displayed shikona and chii are currently sourced from the most recent basho within the reporting period in which the rikishi appears.

This is an implementation method used to realise the specification concept of end-of-period identity.

Alternative sourcing rules are possible but not currently preferred.

---

# 10. Division Filtering

Current filtering uses displayed division identity derived from the displayed chii.

This is simple and understandable.

More historically strict interpretations were considered but deferred.

---

# 11. CSS / Presentation Layer

## Current principles

* compact dense data-table presentation
* readable but subdued row-number styling
* visual separator between Average and Win % blocks in Combined mode
* conservative colour palette
* desktop-first usability

## Known tuning area

Spacing remains iterative and may be further refined.

---

# 12. Notes System

## Current implementation

Notes are presently embedded in page markup.

Some notes can be shown or hidden by selected view.

## Likely future direction

A structured notes model may later be desirable, where notes are:

* tagged by relevance
* mode-specific
* generated from configuration

Not currently necessary.

---

# 13. Current Technical Debt / Legacy Effects

The project evolved through iterative exploration rather than top-down design.

As a result, some legacy artefacts may still exist:

* terminology drift in code/comments
* historical helper fields no longer semantically primary
* mixed rendering styles
* earlier assumptions preserved in places

This is expected and manageable.

---

# 14. Known Design Tensions

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

# 15. Deferred Ideas

## Automatic ellipsis rows

Rejected/deferred for now.

## Advanced / Expert options panel

Possible future enhancement.

## Alternate win policies

Likely future feature.

## Additional metrics

Possible if justified.

---

# 16. Recommended Next Engineering Steps

1. Verify sort fallback across all view transitions.
2. Harmonise labels in HTML / JS / spec.
3. Simplify view renderers into explicit per-mode logic.
4. Review CSS spacing and visual hierarchy.
5. Remove obsolete backend ranking assumptions.
6. Consolidate comments and internal terminology.

---

# 17. Longer-Term Possible Refactor

If feature scope expands materially:

* formal data contract
* clearer separation of publisher vs browser layers
* componentised UI rendering
* dedicated notes/config system
* stronger automated regression checks

Not presently required.

---

# 18. Governing Principle

The current implementation is intentionally pragmatic.

Where the specification and existing code diverge, code should evolve toward the specification rather than the reverse.

