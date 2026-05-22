# Incremental Migration Plan: `make_site` to `make_site2`

## Purpose

`make_site2` is a parallel implementation of the public site builder. Its purpose is not to preserve every behavior of `make_site`, but to prove the new UI model cleanly before replacing the existing package.

The current `make_site` implementation has accumulated several transitional mechanisms:

- a shell that routes selected pages through an iframe;
- page views that may copy or wrap existing HTML entrypoints;
- custom page renderers alongside PA-manifest-backed pages;
- a partially implemented PA runtime;
- a strong documentation model that is ahead of some implementation details.

`make_site2` should start from the new model and migrate incrementally.

The target model is:

```text
PublicUI = Sidebar + ContentPanel

ContentPanel = Heading + Options? + Contents

Contents = PA | PASet

PA = PATitle? + Artifact + Notes?

Artifact = Chart | Table | Prose
```

The first milestone is intentionally narrow:

> Build an iframe-free static shell that renders nav item **7.1 Basho Results / Basho Results Browser / BRB** directly into a shared ContentPanel using the PA model.

BRB is the best starting point because it is already close to the desired architecture: it is PA-backed, data-driven, optioned, table-based, and important enough to exercise the real site model.

---

## Goals

### Primary goals

1. Create a clean `make_site2` package that can evolve independently of `make_site`.
2. Remove the iframe as the normal content-panel mechanism.
3. Render PA-backed content directly inside the main public shell.
4. Use BRB as the first reference implementation.
5. Establish a clear migration path for additional PA types.
6. Keep legacy/copied/free-standing HTML out of the promoted `make_site2` path.

### Non-goals for the first milestone

The first milestone does **not** need to:

* replace `make_site`;
* render every current page;
* support all current custom views;
* support copied standalone HTML;
* perfectly finalize all visual design;
* fully solve every chart/table edge case;
* migrate all archived or prototype content.

The first milestone should prove the architecture, not complete the product.

---

## Key architectural decision

`make_site2` should not inherit the current iframe shell.

Current `make_site` behavior is approximately:

```text
index.html
  sidebar/nav
  iframe
    selected page document
```

The target `make_site2` behavior is:

```text
index.html
  sidebar/nav
  content panel
    PA-rendered page contents
```

In the current shell, clicking a nav item selects a page by setting the iframe source. In `make_site2`, clicking a nav item should select a page by loading or locating the corresponding PA manifest and rendering its content directly into the ContentPanel.

This decision is important because the iframe is not merely a visual implementation detail. It preserves an older page-as-document model. Removing it forces the public UI to become a coherent single model.

---

## Starting point: 7.1 Basho Results / BRB

The first page should be:

```text
Nav item: 7.1 Basho Results
Page id: basho_results_browser
Common name: Basho Results Browser / BRB
PA kind: IndexedTablePA
Renderer: basho_results_table
```

BRB is a good first target because it exercises:

* direct nav-to-content rendering;
* heading and page metadata;
* options;
* indexed data loading;
* table rendering;
* column configuration;
* notes/provenance;
* URL state;
* meaningful user interaction.

It is complex enough to validate the model, but already close enough to the PA-runtime path that it should not require inventing the whole system from scratch.

---

## Proposed package shape

Initial package:

```text
src/products/make_site2/
  __init__.py
  cli.py
  builder.py
  site_model.py
  pa_model.py
  render.py
  site_definition.py
  runtime/
    make_site2.css
    make_site2.js
  files/
  docs/
    01 Incremental Migration Plan.md
```

This structure is only a starting point. The important separation is:

* `site_model.py` defines public-site concepts;
* `pa_model.py` defines or adapts PA/PASet concepts;
* `builder.py` writes the static output;
* `render.py` emits the initial HTML shell and manifest references;
* `runtime/` owns browser-side rendering and interaction;
* `site_definition.py` declares which pages are promoted in `make_site2`.

`make_site2` may copy selected code from `make_site`, but it should avoid importing large compatibility surfaces unless the dependency is explicitly part of the new model.

---

## Migration phases

## Phase 0: Create the empty package and docs

Create:

```text
src/products/make_site2/
src/products/make_site2/docs/
```

Add this migration plan as the first document.

No runtime behavior is required yet.

Deliverable:

```text
src/products/make_site2/docs/01 Incremental Migration Plan.md
```

---

## Phase 1: BRB-only static shell

Build the smallest possible static site shell that can render BRB without an iframe.

The generated site should contain:

```text
index.html
runtime/make_site2.css
runtime/make_site2.js
data/...
manifests/...
```

The shell should include:

```text
Sidebar
ContentPanel
```

The ContentPanel should include:

```text
Heading
Options
Table artifact
Notes
```

Acceptance criteria:

