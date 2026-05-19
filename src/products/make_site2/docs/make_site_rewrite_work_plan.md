# make_site Rewrite Work Plan

## Purpose

This document sketches a disciplined work plan for replacing the prototype rendering parts of `make_site` with a more formal publication UI model.

The aim is not to refactor the current implementation until it looks cleaner. The aim is to treat the current `make_site` as a prototype that discovered important requirements, then design a successor from those requirements. Existing code may be copied where appropriate, but only after considering whether it still serves the new design.

The current working assumption is:

> The top-level architecture of `make_site` is broadly sound, but the design becomes increasingly ad hoc as it approaches concrete HTML/CSS/JS production.

The existing `make_site2` package should be understood as a UI model experiment, not as a production replacement. It tested whether public pages could be represented through a small number of formal page grammars rather than through bespoke page shells and page-specific renderers.

## Core Diagnosis

The failure in `make_site` is not primarily functional. The site can be built, pages can be produced, and existing outputs can be published. The failure is architectural: the rendering layer does not have a sufficiently formal model of what it is rendering.

The symptoms include:

- repeated CSS, sometimes inconsistently;
- page-specific HTML/CSS/JS handlers;
- custom renderers that mix page structure, artefact rendering, layout, and styling;
- iframe/page-shell dependencies for migrated or embedded pages;
- unclear boundaries between shared page behavior and artefact-specific behavior;
- difficulty diagnosing whether a visual problem is a rendering bug or a modelling error.

The underlying issue is:

> The prototype discovered what the public site should look like, but it did not formalize the structure being rendered.

The proposed solution is to insert a formal publication UI model between the existing site/page/route layer and concrete HTML/CSS/JS rendering.

## Conceptual Architecture

The successor design should preserve the useful upper-level shape of `make_site` while replacing the ad hoc rendering model.

The conceptual flow should be:

```text
CLI / build orchestration
→ site definition
→ site/page/navigation model
→ producer or artefact preparation
→ route/publication resolution
→ publication UI model
→ shared UI renderer
→ artefact renderers
→ static output/assets
→ deployment
```

The key seam is:

```text
Page + route + artefact/manifest references
→ Publication UI Model
→ HTML/CSS/JS rendering
```

The UI model should not be treated as merely another view type inside the old `builder.write_page` dispatch. It should replace the old page-kind rendering dispatch as the normal way public pages are represented before rendering.

## Design Rule

A useful responsibility split is:

```text
PageRegistry decides what exists.
NavigationTree decides where it belongs.
Routes decide where it is published.
The UI Model decides what the page structurally is.
Renderers decide how that structure becomes HTML.
```

The shared UI renderer should own page structure. Artefact-specific renderers may still exist, but only inside established structural slots.

For example, a Banzuke Changes table may need a custom artefact renderer, but that renderer should not redefine the surrounding page shell, navigation, heading, filter placement, notes, or content panel behavior.

## Role of make_site2

The current `make_site2` package should be treated as evidence from a completed experiment.

Its value is that it tested a formal model of the UI against representative pages. It should not automatically be promoted wholesale into production.

A better name for it in retrospect would have been something like:

```text
UI_model_idea
```

The useful result is the model, not necessarily the package boundary or implementation details.

The model vocabulary includes concepts such as:

- `NavigationBar`
- `ContentPanel`
- `Contents`
- `FilterSection`
- `PA`
- `Artifact`
- `Note`
- `BranchSelector`
- `Branch`

The experiment suggests that most pages fit one of two live grammar shapes.

### G1: Single Visible Artefact

```text
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA . Note*
PA -> Artifact
```

G1 describes pages whose content consists of one visible published analytical artefact, optionally controlled by filters and accompanied by notes.

### G2: Selected Alternative

```text
ContentPanel -> Heading . Contents
Contents -> BranchSelector . Branch+ . Note*
Branch -> FilterSection . PA
PA -> Artifact
```

G2 describes pages where a selector chooses between alternative branches, and only the selected branch contributes a visible artefact.

The key lesson from the Career Length pressure case is that a bad-looking UI may indicate a bad parse of the page structure, not merely a CSS problem.

## Work Plan

### 1. Document the existing make_site architecture

Describe the current `make_site` package closely enough to locate the first point where the design ceases to be coherent.

The documentation should follow the current flow:

```text
CLI / orchestration
→ site definition
→ site/page/navigation model
→ producer invocation
→ route/publication structure
→ static builder
→ page view dispatch
→ rendering
→ PA runtime/manifests
→ static assets
→ deployment
```

The goal is not to criticize every rough edge. The goal is to identify the architectural fault line.

Expected finding:

> The top-level architecture is broadly sound, but the rendering problem first manifests near the transition from `Page` / `ViewSpec` / manifest / route into concrete HTML/CSS/JS generation.

### 2. State the rendering problem precisely

Describe the problem as a missing or insufficient UI model.

The problem should not be reduced to “bad CSS.” CSS repetition is a symptom. The deeper issue is that the renderer repeatedly decides page structure locally instead of rendering from a shared formal structure.

### 3. Describe the required solution

Define the need for an intermediate publication representation between:

```text
This page exists at this route with this artefact
```

and:

```text
Write these concrete HTML/CSS/JS files
```

