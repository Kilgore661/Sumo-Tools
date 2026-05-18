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

The first milestone is intentionally narrow:

> Build an iframe-free static shell that renders nav item **7.1 Basho Results / Basho Results Browser / BRB** directly into a shared ContentPanel using the new filter-and-PA model.

BRB is the best starting point because it is already close to the desired architecture: it is PA-backed, data-driven, filterable, table-based, and important enough to exercise the real site model.

---

## Target model

The `make_site2` model starts from a deliberately simple idea:

> Informally, there is one giant table with all the data. We filter/project what we want from the table, and sometimes present the result as a table and sometimes as a chart.

The public UI model should not expose the distinction between row filters, column projections, source selection, measure selection, or similar implementation details unless it becomes necessary later. The reader-facing idea is always:

> show this part of the available view, and ignore the rest.

For that reason, `make_site2` should use **Filter** as the public model term. It should not use **Option** as a model term.

A `PA` remains the public-facing unit of presentable analysis. Conceptually, a non-prose PA is a filtered/projected table-shaped view of the data. It may be rendered as a table or as a chart.

Prose is not a pressure point for the initial model. If needed, prose can be treated as a degenerate table-shaped view, for example a one-column, one-cell view. The immediate goal is to settle table and chart organisation.

### Filter structure

Filters are organised as a structured filter section:

```text
FilterSection -> Filter*

Filter -> SimpleFilter | FilterGroup

FilterGroup -> Tag . Filter+
```

Most filters are simple controls. If one item becomes more complicated, it can become a tagged group.

For example, this flat filter list:

```text
a
b
c
```

can become:

```text
a
B:
  b1
  b2
c
```

without changing the surrounding page model.

A filter may have a label, control type, allowed values, default value, URL-state key, and possibly concise help or popover text.

Filters do **not** have Notes.

### Notes

Notes explain visible table content.

In the initial `make_site2` model:

- notes only pertain to table PAs;
- charts do not have notes;
- filters do not have notes;
- notes are shown only when the relevant table PA is visible;
- if a note explains a column, column group, or table-specific convention, it is shown only when that relevant table feature is visible.

This lets notes be carried at the contents level in the grammar while still being filtered behind the scenes according to the table PA and visible columns/groups they explain.

### Two initial grammars

The current project appears to need two structural cases.

#### G1: contents-level filters

```text
ContentPanel -> Heading . Contents

Contents -> FilterSection . PA+ . Note*

PA -> Title . Artifact
```

G1 is the normal case.

The filter section applies to the contents as a whole. The contents may contain one PA or several PAs. Notes, if present, are contents-level but operationally apply only to visible table PAs or visible table features.

This covers almost all current pages, including pages with one table PA, one chart PA, or several chart PAs sharing the same filter set.

#### G2b: branch-selected contents

```text
ContentPanel -> Heading . Contents

Contents -> BranchSelector . Branch+ . Note*

Branch -> Tag . FilterSection . PA

PA -> Title . Artifact
```

G2b replaces the earlier G2 attempt. G2 modeled a page as multiple structurally present PAs, each with its own filtering. That allowed an implementation to render both a chart and a table simultaneously for Career Length, which is not the intended structure.

G2b handles pages where the contents first choose one branch, then render the selected branch's filters and PA. The unselected branches may exist in the manifest/model, but their PAs are not rendered as active contents.

The current known pressure case is **7.3.1 Career Length**:

```text
Branch = Chart | Table

Chart branch:
  chart = distribution | PMF | CDF | survival
  PA = selected career-length chart

Table branch:
  active = all rikishi | active only
  PA = longest-careers table
```

Only the selected branch's PA is rendered. Table notes are shown only when the selected branch exposes the relevant table PA and table feature.

### Why there are currently two grammars

The aim is not to invent a general-purpose grammar system. The aim is to describe the structures that the current project actually needs.

At present, G1 appears to cover the ordinary case, and G2b appears to cover Career Length. Keeping them separate is useful because it keeps focus on the real distinction:

