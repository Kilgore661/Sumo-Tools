# Second `make_site2` Review

## Status

Current review of `src/products/make_site2` against the replacement active
documentation set drafted in May 2026, updated after the first corrective
implementation work and the decision on public-view linking.

This review is comparative. It asks whether the current code implements the new
requirements, specification, model boundaries and rendering discipline. It is
not a historical record of every implementation state: findings that have been
corrected are recorded as such, and current remaining mismatches are given
priority.

The `PAPanel`/Notes correction and modular-runtime activation have been checked
through the normal local build/deploy inspection workflow and reported as
working. The canonical single-shell public-link design has now been agreed in
the active documentation, but the corresponding code correction has not yet
been made or verified.

---

## 1. Active Documentation Baseline

The active documentation establishes this design sequence:

```text
01 Requirements
  The public site must remain a coherent publication surface as more
  analytical artefacts are added.

02 Specification
  The page grammar PG specifies the whole visible public page and every
  material public view has a canonical copyable link.

03 Architecture and Design Thesis
  No promoted public page is rendered until represented in the UI Model.

04 Model Design
  Site Definition, Publication Plan, Public UI Model and Published Artifact
  Model have distinct responsibilities.

05 Rendering Design
  Rendering is an auditable realisation of modelled owners and declared
  presentation policy.

06 Rendering Audit and Changes
  Visible facts are tested for ownership, conformance and implied meaning.

07–09
  Build/runtime, integration/migration and deployment deliver the modelled and
  rendered site without redefining it.

10
  Unresolved issues are recorded rather than settled implicitly in code.
```

The governing page structure is:

```text
PublicUI -> NavigationBar . ContentPanel
NavigationBar -> <site caption> . Navigation . <hider>
ContentPanel -> Heading . Contents
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

The governing current public-view-link policy is:

```text
one static application shell
canonical public link = selected Page + all applicable material Filter values
Navigation destination = canonical default public view of its Page
```

`A Appendix - Better Models.md`, currently restored outside `docs/archive`, is
not assessed here as active normative design. Its status should be considered
only when richer-page pressure is reviewed deliberately.

---

## 2. Current Implementation Areas Considered

This review concerns the following current implementation areas:

```text
models.py
site_definition.py
navigation.py
publication_model.py
ui_model.py
artifact_model.py
site_manifest.py
manifest/
  filters.py
  artifacts.py
  builder.py
render.py
runtime/site.css
runtime/site-refactor/
build.py
data_output.py
routes.py
deploy.py
__main__.py
```

The implementation has changed since the initial review:

- the browser runtime is now modular and is loaded as an ES module;
- `ui_model.py` now represents `Contents`, `PAPanel` and `Notes` directly;
- manifest declarations have been split behind a stable `site_manifest.py`
  facade;
- manifest assembly now constructs `PAPanel` directly and exports artefacts for
  planned public panels;
- Notes now render within the PA-owned region.

The active documentation has additionally changed since the initial review:

- a single static shell has been selected as the current public-view output
  design;
- canonical Public View Links must state selected Page identity and all
  applicable material Filter values, including defaults;
- Navigation destinations must identify canonical default Page views rather
  than unwritten route-local entry documents.

---

## 3. Overall Assessment

The implementation is now substantially closer to the new design than at the
start of this review.

It already had useful architectural seams:

- explicit Site Definition and subject-led Navigation;
- explicit Page statuses;
- a `PublicationPlan` layer;
- semantic PA declarations and site-facing structured data;
- static output and browser runtime;
- local and remote deployment paths;
- implemented table readability rules and PA-specific Banzuke Changes movement
  direction.

The first material conflict with the new `PG`-centred model has now been
corrected:

```text
formerly:
  inner selected-page contents used G1 and Notes rendered outside the PA region

now:
  ContentPanel contains Contents; Contents contains optional FilterSection and
  PAPanel; PAPanel contains PA and Notes; runtime renders that relationship
