# 02 Rendering Model

## Status

Canonical rendering model for `src.products.make_site`.

This document replaces the scattered rendering material formerly spread across
public UI rendering drafts, ContentPanel notes, Sidebar notes, table styling
notes, and component-specific rendering discussions.

It depends on `01 Public Site Model.md`.

`01 Public Site Model.md` defines the semantic publication model. This document
defines how the standard renderer should make that model visible.

---

# Purpose

The rendering model defines the contract between semantic public-site structures
and rendered public analytical pages.

In short:

```text
semantic publication structures
    -> rendered public analytical pages
```

The renderer should preserve:

- semantic structure,
- ownership boundaries,
- composition relationships,
- public route/page identity,
- option scope,
- notes/provenance scope,
- and artefact status.

The goal is not arbitrary frontend polish. The goal is a renderer that makes the
publication model visible and consistent.

---

# Core Principle

Rendering is the realization of a semantic model.

The key question is not merely:

```text
How should this look?
```

but:

```text
What semantic structure is being realized here?
```

A rendering decision is good when it clarifies the underlying publication
structure.

A rendering decision is suspect when it hides or confuses:

- ownership,
- hierarchy,
- scope,
- analytical meaning,
- interaction responsibility,
- provenance,
- public status,
- or page structure.

---

# Semantic Model vs Rendering Contract

The renderer does not define the semantic model. It realizes it.

## Semantic specification

Defines what exists.

Examples:

```text
PublicUI comprises:
    Navigation
    ContentPanel
```

```text
A Chart may have:
    title
    notes
    controls
    figure
    provenance
```

## Rendering contract

Defines how those things may be acceptably realized.

Examples:

```text
Navigation is rendered as a nested public structure.
```

```text
Chart notes are rendered near the chart when they belong to the chart.
```

```text
Page-level notes are rendered outside individual charts or tables.
```

The renderer must respect the semantic ownership implied by the model.

---

# Standard Page Shell

At the highest level, the standard public UI is rendered as:

```text
PublicUI
  Navigation region
  Content region
```

On desktop-width displays, this is normally realized as:

```text
left navigation region
right content region
```

Responsive layouts may collapse or move regions, but the semantic distinction
must remain.

The navigation region is responsible for publication structure.

The content region is responsible for the active analytical page.

---

# Navigation Rendering

Navigation renders the publication structure.

It is not merely a decorative sidebar.

The renderer should preserve the distinction between:

- hierarchy,
- labels,
- page links,
- active page state,
- collapsed or expanded groups,
- non-clickable structural headings,
- and readiness/status metadata where exposed.

Navigation is conceptually a rooted labelled tree. Rendering should make that
tree understandable.

## Navigation nodes

| Node role | Rendering expectation |
|---|---|
| Page link | Clickable public navigation target |
| Active page link | Clickable target with active-page state |
| Section label | Non-clickable grouping label |
| Collapsible group | Expandable structural grouping |
| Leaf item | Terminal page or label |
| Prototype/legacy item | Visibly statused where appropriate |

The renderer should not collapse all node types into identical links.

## Active state

The active page should be visually identifiable.

Users should be able to determine:

- where they are,
- which page is active,
- and how that page sits within the wider publication hierarchy.

## Navigation depth

Nested structure should be clear but not overwhelming.

Very deep trees should be handled through grouping, indentation, collapsibility,
or other conventions that preserve hierarchy without flooding the page.

---

# ContentPanel Rendering

The ContentPanel is the primary rendered region for analytical content.

It owns page-level presentation structure.

The renderer should clearly distinguish:

- page title,
- page summary or introduction,
- page-level options,
- page-level notes,
- sections,
- charts,
- tables,
- prose,
- controls,
- metadata,
- provenance,
- prototype/legacy embeds.

The ContentPanel should not become an undifferentiated list of visual widgets.
Its rendered structure should communicate the semantic organization of the
active page.

---

# Page Rendering

A Page is rendered as an organized analytical publication unit.

A typical page may include:

```text
Page
  title
  summary/introduction
  page-level status or provenance
  page-level options
  sections
  artefacts
  page-level notes
```

The renderer should preserve the difference between:

- page-level titles and artefact-level titles,
- page-level controls and artefact-level controls,
- page-level notes and artefact-level notes,
- page sections and arbitrary visual boxes,
- public content and diagnostic/prototype content.

## Page title