- in G1, one contents group renders one or more simultaneous PAs with contents-level filters;
- in G2b, one selected branch renders branch-local filters and one PA.

The grammars may later be merged into a single more abstract model, but that should happen only after the case studies have been worked through.

### Relationship to older terms

The older model used language like:

```text
ContentPanel = Heading + Options? + Contents

Contents = PA | PASet

PA = PATitle? + Artifact + Notes?

Artifact = Chart | Table | Prose
```

That wording is now considered transitional.

In `make_site2`:

- use **Filter**, not **Option**;
- do not introduce `PASet` as a first-class target model until the G1/G2b model has been tested against the case studies;
- treat tables and charts as renderings of filtered/projected table-shaped views;
- keep notes table-specific;
- do not attach notes to filters.

---

## Goals

### Primary goals

1. Create a clean `make_site2` package that can evolve independently of `make_site`.
2. Remove the iframe as the normal content-panel mechanism.
3. Render PA-backed content directly inside the main public shell.
4. Use BRB as the first reference implementation.
5. Establish a clear migration path for additional PA shapes and renderings.
6. Keep legacy/copied/free-standing HTML out of the promoted `make_site2` path.
7. Replace the vague “options” model with the filter model.

### Non-goals for the first milestone

The first milestone does **not** need to:

- replace `make_site`;
- render every current page;
- support all current custom views;
- support copied standalone HTML;
- perfectly finalize all visual design;
- fully solve every chart/table edge case;
- migrate all archived or prototype content;
- merge G1 and G2b into a single generalized grammar.

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
    heading
    filters
    PA-rendered contents
    table notes, when applicable
```

In the current shell, clicking a nav item selects a page by setting the iframe source. In `make_site2`, clicking a nav item should select a page by loading or locating the corresponding page/content manifest and rendering its heading, filters, PAs, and table notes directly into the ContentPanel.

This decision is important because the iframe is not merely a visual implementation detail. It preserves an older page-as-document model. Removing it forces the public UI to become a coherent single model.

---

## Starting point: 7.1 Basho Results / BRB

The first page should be:

```text
Nav item: 7.1 Basho Results
Page id: basho_results_browser
Common name: Basho Results Browser / BRB
Current PA kind: IndexedTablePA
Current renderer: basho_results_table
Target grammar: G1
```

BRB is a good first target because it exercises:

- direct nav-to-content rendering;
- heading and page metadata;
- filters;
- indexed data loading;
- table rendering;
- column configuration;
- table notes/provenance;
- URL state;
- meaningful user interaction.

It is complex enough to validate the model, but already close enough to the PA-runtime path that it should not require inventing the whole system from scratch.

In the new model, BRB is a G1 page:

```text
ContentPanel
  Heading: Basho Results
  Contents
    FilterSection
      basho/date
      division
      table/column/context filters
    PA+
      PA: Basho Results table
    Note*
      table notes shown only when relevant table columns/groups are visible
```

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

- `site_model.py` defines public-site concepts;
- `pa_model.py` defines or adapts PA/content concepts;
- `builder.py` writes the static output;
- `render.py` emits the initial HTML shell and manifest references;
- `runtime/` owns browser-side rendering and interaction;
- `site_definition.py` declares which pages are promoted in `make_site2`.

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
FilterSection
Table artifact
Table notes
```

Acceptance criteria:

