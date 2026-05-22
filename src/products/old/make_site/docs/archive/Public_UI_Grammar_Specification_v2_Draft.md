# Public UI Grammar — Specification v2 (Draft)

## What Has Been Achieved

This work began as an attempt to understand rendering inconsistencies across a set of analytical publication pages.

Initially the observed problems appeared local and implementation-specific:

- duplicated headings,
- inconsistent chart framing,
- inconsistent table framing,
- differing option layouts,
- duplicated CSS,
- unclear ownership of labels and notes.

However, investigation showed that these were not primarily styling problems.

They were symptoms of an insufficiently explicit semantic model.

The project already contained strong recurring structures:

- navigation trees,
- grouped options,
- page headings,
- analytical artefacts,
- contextual notes,
- stable publication patterns.

The task therefore became:

```text
make implicit semantic structure explicit
```

rather than:

- introduce a frontend framework,
- build a component library,
- or create an executable UI DSL.

The resulting approach treats the public UI as a constrained publication grammar.

The specification is:

- semantic,
- normative,
- descriptive.

It is not currently intended to be:

- executable,
- renderer-driven,
- or framework-like.

Its purpose is:

- architectural clarity,
- renderer conformance discussion,
- semantic consistency,
- and stabilization of ownership boundaries.

---

# Fundamental Principles

## 1. Semantic Structure Precedes Rendering

The specification defines:

- what entities exist,
- what they mean,
- how they compose,
- and what they own.

Rendering choices are secondary.

---

## 2. Rendering is a Realization of Semantic Structure

A renderer realizes the semantic structure into:

- HTML,
- CSS,
- JavaScript,
- and interaction patterns.

A renderer may vary in implementation while remaining conformant to the specification.

---

## 3. The Specification is Normative Rather Than Executable

The notation used here:

- algebraic signatures,
- grammar-like notation,
- and prose rules,

exists for:

- thought,
- communication,
- and evaluation.

It is not currently intended as:

- renderer input,
- runtime data,
- or executable infrastructure.

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

- site identity,
- navigation hierarchy,
- and sidebar visibility controls.

---

# Caption

## Semantics

Caption represents:

- site identity,
- publication identity,
- or installation identity.

Caption is distinct from:

- page identity,
- artefact identity,
- and Artifact framing.

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

## Derived Predicates

```text
leaf(node)
    = node has no children

clickable(node)
    = node has target
```

Leafness and clickability are distinct concepts.

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

- hiding,
- collapsing,
- or restoring

the Sidebar.

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

## Semantics

Heading owns:

- page framing,
- page identity,
- and publication naming.

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

- boolean,
- enum,
- integer,
- float,
- text,
- multi-enum.

## Semantics

Options represent:

```text
reader-adjustable semantic state
```

Examples include:

- filtering,
- artefact selection,
- display configuration,
- analytical configuration.

Options answer:

```text
how am I viewing this?
```

## Important Distinction

Options are not controls.

The specification defines semantic adjustable state.

The renderer chooses:

- dropdowns,
- checkboxes,
- tabs,
- segmented controls,
- etc.

---

# Published Artefact (PA)

## Definition

```text
PA
    = PATitle? + Artifact + Notes?
```

PA comprises:

- optional artefact framing,
- the currently displayed Artifact,
- optional Notes.

PATitle may be empty.

This allows:

- stable page framing,
- while Options change the currently displayed Artifact.

---

# PATitle

## Definition

```text
PATitle
    = PAHead + PASubHead?
```

## Semantics

PATitle provides framing for the currently displayed Artifact.

PATitle is distinct from:

- site identity,
- page identity,
- Artifact internals.

PATitle does not belong to the Artifact.

---

# Artifact

## Definition

```text
Artifact
    = Chart | Table | Prose
```

## Semantics

Artifacts are opaque to the publication grammar.

The grammar does not inspect:

- Plotly internals,
- table implementation details,
- rendering-library structures.

Artifacts are treated as black boxes with external contracts.

Artifacts do not own captions/titles.

If artefact framing is required, it is supplied externally by PATitle.

---

# Chart

## Semantics

A Chart is a black-box visual representation.

Charts may internally contain:

- axis labels,
- legends,
- trace labels,
- annotations,
- interaction affordances.

Charts do not own captions/titles.

If chart framing is required, it is supplied by PATitle.

---

# Table

## Semantics

A Table is a black-box tabular representation.

Tables may internally contain:

- column headings,
- row labels,
- group labels,
- sorting indicators.

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

## Note

```text
Note
    = content
```

## Semantics

Notes provide:

- explanation,
- qualification,
- interpretation,
- contextualization

for the currently displayed Artifact.

Notes are distinct from:

- page headings,
- PATitle,
- Artifact internals,
- navigation structure.

---

# Renderer Conformance

The purpose of the specification is to support questions such as:

```text
Does this renderer conform to the specification?
```

Examples:

- Does the renderer preserve Navigation hierarchy?
- Does it distinguish links from labels?
- Does it preserve Heading ownership?
- Does it preserve PATitle ownership?
- Does it avoid artifact-owned titles?
- Does it expose Options coherently?
- Does it preserve semantic grouping?
