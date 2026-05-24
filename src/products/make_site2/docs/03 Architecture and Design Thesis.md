# 03 Architecture and Design Thesis

## Status

Draft architecture and design-thesis document for `src/products/make_site2`.

This document explains the solution chosen to satisfy `01 Requirements.md` and
`02 Specification.md`. It is not itself the public specification and does not
replace model, rendering, build, integration or deployment design documents.

---

## 1. The Problem the Architecture Must Solve

`make_site2` publishes an analytical public website that is expected to grow.
As further Published Artifacts are promoted, it would be easy for the product to
become a collection of separate tools, each with its own assumptions about page
layout, Filters, Notes, navigation, styling, data loading and runtime behaviour.

Such an implementation could display useful analytical outputs while failing as
a coherent public site. The problem is not only visual inconsistency. If page
structure and behaviour are invented separately within renderers, there is no
stable way to determine:

- what a public page is;
- which parts of the visible interface are shared site structure;
- what a Filter governs;
- where Notes belong;
- which decisions are part of a Published Artifact and which are part of the
  surrounding site;
- whether a new page is consistent with the public product already published.

The architecture shall make those questions answerable before page-specific
rendering convenience determines the answer.

---

## 2. Design Thesis

The central design thesis is:

```text
No promoted public page is rendered until it has been represented in the UI
Model.
```

The page grammar `PG`, specified in `02 Specification.md`, defines the semantic
shape of the visible public page:

```text
PublicUI -> NavigationBar . ContentPanel
ContentPanel -> Heading . Contents
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

The UI Model represents that specified public shape for the planned site. The
renderer consumes the model and realises it as browser-visible output.

This approach is chosen because it makes coherence enforceable as the site
grows. A newly promoted page is not permitted to become public merely by having
an output file and a bespoke rendering path. It must first be represented as a
public page within the same semantic interface model as the other promoted
material.

---

## 3. Rendering as an Auditable Realisation of the Model

Rendering is not expected to be mechanically determined in every detail by
`PG`. The grammar determines visible entities, ownership and relationships. It
does not by itself determine every size, colour, spacing value, browser widget
or detailed terminal presentation.

The architectural discipline is that visible authored behaviour must remain
auditable against the model. For any significant visible fact, it should be
possible to ask:

- which `PG` entity or Published Artifact feature owns this fact;
- whether the fact follows directly from the specified structure;
- whether it is a declared rendering rule for that modelled owner;
- whether it is accepted default behaviour;
- or whether it is a justified exception that should be recorded and reviewed.

Examples include:

- the NavigationBar and ContentPanel appearing as separate top-level regions;
- the NavigationBar hider affecting the NavigationBar rather than the selected
  analytical state;
- Filters being visually separate from the PAPanel they govern;
- Notes appearing as part of the PAPanel rather than spanning the sibling
  FilterSection;
- shared table treatment applying to table PAs rather than being copied into
  individual pages;
- artefact-specific features, such as Banzuke Changes movement direction, being
  owned by the relevant PA rather than by incidental CSS or page layout.

The purpose of this discipline is not to pretend that presentation is forced by
grammar. It is to prevent unowned presentation decisions from gradually
becoming the real public-site architecture.

---

## 4. Architectural Principle: Meaning Before Rendering

The package shall distinguish three stages of decision-making:

```text
Public intent
  -> semantic public model
  -> rendered public site
```

Public intent establishes which material is deliberately published, where it
belongs in the public site and what public selection/state is meaningful.

The semantic public model establishes what interface structure exists for that
published material: NavigationBar, Navigation, selected ContentPanel, Heading,
FilterSection where present, PAPanel, PA and Notes.

Rendering decides how those established entities are expressed as HTML, CSS and
client-side behaviour, subject to the public specification and the rendering
rules adopted for the model.

A renderer shall not repair a missing semantic decision by inventing a new
public structure privately. Where an intended promoted page or feature does not
fit the specified/modelled public shape, the model or specification must be
extended deliberately, or promotion must wait.

---

## 5. Processing Pipeline

The high-level processing pipeline is:

```text
Site Definition
  -> Publication Plan
  -> UI Model
  -> Renderer
  -> Static Output
  -> Optional Deployment
```

Expanded conceptually:

```text
Command / Build Configuration
  -> Build Context
  -> Site Definition
  -> Publication Planner
  -> Publication Plan
  -> UI Model Resolver
  -> UI Model
  -> UI Renderer and PA Renderers
  -> Output Writer
  -> Static Site Output
  -> Optional Deployment
