# 05 Open Issues

## Status

Canonical open-issues register for `src.products.make_site`.

This document replaces the former `TBD Register.md` and consolidates unresolved
work from the implementation notes, rendering notes, feature notes, and current
code review.

It depends on:

- `01 Public Site Model.md`, which defines the intended semantic model;
- `02 Rendering Model.md`, which defines the rendering contracts;
- `03 Implementation State.md`, which describes the current code reality;
- `04 Features and Applications.md`, which records feature-specific decisions.

This document is deliberately actionable.  It should record decisions still to
make, gaps still to close, and checks still to perform.  It should not become a
second design notebook.

---

# Issue Statuses

Use these statuses when maintaining this file:

| Status      | Meaning                                                           |
| ----------- | ----------------------------------------------------------------- |
| Open        | Known issue with no settled solution yet.                         |
| Decided     | Policy is settled but implementation or documentation may remain. |
| In progress | Active implementation or migration work.                          |
| Blocked     | Cannot proceed until another issue or dependency is resolved.     |
| Done        | Completed; remove from this document after the next docs tidy.    |

Default assumption: if an issue is still in this document and has no explicit
status, it is **Open**.

---

# Priority Groups

## P0 — Blocks Public Readiness

These issues should be resolved before treating the generated site as a stable
public surface.

1. Stable public route hierarchy.
2. PA runtime contract coverage for promoted pages.
3. Removal or containment of deep-link/page-specific adapters.
4. Consistent page option and URL-state ownership.
5. Public/research/diagnostic page status policy.
6. Styling consistency audit for public charts and tables.
7. Production build/deployment/cache policy.

## P1 — Important Architectural Clean-up

These issues can coexist with a provisional public site, but should be addressed
before the architecture spreads further.

1. Shared CSS extraction.
2. Semantic table column styling metadata.
3. Shared chart model before site-wide chart styling.
4. Producer contract normalization for current integrated apps.
5. Single source of truth for page defaults.
6. Qualified-shikona/link identity service.
7. Date type boundary policy.

## P2 — Feature and Presentation Refinement

These improve the site but do not block the core architecture.

1. Home-page quick entry points.
2. Glossary and data/method explanation pages.
3. Chart affordance hints.
4. Future feature families such as Equelo records and participation-volume
   exhibits.
5. Detailed career-lifecycle table refinements.

---

# 1. Navigation and Information Architecture

## 1.1 Final Navigation Depth

The development navigation currently exposes a large subject tree.  This is
useful for stress-testing but may be too deep as global public navigation.

Decide which levels belong to:

- global navigation;
- page-local navigation;
- tabs;
- filters/options;
- accordions;
- explanatory sections.

Target principle: global navigation should expose public information structure,
not every implementation subdivision.

## 1.2 Quick Entry Points

The subject-led tree is the canonical information architecture, but casual
visitors may need faster routes into common questions.

Decide whether the home page should include quick links such as:

- latest standings;
- banzuke changes;
- rikishi lookup;
- rank outcomes;
- ratings/model explanation;
- basho results.

If added, quick links should be entry points into the canonical site structure,
not a competing navigation model.

## 1.3 Implemented vs Planned Items

During development, it is useful to distinguish implemented pages from planned
pages.

Before publication, decide whether this distinction should:

- disappear;
- become a subtle status marker;
- remain visible only in development builds;
- or be replaced by explicit public/research/diagnostic status.

## 1.4 Stable Route Hierarchy

The current route hierarchy is still provisional.

Before public linking matters, decide which routes are stable public URLs.  Once
routes are public, changing them should require a deliberate redirect or
compatibility decision.

Open questions:

- Which routes are canonical enough to expose externally?
- Should generated page ids exactly match route ids?
- What is the redirect policy for renamed pages?
- Which routes remain development-only?

## 1.5 Source Layout vs Site Navigation

Some analysis modules have started moving toward a source layout that mirrors
public-site sections, for example career-lifecycle material under
`sumo_history/career_lifecycle`.

