# 

# Introduction to the Sumo-Tools Project and Its UI Rendering Model for LLMs

This repository is a Python-driven publication system for professional sumo analysis.

At first glance it can look like:

- a data science project,

- a static site generator,

- or a collection of one-off analysis scripts.

In reality it is becoming something more specific:

> a system for publishing analytical “exhibits” as coherent static web pages.

The important thing to understand is that the web frontend is *not* the computational core of the project.

The pipeline is fundamentally:

```text
historical sumo data
    ->
domain models / analysis
    ->
published artefacts
    ->
assembled static website
```

The site renderer exists primarily to:

- present analytical outputs consistently,

- provide shared navigation and interaction patterns,

- and expose analytical state through URLs/options.

The frontend is therefore best understood as a *publication renderer*, not a conventional web application.

---

# The Data/Build Architecture

The project maintains a local normalized historical database of professional sumo records.

The canonical in-memory representation is usually called `History`.

`History` is treated as infrastructure:

- always available,

- queryable by analysis code,

- and independent from rendering.

Analysis jobs consume `History` and generate publication artefacts such as:

- JSON bundles,

- CSV files,

- precomputed tables,

- Plotly specifications,

- metadata,

- explanatory notes.

These artefacts are written into output directories.

A later pipeline stage (`make_site`) assembles:

- generated artefacts,

- permanent runtime assets,

- shared CSS/JS,

- templates/navigation definitions,

into a deployable static website.

This means the renderer does **not** perform:

- statistical analysis,

- ranking logic,

- historical computation,

- or live data fetching.

Instead it renders precomputed semantic outputs.

---

# The Emerging UI Model

A crucial observation is that the repository already contains a partially formalized UI model.

The project is *not* using:

- React,

- a component framework,

- a virtual DOM,

- or a general frontend architecture.

However, it *does* contain a semantic rendering model implemented mostly in Python.

The recurring conceptual structure of a page is approximately:

```text
Site
    Navigation
    Page
        Heading
        Options
        Published Artefact
        Notes
```

Typical pages therefore look like:

```text
full page
    = navigation + content area

content area
    = title + controls + primary artefact + explanatory material

primary artefact
    = chart | table | prose | custom view
```

This structure appears repeatedly throughout the repository.

---

# The Important Architectural Separation

The project strongly separates:

## Producers

Code that:

- computes analysis,

- defines semantic options,

- emits artefacts.

from:

## Renderers

Code that:

- provides layout/chrome,

- manages controls,

- renders tables/charts,

- manages URL state,

- applies CSS and interaction conventions.

This separation is one of the deepest architectural ideas in the repository.

The intent is that an analysis page should increasingly describe:

> “what this page contains”

rather than:

> “how to manually construct frontend HTML.”

---

# The Existing Rendering Abstractions

The repository already contains model-like concepts such as:

- pages,

- view specifications,

- options,

- navigation structures,

- publication artefacts.

Examples of view concepts include:

- standalone HTML views,

- Plotly views,

- table applications,

- essays/custom views.

Options are also modeled semantically rather than as raw widgets.

For example:

- enum,

- boolean,

- numeric,

- multi-select,

with the renderer choosing how to display them.

This is effectively a lightweight rendering DSL (domain-specific language), even though it is not described using that terminology everywhere.

---

# The Current Tension in the Repository

The repository is in an intermediate state.

The docs repeatedly acknowledge:

- duplicated CSS,

- inconsistent rendering patterns,

- page-specific ad hoc structures,

- incomplete abstraction boundaries.

At the same time, the docs also resist:

- premature generalization,

- over-engineered frontend frameworks,

- artificial component hierarchies,

- “framework hell.”

This creates an important tension:

## One direction:

A shared semantic publication grammar.

## The opposing direction:

Avoid inventing abstractions before the real common structure is understood.

As a result, the current system often feels:

- more structured than a collection of scripts,

- but less formalized than a true rendering framework.

---

# The Core Question

The key architectural question is therefore:

> Is there now enough stable semantic structure in the project to justify a more explicit rendering model?

More specifically:

- Which concepts are genuinely universal?

- Which are accidental properties of current pages?

- What belongs in the renderer?

- What belongs in producers?

- How much layout structure should be modeled?

- How much should remain plain HTML/CSS conventions?

- Can duplication be reduced without creating a rigid frontend framework?

- Is the project actually converging on a coherent publication grammar?

This discussion is specifically about those rendering/model boundaries.