```

The most significant remaining current inconsistency is now governed by an
agreed correction rather than an unresolved choice:

> Navigation links still advertise route-local static destinations while current
> output supplies a single root application entry and JavaScript query-state
> selection. The agreed fix is to emit and maintain canonical Public View Links
> in the existing single static shell.

Other remaining matters are a mixture of genuine design decisions, incomplete
layer control and operational safety improvements rather than evidence that the
product needs to be started again.

---

## 4. Summary of Current Findings

| Priority | Finding | Current assessment |
| --- | --- | --- |
| Done | `Contents`, `PAPanel` and `Notes` are explicitly modelled; Notes render inside the PA region and no longer span Filters. | First central `PG` structural nonconformance corrected and locally verified. |
| Done | `site_manifest.py` previously mixed declarations, UI assembly and runtime export behind a temporary `G1` adapter. | Split behind a stable facade; new assembly constructs the active model directly and removes the `G1` seam. |
| Done | The monolithic browser runtime impeded manageable change. | Modular ES-module runtime activated and working locally. |
| Decided / P0 implementation | Navigation `href`s are route-local `.../index.html` paths while build output supplies only root `index.html` and runtime query-state navigation. | Implement canonical single-shell Page-plus-material-Filter links and verify copied/reloaded/new-tab behaviour. |
| P1 | Publication planning controls visible panels/exported artefacts more directly than before, but data staging and wider runtime dependencies remain largely hard-coded in the build. | Layer boundary improved but incomplete. |
| P1 | Runtime renderer branches still repeat ContentPanel/PAPanel assembly around specialised PA internals. | Scaling/drift risk remains, though duplicated shape now renders correctly. |
| P1 | All currently declared Pages remain `PROMOTED`, despite still-open status/inclusion and rendering-policy questions. | Curation/status review still required. |
| P1 | Local deployment cleaning accepts arbitrary supplied roots without the documented successor-target safety validation. | Operational safety improvement required. |
| P2 | Heading typography, Rank-cell semantics, Notes visual/dimension policy and context-colour meaning remain unsettled. | Deliberate open rendering/design questions. |
| P2 | PA metadata partly mixes analytical/semantic material and rendering/runtime hints in `provenance`. | Align gradually under real PA pressure. |

---

## 5. Site Definition and Publication Planning (`04.1`, `04.2`)

### 5.1 Strong Existing Alignment

`SiteDefinition`, Page declarations, statuses and subject-led Navigation remain a
sound implementation basis for the active model. Public intent is declared
separately from HTML rendering, and only planned Pages participate in public
panel assembly.

### 5.2 Improvement Since Initial Review

The new internal manifest assembly layer now provides a `PanelDeclaration` for
each public Page and resolves public panels from the `PublicationPlan`. It also
raises an error if an included planned Page has no panel declaration and exports
runtime artefacts only for planned panels.

This removes the earlier unconditional artefact-export list problem and makes
public assembly more accountable to planning.

### 5.3 Immediate Planning Correction Required

The active Publication Plan design now requires each included selectable Page to
have a canonical default Public View Link and each Navigation destination to use
that link. The implementation still exposes route-local hrefs inherited from
its former route representation.

The immediate correction should generate visible Navigation destinations from:

```text
Page identity + declared default values of the Page's material Filters
```

rather than from unwritten route-local HTML paths.

### 5.4 Remaining Broader Boundary Gap

`build.py` still stages/copies or generates data through a fixed series of calls
before or independently of a richer resolved Page-dependency contract.
Consequently:

- status/inclusion changes may not yet drive data preparation completely;
- data can be staged for Pages not ultimately included in a future build mode;
- producer/input failures arise through hard-coded build steps rather than a
  fully resolved dependency plan.

This remains a P1 maturation issue, not part of the canonical-link correction.

---

## 6. Public UI Model and `PG` (`02`, `03`, `04.3`)

### 6.1 Corrected Model Relationship

The implementation now directly models the key ordinary page relationship:

```text
PublicSiteShell
  NavigationBar
  ContentPanel
    Heading
    Contents
      FilterSection?
      PAPanel
        PA
        Notes