Revisit this after more pages exist.

Decision needed: should analysis modules, bundle writers, renderers, docs, and
tests follow the public navigation tree, or should the public tree remain only a
site-layer concept?

---

# 2. Page Contracts and PA Runtime

## 2.1 PA Manifest Contract Coverage

Python dataclasses are currently the canonical in-repo representation for PA
manifests.  `make_site` owns canonical public routes derived from navigation.

Remaining question: do the current manifest classes expose enough metadata for
all promoted page types?

Check coverage for:

- tables;
- indexed tables;
- charts;
- multi-view artefacts;
- essays or narrative pages;
- runtime-loaded data;
- provenance;
- public status;
- notes/caveats;
- option state;
- validation requirements;
- legacy/prototype compatibility.

Do not add manifest fields speculatively.  Add them when a promoted page exposes
a concrete gap.

## 2.2 Page Option Coverage

The settled policy is that options are page state, not widget declarations.

Remaining work:

- add option kinds only when real pages need them;
- define URL-state metadata where needed;
- specify validation rules;
- decide default-state normalization;
- keep option scope visible in rendering.

BRB remains the main forcing example for date/division/table options.

## 2.3 View and PA Type Rationalisation

Target architecture: promoted public pages are rendered from PA manifests by
`make_site`.

Static HTML, iframe wrappers, and custom renderers are allowed as temporary or
exceptional paths, not the default architecture.

Remaining work:

- remove or narrow legacy view types as pages migrate;
- avoid adding new view types unless a real page cannot be expressed through PA
  classes or a deliberately local custom renderer;
- document any retained exceptional view type as exceptional.

## 2.4 Remove Deep-Link Adapters

Current deep-link adapters are scaffolding, not the target architecture.

The target is PA-runtime ownership of:

- option rendering;
- URL state;
- cache-busting;
- shared styling;
- table/chart behaviour;
- state restoration.

Migration rule: when a promoted page still needs page-specific adapter logic,
prefer moving it into a PA manifest/runtime contract rather than extending the
adapter surface.

Completion condition:

```text
no promoted public page needs a bespoke deep-link adapter
```

## 2.5 Shell-to-Page State Contract

The shell owns selected page state.  Individual pages own page-local display
state only when they are still outside the PA runtime.

Target contract:

- shell owns navigation/page identity;
- PA runtime owns promoted page options;
- page manifests declare accepted option state;
- page-specific query parameters do not leak into the shell by accident;
- all meaningful public display state can be shared through URLs.

## 2.6 Single Source of Truth for Page Defaults

Some transitional pages still contain defaults in more than one place, such as
legacy standalone app code, producer-written bundles, and native manifests.

Target policy:

- producer/page contract owns semantic defaults once;
- browser/runtime consumes those defaults;
- JavaScript hardcoded defaults are defensive fallbacks only;
- copied prototype defaults do not become public policy by accident.

---

# 3. Browser State and Shareable URLs

## 3.1 Route and Query Model

The current shell has first-pass deep-link support using shell-owned page state
and page-owned option parameters.

Remaining work: move toward the target route/query model.

Open decisions:

- Should selected page be represented by path rather than `?page=...`?
- Which option values should be omitted when equal to defaults?
- How should invalid or stale option parameters be handled?
- What is the canonical form of a shareable URL?

## 3.2 Back and Forward Buttons

The shell and some participating pages update browser history for page selection
and option changes.

Define push-vs-replace policy for:

- page changes;
- ordinary option changes;
- default-state normalization;
- table sorting;
- chart trace toggles;
- rapid changes such as typing/search/filtering.

Principle: meaningful navigational state should be recoverable; noisy transient
UI interaction should not flood browser history.

## 3.3 Date and Date-Range Parameters

Some pages need a selected basho date or date range.

Policy direction:

- dates/ranges should be page options backed by producer data/config;
- do not multiply one-date HTML artefacts where one parameterized page is the
  intended public concept;
