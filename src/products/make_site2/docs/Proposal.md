# Proposal: Redocument `make_site2` Around the Public Page Model

## Status

Proposal for replacing the active `make_site2` documentation set.

The previous documents have been moved to `docs/archive` and remain available as
historical evidence while the replacement documentation is developed.

---

## 1. Why Redocument the Project

The archived documentation contains much of the information needed to describe
`make_site2`, but it does not tell one clear story from requirement to model to
rendering. It begins largely with contracts for data, declarations and public
publication units, then introduces visible UI structure in several places. In
particular, it states that the UI Model owns the full public interface, including
the navigation bar and content panel, but gives the named content grammar to the
interior of the content panel only. That makes it too easy to discuss page
rendering as though the outer shell were merely implementation while the inner
content were model-governed.

That weakness became visible during styling work. Questions about navigation
spacing, notes placement and the relationship between filters and Published
Artifacts could not be answered cleanly from a single governing model. The old
documents contain relevant principles, but their structure obscures the central
idea: the visible public page is a modelled object, and rendering decisions
throughout that page should be auditable against the model.

The new documentation will make that idea explicit and central. It will begin
with the public-site problem and requirement, define the full public page model
normatively, state the model-first design thesis, and then explain the model,
renderer, build and deployment layers as means of satisfying that requirement.
The result should be easier to read, harder to misinterpret, and more useful as
the site grows.

---

## 2. The Problem Being Addressed

`make_site2` exists to publish curated professional sumo analysis as a coherent
static public website. As more analytical artefacts are promoted, the public
site must not spiral into a collection of independently designed tools with
inconsistent navigation, page framing, controls, notes, layouts and styling.

The required result is a coherent public publication surface:

- subject-led navigation;
- a selected-page content display;
- clear page framing;
- filters where needed;
- one visible Published Artifact in the initial page shape;
- relevant explanatory notes and caveats;
- stable reproducible public views;
- static build and deployment.

These are product requirements. They do not, on their own, require a particular
implementation architecture or grammar notation.

---

## 3. Design Thesis

`make_site2` will preserve coherence as the site grows by modelling the public
interface before rendering it.

The central design thesis is:

```text
No promoted public page is rendered until it has been represented in the UI
Model.
```

The public page grammar, `PG`, defines the semantic shape of the visible public
page. The renderer realises that model as HTML, CSS and browser behaviour.
Visible authored structure and layout must therefore flow from:

1. the page grammar or associated model;
2. a declared rendering rule attached to an entity in that model;
3. an explicitly accepted browser/default behaviour; or
4. a justified and recorded exception.

This makes rendering auditable. It permits an auditor to ask not only whether a
Published Artifact is rendered correctly, but also whether NavigationBar layout,
navigation presentation, content-panel structure, filter placement and notes
placement are justified by the same public page model.

---

## 4. Proposed Normative Page Grammar

The replacement specification will define a full-page grammar called `PG`.
Unlike the archived `G1` presentation, `PG` begins at the visible public page
rather than only within the selected page contents.

```text
PG

PublicUI -> NavigationBar . ContentPanel

NavigationBar -> <site caption> . Navigation . <hider>

Navigation -> <hierarchical numbered navigation items>

ContentPanel -> Heading . Contents

Heading -> <main heading> . <sub heading>?

Contents -> FilterSection? . PAPanel

FilterSection -> FilterItem*

FilterItem -> BooleanChoice | SingleFiniteChoice

BooleanChoice -> <label> . <default>

SingleFiniteChoice -> <label> . Values . <default>

Values -> <value>+

PAPanel -> PA . Notes

PA -> <table> | <indexed table> | <chart> | <sectioned table> |
      <prose> | <custom artifact>

Notes -> Note*
```

`PA` always means **Published Artifact**.

The grammar is intentionally at public-page level. Artefact internals may be
modelled separately where needed, but at this level each artefact form is a
terminal of the page grammar.

### Material differences from the archived specification

The proposed grammar makes two substantive changes:

1. `PG` governs the whole visible page, including the relationship between the
   `NavigationBar` and `ContentPanel`.
2. `PAPanel` is an explicit entity containing the Published Artifact and its
   Notes, while the `FilterSection` is its sibling.

The second point makes note ownership visible in the structure: filters govern
what is displayed, while notes explain or qualify the Published Artifact or its
visible features. It also exposes a current rendering error: notes must not be
laid out as spanning both the filters and the Published Artifact panel.

---

## 5. Proposed Documentation Set

The new active documentation should be written in the following order. Archived
documents may be consulted as evidence, but should not remain as competing
active authority.

### `01 Requirements.md`

Defines what product must exist and why.

It should cover:

- purpose: publishing curated sumo analysis as a coherent static public site;
- reader needs and curation requirements;
- required public website shape in ordinary language;
- the risk of uncontrolled growth as more artefacts are added;
- responsibilities of `make_site2` versus producer modules;
- static deployment requirements;
- public status/candidate/legacy requirements;
- non-requirements.

It should describe the required visible website without prescribing `PG` or the
model-first solution.

### `02 Specification.md`

Defines the normative public model and observable public behaviour.

It should cover:

- the full page grammar `PG`;
- public site, page and navigation contracts;
- Published Artifact and Notes contracts;
- filter terminology and behaviour;
- deep-link and URL-state requirements;
- public status and curation vocabulary;
- error/missing-state behaviour;
- acceptance criteria.

This is the normative centre of the documentation set. It should state that
`PG` is the formal refinement of the public website required by
`01 Requirements.md`.

### `03 Architecture and Design Thesis.md`

Explains why the system is built as it is and how it satisfies the
specification.

It should cover:

- the model-first design thesis;
- the requirement that rendering be auditable against `PG`;
- the processing pipeline;
- major layers and responsibility boundaries;
- why page-specific HTML/CSS/JavaScript must not become the architecture.

The high-level pipeline is:

```text
Site Definition
  -> Publication Plan
  -> UI Model
  -> Renderer
  -> Static Output
  -> Deployment
```

### `04 Model Design.md` and supporting model documents

Defines the semantic models that represent the public site before rendering.

Proposed document family:

```text
04 Model Design.md
04.1 Site Definition Model.md
04.2 Publication Plan Model.md
04.3 Public UI Model.md
04.4 Published Artifact Model.md
```

The Public UI Model document must represent the full `PG` tree, including the
NavigationBar, content panel and `PAPanel` relationship. It must not present the
NavigationBar as outside the named page grammar.

### `05 Rendering Design.md`

Defines how the UI Model is realised as visible output.

It should be organised around the productions of `PG`, including:

```text
Rendering PublicUI
Rendering NavigationBar
Rendering Navigation
Rendering ContentPanel
Rendering Heading
Rendering Contents
Rendering FilterSection
Rendering PAPanel
Rendering PA terminals
Rendering Notes
```

It should also define:

- shared table/chart/prose treatment;
- theme and density decisions where settled;
- permitted browser defaults;
- semantic CSS ownership;
- how justified deviations are documented.

### `06 Rendering Audit and Change Record`

Defines the audit procedure and records staged rendering decisions that have not
yet been incorporated into normative design.

Proposed documents:

```text
06.1 Rendering Audit Method.md
06.2 Rendering Changes.md
```

The existing `09.1 Rendering Changes.md` material should be reviewed and moved
into this part of the new document set, separating completed rendering rules
from open action items.

### `07 Build, Output and Runtime Design.md`

Defines how the modelled and rendered site becomes a runnable static output
 tree.

It should cover:

- build modes;
- output-tree structure;
- runtime manifest/data assets;
- browser runtime behaviour and URL-state restoration;
- build errors and diagnostics;
- local inspection workflows.

### `08 Producer Integration and Migration.md`

Defines how analytical producers provide public material and how existing
outputs are assessed or migrated.

It should cover:

- site-facing inputs;
- Published Artifact promotion;
- producer ownership of analytical meaning;
- legacy `make_site` as evidence rather than authority;
- migration and regression checking.

### `09 Deployment and Operations.md`

Defines local and remote delivery of built output, configuration and operational
verification.

### `10 Open Issues and Deferred Design.md`

Records unresolved questions and explicitly deferred design work, including
possible richer future page grammars.

### Appendices

Supporting and historical material may remain available without defining active
normative behaviour, for example:

```text
A Alternative and Richer Page Grammars.md
B Legacy Evidence and Comparative Notes.md
C Review History and Actions.md
```

---

## 6. Immediate Design Consequences to Carry Forward

The new documentation work should preserve the useful decisions already made
while re-evaluating them against `PG`.

In particular:

- NavigationBar and Navigation layout are rendered consequences of the public
  page model, not incidental shell styling;
- notes belong in `PAPanel`, below or alongside the Published Artifact as
  declared by rendering design, and must not span the sibling `FilterSection`;
- shared table treatment is a rendering rule for Published Artifact table
  terminals, not a collection of page-specific fixes;
- unresolved typography ownership should remain an explicit action item until a
  coherent heading-rendering rule is chosen;
- Banzuke Changes direction rendering is a Published Artifact-specific visible
  rule that must remain auditable within the model/rendering boundary.

---

## 7. Work Plan

The proposed redocumentation should proceed in this order:

1. Agree this proposal and the role of `PG`.
2. Write `01 Requirements.md` in requirement language, avoiding premature
   solution claims.
3. Write `02 Specification.md` with `PG` as its normative centre.
4. Write `03 Architecture and Design Thesis.md` to explain the model-first
   solution and auditability principle.
5. Rebuild model and rendering design documents against the new specification.
6. Re-home existing rendering-change notes and unresolved action items.
7. Rebuild build, integration, deployment and open-issues documentation only
   after the public model and rendering story are stable.
8. Use archived documents as evidence to ensure useful contracts are not lost,
   without copying forward contradictory framing.

---

## 8. Expected Outcome

The new document set will provide one intelligible line of reasoning:

```text
The site must remain a coherent public publication as it grows.

PG specifies the visible public-page structure that provides that coherence.

The UI Model represents PG before rendering.

Rendering is an auditable realisation of the model.

Build and deployment publish the resulting static website.
```

This should make future page additions and styling changes easier to assess,
make regressions easier to identify, and prevent implementation convenience from
quietly redefining the public site.