- `index.html` contains no iframe.
- Clicking “Basho Results” does not set `frame.src`.
- The BRB page renders inside the ContentPanel.
- BRB renders from a manifest or normalized content object, not from copied page HTML.
- BRB can load its indexed data.
- BRB filters update the rendered table.
- Table notes render only when relevant.
- Reloading the page with selected state is possible, at least minimally.

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
    "contents": {
      "grammar": "G1",
      "filters": [],
      "pas": [],
      "notes": []
    }
  }
}
```

For a G2b page, the shape should be close to:

```json
{
  "page": {
    "id": "career_length",
    "title": "Career Length",
    "summary": "..."
  },
  "contentPanel": {
    "heading": {},
    "contents": {
      "grammar": "G2b",
      "branchSelector": {
        "id": "branch",
        "label": "Show",
        "default": "chart",
        "values": [
          { "value": "chart", "label": "Chart" },
          { "value": "table", "label": "Table" }
        ]
      },
      "branches": [
        {
          "id": "chart",
          "tag": "Chart",
          "filters": [],
          "pa": { "id": "career_length_chart", "title": "Charts" }
        },
        {
          "id": "table",
          "tag": "Table",
          "filters": [],
          "pa": { "id": "longest_careers", "title": "Longest Careers" }
        }
      ],
      "notes": []
    }
  }
}
```

The exact JSON is provisional. This phase should avoid overfitting to BRB. The goal is to clarify the boundary between:

```text
site/page/navigation metadata
content-panel metadata
filters
PA content
artifact rendering metadata
table notes
```

Acceptance criteria:

- BRB renders through the normalized envelope.
- The runtime does not need page-specific knowledge outside the selected artifact renderer and table-specific behavior.
- The Python builder and browser runtime agree on the manifest shape.
- The envelope can plausibly represent G1 and G2b pages.
- The envelope does not use `Option` as a model term.

---

## Phase 3: Harden BRB as the reference page

Improve BRB until it can serve as the reference implementation.

Areas to settle:

- filter declaration and default values;
- URL state format;
- selected basho/date handling;
- division handling;
- column visibility or column group handling;
- loading states and error states;
- empty table behavior;
- table notes/provenance display;
- title/heading hierarchy;
- CSS class naming;
- accessibility basics.

Acceptance criteria:

- BRB is usable as a public page.
- BRB has stable URLs for meaningful selected states.
- The runtime has clear error messages for missing data or invalid state.
- The BRB implementation distinguishes generic table behavior from BRB-specific behavior.
- Notes are shown only for visible relevant table content.

---

## Phase 4: Add one ordinary chart page

After BRB works, migrate one comparatively simple chart page.

Candidate examples:

```text
win_probability_by_standing
division_stability
makuuchi_rank_by_era
```

The goal is to prove that `make_site2` is not only a table renderer.

A chart page should still be understood as a PA over a table-shaped view. The chart artifact is the way that view is presented.

Acceptance criteria:

- A chart page renders without iframe.
- The page uses the same Sidebar + ContentPanel structure.
- Chart filters, if present, use the same filter model as BRB.
- Chart rendering does not require a copied standalone HTML page.
- Chart pages do not introduce chart notes.

---

## Phase 5: Add one ordinary table page

After BRB and one chart work, add a non-indexed table page.

Candidate:

```text
standings_by_wins
```

This page is valuable because the current implementation may still have a legacy table-app path. Migrating it to `make_site2` should prove that table behavior can be PA-driven instead of copied from an existing HTML app.

Acceptance criteria:

- The table renders through the new content/PA model.
- It does not use `TableAppView`.
- It does not copy an existing HTML entrypoint.
- Sorting, pagination, and other table-internal interactions are handled by the table runtime and are not model-level filters unless explicitly promoted.
- Filter and column behavior is handled through the shared filter/table runtime where possible.
- Any remaining page-specific behavior is explicit.

---

## Phase 6: Add the G2b pressure case: Career Length / 7.3.1

Add the known page that requires branch-selected contents and branch-local filters.

Candidate:

```text
career_length
```

The purpose is no longer to prove `Contents = PA | PASet`. The purpose is to prove G2b:

```text
ContentPanel -> Heading . Contents

Contents -> BranchSelector . Branch+ . Note*

Branch -> Tag . FilterSection . PA

PA -> Title . Artifact
```

Career Length should not be treated as five flat views or two simultaneous PAs. It should be treated as a branch-selected page:

```text
Branch = Chart | Table

Chart branch:
  filter:
    chart = distribution | PMF | CDF | survival
  PA:
    selected career-length chart

Table branch:
  filter:
    active = all rikishi | active only
  PA:
    longest-careers table