The page title belongs to the page.

It should not be owned by the first chart, table, section, or embedded artefact
unless the semantic model explicitly says so.

## Page introduction

Introductory text should orient the reader before detailed artefacts appear.

It should be visually distinct from chart notes, table notes, provenance, and
footnotes.

## Page-level controls

Controls that affect the whole page should be rendered at page scope.

They should not be visually embedded inside a chart or table unless their scope
is explicitly local to that artefact.

---

# Section Rendering

Sections organize content inside a page.

A section may contain:

- heading,
- explanatory text,
- charts,
- tables,
- notes,
- controls,
- subsections.

The renderer should make sections visible enough to support comprehension
without over-boxing every block of content.

A section heading owns the content that follows within that section.

Sections should not be confused with arbitrary visual cards.

---

# Published Artefact Rendering

A Published Artefact, or PA, is rendered according to its manifest class and
renderer id.

The renderer should treat PA manifests as intentional site-facing inputs, not as
HTML blobs to be reverse-engineered.

Common PA rendering responsibilities include:

- resolving data sources,
- applying default state,
- rendering consumed options,
- rendering notes/caveats,
- rendering provenance,
- applying validation rules,
- presenting public status clearly.

Different PA classes may have different visual forms, but they should share
common ownership and page-integration conventions.

---

# Chart Rendering

Charts are semantic analytical artefacts.

A rendered chart block may include:

```text
Chart
  title
  subtitle
  controls
  figure
  legend
  notes
  provenance
```

The renderer should preserve the distinction between:

- the chart as an analytical artefact,
- the plotting-library figure,
- surrounding explanatory text,
- chart-local controls,
- page-level context,
- and producer-specific data/config.

## Chart title ownership

A chart title belongs to the chart only when it identifies the analytical
meaning of that chart.

A page title or section title should not be duplicated as a chart title unless
that duplication is intentional and meaningful.

## Chart container

A chart may be visually grouped when the grouping communicates artefact
boundaries.

Boxes should not appear merely because a plotting library or template happens
to emit one.

Ask:

```text
Does this visual boundary clarify the semantic boundary?
```

## Chart notes

Chart notes should be rendered near the chart when they belong specifically to
that chart.

Examples include:

- interpretation notes,
- caveats,
- data provenance,
- methodological comments,
- legend explanations.

Page-level commentary should not be visually attached to an individual chart.

## Chart controls

Controls that affect only one chart should be rendered as chart-local controls.

Controls that affect multiple artefacts should be rendered at the smallest
semantic scope that contains all affected artefacts.

## Plotly and generated figures

Plotly or other figure libraries are implementation mechanisms.

Their generated structure should not decide page-level ownership. The renderer
should wrap or adapt library output so that public-site title, note, control,
and provenance conventions remain consistent.

---

# Table Rendering

Tables are semantic analytical presentations of structured information.

A rendered table block may include:

```text
Table
  title
  subtitle
  controls
  table body
  notes
  provenance
```

The renderer should preserve the difference between:

- raw data,
- analytical table,
- navigational table,
- diagnostic table,
- layout table.

## Column semantics

Columns may carry semantic meaning beyond their displayed labels.

For example, a column may represent:

- identifier,
- metric,
- category,
- rank,
- score,
- label,
- status,
- delta,
- link target,
- explanatory text.

Stable column-level styling and behavior should follow recurring semantics, not
one-off formatting preference.

## Column groups and visibility

Where a table has column groups, presets, or visibility rules, the renderer
should make these understandable as table semantics rather than arbitrary UI
switches.

Visible columns should support the public analytical purpose of the page.

## Table controls

Sorting, filtering, pagination, search, and column visibility should be used
only where they serve the analytical purpose of the table.

A small explanatory table may not need interactive behavior.

A large diagnostic or exploratory table may require it.

## Table notes

Table notes should be rendered near the table when they explain table-specific
structure, caveats, or interpretation.

They should not be used as a substitute for page-level explanation.

---

# Multi-View Rendering

A multi-view artefact renders one selected child artefact from a structured set.

The renderer should distinguish:

- the multi-view container,
- the selected child artefact,
- controls that select the child,
- controls owned by the selected child,
- URL state needed to share the selected view,
- notes/provenance for the container,
- notes/provenance for the child.

Selection UI should make the available alternatives clear without pretending
that diagnostic stages are public concepts unless they have been promoted.

---