That intermediate representation should describe the page structurally before rendering begins.

### 4. Recognize make_site2 as the UI model evidence

Record that `make_site2` already tested this idea against representative pages.

The conclusion should be:

> `make_site2` is not the production replacement for `make_site`; it is the experiment that proves the missing UI model is viable.

### 5. State the conceptual replacement

The conceptual proposal is:

> Delete the old prototype rendering model and replace it with the UI Model.

More carefully:

- keep high-level site/build/navigation/page machinery where still valid;
- replace ad hoc page-view rendering with a formal publication UI model plus shared renderer;
- allow custom artefact renderers only inside established structural slots;
- avoid making the UI model just another old-style `ViewSpec` branch.

### 6. Rewrite requirements for the successor package

Write requirements from first principles for the successor site builder package.

These requirements may turn out to be very close to the current `make_site` requirements, but they should not be copied uncritically.

The requirements should cover:

- site definition;
- navigation;
- routing;
- producer or artefact preparation;
- page publication structure;
- manifest and data handling;
- static output generation;
- runtime assets;
- build modes;
- deployment or cutover;
- diagnostics and parity checks.

They should also state non-goals, such as:

- no live application server;
- no database-backed public API;
- no dynamic user accounts;
- no page-local layout hacks as a primary design mechanism.

### 7. Rewrite the specification

Turn the requirements into a behavioral spec for the successor package.

The spec should describe observable behavior and interfaces, not historical implementation accidents.

Examples of spec statements:

- A page declaration produces one routed public page.
- Navigation is derived from the declared navigation tree.
- A publication page is rendered through a normalized UI structure.
- A G1 page renders one visible artefact.
- A G2 page renders one selected branch at a time.
- Shared page chrome is rendered by the shared UI renderer.
- Artefact-specific renderers cannot redefine the surrounding page structure.

The spec may overlap heavily with the old `make_site` spec, but the rendering section should be materially different.

### 8. Evaluate the UI Model against the spec

Where the spec talks about rendering, ask:

- Does the UI Model already satisfy this?
- Can it be adapted cleanly?
- Does the spec reveal a missing grammar?
- Is the old prototype behavior actually required, or merely accidental?

The UI Model should be treated as strong evidence, not as unquestionable authority. If the spec contradicts the model, resolve that disagreement at the requirements/spec/design level before coding.

### 9. Write the new design using the UI Model

The design should introduce a clear publication-model seam:

```text
Page + route + manifest/artifact references
→ Publication Model Adapter
→ PublicationPage / ContentPanel / G1 / G2
→ shared UI renderer
→ artefact renderer registry
→ output files/assets
```

The design should identify:

- which parts of the existing `make_site` architecture survive;
- which parts of `make_site2` become the formal UI model;
- which renderers are shared structural renderers;
- which renderers are artefact renderers;
- how manifests and data files are resolved;
- how old pages migrate gradually;
- how parity with the current site is checked.

### 10. Define copy/paste rules

Copying code is allowed, but only after considering the implications.

Suggested rules:

- Copy code only if its responsibility remains valid in the new design.
- Do not copy code whose purpose is to preserve old rendering structure.
- Do not copy CSS merely because it makes a page look right.
- Copied code must be renamed or relocated to match its new responsibility.
- Every copied renderer must declare whether it renders shared structure or artefact internals.
- If copied code forces the new model to imitate an old accident, stop and revisit the design.

### 11. Implement incrementally

Implementation should be incremental, but the design should not be.

A possible implementation sequence is:

1. Create the successor package skeleton.
2. Port or rewrite the site/page/navigation definitions.
3. Implement route/output assembly without changing rendering yet.
4. Implement the publication model: `PublicationPage`, `ContentPanel`, G1, and G2.
5. Adapt one simple G1 page end to end.
6. Adapt one G1 page with a custom artefact renderer, such as Banzuke Changes.
7. Adapt the G2 pressure case, Career Length.
8. Add parity checks against current output where useful.
9. Migrate remaining pages by artefact class.
10. Retire old rendering paths once covered.
11. Reconnect full CLI/build/deploy behavior.
12. Perform final cutover when the successor package owns the required production behavior.

## Migration Principle

The migration may proceed in small slices, but each slice should be based on the new model.

Do not gradually patch the old renderer until it resembles the UI Model. Instead, introduce the UI Model at the correct conceptual seam, migrate pages into it, and retire the old rendering paths as they become unnecessary.

## Open Naming Question

The final package name is deliberately unresolved.

The name `make_site2` is already used for the UI model experiment and may be misleading for the production successor. A later decision should choose whether to:

- replace `make_site` in place;
- create a new package name temporarily;
- rename the UI model experiment;
- or promote selected UI model modules into the production package.

This naming decision should not block the conceptual design.

## Summary

The current `make_site` prototype discovered much of the correct public-site architecture, but it lacks a sufficiently formal UI model at the point where pages become HTML/CSS/JS.

The `make_site2` experiment appears to provide the missing model: a small grammar for publication pages, a shared content panel structure, and a disciplined split between shared page rendering and artefact-specific rendering.

The rewrite should therefore preserve the valid upper-level site architecture, replace the ad hoc rendering layer with the UI Model, and implement the successor package incrementally under a fresh requirements/spec/design process.