- use the canonical domain date type at domain boundaries;
- serialize explicitly at browser/runtime boundaries.

BRB is the current main example.

---

# 4. Current App Integration

## 4.1 Banzuke Changes Data Source

The current integration consumes Banzuke Changes data from `files/output/bcr`.
Earlier notes record that this depended on copied local-publication data because
regeneration required a missing legacy v9 pickle.

Decision needed: should Banzuke Changes be fully reproducible inside Sumo-Tools
before it is considered final public content?

## 4.2 Standings by Wins Data Source

The current integration consumes standings data from
`files/output/standings/publisher/latest_data`.

Confirm whether this is the intended producer contract or merely a convenient
publisher implementation detail.

## 4.3 `.js.txt` JavaScript Files

Some JavaScript is intentionally stored as `.js.txt` for workflow reasons.

Policy for now:

- preserve filenames expected by source HTML and copied artefacts;
- do not silently normalize `.js.txt` to `.js`;
- revisit only if the workflow changes or the files move fully into shared site
  assets.

## 4.4 Prototype and Embedded Artefacts

Prototype embeds are allowed when they preserve useful work without forcing a
premature migration.

Open questions:

- which embedded/prototype pages are still public candidates;
- which should be marked diagnostic or research;
- which should be replaced by PA-backed pages;
- which should be archived or excluded.

---

# 5. Plotly and Interactive Charts

## 5.1 Plotly Legend Double-Click

Known policy: public Plotly charts should usually disable Plotly's default
legend double-click behavior and use an explicit trace-isolation handler where
needed.

Reference behavior:

- set `layout.legend.itemdoubleclick` to `False`;
- listen for `plotly_legenddoubleclick`;
- perform isolation manually;
- return `false` from the event handler.

Apply this policy unless a chart has a documented reason to keep Plotly's
native behavior.

## 5.2 Plot Titles vs Page Titles

Final public pages should avoid confusing double-title structures.

Policy direction:

- page owns main title and explanatory context;
- chart owns chart-specific labels, axes, legends, hover text, and annotations;
- copied standalone Plotly HTML may retain chart titles during migration only.

## 5.3 Shared Plotly Page Template

Decide when to stop copying standalone Plotly HTML and instead emit:

- chart data;
- chart configuration;
- PA manifest metadata;
- shared public rendering template.

Copying works as a compatibility path.  It should not become the long-term
contract for promoted chart pages.

## 5.4 Chart Model Before Site-Wide Chart Styling

Do not settle a global chart skin until chart manifests expose the semantic
information that styling depends on.

Needed semantics may include:

- axis value types;
- trace roles;
- support/confidence displays;
- legend policy;
- hover text policy;
- public exhibit vs diagnostic/research status;
- comparison view vs single narrative chart.

## 5.5 Support and Confidence Presentation

Charts that imply statistical or model confidence need visible support-aware
interpretation.

Open work:

- show sample size where relevant;
- show confidence intervals or equivalent warnings where useful;
- avoid low-support points looking overprecise;
- decide default support/caveat presentation for public charts.

## 5.6 Large Trace Sets

Investigate readable styling for charts with many traces, especially when
`n > 20`.

Potential dimensions:

- colour;
- dash pattern;
- marker shape;
- line width;
- opacity;
- grouped palettes by division or subject.

This is a readability and interpretability issue, not only a design issue.

## 5.7 Legend vs Page Option

Decide when trace visibility belongs to the Plotly legend and when it should be
a page option.

Use the legend when:

- trace count is modest;
- direct chart toggling is natural;
- trace state does not need canonical URL state.

Use explicit page options when:

- trace universe is large;
- only one or a few traces should normally be visible;
- selection needs URL state, presets, or explanatory grammar.

## 5.8 Full-Height and Percentage Chart Policy

Add chart-level layout policy:

- chart-bearing pages should use available content height deliberately;
- public percentage/probability/CDF/PMF/survival charts should normally default
  to a full 0--100% y-axis unless a page-specific reason is documented;