```

`NavigationBar` remains the accepted model term. The obsolete inner-content
`G1` arrangement and its compatibility adapter have been removed.

### 6.2 Corrected Rendering Relationship

The modular runtime now renders the visible relationship as:

```html
<div class="content-body">
  <!-- optional FilterSection -->
  <section class="pa-panel">
    <div class="pa-slot">...</div>
    <aside class="notes-panel">...</aside>
  </section>
</div>
```

and limits visible Notes to the Note ids owned by the visible `PAPanel`.

This correction matters because it does not merely place Notes more attractively:
it makes their visible ownership conform to `PG`.

### 6.3 Minor Remaining Naming Point

The implementation class remains named `PublicSiteShell` rather than
`PublicUI`. This is not currently a material mismatch: the class now contains
the modelled top-level visible regions and no longer depends on a competing
inner-content grammar. A rename should occur only if it improves clarity during
a later model tidy, not as a priority correction.

---

## 7. Public Selection and Static Output (`02`, `04.2`, `07`)

### 7.1 Current Implementation Mismatch

`routes.py` derives route-like Page hrefs such as:

```python
def route_href(parts: tuple[str, ...]) -> str:
    return PurePosixPath(*parts, "index.html").as_posix()
```

Navigation anchors expose those hrefs. The current build, however, writes a
single root `index.html`, and browser runtime intercepts ordinary clicks and
uses query-state selection.

The result is that the ordinary JavaScript-click experience can appear to work
while the anchor itself promises a static destination the output tree does not
provide. Likely affected behaviours include open-in-new-tab, copy-link/direct
navigation and operation without successful runtime interception.

### 7.2 Decision Made

The active specification and design now choose:

```text
one static application shell
canonical Public View Link = Page identity + all applicable material Filter values
Navigation link = canonical default Public View Link for the Page
```

Human-readable route-local paths are not required. The required behaviour is
that every material public view has a deterministic link which can be copied,
pasted and reopened to restore the same view.

Canonical links must state applicable material Filter values explicitly,
including default values. Shell-only/transient state such as NavigationBar
visibility, scroll, hover or ordinary tooltip state is excluded.

### 7.3 Implementation and Verification Required

The next code correction shall:

1. emit Navigation hrefs into the existing single shell using Page identity and
   declared default Filter values;
2. centralise canonical runtime URL writing/restoration for selected Page and
   all applicable material Filter state;
3. remove irrelevant Filter parameters when the selected Page changes;
4. resolve incomplete or safely recoverable invalid incoming URLs and expose
   the canonical link for the valid displayed view; and
5. verify ordinary click, new-tab/copied/direct navigation, reload, filtered
   view restoration and back/forward behaviour.

Longer-term compatibility guarantees for links that have been published remain
a later policy matter; they do not block implementing the chosen current
contract.

---

## 8. Published Artifact Model (`04.4`)

### 8.1 Strong Existing Basis

The implementation continues to model meaningful PA concepts:

- indexed sources and ordinary data sources;
- table columns and column groups;
- chart traces and axes;
- sectioned-table sections;
- Notes and Note relevance;
- specialised Banzuke Changes and Standings declarations.

The refactor into `manifest/artifacts.py` makes these declarations easier to
locate and separates them from public UI assembly.

### 8.2 Terminal-Form Alignment Still Incomplete

The documentation names broad PA terminal forms such as `<table>`, `<indexed
table>`, `<chart>`, `<sectioned table>`, `<prose>` and `<custom artifact>`.
Current implementation kinds include specialised forms such as
`banzuke_changes` and `standings`.

This is not an immediate blocker. It remains an evidence-driven question:
whether these should remain terminal kinds, become renderer kinds beneath a
broader terminal form, or motivate a clearer custom-artifact registration
boundary.

### 8.3 Metadata Ownership Still Needs Care

Some chart declaration `provenance` material represents rendering/runtime hints
rather than public source/method provenance, including colour maps, tick angles,
legend instructions and view configuration. The separation between analytical
meaning, public explanation and rendering configuration should be clarified as
real PA work makes that worthwhile.

---

## 9. Filters and Notes (`02`, `04.3`, `05`)

The current Filter model and runtime already provide declared reader-visible
state, allowed/default values, URL restoration, data/source selection and Note
relevance behaviour.

The formal specification distinguishes:

```text
FilterItem -> BooleanChoice | SingleFiniteChoice
```

whereas the implementation currently models generic `Filter` declarations with
widget-flavoured `control` values and selects radio versus dropdown rendering
for finite choices in runtime. This remains a model/rendering-policy refinement,
not an immediate correctness blocker.

The Notes ownership issue is no longer open: Notes are now owned and rendered by
`PAPanel`. Richer Note targets remain deferred until real cases require them.

The chosen canonical-link design now makes all material Filter state part of the
public-view link contract. The current runtime's URL behaviour must therefore be
checked and amended so every applicable Filter value, including defaults, is
written canonically for the displayed selected-Page view.

---

## 10. Rendering Design and Audit (`05`, `06`)

### 10.1 Implemented Shared Treatments

The following rendering treatments are implemented and already documented as
agreed rules or corrections:

| Rendering treatment | Current status |
| --- | --- |
| Navigation-local line height | Incorporated shared rule. |
| Filter structural lists without bullets | Incorporated shared rule. |
| Shared table cell padding | Incorporated shared rule. |
| Alternating data-row backgrounds | Incorporated shared rule. |
| Continuous table-row colouring without unintended cell gaps | Incorporated shared rule. |
| Banzuke Changes `⇅` movement-direction feature in both table forms | Incorporated PA-specific rule. |
| Notes rendered within `PAPanel` rather than beneath Filters and PA together | Implemented and locally verified structural correction. |

### 10.2 Open Rendering Decisions

The following remain genuinely open:

- heading typography ownership between role-specific selectors and HTML heading
  defaults;
- semantic/visible treatment of Banzuke Changes central Rank cells;
- Notes-panel maximum height, overflow and additional visual framing;
- whether local/remote/preview background colours are an intended operational
  cue or should be revised/removed.

These should remain separate from the public-link/output correction.

---

## 11. Runtime Architecture and Scaling Risk (`03`, `05`, `07`)

### 11.1 Improvement Since Initial Review

The browser runtime has been split into manageable ES modules and is now the
active build output source. This reduces editing risk and makes responsibilities
such as URL state, Filters, Notes, tables, charts and panel dispatch easier to
inspect.

### 11.2 Immediate Runtime Work

The modular runtime's URL-state responsibility is now the natural implementation
point for canonical Public View Link restoration and writing. That work should
remain focused on public state and avoid simultaneously centralising all repeated
panel-renderer structure.

### 11.3 Remaining Duplication

The runtime still has PA-specific content-panel renderer functions that repeat
Heading, ContentBody, optional FilterSection, PAPanel and Notes assembly around
PA internals. They now repeat the **correct** shape, but repetition still creates
future drift risk.

A later refactor should make common page/PAPanel assembly occur once and keep
specialisation within PA internals. This should not be combined with the next
public-link/output correction unless doing so becomes technically unavoidable.

---

## 12. Build, Output and Runtime (`07`)

### 12.1 Current Alignment

The build/runtime path now includes:

- clean static output-tree creation;
- a root entry HTML document;
- serialized public UI/runtime manifest material;
- a modular ES-module browser runtime copied into output;
- development cache-busting extended across relative ES-module imports;
- static PA data staging;
- browser restoration of Page and Filter state;
- `BuildOutput` reporting.

These support the selected single-shell design in broad form.

### 12.2 Required Current Correction

The current output already supplies the selected shell, but live Navigation links
and URL-state writing do not yet implement the newly settled canonical link
contract. The immediate implementation change is therefore alignment within the
existing output architecture, not a redesign of output around per-Page entry
files.

### 12.3 Remaining Later Work

Longer-term issues remain:

- broader dependency/data staging driven by the Publication Plan;
- documented/versioned bootstrap-manifest policy;
- optional build metadata;
- validation that promoted planned Pages have all required model/data/runtime
  support;
- compatibility policy for canonical links after public publication.

---

## 13. Producer Integration and Migration (`08`)

The current product consumes structured site-facing data/configuration and
renders PAs in the public runtime; it does not normally publish copied standalone
legacy pages. This remains a strong alignment with the migration boundary.

The restored Banzuke Changes `⇅` feature remains a useful example of legacy
evidence being assessed and adopted as public analytical meaning rather than old
page structure being copied wholesale.

Integration contracts remain spread across Page declarations, PA declarations,
data-output preparation, build orchestration and runtime assumptions. The new
manifest split improves local clarity, but larger producer/build integration
should be refined only while migrating real Pages.

---

## 14. Deployment and Operations (`09`)

Existing build/deploy commands support build-only, local deployment, remote
SFTP deployment and deploying existing output. These broadly align with the
operations design.

Two concrete operational concerns remain:

1. check the documented local target spelling (`A:\local\htm\sumo-tools2`)
   against the current code value (`A:/local/html/sumo-tools2`); and
2. add clean-target safety validation before treating arbitrary CLI-supplied
   local roots as safe for destructive replacement.

The second concern is P1 because it has potential destructive impact.

---

## 15. Additional Specific Findings Still Open

### 15.1 Page Summary Containing Escaped HTML

A Page summary for `first_chii_appearance` has previously contained embedded HTML
anchor markup while the runtime escapes summaries as text. Unless already
corrected outside this review, that should be treated as a plain-text wording bug
or become a deliberately modelled structured-framing feature; embedded HTML in
an escaped string is not a valid link implementation.

### 15.2 Home/Landing Presentation

Runtime landing behaviour remains outside the declared Page set and primarily
signals local/remote/preview context. Since home/landing policy is still open,
this is implemented provisional behaviour requiring later review, not an
immediate blocker for the current next fix.

The selected single-shell link design permits the root shell URL to remain the
landing view for now; it must not also become an alternative canonical link for
a material selected-Page view.

---

## 16. Recommended Correction Sequence From Here

### Completed

```text
Activate modular runtime without intended behaviour change.
Correct active terminology to NavigationBar.
Model Contents / PAPanel / Notes explicitly.
Render Notes within PAPanel and verify locally.
Split manifest declarations behind a stable facade and remove the G1 seam.
Decide that public material views use canonical Page-plus-Filter links in one
static shell.
```

### Next: Implement the Canonical Public Link Contract

1. Generate Navigation hrefs from Page identity plus declared default material
   Filter values, not unwritten route-local output paths.
2. Centralise canonical URL restoration/writing in the modular runtime.
3. Ensure every applicable material Filter value, including defaults, is present
   in the displayed view's canonical link.
4. Ensure Page selection removes stale parameters belonging to another Page.
5. Verify ordinary click, copied/new-tab/direct link, reload, filtered-view and
   back/forward behaviour.

### Then: Address High-Value Independent Matters

1. Decide heading typography ownership.
2. Decide Banzuke Changes Rank-cell semantics.
3. Decide Notes-panel visual/dimension policy.
4. Decide context-colour presentation policy.
5. Add deployment target-safety validation.

### Later: Mature the Scaling Boundaries

1. Reduce repeated page/PAPanel runtime assembly.
2. Move data/runtime dependencies toward Publication Plan-driven resolution.
3. Review Page promotion status and build-mode inclusion.
4. Refine producer integration while migrating the next real PA family.

---

## 17. Conclusion

The first correction cycle has materially improved alignment between the active
new documentation and the code. The implementation no longer carries the old
`G1` inner-content story in its active public UI model or runtime rendering:
`PAPanel` is now an explicit modelled and rendered owner of PA and Notes.

The next mismatch also now has an explicit design resolution: the current public
site uses one static application shell, and every material selected-Page view is
to be represented by a canonical link containing Page identity and all
applicable material Filter values. Code still needs to implement that decision
by replacing route-local live Navigation destinations and canonically maintaining
runtime URL state.

The codebase remains worth evolving rather than replacing. After canonical
public links are implemented and verified, the remaining issues are contained
rendering-policy, planning-maturity and operational-safety choices. Addressing
them in sequence will continue the intended approach: visible and operational
behaviour should flow from explicit public-model and design decisions rather
than accumulate as unexamined implementation convenience.