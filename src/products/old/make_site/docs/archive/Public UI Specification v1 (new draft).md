# Public UI Grammar — Specification v1 (Draft)

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

For example:

```text
Heading owns publication framing.
Representations do not own titles.
```

This distinction removes ambiguity and duplicated structure.

---

# Top-Level Grammar

```text
PublicUI
    = Navigation + ContentPanel

ContentPanel
    = Heading + Options + PA

PA
    = Representation + Notes

Representation
    = Chart | Table | Prose
```

---

# PublicUI

## Definition

```text
PublicUI
    = Navigation + ContentPanel
```

`PublicUI` is the complete public-facing page structure.

It comprises:

* a navigation structure,
* and the currently visible content panel.

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

Leafness and clickability are distinct concepts.

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

It represents site structure.

---

## Canonical Rendering

A conforming renderer presents Navigation as:

* a nested list,
* recursively rendered,
* optionally collapsible.

Nodes with targets render as links.

Nodes without targets render as labels/group headings.

The current route must be distinguishable.

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

* publication framing,
* page identity,
* and page naming.

Heading is the sole owner of publication-level titles.

---

## Invariants

Representations do not own titles.

Therefore:

* charts do not own titles,
* tables do not own titles,
* duplicated publication framing inside representations is non-conforming.

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

Examples:

* filtering,
* representation configuration,
* artefact selection,
* display configuration.

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

## Canonical Rendering

A conforming renderer presents Options as:

* grouped controls,
* recursively rendered,
* optionally collapsible.

A nested-list-like realization is canonical.

---

# Published Artefact (PA)

## Definition

```text
PA
    = Representation + Notes
```

`PA` is the thing being published.

It comprises:

* the primary analytical representation,
* plus contextual/supporting material.

---

# Representation

## Definition

```text
Representation
    = Chart | Table | Prose
```

---

## Semantics

Representations are opaque to the publication grammar.

The grammar does not inspect:

* Plotly internals,
* table implementation details,
* rendering-library structures.

Representations are treated as black boxes with external contracts.

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

Charts do not own publication framing.

---

## Invariants

A conforming Chart representation must not contain:

* publication titles,
* duplicated page headings,
* title-like framing.

Any Plotly title intended as publication framing is non-conforming.

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

---

## Invariants

Tables do not own publication titles.

Captions functioning as page titles are non-conforming.

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

Possible future refinements:

* note kinds,
* warnings,
* methodological notes,
* provenance notes.

These remain intentionally unspecified in v1.

---

## Semantics

Notes provide:

* explanation,
* qualification,
* interpretation,
* and contextualization

for the PA.

Notes are distinct from:

* page headings,
* representation internals,
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
* Does it avoid representation-owned titles?
* Does it expose Options coherently?
* Does it preserve semantic grouping?

The specification therefore defines:

* semantic structure,
* ownership,
* and invariants,

against which concrete renderers may be evaluated.


# Amendments to “Public UI Grammar — Specification v1 (Draft)”

## Revised Top-Level Grammar

Replace:

```text id="0ll46x"
PublicUI
    = Navigation + ContentPanel
```

with:

```text id="mml0xp"
PublicUI
    = Sidebar + ContentPanel

Sidebar
    = Caption + Navigation + Hider
```

---

# Sidebar

## Definition

```text id="mh0n1l"
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

Caption is distinct from Heading.

---

## Invariants

Caption does not own:

* page identity,
* PA identity,
* or Representation framing.

Heading remains the sole owner of page/publication framing.

---

# Navigation

No semantic changes.

Navigation remains:

```text id="c34yk0"
a rooted labelled tree
```

Navigation represents:

```text id="z3u3pa"
where the user is
and
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

```text id="wceyd9"
how the current PA is viewed
```

Hider affects:

```text id="n39q6o"
how the UI shell itself is realized
```

Therefore:

```text id="jv8qiy"
Hider ∉ Options
```

---

# Amendments to “Public UI Rendering — Draft Rendering Notes v1”

## Revised General Layout Structure

Replace:

```text id="9mjlwm"
PublicUI
    = Navigation region
    + ContentPanel region
```

with:

```text id="j4pvzg"
PublicUI
    = Sidebar region
    + ContentPanel region
```

---

## Sidebar Realization

A standard renderer realizes Sidebar approximately as:

```text id="eq55ig"
Sidebar region:
    Caption region
    Navigation region
    Hider widget
```

Typical realization:

* Caption near the top of the Sidebar,
* Navigation occupying the main Sidebar body,
* Hider positioned consistently within the Sidebar shell.

Exact positioning remains renderer policy.

---

## Hider Behaviour

A conforming renderer:

* preserves access to Navigation when the Sidebar is visible,
* preserves recoverability when the Sidebar is hidden/collapsed,
* and ensures the Hider remains discoverable.

The precise visual realization of hiding/collapse remains renderer policy.

