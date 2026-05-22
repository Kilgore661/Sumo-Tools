# Public UI Grammar — Specification v2 (Draft)

## What Has Been Achieved

This work began as an attempt to understand rendering inconsistencies across a set of analytical publication pages.

Initially the observed problems appeared local and implementation-specific:

* duplicated headings,
* inconsistent chart framing,
* inconsistent table framing,
* differing option layouts,
* duplicated CSS,
* unclear ownership of labels and notes.

However, investigation showed that these were not primarily styling problems.

They were symptoms of an insufficiently explicit semantic model.

The project already contained strong recurring structures:

* navigation trees,
* grouped options,
* page headings,
* analytical artefacts,
* contextual notes,
* stable publication patterns.

The task therefore became:

```text
make implicit semantic structure explicit
```

rather than:

* introduce a frontend framework,
* build a component library,
* or create an executable UI DSL.

The resulting approach treats the public UI as a constrained publication grammar.

The specification is:

* semantic,
* normative,
* and descriptive.

It is not currently intended to be:

* executable,
* renderer-driven,
* or framework-like.

Its purpose is:

* architectural clarity,
* renderer conformance discussion,
* semantic consistency,
* and stabilization of ownership boundaries.

---

# Fundamental Principles

## 1. Semantic Structure Precedes Rendering

The specification defines:

* what entities exist,
* what they mean,
* how they compose,
* and what they own.

Rendering choices are secondary.

---

## 2. Rendering is a Realization of Semantic Structure

A renderer realizes the semantic structure into:

* HTML,
* CSS,
* JavaScript,
* and interaction patterns.

A renderer may vary in implementation while remaining conformant to the specification.

---

## 3. The Specification is Normative Rather Than Executable

The notation used here:

* algebraic signatures,
* grammar-like notation,
* and prose rules,

exists for:

* thought,
* communication,
* and evaluation.

It is not currently intended as:

* renderer input,
* runtime data,
* or executable infrastructure.

---

## 4. Ownership Boundaries Matter

A major outcome of the work is the clarification of ownership.

The ownership hierarchy is:

```text
Caption:
    site identity

Heading:
    page identity

PATitle:
    artefact identity

Artifact:
    owns no caption/title
```

This distinction removes ambiguity and duplicated structure.

---

# Top-Level Grammar

```text
PublicUI
    = Sidebar + ContentPanel

Sidebar
    = Caption + Navigation + Hider

ContentPanel
    = Heading + Options + PA

PA
    = PATitle? + Artifact + Notes?

PATitle
    = PAHead + PASubHead?

Artifact
    = Chart | Table | Prose
```

---

# PublicUI

## Definition

```text
PublicUI
    = Sidebar + ContentPanel
```

`PublicUI` is the complete public-facing page structure.

---

# Sidebar

## Definition

```text
Sidebar
    = Caption + Navigation + Hider
```

The Sidebar is the persistent site-level navigation structure.

It comprises:

* site identity,
* navigation hierarchy,
* and sidebar visibility controls.

---

# Caption

## Semantics

Caption represents:

* site identity,
* publication identity,
* or installation identity.

Caption is distinct from:

* page identity,
* artefact identity,
* and Artifact framing.

---

# Navigation

## Definition

```text
Navigation
    = rooted labelled tree
```

More formally:

```text
Navigation ::= NavNode

NavNode ::=
    id
    label
    target?
    children*
```

---

## Derived Predicates

```text
leaf(node)
    = node has no children

clickable(node)
    = node has target
```

---

## Semantics

Navigation expresses:

```text
where the user is
```

and:

```text
where the user may go
```

within the site structure.

---

# Hider

## Semantics

Hider is a UI-shell visibility control.

Hider allows:

* hiding,
* collapsing,
* or restoring

the Sidebar.

---

## Important Distinction

Hider is not an Option.

Options affect:

```text
how the current PA is viewed
```

Hider affects:

```text
how the UI shell itself is realized
```

---

# ContentPanel

## Definition

```text
ContentPanel
    = Heading + Options + PA
```

`ContentPanel` represents the currently visible publication page.

---

# Heading

## Definition

```text
Heading
    = MainHeading + SubHeading?
```

---

## Semantics

Heading owns:

* page framing,
* page identity,
* and publication naming.

Heading does not own artefact framing.

---

# Options

## Definition

```text
Options
    = rooted tree of option nodes
```

More formally:

```text
Options ::= OptionGroup

OptionGroup ::=
    label?
    children*

children ::=
    OptionGroup | Option
```

