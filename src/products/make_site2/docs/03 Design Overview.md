# 03 Design Overview

## Status

Initial design overview for `src/products/make_site2`.

This document describes the overall design of the successor public-site builder.
It is intentionally high-level. It defines the major layers, responsibilities,
and seams. Later design documents should refine the core model, rendering,
build pipeline, producer integration, deployment, and migration details.

---

# 1. Design Thesis

`make_site2` is a static analytical publication builder.

It reads a declared public site, resolves curated page publications and stable
public page-selection/deep-link references, converts each promoted page into an
explicit UI Model, and renders that model through a shared shell and artifact
renderer registry.

The central design rule is:

```text
No promoted page is rendered until it has first been represented in the UI Model.
```

The package does not go directly from page declarations to handwritten
HTML/CSS/JS. It first models the interface, then renders the model.

---

# 2. Why the UI Model Is Central

The UI Model is not an optional abstraction or a frontend framework layer.

It is the ordinary model of the interface that the package is responsible for
rendering.

Because `make_site2` generates a public UI, it must define what that UI is
before it defines how to render it.

The previous prototype failed near the rendering layer because it lacked an
adequate UI Model. As a result, structural decisions escaped into custom page
handlers, copied HTML, local CSS, and page-specific JavaScript.

`make_site2` corrects this by making the UI Model an explicit architectural
layer.

The UI Model defines semantic interface entities such as:

```text
Sidebar
Navigation
ContentPanel
Heading
Contents
FilterSection
FilterItem
PA
Artifact
Note
```

The UI Model is not:

```text
a browser framework
a component system
a template language
a CSS system
an executable UI language
```

It is the normalized semantic structure that the renderer consumes.

---

# 3. Overall Pipeline

The overall design is a pipeline:

```text
Site Definition
  -> Build / Publication Plan
  -> UI Model
  -> UI Renderer
  -> Static Output
  -> Optional Deployment
```

Expanded:

```text
CLI / command entry
  -> BuildContext
  -> SiteDefinition
  -> SitePlanner
  -> PublicationPlan
  -> UIModelResolver
  -> UIModel
  -> UIRenderer
  -> OutputWriter
  -> Static site directory
  -> Deployment
```

The key semantic seam is:

```text
PageDefinition + public page-selection/deep-link reference + artifact/data references
  -> UIModelResolver
  -> UIModel
```

The renderer consumes the UI Model. It does not discover page structure by
inspecting old HTML or by branching on page-specific handlers.

---

# 4. Major Layers

## 4.1 CLI / Command Entry

The CLI starts a build or deployment command.

It should remain thin.

It may select:

```text
build mode
configuration file or default site definition
output root
local deployment target
remote deployment target
development or production mode
```

It should not contain page-specific rendering logic.

---

## 4.2 BuildContext

`BuildContext` represents the current build environment.

It may contain:

```text
repository root
product root
output root
build timestamp
development/production mode
cache/version token
logging/warning collector
deployment configuration
```

It should provide common build information without becoming a global dumping
ground.

---

## 4.3 Site Definition

The site definition declares public intent.

It owns:

```text
site id
site title
navigation tree
page registry
global assets
build defaults
```

A site definition answers questions such as:

```text
What public pages exist?
Where do they belong in the navigation tree?
Which pages are promoted, candidate, research, diagnostic, legacy, superseded,
or excluded?
Which global runtime assets are required?
```

It does not render HTML.

It does not know artifact internals.

Example responsibility:

```text
There is a promoted page called "Basho Results".
It lives under the appropriate subject navigation node.
It uses the Basho Results site-facing artifact input.
```

---

## 4.4 SitePlanner / PublicationPlan

The planner turns declarations into a concrete build plan.

It owns:

```text
public page-selection/deep-link resolution
page inclusion/exclusion
status filtering
dependency collection
artifact input references
asset references
data references
pre-render consistency
```