- dense x-axis labels need explicit review and possibly sparse ticks, shorter
  labels, rotation, zoom defaults, or a different axis treatment.

## 5.9 Plotly Controls Hint

Decide whether public charts need a small, reusable hint that Plotly charts can
be zoomed, panned, autoscaled, reset, or otherwise interacted with.

The hint should not clutter every chart or describe Plotly technically.

## 5.10 Equlo Chart

Investigate the provenance of 6.3.1's Equelo chart data: why are the traces not smooth?

---

# 6. Tables and Shared Presentation

## 6.1 Styling Consistency Audit

Before public readiness, review all public tables and charts for consistency.

Audit:

- table headers;
- sticky behavior;
- notes;
- legends;
- controls;
- chart colours;
- axis ranges;
- spacing;
- link behavior;
- responsive layout;
- public wording;
- table width and centering.

Default table rule: columns should be no wider than their contents require;
tables should be no wider than their columns require; tables should be centered
inside the content area unless a page has a documented reason for full-width
layout.

## 6.2 Site-Wide CSS Rationalisation

Current renderer code still contains repeated inline CSS for shells, option
panels, table panels, notes, links, and dark-theme variables.

Target direction:

- extract shared page, tool, table, chart, control, note, and link styling into
  site-wide CSS assets;
- reserve page-specific CSS for genuine local layout or visualization needs;
- ensure new PA runtime pages inherit shared styling by default.

Coordinate this with direct-rendering and PA-runtime migration.

## 6.3 Semantic Table Column Styling

Implement semantic table column styling metadata when enough examples justify
it.

Candidate metadata:

```text
value_kind
role
alignment
sort_kind
link_kind
```

Candidate shared classes:

```text
value-chii
value-rating
value-row-number
value-record
role-previous
role-context
```

Goal: repeated value types should not drift visually across public tables just
because each page has local CSS.

## 6.4 Sortable Public Tables

Public table columns should be sortable where sorting makes analytical sense.

Rules:

- non-data orientation columns such as row numbers should not be sortable;
- chii-like values must sort by model/order ordinal, not alphabetically;
- hidden or optional columns need explicit fallback behavior if involved in
  default sort;
- first-click direction should be deliberate.

## 6.5 Table Scrolling Policy

For each public table, decide whether scrolling belongs to:

- the browser/page;
- the content panel;
- the table body with sticky headers;
- or a page-specific layout.

Use Career Length -> Longest as the reference for constrained table body
scrolling with visible headers.

## 6.6 Table Header Wording and Wrapping

Review public table headings for natural language and compact layout.

Avoid exposing implementation-style headings such as `after_basho_chii`.
Prefer display labels such as `After Basho Chii`.

When headings are long, prefer controlled line breaks and taller headers over
forcing the whole table wider.

## 6.7 Row Numbers and Orientation Columns

Dense public tables may need an initial muted row-number column for orientation.

Policy direction:

- row numbers are visual/orientation aids;
- they should be visually quiet;
- they should not be sortable;
- they should not be treated as data identity.

Career Length tables are the current forcing case.

---

# 7. Theme, Public Status, and Page Explanation

## 7.1 Shared Public Theme

Not all currently integrated charts and embedded artefacts use the same public
theme or page grammar.

For final public readiness, each promoted page should either:

- conform to the shared public theme;
- or be explicitly framed as legacy, research, diagnostic, or prototype content.

## 7.2 Page Self-Explanation

If the shell no longer shows page summaries, each page must be self-explanatory
enough to stand on its own.

This means:

- good page titles;
- clear controls;
- natural labels;
- concise notes;
- visible caveats where needed;
- no reliance on implementation vocabulary.

It does not mean adding verbose instructions to every page.

## 7.3 Public vs Research vs Diagnostic Status

Decide how to mark content status.

Candidate statuses:

- public-ready;
- candidate;
- research;
- diagnostic;
- legacy;
- superseded;
- excluded.