---

## Option

```text
Option ::=
    id
    label
    kind
    default
    admissible_values?
```

Typical kinds include:

* boolean,
* enum,
* integer,
* float,
* text,
* multi-enum.

---

## Semantics

Options represent:

```text
reader-adjustable semantic state
```

Examples include:

* filtering,
* artefact selection,
* display configuration,
* and analytical configuration.

Options answer:

```text
how am I viewing this?
```

---

## Important Distinction

Options are not controls.

The specification defines semantic adjustable state.

The renderer chooses:

* dropdowns,
* checkboxes,
* tabs,
* segmented controls,
* etc.

---

# Published Artefact (PA)

## Definition

```text
PA
    = PATitle? + Artifact + Notes?
```

PA comprises:

* optional artefact framing,
* the currently displayed Artifact,
* and optional Notes.

PATitle may be empty.

This allows:

* stable page framing,
* while Options change the currently displayed Artifact.

---

# PATitle

## Definition

```text
PATitle
    = PAHead + PASubHead?
```

---

## Semantics

PATitle provides framing for the currently displayed Artifact.

PATitle is distinct from:

* site identity,
* page identity,
* and Artifact internals.

PATitle does not belong to the Artifact.

---

# Artifact

## Definition

```text
Artifact
    = Chart | Table | Prose
```

---

## Semantics

Artifacts are opaque to the publication grammar.

The grammar does not inspect:

* Plotly internals,
* table implementation details,
* rendering-library structures.

Artifacts are treated as black boxes with external contracts.

Artifacts do not own captions/titles.

If artefact framing is required, it is supplied externally by PATitle.

---

# Chart

## Semantics

A Chart is a black-box visual representation.

Charts may internally contain:

* axis labels,
* legends,
* trace labels,
* annotations,
* interaction affordances.

Charts do not own captions/titles.

If chart framing is required, it is supplied by PATitle.

---

# Table

## Semantics

A Table is a black-box tabular representation.

Tables may internally contain:

* column headings,
* row labels,
* group labels,
* sorting indicators.

These are internal structural labels, not publication framing.

Tables do not own captions/titles.

If table framing is required, it is supplied by PATitle.

---

# Prose

## Semantics

Prose is a textual representation.

The exact structure of Prose remains intentionally under-specified in this draft.

---

# Notes

## Definition

```text
Notes
    = Note*
```

---

## Note

```text
Note
    = content
```

---

## Semantics

Notes provide:

* explanation,
* qualification,
* interpretation,
* and contextualization

for the currently displayed Artifact.

Notes are distinct from:

* page headings,
* PATitle,
* Artifact internals,
* and navigation structure.

---

# Renderer Conformance

The purpose of the specification is to support questions such as:

```text
Does this renderer conform to the specification?
```

Examples:

* Does the renderer preserve Navigation hierarchy?
* Does it distinguish links from labels?
* Does it preserve Heading ownership?
* Does it preserve PATitle ownership?
* Does it avoid artifact-owned titles?
* Does it expose Options coherently?
* Does it preserve semantic grouping?

---

# Sidebar Rendering — Draft Notes v2

## Relationship to the Semantic Specification

The semantic specification defines:

```text
Sidebar
    = Caption + Navigation + Hider
```

This document concerns the realization of Sidebar within the standard renderer.

---

# General Sidebar Structure

The standard renderer realizes Sidebar as:

* a fixed-width vertical site-navigation region,
* positioned alongside the ContentPanel.

Sidebar comprises:

* Caption region,
* Navigation region,
* Hider widget.

---

# Sidebar Dimensions

```text
Sidebar.Width = SIDEBAR_WIDTH
```

Sidebar width is fixed by renderer policy.

Sidebar height equals the viewport height.

ContentPanel occupies the remaining horizontal space.

---

# Sidebar Colours

Default Sidebar colours:

```text
Foreground = WHITE
Background = NAVY
Muted      = MUTED
```

These are renderer tokens/constants rather than literal colour values.

---

# Sidebar Typography

Default Sidebar typography:

```text
normal-weight sans
```

Typography scales are referred to using symbolic size names:

```text
h1
h2
h3
h4
h5
```

These refer to renderer typography scales rather than HTML heading semantics.

---

# Sidebar Overflow Behaviour

Sidebar scrolls independently when its contents exceed available vertical space.

Scrolling the Sidebar does not scroll the ContentPanel.

---

# Caption

## Content

