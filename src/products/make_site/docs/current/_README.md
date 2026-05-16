# make_site Docs

This directory contains the architectural, semantic, rendering, and implementation  
documentation for `src.products.make_site`.

The goal of these docs is not merely to describe page implementations.

The project is increasingly understood as:

```text
a constrained semantic publication system
for analytical public sites
```

The central problem is therefore primarily semantic rather than technical.

The docs aim to make explicit:

- the stable semantic structures of the system,

- ownership and composition boundaries,

- rendering contracts,

- and the relationship between semantic specification and concrete realization.

---

# Documentation Structure

The docs are intentionally consolidated into a small number of canonical files.

## Core Documents

### 1. Public Site Model

The primary conceptual and semantic specification.

Covers:

- the publication model,

- semantic UI grammar,

- ownership boundaries,

- admissible composition,

- PA concepts,

- rendering-vs-semantics distinctions,

- and the overall architectural direction.

Read this first.

---

### 2. Rendering Model

Defines how semantic structures are realized in the standard renderer.

Covers:

- page realization,

- navigation realization,

- content-panel structure,

- rendering contracts,

- layout conventions,

- chart/table realization,

- and renderer consistency rules.

---

### 3. Implementation State

Describes the current implementation reality.

Covers:

- current architecture,

- migration progress,

- known deviations from the target model,

- technical compromises,

- and builder/runtime state.

This document is operational rather than conceptual.

---

### 4. Features and Applications

Feature-specific and application-specific work.

Examples include:

- Basho Results Browser (BRB),

- producer embeds,

- chart/table behavior,

- Plotly work,

- and Equelo-specific public-site material.

---

### 5. Open Issues

Active unresolved questions, deferred work, and architectural gaps.

---

# Reading Order

Recommended reading order:

1. `Public Site Model.md`

2. `Rendering Model.md`

3. `Implementation State.md`

4. `Features and Applications.md`

5. `Open Issues.md`

---

# Documentation Philosophy

The docs prioritize:

- semantic clarity,

- stable conceptual distinctions,

- explicit ownership boundaries,

- and renderer consistency.

The goal is not to design a generalized frontend framework.

The goal is to formalize only those distinctions that repeatedly prove  
semantically stable and operationally useful.

The preferred style is semi-formal and specification-oriented.

Useful forms include:

- prose,

- algebraic signatures,

- invariants,

- admissible composition rules,

- and rendering contracts.

For example:

```text
make_PublicUI :
    Navigation × ContentPanel
        -> PublicUI
```

These expressions are primarily intended as specification and conceptual  
clarification rather than executable runtime definitions.

---

# Archive Policy

The `archive/` directory contains superseded drafts, exploratory notes,  
and older document versions retained temporarily for reference; in principle they can just be deleted.

Documents in `current/` are considered authoritative.

When consolidating docs:

- preserve durable semantic insight,

- aggressively remove duplication,

- and prefer merging over proliferation.