```

Only the selected branch's PA is rendered.

The visual design may render the branch selector and branch-local filters together in one grouped filter area:

```text
Show:
  Chart | Table

Chart:
  Distribution
  PMF
  CDF
  Survival

Table:
  All rikishi
  Active only
```

or with equivalent controls. The important point is that only one branch is active at a time.

Acceptance criteria:

- Career Length renders inside the same ContentPanel, without iframe.
- Career Length is represented as a G2b page.
- It has a branch selector: Chart | Table.
- The Chart branch has a chart filter with four values.
- The Table branch has an active-status filter.
- The chart and table are not rendered simultaneously.
- These controls are represented as filters, not options or views.
- The URL state can represent the selected branch, selected chart filter, and active-status filter.
- Any table notes apply only to the relevant table PA and visible table features.

---

## Phase 7: Add `finish_by_chii` as a migrated G1 chart group

`finish_by_chii` is currently outside the target PA architecture because it comes from standalone HTML. It should not remain permanently excluded if it belongs in the public project.

When migrated, it should be treated as a G1 page:

```text
ContentPanel
  Heading
  Contents
    FilterSection
      shared filters
    PA+
      chart PA
      chart PA
      chart PA
    Note*
      empty
```

The important point is that `finish_by_chii` is not a special selector case. Its PAs are charts, and its filters apply to the chart group as a whole.

Acceptance criteria:

- `finish_by_chii` no longer uses `StandaloneHtmlView`.
- It does not copy an existing standalone HTML document.
- It renders without iframe.
- It is represented as a G1 page.
- Shared filters apply across the chart PA group.
- It has no notes unless a future table PA is introduced.

---

## Phase 8: Decide promoted, prototype, legacy, and excluded pages

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

- `promoted` pages must render through the `make_site2` content/PA path.
- `prototype` pages may be incomplete but should still avoid iframe usage if possible.
- `diagnostic` pages may expose implementation details.
- `legacy` pages may be listed only if explicitly marked as legacy.
- `excluded` pages are not rendered in the public nav.

This should replace accidental inclusion of pages just because `make_site` can build them.

Acceptance criteria:

- Every `make_site2` nav item has an explicit status.
- No copied standalone HTML page appears as promoted content.
- `finish_by_chii` is either migrated as G1 or remains explicitly marked as not yet migrated.
- Legacy support, if any, is visibly separate from the normal public UI model.

---

## Phase 9: Compare `make_site2` against `make_site`

At this point, run both packages side by side.

Compare:

- visual layout;
- navigation;
- page load behavior;
- URL behavior;
- available pages;
- table behavior;
- chart behavior;
- filter behavior;
- table notes/provenance;
- build complexity;
- runtime complexity;
- maintainability.

The goal is not exact parity. The goal is to determine whether `make_site2` is the better architecture.

Acceptance criteria:

- There is a clear list of pages supported by both.
- There is a clear list of pages intentionally omitted from `make_site2`.
- Regressions are documented.
- Improvements are documented.
- The remaining blockers to replacing `make_site` are concrete.

---

## Phase 10: Replacement decision

Only after `make_site2` has proven the main content shapes should the project decide whether to replace `make_site`.

Possible outcomes:

1. `make_site2` becomes the new `make_site`.
2. `make_site2` remains an experimental builder.
3. Selected pieces of `make_site2` are backported into `make_site`.
4. The model is revised again before replacement.

Replacement should require:

- no iframe for promoted pages;
- no copied standalone HTML for promoted pages;
- working BRB;
- at least one ordinary chart page;
- at least one ordinary table page;
- Career Length represented as a G2b page;
- `finish_by_chii` either migrated or explicitly excluded;
- explicit page statuses;
- stable public theme;
- documented build command;
- documented output structure.

---

## Model case studies

The case studies are the next important task after this plan. They should verify that the G1/G2b model actually describes the current project.

Initial working partition:

```text
G1:
  7.1 Basho Results / BRB
  ordinary chart pages
  ordinary table pages
  finish_by_chii, once migrated

