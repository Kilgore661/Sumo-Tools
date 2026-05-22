# Public UI Rendering — Draft Rendering Notes v2

## Relationship to the Semantic Specification

This document complements:

```text
Public UI Grammar — Specification v2 (Draft)
```

The semantic specification defines:

- entities,
- ownership,
- admissible composition,
- semantic invariants.

This rendering document concerns:

- realization,
- layout,
- overflow behaviour,
- scrolling,
- responsive sizing,
- renderer policy.

The rendering layer must preserve the semantic structure defined in the specification.

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

- Notes belong to the Published Artefact,
- not:
  “Notes must appear after the Artifact in document flow.”

This distinction proved essential once layout and overflow behaviour were considered.

---

# Semantic Model vs Renderer Policy

The discussion strongly clarified the separation between semantic specification and renderer policy.

## Semantic specification

Defines:

- composition,
- ownership,
- admissible structure,
- invariants.

Examples:

- Heading owns page framing.
- PATitle owns artefact framing.
- Artifacts do not own captions/titles.
- Notes belong to the PA.
- Navigation is a rooted labelled tree.

## Renderer policy

Defines:

- scrolling,
- overflow,
- viewport ownership,
- sticky behaviour,
- responsive sizing,
- height allocation,
- visual realization.

Examples:

- whether Notes scroll independently,
- whether tables scroll internally,
- whether headings remain visible,
- whether Notes occupy reserved space,
- whether PATitle and table headers are sticky.

---

# Rendering Responsibilities

The renderer is responsible for:

- spatial layout,
- responsive behaviour,
- overflow management,
- viewport ownership,
- interaction realization.

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

- PATitle,
- Artifact,
- Notes,

using distinct layout regions.

However:

```text
these regions are renderer concepts,
not semantic entities.
```

The semantic specification intentionally does not define:

- Regions,
- Frames,
- Panels,
- viewport ownership structures.

---

# Responsive Charts

Charts are expected to behave responsively.

In practice this means:

- the chart scales to the available rendering space,
- while preserving semantic content.

Responsive chart sizing is considered renderer behaviour, not semantic structure.

---

# Tables

Tables differ from charts in an important practical respect:

```text
tables cannot always shrink semantically
to fit available space
```

Therefore tables may require:

- internal scrolling,
- constrained viewport regions,
- overflow handling.

The desired behaviour for analytical tables is:

- PATitle remains visible when present;
- column headings remain visible;
- row data scrolls.

The renderer may implement this using a sticky header stack or another equivalent technique.

This implementation mechanism is not semantic structure.

---

# Notes

The semantic specification states:

```text
Notes belong to the PA.
```

The semantic specification does not require:

- document-flow ordering,
- immediate adjacency,
- any specific viewport behaviour.

Therefore a renderer may realize Notes as:

- flowing after the Artifact,
- fixed/sticky regions,
- reserved bottom areas,
- collapsible sections,
- independently scrollable regions,

provided semantic association is preserved.

In the current preferred desktop design, Notes may be reserved at the bottom of the PA realization and may determine the remaining viewport height available to PATitle and Artifact.

---

# Scroll Ownership

Current implementation issues suggest that:

```text
scroll ownership must be explicitly defined
```

Observed problematic behaviours include:

- multiple nested scroll regions,
- sticky Notes overwritten by scrolling tables,
- inconsistent heading behaviour,
- inconsistent table overflow handling.

A renderer should define:

- which region owns scrolling,
- which regions remain fixed,
- which regions may overflow,
- how nested scrolling is handled.

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
Does table scrolling preserve column-heading context?
Does PATitle remain available when table content scrolls?
```

These questions belong to renderer conformance rather than semantic specification.

---

# Important Non-Goals

This rendering document does not:

- define executable layout infrastructure,
- define renderer APIs,
- define CSS frameworks,
- define DOM structure,
- define implementation technology.

Its purpose is:

- to clarify renderer responsibilities,
- to separate layout policy from semantics,
- to make rendering decisions discussable and reviewable.
