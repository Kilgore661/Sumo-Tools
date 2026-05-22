This doc is for LLMs to understand how we are trying to understand the
redering of the web pages.

--------------

Right now there is a shared understanding emerging about:

* what kind of system this is,
* what kind of abstraction problem it is,
* and what kinds of abstractions are *not* desired.

Capturing that would help future-you avoid:

* slipping back into implementation-first thinking,
* accidental framework design,
* or confusing rendering details with semantic structure.

---

I think the most important things established so far are:

# 1. The problem is semantic before it is technical

The core issue is not:

* CSS duplication,
* frontend tooling,
* component reuse,
* framework choice.

It is:

```text
What are the stable semantic categories
of the publication system?
```

---

# 2. The system is best viewed as a publication grammar

Not:

```text
a web app
```

and not:

```text
a component library
```

but:

```text
a constrained grammar
for analytical publication pages
```

---

# 3. The existing repo already contains an implicit model

The task is not:

```text
invent a model from nothing
```

but:

```text
discover and formalize
the stable distinctions
already emerging naturally
```

---

# 4. Repeated friction signals missing semantic boundaries

Observations like:

* “why does this chart have a box?”
* “who owns titles?”
* “where do notes belong?”
* “why are these controls inconsistent?”

are not primarily styling complaints.

They are evidence that:

* ownership,
* composition,
* and rendering contracts

are currently implicit.

---

# 5. The useful questions are of the form “What is X?”

Examples:

* What is a Page?
* What is a Chart?
* What is a Table?
* What is a Note?
* What is Navigation?
* What is an Option?
* What is a View?

These are ontological questions about:

* responsibility,
* admissible structure,
* rendering ownership,
* and composition.

---

# 6. Grammar/algebra framing is productive

The system can be thought of as:

* sorts/types,
* constructors,
* operations,
* predicates,
* admissible compositions.

For example:

```text
make_PublicUI :
    Navigation × ContentPanel
        -> PublicUI
```

This framing is likely healthier than:

* large inheritance trees,
* arbitrary widgetization,
* or generalized frontend abstraction.

---

# 7. OO vocabulary is still pragmatically useful

Even if the conceptual model is algebraic,
phrases like:

* “has a”
* “is a”
* “owns”
* “renders”

remain useful shorthand for:

* composition,
* specialization,
* and responsibility boundaries.

The implementation will likely still involve:

* Python classes,
* renderers,
* dataclasses,
* methods/protocols.

---

# 8. The goal is not maximal abstraction

The emerging direction is:

```text
formalize only the distinctions
that repeatedly prove semantically stable
```

not:

```text
invent a universal UI framework
```

This constraint is important and healthy.

---

# 9. Rendering should probably be treated as a homomorphism

That is:

* semantic publication structures
  map into
* HTML/CSS/JS realizations.

The renderer should preserve:

* semantic structure,
* ownership,
* and composition,

while allowing multiple realizations.

That appears closely aligned with the repo’s existing instincts.

I think this should be a **separate addendum** rather than an amendment.

The earlier account explains:

- what the repository is,

- what the emerging model is,

- and why the modelling problem exists.

This newer alignment is more specific and methodological:

- what kind of formalism is desired,

- what the formalism is *for*,

- and what it is *not* for.

That deserves its own section/document.

---

# Addendum: Semantic Specification vs Executable Model

The emerging UI work should be understood primarily as the construction of a **semantic specification**, not an executable rendering system.

The goal is:

- architectural clarity,

- semantic consistency,

- and renderer evaluation.

The goal is *not*:

- a new frontend framework,

- a declarative runtime,

- or a fully executable UI language.

---

# The Core View

The public site is best treated as a constrained publication grammar.

The grammar defines:

- semantic categories,

- admissible compositions,

- ownership boundaries,

- and rendering contracts.

Typical questions therefore take the form:

```text
What is a Navigation?
What is a Page?
What is a Table?
What is a Chart?
What is a Note?
```

These are ontological questions about:

- responsibility,

- structure,

- composition,

- and realization.

---

# Formalism

The preferred style is semi-formal rather than executable.

Useful tools include:

- prose,

- algebraic signatures,

- grammar-like notation,

- predicates/invariants,

- and canonical rendering descriptions.

For example:

```text
make_PublicUI :
    Navigation × ContentPanel
        -> PublicUI
```

or:

```text
Navigation is a rooted labelled tree.
```

These expressions are intended as:

- specification,

- communication,

- and conceptual clarification.

They are not necessarily intended as:

- Python classes,

- parser inputs,

- or runtime data structures.

---

# Semantic Model vs Rendering Contract

A crucial distinction is:

## Semantic specification

Defines what exists.

Example:

```text
PublicUI comprises:
    Navigation
    ContentPanel
```

or:

```text
Navigation is a rooted labelled tree.
```

---

## Rendering contract

Defines acceptable realizations.

Example:

```text
The standard renderer presents Navigation
as a nested collapsible list.
```

or:

```text
The standard desktop renderer presents
PublicUI as:
    left navigation region
    right content region
```

This separation is intentional.

The semantic model defines:

- structure,

- ownership,

- admissible composition.

The rendering contract defines:

- realization,

- layout,

- interaction conventions,

- and presentation rules.

---

# Renderer Conformance

The purpose of the specification is not automatic execution.

It is primarily to support questions like:

```text
Does this renderer conform to the specification?
```

Examples:

```text
Does the renderer preserve Navigation hierarchy?
Does it distinguish links from labels?
Does it expose active-page state?
Does it preserve the ownership boundary
between page titles and charts?
```

This is a normative/specification-oriented approach rather than a framework-oriented approach.

---

# Relationship to Implementation

The specification may eventually influence:

- Python structures,

- renderer APIs,

- templates,

- CSS organization,

- or validation tooling.

However, executable realization is not currently the objective.

The immediate goal is:

```text
make implicit semantic structure explicit
```

so that:

- rendering decisions become discussable,

- inconsistencies become identifiable,

- and future abstractions emerge from stable semantics rather than accidental implementation patterns.