```

Each layer exists to preserve a distinct responsibility boundary. No later
layer should quietly take ownership of meaning that belongs to an earlier one.

---

## 6. Layers and Responsibilities

### 6.1 Build Context and Command Entry

Command entry initiates build or deployment activity and selects operational
configuration.

It may determine matters such as:

- build mode;
- output destination;
- local or remote target;
- development/production context;
- date or data-instance selection where that is build configuration.

It shall not contain page-specific public semantics or page rendering rules.

A Build Context carries operational information needed during a build without
becoming the owner of the public site model.

### 6.2 Site Definition

The Site Definition declares intended public organisation.

It owns matters such as:

- site identity;
- the public navigation tree;
- the public page registry;
- page status declarations;
- references to public assets and site-facing material;
- site-level build defaults where applicable.

It says which public site is intended. It does not render the site and does not
own PA internals.

### 6.3 Publication Plan

The Publication Plan resolves the Site Definition for a particular build.

It owns matters such as:

- which declared pages are included;
- public status handling for the build;
- stable public page-selection/deep-link references;
- required site-facing inputs, data and assets;
- consistency checks necessary before modelling or rendering;
- planned output dependencies.

The Publication Plan answers what will be published in this build and what is
required to publish it. It is not a visible UI and does not decide rendering.

### 6.4 UI Model Resolver

The UI Model Resolver converts planned public material into semantic interface
structure conforming to the applicable public grammar.

For a promoted page conforming to `PG`, it resolves:

- the NavigationBar and Navigation required for the visible PublicUI;
- the selected ContentPanel;
- the Heading;
- the Contents structure;
- any FilterSection and its Filters;
- the PAPanel;
- the PA reference or PA model handoff;
- Note ownership and relevant Note declarations.

The resolver may rely on public declarations and site-facing input metadata. It
shall not resolve semantic structure by writing arbitrary HTML or inspecting
legacy rendered output as its normal mechanism.

### 6.5 UI Model

The UI Model is the semantic representation of the public interface that will be
rendered.

It represents the public page structure specified by `PG`, together with the
selection, identity, state and ownership information needed for rendering.

At high level, it contains concepts including:

```text
PublicUI
NavigationBar
Navigation
ContentPanel
Heading
Contents
FilterSection
FilterItem
PAPanel
PA
Notes
Note
```

The UI Model owns interface structure. It does not own analytical computation,
HTML/CSS implementation, output-file writing or deployment.

### 6.6 Published Artifact Model and Producer Handoff

A PA represents deliberately published analytical material within a PAPanel.
The page grammar reaches PA terminal forms such as tables and charts; further
artefact-specific semantic structure may be defined by the Published Artifact
model where necessary.

Producer modules own analysis-specific meaning and provide deliberate
site-facing material for promoted PAs. The PA model/handoff preserves what the
public renderer needs to present that material intelligibly, such as meaningful
columns, traces, labels, Filter interactions, Notes, provenance and public
consistency requirements.

A specialised PA may have specialised internal rendering. It shall not take
over the surrounding public page structure established by `PG`.

### 6.7 UI Renderer

The UI Renderer consumes the UI Model and realises public page structure.

It owns shared realisation of modelled page entities, including:

- the PublicUI shell;
- NavigationBar and Navigation presentation;
- ContentPanel, Heading and Contents layout;
- FilterSection presentation;
- PAPanel placement;
- Notes placement and shared Notes treatment;
- shared CSS and client-side runtime behaviour associated with the public UI.

The UI Renderer shall not invent page-specific public grammar. Its visible
choices are governed by the specification and by declared Rendering Design.

### 6.8 PA Renderers

PA Renderers render Published Artifact terminal forms within the PAPanel.

They may own matters such as:

- table internals;
- chart internals;
- indexed-table loading and selection behaviour declared for the PA;
- sectioned-table internals;
- specialised/custom artefact internals.

They shall not own:

- the public shell;
- NavigationBar or Navigation structure;
- selected-page Heading;
- FilterSection/PAPanel relationship;
- Notes placement outside their declared PA/Note relationship;
- public page-selection conventions.

### 6.9 Output Writer and Runtime Assets

The Output Writer writes the static public site resulting from the resolved
models and rendering decisions.

It may write:

- HTML entry points;
- CSS and JavaScript runtime assets;
- serialized UI/PA/runtime data;
- copied public data and assets;
- build metadata and diagnostics.

Browser runtime assets may restore public state and perform declared interactive
behaviour. They shall not redefine public structure privately in ways that
contradict the specification or UI Model.

### 6.10 Deployment

Deployment transfers completed static output to a local or remote destination.

It shall not influence public page meaning, `PG`, navigation organisation, PA
semantics or Rendering Design. Build and deployment remain separable.

---

## 7. Key Ownership Boundaries

### 7.1 Requirements Own the Product Need

Requirements state what public product must exist and what failure must be
avoided: a coherent, curated site rather than uncontrolled accumulation of
unrelated tools.

### 7.2 Specification Owns Public Structure and Observable Contract

`02 Specification.md` owns the normative public page grammar `PG` and public
behaviour contracts.

### 7.3 UI Model Owns Semantic Interface Structure

The UI Model represents `PG` and associated public state before rendering.

### 7.4 Rendering Design Owns Chosen Visible Realisation

Rendering Design states how modelled entities are visibly realised where the
specification establishes ownership or relationship but does not require one
unique presentation.

### 7.5 PA Design and Producers Own Analytical Presentation Meaning

Producer and PA design own analysis-specific meaning and the features needed for
public presentation of a PA.

### 7.6 Build and Deployment Own Delivery, Not Meaning

Build, output writing and deployment make the specified site available; they do
not decide its public semantics.

---

## 8. Relationship Between PG and Rendering Design

`PG` is a public structural specification, not a stylesheet and not an HTML
template.

For example, `PG` establishes that:

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

This is enough to reject a normal rendering in which Notes are visually laid
out as spanning both the sibling FilterSection and the PA region.

It does not by itself establish:

- the width of the FilterSection;
- whether the PAPanel uses flex or grid layout;
- how much space appears between PA and Notes;
- a maximum Notes height;
- table row colouring;
- text sizes or colours.

Those decisions belong in Rendering Design once chosen, attached to the entity
or terminal form they realise. Rendering Audit then tests whether the visible
site is explained by `PG`, Rendering Design, accepted defaults or recorded
exceptions.

This separation allows the specification to stay clear while ensuring that
presentation decisions do not escape ownership or review.

---

## 9. Relationship to Legacy Evidence

The old `make_site` implementation and earlier documentation may reveal public
behaviour worth retaining or regressions worth correcting. They are evidence,
not authority.

For example, a legacy page may show that readers previously saw a meaningful PA
feature by default, or that Notes were placed with the artefact rather than
under Filters. Such evidence should trigger evaluation against current
requirements and `PG`; it should not be copied merely because it existed.

The replacement documentation and active implementation shall become the source
of authority for `make_site2`.

---

## 10. Growth and Change Discipline

As the public site grows, a proposed promoted page or visible feature shall be
considered in this order:

1. Does it meet the public-site requirements and curation policy?
2. Can it be represented by the existing public specification and `PG`?
3. Can it be represented in the UI Model and relevant PA model without private
   structural invention by a renderer?
4. What Rendering Design rules are required to realise it coherently?
5. What build/runtime/deployment support is required to publish it?

Where the answer to step 2 or 3 is no, the response is not to add unmodelled
page-specific rendering. The specification or model must be extended
explicitly, or the page must remain unpromoted until an acceptable public
structure is agreed.

---

## 11. Design Documents Following This Thesis

The remainder of the active document set shall refine this architecture:

- `04 Model Design.md` and supporting documents shall specify the model layers
  representing public declarations, publication resolution, `PG` and PAs;
- `05 Rendering Design.md` shall specify visible realisation of `PG` and PA
  terminal forms;
- `06 Rendering Audit and Changes.md` shall define how rendering is checked and
  how provisional changes are staged;
- `07 Build, Output and Runtime Design.md` shall specify production of the
  runnable static output;
- `08 Producer Integration and Migration.md` shall specify PA inputs and use of
  legacy evidence;
- `09 Deployment and Operations.md` shall specify delivery and verification;
- `10 Open Issues and Deferred Design.md` shall record unresolved or postponed
  decisions without silently redefining active specification.

---

## 12. Summary

`make_site2` is designed to prevent a growing analytical website from becoming
an incoherent set of individually implemented tools.

The requirements define the needed coherent public product. The specification
defines the public page grammar `PG` and observable contracts. The UI Model
represents that specified interface before rendering. Rendering then realises
the model under declared rules that can be audited. Static output and deployment
publish the result.

The central architectural commitment remains:

```text
No promoted public page is rendered until it has been represented in the UI
Model.
```

That commitment is the mechanism by which the public site remains coherent,
explainable and maintainable as more Published Artifacts are added.