# Essay and Prose Rendering

Essay/prose pages should be rendered as first-class public pages, not as
unstructured text dumps.

The renderer should support:

- headings,
- explanatory paragraphs,
- lists,
- callouts or notes,
- embedded charts/tables where semantically owned,
- provenance or method metadata,
- references to related pages.

Prose should integrate with the same page title, navigation, status, and note
ownership conventions as other public pages.

---

# Static HTML and Prototype Embed Rendering

Static/prototype HTML may be included for stress tests, legacy material, or
short-term public-site experiments.

When rendering embedded or copied HTML, the renderer should make status clear
where appropriate:

- canonical public page,
- prototype embed,
- legacy inclusion,
- diagnostic view,
- external/semi-external artefact.

Prototype content should not silently appear to have the same status as a
canonical PA-backed public page.

The renderer should avoid letting embedded HTML determine public shell,
navigation, page title, route, or ownership conventions.

---

# Notes Rendering

Notes are semantic annotation structures.

They should be rendered according to ownership.

A note may belong to:

- page,
- section,
- chart,
- table,
- control group,
- data source,
- producer output.

The renderer should make the note’s scope reasonably clear.

| Note owner | Expected placement |
|---|---|
| Page | Near page intro or page end |
| Section | Within section boundary |
| Chart | Inside or immediately below chart block |
| Table | Inside or immediately below table block |
| Control group | Near the relevant controls |
| Data source | Near provenance or metadata area |

Notes should be visually distinct from primary analytical content, but not so
strongly styled that they dominate the page.

---

# Controls Rendering

Controls should be rendered according to semantic scope.

The key question is:

```text
What does this control affect?
```

Possible scopes include:

- page,
- section,
- chart,
- table,
- multi-view container,
- comparison group,
- global site state.

The renderer should make scope visible.

## Page-level controls

Affect the whole page or a major page-level view.

They should appear before the affected content or in a clearly page-level
control area.

## Artefact-level controls

Affect a single chart, table, or other artefact.

They should appear within the artefact boundary.

## Shared controls

Affect a group of artefacts.

They should appear at the smallest visible container that owns the full affected
group.

Controls should not be placed based only on implementation convenience.

---

# URL State and Shareability

Rendered state that changes public page meaning should be serialisable where
appropriate.

Examples include:

- selected option values,
- selected multi-view child,
- selected table view or preset,
- selected chart variant,
- public filters that materially change interpretation.

Default state need not always appear in the URL.

Non-default state should be represented when shareability matters.

Renderer-owned URL state should not be confused with producer-internal file
names or diagnostic stage names.

---

# Metadata and Provenance Rendering

Analytical public pages often need to communicate provenance.

Metadata may include:

- source data,
- generation date,
- model or artefact version,
- curve/version naming policy,
- audit trail,
- assumptions,
- diagnostic stage,
- publication status.

The renderer should distinguish provenance from ordinary explanatory prose.

Where provenance is important for interpretation, it should be visible enough to
be useful.

Where provenance is secondary, it may be placed in a quieter metadata area.

Internal diagnostic names should not be foregrounded as public names unless they
have been deliberately promoted.

---

# Visual Grouping

Visual grouping should reflect semantic grouping.

Cards, boxes, borders, panels, spacing, and background treatments should clarify
structure, not merely decorate the page.

Before adding a visual boundary, ask:

```text
What semantic boundary does this represent?
```

Before removing a visual boundary, ask:

```text
Will the semantic boundary still be clear?
```

Over-boxing can make pages feel fragmented.

Under-grouping can make ownership unclear.

The renderer should aim for stable, predictable grouping conventions.

---

# Layout

The standard layout should prioritize analytical readability.

Important goals include:

- clear page hierarchy,
- readable chart and table widths,
- stable navigation,
- predictable spacing,
- minimal visual noise,
- clear ownership boundaries,
- coherent relationship between page, section, and artefact levels.

Layout should not be driven primarily by individual artefact implementation.

The page should feel like a coherent analytical publication, not a collection of
unrelated embedded widgets.

---

# Responsive Rendering

Responsive behavior may change visual layout, but not semantic structure.

For example:

- navigation may collapse,
- sidebars may become drawers,
- multi-column layouts may stack,
- tables may scroll,
- chart dimensions may adapt.

However, the renderer should preserve:

