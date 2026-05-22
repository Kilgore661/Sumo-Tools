# make_site Docs

This directory contains the architectural, semantic, rendering, implementation, and open-issue documentation for `src.products.make_site`.

The goal of these docs is not merely to describe page implementations.

The project is increasingly understood as:

```text
a constrained semantic publication system
for analytical public sites
```

The central problem is therefore primarily semantic rather than technical.

The docs aim to make explicit:

- the stable semantic structures of the system;
- ownership and composition boundaries;
- rendering contracts;
- implementation contracts;
- and the relationship between semantic specification and concrete realization.

---

# Documentation Structure

The docs are intentionally consolidated into a small number of canonical files.

## Core Documents

### 01 Public Site Model

The primary conceptual and semantic specification.

Covers:

- the publication model;
- semantic UI model;
- ownership boundaries;
- admissible composition;
- PA concepts;
- rendering-vs-semantics distinctions;
- and the overall architectural direction.

Read this first.

---

### 02 Rendering Model

Defines how semantic structures are realized in the standard renderer.

Covers:

- page realization;
- navigation realization;
- content-panel structure;
- rendering contracts;
- layout conventions;
- chart/table realization;
- and renderer consistency rules.

---

### 03 Implementation State

Describes the current implementation reality.

Covers:

- current architecture;
- migration progress;
- known deviations from the target model;
- technical compromises;
- and builder/runtime state.

This document is operational rather than conceptual.

---

### 04 Features and Applications

Feature-specific and application-specific work.

Examples include:

- Basho Results Browser (BRB);
- producer embeds;
- chart/table behavior;
- Plotly work;
- career lifecycle pages;
- and Equelo-specific public-site material.

---

### 05 Open Issues

Active unresolved questions, deferred work, and architectural gaps.

This is the issue register, not a second design notebook.

---

### 06 UI Model Implementation Contract

The implementation-facing contract for the UI Model.

Covers:

- the working implementation model;
- Python object to manifest boundaries;
- manifest JSON structure;
- JS renderer responsibilities;
- DOM/CSS vocabulary;
- chart/table/prose artifact contracts;
- note and option handling;
- and reconciliation with existing PA manifest classes.

This document bridges the conceptual model and the hand-written renderer.

---

# Reading Order

Recommended reading order:

1. `01 Public Site Model.md`
2. `02 Rendering Model.md`
3. `03 Implementation State.md`
4. `04 Features and Applications.md`
5. `05 Open Issues.md`
6. `06 UI Model Implementation Contract.md`

---

# Documentation Philosophy

The docs prioritize:

- semantic clarity;
- stable conceptual distinctions;
- explicit ownership boundaries;
- renderer consistency;
- and implementation contracts grounded in the model.

The goal is not to design a generalized frontend framework.

The goal is to formalize only those distinctions that repeatedly prove semantically stable and operationally useful.

The preferred style is semi-formal and specification-oriented.

Useful forms include:

- prose;
- algebraic signatures;
- invariants;
- admissible composition rules;
- rendering contracts;
- and implementation contracts.

For example:

```text
make_PublicUI :
    Navigation × ContentPanel
        -> PublicUI
```

These expressions are primarily intended as specification and conceptual clarification rather than executable runtime definitions.

---

# Working Notes and Case Studies

Working discussion notes, case studies, and synthesis notes may be used while the model and implementation contract are being refined.

They are source material for the canonical documents. They should not become permanent peers of the numbered core documents unless they introduce a stable new role.

Durable conclusions from working notes should be carried forward into the numbered documents. Stale or superseded material should be archived or deleted according to the archive policy.

---

# Archive Policy

The `archive/` directory contains superseded drafts, exploratory notes, and older document versions retained temporarily for reference; in principle they can be deleted once their durable content has been merged.

Documents in `current/` are considered authoritative.

When consolidating docs:

- preserve durable semantic insight;
- aggressively remove duplication;
- prefer merging over proliferation;
- and retire working notes once their durable content has been carried forward.
