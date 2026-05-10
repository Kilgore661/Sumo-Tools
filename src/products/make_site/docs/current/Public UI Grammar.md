# Public UI Grammar

## Status

Current target architecture, created 2026-05-09.

This document specifies the public UI grammar for the generated Sumo-Tools site.
It implements the working requirement:

```text
show me things I want to see in the way we have more-or-less settled on
```

The current implementation does not yet fully satisfy this grammar.  The
purpose of this document is to give the implementation a clear target before
deep-site URLs, BRB, and native table-page rendering are built.

This document deliberately gives little design weight to existing static HTML
artefacts.  If static HTML inclusion gets in the way of the target architecture,
exclude it from the first implementation and restore it later through an
explicit manifest/renderer path.

## Core Model

The public UI has:

```text
navigation
content panel
```

Clicking a navigation node selects a page.  A selected page is rendered in the
content panel.

Every selected page has the same conceptual grammar:

```text
Heading + Options + Published Artefact
```

Where:

* `Heading` is the page title and any immediate page-level framing;
* `Options` is the page state exposed to the reader;
* `Published Artefact` is the thing being shown: table, chart, prose, or
  legacy/static HTML.

The options set may be empty.  A page with no adjustable reader state is still
understood as a page with:

```text
Options = empty
```

This keeps the page grammar uniform.

## Options

Options are state, not widgets.

An option definition records:

* stable id;
* kind;
* label;
* allowed values where applicable;
* default;
* whether it participates in URL state;
* optional presentation hints.

The renderer chooses controls from the option model:

* booleans use checkboxes or toggles;
* exactly-one choices use radio groups, segmented controls, tabs, or dropdowns;
* zero-or-more choices use visible checkbox/toggle-style controls where the
  list is short, and menus/dropdowns where the list is long or cramped;
* numeric values use appropriate numeric controls.

URLs should be explicit.  On arrival, missing option parameters are interpreted
from the option defaults, but the renderer should normalise the address bar to
the explicit canonical state.  For example, if `opt` defaults to `off`, these
inputs are equivalent:

```text
u/N
u/N?opt=off
```

and the canonical address bar should become:

```text
u/N?opt=off
```

This makes copied URLs more descriptive and debugging easier.

## Published Artefact

A Published Artefact is a renderer contract.  It is not necessarily a physical
HTML file.

Each Published Artefact should be described by a PA manifest.  A PA manifest is
an instance of a PA manifest class.  The manifest is the producer/site contract
that identifies the artefact kind, option model, data files, rendering
metadata, notes, and provenance needed by `make_site`.

The manifest class model is specified in `PA Manifest Classes.md`.

Supported target PA manifest classes:

```text
TablePA
ChartPA
MultiViewPA
EssayPA
```

### `TablePA`

Use for tables whose rows and metadata are supplied by producer-written data
and config.

The page renderer owns:

* option controls;
* table HTML;
* visible column rules;
* sorting;
* note/popover behaviour;
* shikona link behaviour;
* URL state.

The producer owns:

* row data;
* option definitions and defaults, where analysis-specific;
* column definitions and sort keys;
* notes;
* provenance.

Examples and candidates:

* Standings by Wins;
* Banzuke Changes after migration;
* future BRB.

### `ChartPA`

Use for charts rendered from producer-written data and chart config.

The page renderer owns:

* option controls, if any;
* chart container and page chrome;
* chart rendering using the chosen browser library;
* URL state for site-owned options.

The producer owns:

* chart data;
* chart-specific config;
* notes;
* provenance.

Current examples are the newer `make_site` chart pages that load CSV/JSON and
render Plotly in browser code.

### `MultiViewPA`

Use when one page can show one of several related artefact views.  A view may
be a chart, a table, or another supported renderer type.

This is not a separate visual style.  It is a page whose options include a view
selector.

Current examples:

* Career Length, where the selected view can be a chart or the Longest table;
* Win Probability by Standing, where options select the source/division/error
  bar display.

Future table pages may also become multi-view if a real public question
requires a choice between multiple tables.

### `EssayPA`

Use for explanatory pages.  The producer may provide Markdown or structured
prose metadata, but not semi-rendered HTML snippets as the public integration
contract.

HTML-fragment/snippet mode has been removed.

## Current Non-Goals

The target grammar does not require:

* a server-side application;
* client-side computation from raw sumo history;
* a full single-page application framework;
* producers owning public app shells for promoted pages;
* semi-rendered HTML snippets.

## Iframe Policy

Iframes are out of the target UI architecture.

The target architecture is direct rendering into generated public pages using
the grammar above.  A page route should identify the selected page.  Page-local
options should be encoded as URL state for that page.

If a current Published Artefact needs an iframe, it is not part of the target
implementation.  Exclude it for now or migrate it into a PA manifest and a
direct renderer.

## URL State

Deep-site URLs should follow the page grammar:

```text
route path  -> selected navigation page
query/hash  -> explicit page-local option state
```

For example:

```text
/sumo-tools/sumo-history/basho-results/?date=2024-09&division=makuuchi
```

The exact query keys are page-owned but must be stable once public.  Shared
renderers may define common key conventions for common concepts such as
division, sort column, sort direction, and visible columns.

Canonical URLs should spell out option state, including defaults.  The option
model remains the source of truth for interpreting missing parameters on
arrival, but normalisation should make the visible URL explicit.

Back/forward behaviour follows from URL state:

* navigating to another page changes the route;
* changing meaningful page options updates URL state;
* restoring a URL restores the page and its options.

## Relationship To Producers

Producers are responsible for analysis-specific knowledge.

For promoted pages, producers should emit a PA manifest that
identifies:

* page metadata;
* PA kind;
* data files;
* options and defaults;
* columns or chart config;
* notes;
* provenance.

`make_site` owns:

* navigation;
* route derivation;
* page chrome;
* option rendering;
* shared table/chart behaviours;
* link behaviour;
* URL state;
* public styling.

The first provisional PA manifest schema for table pages is:

```text
sumo-tools.table-page-bundle.v0
```

The name still says `bundle` because it predates this terminology decision.
Future schema names should prefer `manifest`.

This schema is intentionally provisional and should evolve as Standings,
Banzuke Changes, and BRB expose real renderer needs.

## Legacy Content

Existing complete HTML pages are not part of the target grammar unless they are
given a PA manifest and a direct renderer.

They should not define public routes, site styling, page grammar, or option
state conventions for promoted pages.

When a legacy artefact becomes important enough to behave like a first-class
page, it should be migrated into the manifest/renderer model rather than
wrapped more elaborately.