This should not create a separate top-level expert section unless later
requirements force one.

## 7.4 Glossary and Public Method Notes

The site needs public-facing explanation for core terms and methods.

Glossary candidates:

- basho;
- banzuke;
- chii;
- ChiiLabel;
- rikishi;
- shikona;
- division;
- record;
- fusen;
- east/west;
- sideless chii.

Method/data note candidates:

- data sources;
- update policy;
- parsed history;
- source limitations;
- parser limitations;
- confidence/support;
- curated domains;
- observed data vs model projection;
- what not to infer.

---

# 8. Deployment, Cache, and Build Behaviour

## 8.1 Production Cache Policy

Development builds can add visible cache-busting query parameters. Production
builds should have a deliberate cache policy.

Decide policy for:

- generated HTML;
- shared assets;
- manifests;
- data payloads;
- runtime-loaded JSON/CSV;
- entry routes;
- current-data refreshes.

Likely direction: cache versioned or content-stamped assets aggressively while
keeping entry HTML and current data easy to refresh after publication.

## 8.2 Local and Remote Deployment Contract

The builder can write to `files/output/make_site`, deploy locally, and deploy
remotely.

Document:

- intended publication defaults;
- build-only/local/remote workflows;
- required environment variables or secrets;
- release checklist;
- failure/retry behavior;
- deployment root.

## 8.3 Deployment Root

Keep this distinction explicit:

```text
make_site  = builder package
sumo-tools = public site root
```

The deployed root should be `sumo-tools`, not `site` or `make_site`.

## 8.4 Script Defaults

Top-level producer/build scripts should not need to override ordinary
publication parameters merely to produce the standard current-site build.

Policy direction:

- normal publication path should be the no-surprises default;
- explicit arguments should be reserved for alternatives, diagnostics, or local
  experiments.

---

# 9. Data, Identity, and Domain Boundaries

## 9.1 Qualified Shikona and Graph Links

Qualified shikona for external graph links currently depend on legacy
compatibility material.

Long-term direction:

- graph modules should use stable rikishi identity, preferably RikId;
- duplicate shikona disambiguation should not define Sumo-Tools identity policy;
- legacy qualified-shikona data should remain an explicit compatibility input
  until replaced.

## 9.2 Consolidated Identity/Linking Service

Move consumers of qualified shikona and graph-link behavior to one shared
identity/linking service.

That service should:

- avoid fragile import-time file I/O;
- expose explicit failure/degradation behavior;
- document compatibility boundaries;
- avoid leaking legacy graph-module assumptions into public-site semantics.

## 9.3 Chii and ChiiLabel Naming Policy

Put the naming policy in the main project/site docs and enforce it in generated
metadata and labels.

Policy:

- `Chii` means the class/object;
- `chii` means full human-facing chii values such as `M3eHD`;
- `ChiiLabel` means project-defined chii-like labels such as `M3`, `O`, or
  `Jd100`;
- avoid using `rank` as a loose substitute when the distinction matters.

This matters especially for Equelo rating landmarks.

## 9.4 Date Type Boundary Policy

Use canonical `sumo_core.History.Date` for basho dates wherever domain work is
being done.

Policy direction:

- replace or contain parser `IntDate` where practical;
- cast serialized dates back to `Date` at load boundaries when used for domain
  logic, ordering, lookup, identity, joins, or page-state contracts;
- allow string dates only when they are genuinely display/output text.

---

# 10. Feature-Specific Open Issues

## 10.1 BRB Next Decisions

BRB remains the current forcing feature for PA-runtime tables.

Open issues:

- finalize selected basho/date option semantics;
- confirm table data payload shape;
- confirm division/date/default behavior;
- decide how first-page load chooses the current/default basho;
- decide what public caveats belong on the page;
- validate rating lookup behavior once ratings are added.

## 10.2 Equelo Landmark vs Process Rating Validation

When BRB or another public page exposes fixed_v2 process ratings, compare actual
process ratings against the illustrative `Typical Equelo Ratings` landmarks for
corresponding chii or ChiiLabel values.