* `index.html` contains no iframe.
* Clicking “Basho Results” does not set `frame.src`.
* The BRB page renders inside the ContentPanel.
* BRB renders from a PA manifest or normalized PA object, not from copied page HTML.
* BRB can load its indexed data.
* BRB options update the rendered table.
* Reloading the page with selected state is possible, at least minimally.

This phase proves the new shell.

---

## Phase 2: Normalize the manifest envelope

Once BRB renders, introduce a stable internal envelope for page content.

The target shape should be close to:

```json
{
  "page": {
    "id": "basho_results_browser",
    "title": "Basho Results",
    "summary": "..."
  },
  "contentPanel": {
    "heading": {},
    "options": [],
    "contents": {
      "kind": "pa",
      "pa": {}
    }
  }
}
```

For multi-view or grouped content:

```json
{
  "contentPanel": {
    "contents": {
      "kind": "paSet",
      "items": []
    }
  }
}
```

This phase should avoid overfitting to BRB. The goal is to clarify the boundary between:

```text
site/page/navigation metadata
content-panel metadata
PA/PASet content
artifact-specific rendering metadata
```

Acceptance criteria:

* BRB renders through the normalized envelope.
* The runtime does not need page-specific knowledge outside the selected artifact renderer.
* The Python builder and browser runtime agree on the manifest shape.
* The envelope can plausibly represent ChartPA, TablePA, IndexedTablePA, EssayPA, and MultiViewPA.

---

## Phase 3: Harden BRB as the reference page

Improve BRB until it can serve as the reference implementation.

Areas to settle:

* option declaration and default values;
* URL state format;
* selected basho/date handling;
* division handling;
* column visibility or column group handling;
* loading states and error states;
* empty table behavior;
* notes/provenance display;
* title/heading hierarchy;
* CSS class naming;
* accessibility basics.

Acceptance criteria:

* BRB is usable as a public page.
* BRB has stable URLs for meaningful selected states.
* The runtime has clear error messages for missing data or invalid state.
* The BRB implementation distinguishes generic table behavior from BRB-specific behavior.

---

## Phase 4: Add one ordinary ChartPA

After BRB works, migrate one comparatively simple chart page.

Candidate examples:

```text
win_probability_by_standing
division_stability
makuuchi_rank_by_era
```

The goal is to prove that `make_site2` is not only an IndexedTablePA renderer.

Acceptance criteria:

* A ChartPA page renders without iframe.
* The page uses the same Sidebar + ContentPanel structure.
* Chart options, if present, use the same option model as BRB.
* Chart notes/provenance use the same PA notes model.
* Chart rendering does not require a copied standalone HTML page.

---

## Phase 5: Add one ordinary TablePA

After BRB and one chart work, add a non-indexed table page.

Candidate:

```text
standings_by_wins
```

This page is valuable because the current implementation may still have a legacy table-app path. Migrating it to `make_site2` should prove that table behavior can be PA-driven instead of copied from an existing HTML app.

Acceptance criteria:

* The table renders through TablePA.
* It does not use `TableAppView`.
* It does not copy an existing HTML entrypoint.
* Sorting/filtering/column behavior is handled through the shared table runtime where possible.
* Any remaining page-specific behavior is explicit.

---

## Phase 6: Add one MultiViewPA / PASet page

Add a page that requires multiple related presentations.

Candidate:

```text
career_length
```

The purpose is to prove the `Contents = PA | PASet` distinction.

Acceptance criteria:

* A PASet or MultiViewPA renders inside the same ContentPanel.
* The selector between views is part of the content model, not an ad hoc page-specific UI.
* Each child PA has a clear title/artifact/notes boundary.
* URL state can represent the selected view.

---

## Phase 7: Decide promoted, prototype, legacy, and excluded pages

Once the first few page types work, define explicit page statuses.

Suggested statuses:

```text
promoted
prototype
diagnostic
legacy
excluded
```

Rules:

* `promoted` pages must render through the `make_site2` PA/PASet path.
* `prototype` pages may be incomplete but should still avoid iframe usage if possible.
* `diagnostic` pages may expose implementation details.
* `legacy` pages may be listed only if explicitly marked as legacy.
* `excluded` pages are not rendered in the public nav.

This should replace accidental inclusion of pages just because `make_site` can build them.

Acceptance criteria:

* Every `make_site2` nav item has an explicit status.
* No copied standalone HTML page appears as promoted content.
* `finish_by_chii` remains excluded or is migrated before promotion.
* Legacy support, if any, is visibly separate from the normal public UI model.

---

## Phase 8: Compare `make_site2` against `make_site`

At this point, run both packages side by side.

Compare:

* visual layout;
* navigation;
* page load behavior;
* URL behavior;
* available pages;
* table behavior;
* chart behavior;
* notes/provenance;
* build complexity;
* runtime complexity;
* maintainability.

