# Public UI Rendering — Draft Rendering Notes v1

## Relationship to the Semantic Specification

This document complements:

```text id="61g0qs"
Public UI Grammar — Specification v1 (Draft)
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

The rendering layer must preserve the semantic structure defined in the specification.

---

# What Has Been Learned

The most important result of implementation discussion is:

```text id="sgof6m"
semantic association does not imply rendering order
```

For example:

```text id="1kbhve"
PA = Representation + Notes
```

means:

* Notes belong to the Published Artefact,
* not:
  “Notes must appear after the Representation in document flow.”

````

This distinction proved essential once layout and overflow behaviour were considered.

---

# Semantic Model vs Renderer Policy

The discussion strongly clarified the separation between:

## Semantic specification

Defines:
- composition,
- ownership,
- admissible structure,
- invariants.

Examples:
- Heading owns publication framing.
- Representations do not own titles.
- Notes belong to the PA.
- Navigation is a rooted labelled tree.

---

## Renderer policy

Defines:
- scrolling,
- overflow,
- viewport ownership,
- sticky behaviour,
- responsive sizing,
- height allocation,
- and visual realization.

Examples:
- whether Notes scroll independently,
- whether tables scroll internally,
- whether headings remain visible,
- whether Notes occupy reserved space.

---

# The Existing Semantic Specification Appears Sound

An important outcome of the discussion is that:
- sticky Notes,
- overlapping regions,
- double scrolling,
- independent table scrolling,
- responsive chart sizing,

did not require changes to the semantic grammar itself.

Instead they exposed deficiencies in renderer policy and implementation.

This is strong evidence that the semantic decomposition:
- PublicUI,
- Navigation,
- ContentPanel,
- Heading,
- Options,
- PA,
- Representation,
- Notes

is already reasonably stable.

---

# Rendering Responsibilities

The renderer is responsible for:
- spatial layout,
- responsive behaviour,
- overflow management,
- viewport ownership,
- and interaction realization.

The renderer is not permitted to violate semantic ownership boundaries.

---

# General Layout Structure

A standard desktop renderer currently appears to follow a structure approximately equivalent to:

```text id="5k46nd"
PublicUI
    = Navigation region
    + ContentPanel region
````

The ContentPanel itself may be realized approximately as:

```text id="2b2ezd"
Heading region

Body region:
    Options region
    PA region
```

The PA region may internally realize:

* Representation,
* and Notes,

using distinct layout regions.

However:

```text id="jot8hl"
these regions are renderer concepts,
not semantic entities.
```

The semantic specification intentionally does not define:

* Regions,
* Frames,
* Panels,
* or viewport ownership structures.

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

```text id="8b5y9e"
tables cannot always shrink semantically
to fit available space
```

Therefore tables may require:

* internal scrolling,
* constrained viewport regions,
* or overflow handling.

This is renderer policy.

---

# Notes

The semantic specification states:

```text id="yj4e9k"
Notes belong to the PA.
```

The semantic specification does not require:

* document-flow ordering,
* immediate adjacency,
* or any specific viewport behaviour.

Therefore a renderer may realize Notes as:

* flowing after the Representation,
* fixed/sticky regions,
* reserved bottom areas,
* collapsible sections,
* or independently scrollable regions,

provided semantic association is preserved.

---

# Scroll Ownership

Current implementation issues suggest that:

```text id="y0urku"
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

```text id="itc6rh"
Does the renderer preserve semantic ownership?
Does the renderer avoid representation-owned titles?
Does the renderer preserve Navigation hierarchy?
Does the renderer expose Options coherently?
Does scrolling behaviour remain understandable?
Does overflow behaviour preserve Notes visibility?
Does responsive sizing behave consistently?
```

These questions belong to renderer conformance rather than semantic specification.

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