- navigation hierarchy,
- active page state,
- title ownership,
- note ownership,
- control scope,
- artefact boundaries,
- public status/provenance.

---

# Interaction Model

Interactions should be predictable and semantically scoped.

Examples include:

- expanding navigation groups,
- selecting views,
- filtering a table,
- changing a chart option,
- toggling diagnostic information,
- opening prototype embeds.

The renderer should avoid interactions whose scope is unclear.

If an interaction affects multiple artefacts, that relationship should be
visible.

---

# Error, Empty, and Missing States

Rendering contracts should include non-happy paths.

Common states include:

- no data,
- missing chart,
- empty table,
- unavailable embed,
- unsupported option,
- stale generated artefact,
- failed data load,
- manifest validation failure.

These should be rendered as explicit publication states rather than accidental
blank space or broken layout.

A missing artefact is still semantically meaningful.

The page should communicate what is missing and, where possible, why.

---

# CSS, Templates, and Components

CSS classes, templates, and components are implementation mechanisms.

They should follow the semantic model rather than define it.

A useful component realizes a stable semantic category.

A questionable component exists only because several things happen to look
similar.

Styling should be organized around semantic roles where possible.

Examples:

```text
navigation-node
page-title
page-summary
page-options
section-heading
chart-block
table-block
multi-view
artefact-note
page-note
control-group
metadata-block
prototype-embed
```

These names are useful only if they reflect real semantic distinctions.

---

# Renderer Conformance Checklist

A renderer conforms to the model when it preserves the semantic structure of the
publication system.

Use these questions as a practical checklist:

## Site and navigation

- Does navigation preserve hierarchy?
- Does it distinguish labels from links?
- Does it expose active-page state?
- Does it avoid deriving public meaning from legacy filenames?
- Does it make prototype/legacy status clear where needed?

## Page structure

- Is the page title owned by the page?
- Is page introduction distinct from artefact notes?
- Are page-level controls placed at page scope?
- Are page-level notes and provenance visually separate from artefact-local material?

## Artefacts

- Are charts, tables, prose, embeds, and multi-view artefacts visually distinct where needed?
- Does each artefact preserve its own title, controls, notes, and provenance?
- Are table column semantics reflected consistently?
- Are Plotly/generated outputs wrapped so that they follow public-site conventions?

## Ownership and scope

- Is it clear what each control affects?
- Is it clear what each note belongs to?
- Is shared state represented at the smallest correct semantic scope?
- Are visual boxes and panels justified by semantic boundaries?

## Public status and provenance

- Is canonical public content distinguishable from prototype, diagnostic, or legacy material?
- Is provenance visible enough for interpretation?
- Are internal diagnostic names kept out of public semantics unless promoted?

## Failure states

- Are empty, missing, failed, or unsupported states rendered explicitly?
- Does the page avoid silent blank regions and broken layout?

---

# Anti-Patterns

The following patterns should be avoided.

## Implementation-first rendering

Rendering should not be determined only by what a library, template, or helper
function happens to emit.

## Ownership confusion

Avoid pages where it is unclear who owns:

- titles,
- notes,
- controls,
- legends,
- captions,
- metadata,
- visual grouping,
- URL state.

## Arbitrary widgetization

Do not turn every repeated visual pattern into a generic widget unless the
underlying semantic category is stable.

## Over-generalized framework design

The goal is not to create a universal UI framework.

The goal is to render this publication grammar clearly.

## Accidental public semantics

Do not let diagnostic file names, old chart stages, or legacy HTML structure
become public concepts by accident.

## Visual inconsistency from implicit semantics

If similar artefacts render differently, the reason should be semantic.

If the reason is accidental implementation history, the rendering model should
be clarified.

---

# Relationship to Public Site Model

`01 Public Site Model.md` defines entities, ownership, and page grammar.

This document defines expected realization.

The two documents should evolve together.

When a rendering question repeatedly arises, it may indicate that the semantic
model is missing a category, boundary, or invariant.

When a semantic distinction is added, this document should explain how it is
made visible.

---

# Current Direction

The rendering system should move toward:

- explicit semantic-to-visual mapping,
- stable ownership conventions,
- predictable chart and table treatment,
- clear navigation structure,
- consistent control placement,
- deliberate note placement,
- explicit public/prototype/diagnostic status,
- visible provenance where useful,
- reduced accidental styling variation.

The aim is not maximal abstraction.

The aim is a renderer that makes the publication model visible.
