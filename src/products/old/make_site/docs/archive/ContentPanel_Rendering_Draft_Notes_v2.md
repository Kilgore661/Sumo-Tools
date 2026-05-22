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

- left-aligned text,
- normal-weight sans typography,
- WHITE foreground,
- NAVY background.

The renderer should prefer:

- inherited defaults,
- semantic typography scales,
- shared layout defaults

over:

- local CSS overrides,
- per-component styling,
- representation-specific styling rules.

---

# Heading Rendering

## Structure

Heading comprises:

- MainHeading,
- optional SubHeading.

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

## Semantics

Heading owns:

- page framing,
- page identity,
- publication naming.

Heading does not own artefact framing.

---

# Body Region

The Body region contains:

- Options region,
- PA region.

The standard renderer positions:

- Options to the left,
- PA to the right.

Exact sizing and overflow behaviour remain renderer policy.

---

# Options Rendering

## Relationship to the Semantic Specification

The semantic structure of Options is defined by:

```text
Public UI Grammar — Specification v2 (Draft)
```

This rendering document specifies only:

- realization,
- layout,
- presentation behaviour.

## General Rendering

Options are rendered as:

- an indented,
- hierarchical,
- non-numbered,
- non-collapsible list.

Options region heading:

```text
"Options"
```

uses:

```text
h3 scale
```

## Typography

Option labels and OptionGroup labels use:

```text
h4 scale
```

Nested OptionGroups do not reduce typography scale.

Hierarchy is expressed through:

- indentation,
- grouping,
- structure,

rather than progressively smaller typography.

## Colours and Defaults

Option controls inherit:

- site-wide defaults,
- ContentPanel defaults,

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

## PATitle Rendering

```text
PATitle
    = PAHead + PASubHead?
```

PAHead uses:

```text
h4 scale
```

PASubHead uses:

```text
h5 scale
```

PATitle provides framing for the currently displayed Artifact.

Artifacts themselves do not own captions/titles.

PATitle may be empty.

---

# Artifact Rendering

```text
Artifact
    = Chart | Table | Prose
```

Artifact is rendered within the PA region.

The renderer must preserve the distinction between:

- artefact framing supplied by PATitle,
- the Artifact itself,
- contextual Notes.

---

# Chart Rendering

Charts are responsive.

Charts are fitted to the available Artifact viewport.

Charts scale to occupy the available width and height while preserving usability and semantic content.

Charts must not contain publication or artefact titles.

Chart sizing is determined by the Artifact viewport allocated by the renderer.

---

# Table Rendering

A table is rendered into the Artifact viewport.

Typography:

- column headings: h4 scale, bold.
- cell values: h4 scale, normal weight.

Vertical overflow:

- if table rows exceed the available Artifact viewport, scrolling is provided for the row area;
- row data scrolls;
- column headings remain visible;
- PATitle, when present, remains visible.

The renderer may realize PATitle and column headings as a sticky header stack.

This is a rendering technique, not a semantic structure.

Tables must not contain publication or artefact titles.

---

# Notes Rendering

Notes are optional.

Notes are rendered as:

- an ordered list,
- of prose notes.

Notes heading:

```text
"Notes"
```

uses:

```text
h5 scale
```

Notes may occupy a reserved region at the bottom of the PA realization.

Notes may be as tall as required.

When Notes occupy reserved vertical space, they determine the remaining viewport available to PATitle and Artifact.

Exact viewport allocation and scroll ownership remain renderer policy.