It answers:

```text
What will be built?
Where will it be published?
What files and site-facing inputs does it require?
Is the plan valid enough to render?
```

Example:

```text
navigation node -> page id
page id -> stable public selection/deep-link reference
page id -> required artifact inputs/data/assets
page status -> include, exclude, or mark explicitly
```

The `PublicationPlan` is still not HTML. It is the resolved plan for the static
publication.

---

## 4.5 UIModelResolver

The `UIModelResolver` is the central design seam.

It converts a planned page into the UI Model.

Input:

```text
PageDefinition
PublicSelectionReference
Status
Producer site-facing input or artifact input
Data references
Asset references
BuildContext
```

Output:

```text
PageUIModel
```

The resolver answers semantic UI questions:

```text
What is the page Heading?
What flat G1 filters exist?
What PA is visible by default?
What artifact is being shown?
Where do notes belong?
Which notes are relevant to which PA/artifact features?
```

The resolver is not allowed to solve these questions by writing arbitrary HTML.

---

## 4.6 UI Model

The UI Model is the normalized semantic model of the public interface.

At overview level, it has the shape:

```text
PublicSiteUI
  Sidebar
  PageUIModel*

Sidebar
  Caption
  Navigation

PageUIModel
  PublicSelectionReference
  Status
  ContentPanel

ContentPanel
  Heading
  Contents

Contents
  G1Contents

G1Contents
  FilterSection?
  PA
  Note*

Richer nested-filter or artifact-view structures are deferred to Appendix A.

PA
  id
  title?
  Artifact
  Note*

Artifact
  table | indexed_table | chart | sectioned_table | prose | custom

FilterSection
  Filter*

Filter
  id
  label
  values/default/url-state/help/presentation hints
```

The exact Python classes may differ. The design commitment is to the ownership
and composition boundaries.

---

## 4.7 UI Renderer

The UI Renderer turns the UI Model into web output.

It owns shared structure:

```text
HTML shell
Sidebar layout
Navigation rendering
ContentPanel layout
Heading rendering
FilterSection rendering
PA placement
Note rendering
CSS class conventions
runtime bootstrap data
```

The UI Renderer delegates artifact internals to artifact renderers.

It does not let artifact renderers redefine page structure.

---

## 4.8 Artifact Renderer Registry

Artifact renderers render artifacts inside UI Model slots.

Initial artifact kinds:

```text
table
indexed_table
chart
sectioned_table
prose
custom_artifact
```

Artifact renderers own:

```text
table internals
chart internals
indexed-table loading
sectioned-table layout
custom artifact internals
```

Artifact renderers do not own:

```text
page title
site navigation
public page-selection/deep-link semantics
global shell
ContentPanel structure
page-level status
```

Custom artifact renderers are allowed, but only inside established artifact
slots.

This preserves flexibility without returning to page-specific shell rendering.

---

## 4.9 OutputWriter

The OutputWriter writes the static site.

It owns:

```text
clearing or preparing the output directory
writing entry HTML
writing application-entry HTML and serialized page/artifact data where needed
writing serialized page/artifact data where needed
copying data files
copying assets
copying runtime CSS/JS
writing build metadata
emitting warnings/errors
```

The OutputWriter does not decide what a page means.

It writes the already-resolved site.

---

## 4.10 Deployment

Deployment is downstream of build.

It owns:

```text
local deployment
remote deployment
deployment target configuration
build-only behavior
```

Deployment should not influence:

```text
site semantics
navigation
public page-selection/deep-link semantics
UI Model structure
artifact rendering
```

Build and deployment are separable operations.

---

# 5. Data Flow

A normal build follows this flow:

```text
1. CLI command starts build.
2. BuildContext is created.
3. SiteDefinition is loaded or constructed.
4. SitePlanner derives the PublicationPlan.
5. PublicationPlan is resolved.
6. UIModelResolver resolves planned pages into UI Model objects.
7. UI Renderer renders shell, navigation, content panels, filters, PAs, and notes.
8. Artifact renderers render artifact internals.
9. OutputWriter writes HTML, serialized model/artifact data where needed, data, assets, and runtime files.
10. Deployment optionally copies or uploads the generated output.
```

A promoted page with missing required inputs is a build error.

---

# 6. Key Ownership Rules

## 6.1 Site Definition Owns Public Structure

The site definition owns:

```text
site title
navigation tree
page registry
page status
global assets
```

It does not own artifact internals.

---

## 6.2 Planner Owns Build Resolution

The planner owns:

```text
public page-selection/deep-link resolution
page inclusion
dependency collection
planned output structure
```

It does not render.

---

## 6.3 UI Model Owns Interface Structure

The UI Model owns:

```text
Sidebar
ContentPanel
Heading
Contents
FilterSection
FilterItem
PA
Artifact slot
Note ownership
```

It is the model of what the interface is.

---

## 6.4 UI Renderer Owns Shared Realization

The UI Renderer owns:

```text
shared layout
shared HTML structure
shared CSS class conventions
filter control rendering
note placement
runtime initialization
```

It renders the UI Model.

---

## 6.5 Artifact Renderers Own Artifact Internals

Artifact renderers own only the artifact slot.

They may implement specialized behavior, but they do not own the surrounding
page.

---

## 6.6 Producers Own Analysis-Specific Meaning

Producer modules own:

```text
what the data means
how the analysis is computed
which columns/traces are meaningful
which filters are valid
what caveats/provenance matter
what labels should be shown
```

Promotion to the public site means producers provide intentional site-facing
inputs.

---

# 7. Relationship to Existing make_site

The previous `make_site` prototype roughly followed this pattern:

```text
Page.view
  -> dispatch by view type
  -> copy HTML or call custom renderer
  -> page-specific rendering paths
```

`make_site2` follows this pattern instead:

```text
PageDefinition
  -> PublicationPlan
  -> UI Model
  -> shared UI rendering
  -> artifact renderer dispatch
```

The old prototype is useful evidence about:

```text
required pages
navigation stress
producer outputs
legacy compatibility needs
runtime issues
styling drift
```

It is not the design authority.

---

# 8. Relationship to ui_model

The previous UI-model experiment is evidence that public pages can be represented
through a small number of structural grammars and that rendering can flow from
the parsed structure.

`make_site2` adopts the UI Model concept as a normal architectural layer.

It does not import the old experiment wholesale as the production application.

Code may be copied or adapted only after deciding that the copied code implements
a responsibility that still exists in the new design.

---

# 9. First Vertical Slice

The first vertical slice should be intentionally narrow.

It should demonstrate:

```text
one generated static site
one subject-led navigation tree
one promoted page
no iframe for promoted content
one G1 page
one FilterSection
one PA
one table or indexed-table artifact
shared ContentPanel rendering
data loaded from intentional site-facing inputs
explicit page status
working local build
```

BRB / Basho Results is a suitable first candidate if its data and artifact input are
available.

---

# 10. Design Questions Deferred

This overview does not settle:

```text
exact Python dataclass names
exact file layout
exact JSON schema
whether site-facing inputs are Python objects, dataclasses, JSON, or generated files
exact CSS class names
exact JavaScript module structure
exact BRB implementation details
full deployment mechanics
```

These belong in later design documents.

---

# 11. Summary

`make_site2` is designed around one central invariant:

```text
No promoted page is rendered until it has first been represented in the UI Model.
```

The architecture therefore separates:

```text
public site declaration
build planning
UI modeling
UI rendering
artifact rendering
static output writing
deployment
```

This separation prevents page-specific HTML/CSS/JS handlers from becoming the
real architecture. It also gives the project a stable place to discuss page
structure, filter scope, artifact ownership, notes, provenance, and public
status before any rendering code is written.