The goal is not exact parity. The goal is to determine whether `make_site2` is the better architecture.

Acceptance criteria:

* There is a clear list of pages supported by both.
* There is a clear list of pages intentionally omitted from `make_site2`.
* Regressions are documented.
* Improvements are documented.
* The remaining blockers to replacing `make_site` are concrete.

---

## Phase 9: Replacement decision

Only after `make_site2` has proven the main PA types should the project decide whether to replace `make_site`.

Possible outcomes:

1. `make_site2` becomes the new `make_site`.
2. `make_site2` remains an experimental builder.
3. Selected pieces of `make_site2` are backported into `make_site`.
4. The model is revised again before replacement.

Replacement should require:

* no iframe for promoted pages;
* no copied standalone HTML for promoted pages;
* working BRB;
* at least one ChartPA;
* at least one TablePA;
* at least one PASet/MultiViewPA;
* explicit page statuses;
* stable public theme;
* documented build command;
* documented output structure.

---

## Implementation principles

## 1. Start narrow

The first version should support BRB only.

A small complete vertical slice is better than a broad partial port.

## 2. Prefer direct rendering over compatibility

Do not preserve iframe behavior for promoted pages.

Do not preserve copied standalone HTML as a normal page mechanism.

## 3. Make legacy explicit

Legacy content can exist, but it should not silently define the architecture.

## 4. Keep the PA model central

The public page should be a rendering of PA/PASet content, not an arbitrary document.

## 5. Separate generic runtime from page-specific behavior

Some page-specific renderers may be necessary, especially early on. But the boundary should be visible.

Example:

```text
generic:
  option controls
  content panel layout
  PA title/notes rendering
  table container
  URL state helpers

specific:
  BRB row formatting
  basho/date selector semantics
  sumo-specific table columns
```

## 6. Make state part of the contract

URL state should not be an afterthought.

For BRB, the first required state keys are likely:

```text
page
basho/date
division
column/context options
```

The exact names can change, but the runtime should treat state as a first-class part of the page contract.

## 7. Do not wait for perfect schema design

The first schema only needs to support the first vertical slice cleanly.

It should be easy to revise after BRB, one chart, one table, and one PASet have been migrated.

---

## Initial acceptance test

The first meaningful acceptance test for `make_site2` is:

> Can a user open the generated `index.html`, click **7.1 Basho Results**, and use BRB inside the main page without an iframe?

Detailed checklist:

```text
[ ] Package exists at src/products/make_site2
[ ] Build command exists
[ ] Output includes index.html
[ ] Output includes runtime CSS and JS
[ ] Output includes BRB manifest
[ ] Output includes or references BRB data
[ ] Sidebar includes 7.1 Basho Results
[ ] index.html contains no iframe
[ ] Nav click does not assign frame.src
[ ] ContentPanel renders BRB heading
[ ] ContentPanel renders BRB options
[ ] ContentPanel renders BRB table
[ ] ContentPanel renders BRB notes/provenance
[ ] Changing options updates the table
[ ] URL state is at least minimally supported
[ ] Missing/invalid state produces understandable behavior
```

---

## Suggested first build command

The first command can be provisional. For example:

```bash
python -m products.make_site2.cli --output build/make_site2
```

or:

```bash
python -m products.make_site2 --output build/make_site2
```

The command should be documented as soon as it exists.

---

## Open questions

These do not need to be answered before starting, but they should be tracked.

1. Should manifests be embedded in `index.html`, emitted as JSON files, or both?
2. Should data sources be copied exactly from current output paths or normalized under `make_site2/data/`?
3. How much of the existing PA runtime should be copied versus rewritten?
4. Should `make_site2` use existing PA manifest classes directly or define a normalized intermediate shape?
5. What is the minimum URL-state contract for BRB?
6. How much table behavior can be generic in the first pass?
7. Should page status live in the site definition, the manifest, or both?
8. How should diagnostic/prototype pages appear in the nav?
9. When should `make_site2` begin sharing CSS with `make_site`, if ever?
10. What is the eventual deprecation path for `StandaloneHtmlView`, `TableAppView`, and iframe-based shell rendering?

---

## Current working hypothesis

The project is close enough to begin `make_site2`.

The first useful build is not a full replacement. It is a BRB-only, iframe-free vertical slice that proves the new public UI model.

If that works, the migration should proceed by adding one page type at a time:

```text
1. IndexedTablePA / BRB
2. ChartPA
3. TablePA
4. MultiViewPA / PASet
5. broader promoted-page set
```

The main risk is not that the model is wrong. The main risk is trying to migrate too many legacy mechanisms at once.

The safest path is:

```text
BRB first.
No iframe.
No copied HTML.
Direct ContentPanel rendering.
Then expand.
```