Caption currently consists of:

```text
line 1: "Gaspode-san's"
line 2: "Sumo Lab"
line 3: deployment timestamp
```

Timestamp format:

```text
YYYY/MM/DD HH:MM:SS
```

---

## Typography

Caption typography:

```text
lines 1–2:
    h1 scale

line 3:
    h4 scale
```

---

## Colours

Default Caption colours inherit Sidebar defaults.

Timestamp line uses:

```text
foreground = MUTED
```

---

# Navigation

## Structure

Navigation is rendered as:

* an indented,
* hierarchically numbered,
* collapsible list.

---

## Implemented Nodes

Nodes with targets render as links.

---

## Unimplemented Nodes

Nodes without targets render as:

* non-link labels,
* using MUTED foreground.

---

## Current Node

The current Navigation node shall be visually distinguished.

Exact realization remains renderer policy.

---

# Hider

## Status

Work in progress.

---

## Purpose

Hider allows the user to:

* hide,
* collapse,
* or restore

the Sidebar.

---

## Likely Rendering

Hider will likely be realized as:

* a sticky widget,
* attached near the Sidebar/viewport boundary.

Indicative display:

```text
"<" when Sidebar visible
">" when Sidebar hidden
```

---

## Positioning

Hider will likely be vertically positioned within or near the Caption band.

---

## Constraint

Hider must not obscure:

* Caption text,
* deployment timestamp,
* or heading/subheading text

when collapsed.

---

# ContentPanel Rendering — Draft Notes v2

## Relationship to the Semantic Specification

The semantic specification defines:

```text
ContentPanel
    = Heading + Options + PA
```

This document concerns the realization of ContentPanel within the standard renderer.

---

# General ContentPanel Structure

The standard renderer realizes ContentPanel approximately as:

```text
ContentPanel
    = Heading band
    + Body region

Body region
    = Options region
    + PA region
```

These are renderer/layout concepts rather than semantic entities.

---

# ContentPanel Colours and Typography

ContentPanel inherits site-wide rendering defaults unless explicitly overridden.

Typical defaults include:

* left-aligned text,
* normal-weight sans typography,
* WHITE foreground,
* NAVY background.

The renderer should prefer:

* inherited defaults,
* semantic typography scales,
* and shared layout defaults

over:

* local CSS overrides,
* per-component styling,
* or representation-specific styling rules.

---

# Heading Rendering

## Structure

Heading comprises:

* MainHeading,
* and optional SubHeading.

---

## Typography

MainHeading uses:

```text
h2 scale
```

SubHeading uses:

```text
h3 scale
```

These are typography scales/tokens rather than HTML heading semantics.

---

## Semantics

Heading owns:

* page framing,
* page identity,
* and publication naming.

Heading does not own artefact framing.

---

# Body Region

The Body region contains:

* Options region,
* and PA region.

The standard renderer positions:

* Options to the left,
* and PA to the right.

Exact sizing and overflow behaviour remain renderer policy.

---

# Options Rendering

## Relationship to the Semantic Specification

The semantic structure of Options is defined by:

```text
Public UI Grammar — Specification v2 (Draft)
```

This rendering document specifies only:

* realization,
* layout,
* and presentation behaviour.

---

## General Rendering

Options are rendered as:

* an indented,
* hierarchical,
* non-numbered,
* non-collapsible list.

Options region heading:

```text
"Options"
```

uses:

```text
h3 scale
```

---

## Typography

Option labels and OptionGroup labels use:

```text
h4 scale
```

Nested OptionGroups do not reduce typography scale.

Hierarchy is expressed through:

* indentation,
* grouping,
* and structure,

rather than progressively smaller typography.

---

## Colours and Defaults

Option controls inherit:

* site-wide defaults,
* and ContentPanel defaults,

unless explicitly overridden.

---

# PA Rendering

## General Structure

The standard renderer realizes PA approximately as:

```text
PATitle region
Artifact region
Notes region
```

These are renderer/layout concepts rather than semantic entities.

---

# PATitle Rendering

## Structure

```text
PATitle
    = PAHead + PASubHead?
```

---

## Typography

PAHead uses:

```text
h4 scale
```

PASubHead uses:

```text
h5 scale
```

---

## Semantics

PATitle provides framing for the currently displayed Artifact.

Artifacts themselves do not own captions/titles.

PATitle may be empty.

---

# Artifact Rendering

## Definition

```text
Artifact
    = Chart | Table | Prose
```

---

## Layout