Goal: not to force agreement, but to understand how large the gap can be around
boundaries, fast-rising rikishi, absences, protected ranks, and low-support
areas.

Use the result to decide whether public wording needs stronger caveats.

## 10.3 Equelo Experiment Story

Equelo experiment charts are not ready-made public pages, but they may help tell
the methodology story.

Decide whether that story belongs under:

- methodology;
- observed vs modelled;
- ratings explanation;
- research archive;
- or not on the public site.

## 10.4 Division Stability and Churn

The current public division-stability page uses a brittle `num_basho=10` choice.

Decide whether this should become:

- a fixed public default;
- a dropdown/page option;
- a parameterized producer contract;
- or a more carefully named exhibit.

Also confirm whether `division_churn.html` is truly superseded by division
persistence before deleting, hiding, or documenting it.

## 10.5 Career Length Refinements

Open refinements:

- add a muted row-number column to long tables;
- rewrite the `Years` note;
- account more clearly for careers that began before the canonical history
  epoch;
- consider using bio/hatsu data where appropriate;
- replace visible `Active` column with a `Show Active` option if that keeps the
  default table clearer.

## 10.6 Future Public Feature Ideas

Candidate future feature families:

- Equelo Records, including highest observed ratings;
- participation-volume exhibits;
- greatest number of bouts;
- greatest number of wins;
- highest win proportion;
- active/retired breakdowns and leader tables.

Do not implement these inside unrelated page plumbing.  Add them only when they
have a public page concept and producer contract.

## 10.7 Excluded Diagnostic HTML

The first public-site stress test excluded many internal or diagnostic artefacts.

Reconsider excluded artefacts only when a public question gives them a real
role.

Examples that should not be promoted accidentally:

- raw parser warnings;
- weirdness pages;
- old standings diagnostics;
- raw HTML result dumps;
- disposable first-app experiments;
- internal pipeline artefacts.

---

# 11. Browser and CSS Bugs

## 11.1 Firefox Navigation Link Colour

Earlier testing showed Firefox not displaying implemented navigation links in
the expected colour, while Chrome did.

Investigate with browser developer tools:

- computed colour;
- loaded CSS;
- visited-link behavior;
- cache state;
- selector specificity;
- generated classes.

## 11.2 Possible Character-Encoding Issues

Review generated public UI text and manifest/runtime labels for possible
encoding/mojibake problems.

This is not yet confirmed as a defect.  Check actual generated site output,
source file encodings, and browser rendering before making corrective changes.

## 11.3 Show/Hide Navigation Control Placement

Review the shell's show/hide navigation control across desktop and mobile.

Decision needed:

- attached to nav edge;
- inside title bar;
- inside sidebar;
- or another stable shell location.

Apply the same placement policy to ordinary shell pages and PA runtime pages.

---

# 12. Documentation Consolidation Follow-Up

## 12.1 Replace Old Register References

After this document is adopted, update references from:

```text
TBD Register.md
```

to:

```text
05 Open Issues.md
```

## 12.2 Archive Superseded Drafts

Once `01`--`05` are accepted, move superseded thinking-session docs to
`archive/` or delete them under the local archive policy.

Do not archive material until durable decisions have been merged into the
canonical files.

## 12.3 Keep Canonical Docs Small Enough to Maintain

The new document set should not begin reproducing the old proliferation pattern.

Before creating a new doc, ask:

```text
Is this a new stable concept,
or should it be a section in 01--05?
```

## 12.4 Review README

After `01`--`05` settle, update the top-level README so its reading order and
file descriptions match the final filenames.

---

# Current Next Actions

Recommended immediate sequence:

1. Confirm `01`--`05` as the canonical current docs.
2. Update `README.md` to point to the new set.
3. Archive or delete superseded drafts once their durable content is merged.
4. Choose P0 issues for the next implementation pass.
5. Use this file as the working issue register instead of creating new ad-hoc
   notes.