G2b:
  7.3.1 Career Length
```

Each case study should record:

```text
nav item
page id
grammar: G1 or G2b
PA list
filter structure
artifact rendering
table notes, if any
URL-state implications
migration risks
```

The case-study pass should be allowed to revise the model if it exposes a real current feature that is not G1 or G2b.

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

The public page should be a rendering of filtered PA content, not an arbitrary document.

## 5. Use filters, not options

Do not use `Option` as a model term in `make_site2`.

Use `Filter` for reader-visible controls that restrict what part of the available view is shown.

Implementation code may still need to know whether a filter acts as a row filter, column projection, source selection, or measure selection, but those distinctions are not separate public UI concepts.

## 6. Keep notes table-specific

Filters do not have notes.

Charts do not have notes.

Notes explain visible table content and should only be shown when the relevant table PA and table feature are visible.

## 7. Separate generic runtime from page-specific behavior

Some page-specific renderers may be necessary, especially early on. But the boundary should be visible.

Example:

```text
generic:
  filter controls
  content panel layout
  PA title rendering
  table notes rendering
  table container
  URL state helpers

specific:
  BRB row formatting
  basho/date semantics
  sumo-specific table columns
```

## 8. Make state part of the contract

URL state should not be an afterthought.

For BRB, the first required state keys are likely:

```text
page
basho/date
division
column/context filters
```

The exact names can change, but the runtime should treat state as a first-class part of the page contract.

For Career Length, the state should distinguish:

```text
selected chart filter
active-status table filter
```

## 9. Do not wait for perfect schema design

The first schema only needs to support the first vertical slice cleanly.

It should be easy to revise after BRB, one chart page, one table page, and Career Length have been migrated.

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
[ ] Output includes BRB manifest/content envelope
[ ] Output includes or references BRB data
[ ] Sidebar includes 7.1 Basho Results
[ ] index.html contains no iframe
[ ] Nav click does not assign frame.src
[ ] ContentPanel renders BRB heading
[ ] ContentPanel renders BRB filter section
[ ] ContentPanel renders BRB table
[ ] ContentPanel renders relevant BRB table notes/provenance
[ ] Changing filters updates the table
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

1. Should manifests/content envelopes be embedded in `index.html`, emitted as JSON files, or both?
2. Should data sources be copied exactly from current output paths or normalized under `make_site2/data/`?
3. How much of the existing PA runtime should be copied versus rewritten?
4. Should `make_site2` use existing PA manifest classes directly or define a normalized intermediate shape?
5. What is the minimum URL-state contract for BRB?
6. How much table behavior can be generic in the first pass?
7. Should page status live in the site definition, the manifest/content envelope, or both?
8. How should diagnostic/prototype pages appear in the nav?
9. When should `make_site2` begin sharing CSS with `make_site`, if ever?
10. What is the eventual deprecation path for `StandaloneHtmlView`, `TableAppView`, and iframe-based shell rendering?
11. Can G1 and G2b later be merged into a single cleaner grammar without obscuring filter scope?
12. Does any current case study require a grammar beyond G1 and G2b?
13. What exact note applicability tags are needed for table columns and column groups?

---

## Current working hypothesis

The project is close enough to begin `make_site2`.

The first useful build is not a full replacement. It is a BRB-only, iframe-free vertical slice that proves the new public UI model.

If that works, the migration should proceed by adding one content shape at a time:

```text
1. G1 Indexed table / BRB
2. G1 ordinary chart page
3. G1 ordinary table page
4. G2b Career Length
5. G1 finish_by_chii chart group
6. broader promoted-page set
```

The main risk is not that the model is wrong. The main risk is trying to migrate too many legacy mechanisms at once, or allowing old vocabulary such as “options” and “views” to smuggle implementation assumptions back into the model.

The safest path is:

```text
BRB first.
No iframe.
No copied HTML.
Filters, not options.
Direct ContentPanel rendering.
Table-specific notes only.
Then expand through the case studies.
```