Artifact is rendered below PATitle.

Notes are rendered below Artifact.

Notes may determine the remaining available viewport height for the Artifact region.

---

# Chart Rendering

Charts are responsive.

Charts scale to fill the available Artifact viewport space.

Charts must not contain publication or artefact titles.

---

# Table Rendering

Tables may require independent overflow handling.

Tables must not contain publication or artefact titles.

---

# Notes Rendering

Notes are optional.

Notes are rendered as:

* an ordered list,
* of prose notes.

Notes heading:

```text
"Notes"
```

uses:

```text
h5 scale
```

Notes may occupy a reserved region at the bottom of the PA realization.

Exact viewport allocation and scroll ownership remain renderer policy.

---

# Public UI Rendering — Draft Rendering Notes v2

## Relationship to the Semantic Specification

This document complements:

```text
Public UI Grammar — Specification v2 (Draft)
```

The semantic specification defines:

* entities,
* ownership,
* admissible composition,
* and semantic invariants.

This rendering document concerns:

* realization,
* layout,
* overflow behaviour,
* scrolling,
* responsive sizing,
* and renderer policy.

---

# What Has Been Learned

The most important result of implementation discussion is:

```text
semantic association does not imply rendering order
```

For example:

```text
PA = PATitle? + Artifact + Notes?
```

means:

* Notes belong to the Published Artefact,
* not:
  “Notes must appear after the Artifact in document flow.”

---

# Semantic Model vs Renderer Policy

The discussion strongly clarified the separation between:

## Semantic specification

Defines:

* composition,
* ownership,
* admissible structure,
* invariants.

---

## Renderer policy

Defines:

* scrolling,
* overflow,
* viewport ownership,
* sticky behaviour,
* responsive sizing,
* height allocation,
* and visual realization.

---

# Rendering Responsibilities

The renderer is responsible for:

* spatial layout,
* responsive behaviour,
* overflow management,
* viewport ownership,
* and interaction realization.

The renderer is not permitted to violate semantic ownership boundaries.

---

# General Layout Structure

A standard desktop renderer currently appears to follow a structure approximately equivalent to:

```text
PublicUI
    = Sidebar region
    + ContentPanel region
```

The ContentPanel itself may be realized approximately as:

```text
Heading region

Body region:
    Options region
    PA region
```

The PA region may internally realize:

* PATitle,
* Artifact,
* and Notes,

using distinct layout regions.

However:

```text
these regions are renderer concepts,
not semantic entities.
```

---

# Responsive Charts

Charts are expected to behave responsively.

In practice this means:

* the chart scales to the available rendering space,
* while preserving semantic content.

Responsive chart sizing is considered renderer behaviour, not semantic structure.

---

# Tables

Tables differ from charts in an important practical respect:

```text
tables cannot always shrink semantically
to fit available space
```

Therefore tables may require:

* internal scrolling,
* constrained viewport regions,
* or overflow handling.

---

# Notes

The semantic specification states:

```text
Notes belong to the PA.
```

The semantic specification does not require:

* document-flow ordering,
* immediate adjacency,
* or any specific viewport behaviour.

Therefore a renderer may realize Notes as:

* flowing after the Artifact,
* fixed/sticky regions,
* reserved bottom areas,
* collapsible sections,
* or independently scrollable regions,

provided semantic association is preserved.

---

# Scroll Ownership

Current implementation issues suggest that:

```text
scroll ownership must be explicitly defined
```

Observed problematic behaviours include:

* multiple nested scroll regions,
* sticky Notes overwritten by scrolling tables,
* inconsistent heading behaviour,
* inconsistent table overflow handling.

A renderer should define:

* which region owns scrolling,
* which regions remain fixed,
* which regions may overflow,
* and how nested scrolling is handled.

---

# Renderer Conformance Questions

A renderer may be evaluated using questions such as:

```text
Does the renderer preserve semantic ownership?
Does the renderer avoid artifact-owned titles?
Does the renderer preserve Navigation hierarchy?
Does the renderer expose Options coherently?
Does scrolling behaviour remain understandable?
Does overflow behaviour preserve Notes visibility?
Does responsive sizing behave consistently?
```

---

# Important Non-Goals

This rendering document does not:

* define executable layout infrastructure,
* define renderer APIs,
* define CSS frameworks,
* define DOM structure,
* or define implementation technology.

Its purpose is:

* to clarify renderer responsibilities,
* to separate layout policy from semantics,
* and to make rendering decisions discussable and reviewable.
