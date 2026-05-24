# Second `make_site2` Review

## Status

Initial review of the existing `src/products/make_site2` implementation against
the replacement active documentation set drafted in May 2026.

This review is deliberately comparative. It asks whether the current code
implements the new requirements, specification, model boundaries and rendering
discipline. It does not assume that the code is wrong merely because the
terminology has changed, nor that the documents are correct merely because they
are newer.

This first pass is based on inspection of the current source on `dev`. It has not
yet included a fresh browser rendering audit or execution of the build/test
workflow. Visible-rendering findings stated from code should therefore be
confirmed in the served output when implementation work begins.

---

## 1. Active Documentation Baseline

The new active documentation establishes the following central story:

```text
01 Requirements
  The public site must remain a coherent publication surface as more
  analytical artefacts are added.

02 Specification
  The page grammar PG specifies the whole visible public page.

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

The principal normative change from the archived documents is the replacement
of the old inner-content `G1` framing by the whole-page grammar `PG`:

```text
PublicUI -> Sidebar . ContentPanel
Sidebar -> <site caption> . Navigation . <hider>
ContentPanel -> Heading . Contents
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

That change is the main test applied in this review.

`A Appendix - Better Models.md`, now restored outside `docs/archive`, is not
assessed here as active normative design. Its status can be reconsidered when
richer-page pressure is reviewed deliberately.

---

## 2. Implementation Inspected

The following current implementation material has been inspected in this pass:

```text
models.py
site_definition.py
navigation.py
publication_model.py
ui_model.py
artifact_model.py
site_manifest.py
render.py
runtime/site.js
runtime/site.css
build.py
data_output.py
routes.py
deploy.py
__main__.py
```

These files are sufficient to assess the principal model/rendering/build and
deployment seams. Further inspection of tests, generated output and browser
behaviour should follow once the first corrective work is selected.

---

## 3. Overall Assessment

The current code is **not a failed precursor that needs discarding**. It already
contains several of the architectural seams now required by the new documents:

- an explicit site declaration and subject-led Navigation tree;
- explicit Page statuses;
- a `PublicationPlan` concept;
- semantic UI-model dataclasses consumed by rendering/runtime output;
- semantic artefact declarations with Notes, Filter relationships and chart/
  table-specific metadata;
- a static application shell and serialized runtime manifest;
- clean build-output generation and separable deployment operations;
- deliberate work already done on Navigation, Filter list and table rendering;
- PA-specific restoration of Banzuke Changes movement direction.

However, the code still expresses the architectural story that the new
documentation was written to correct:

```text
The shell is modelled in one way;
inner selected-page contents are governed by G1;
Notes are attached alongside the PA identifier in G1Contents but rendered
outside the PA region;
page-local runtime renderer functions repeat ContentPanel assembly;
and route declarations and single-shell runtime state are not yet one coherent
public-selection design.
```

The central conclusion is therefore:

> The implementation provides a useful basis for the new design, but it must be
> refactored from an inner-content `G1` model into an explicit full-page `PG`
> model, beginning with `PAPanel`/Notes ownership and public-selection/runtime
> consistency.

---

## 4. Summary of Findings

| Priority | Finding | Assessment |
| --- | --- | --- |
| P0 | UI model still uses `ContentGrammar = Literal["G1"]` and `G1Contents`; it does not represent `PG` or `PAPanel`. | Direct model mismatch with `02` and `04.3`. |
| P0 | Runtime appends `renderNotes(...)` after `.content-body`, outside the region containing the PA and Filters. | Confirmed structural nonconformance with `PAPanel -> PA . Notes`. |
| P0 | Navigation `href`s are derived as route-local `.../index.html` paths, but build writes only root `index.html`; ordinary clicks work only because JavaScript intercepts them and rewrites query-state selection. | Public-selection/output contract is internally inconsistent; new-tab/no-JavaScript/direct href behaviour is likely broken. |
| P1 | Publication planning includes Pages by status, but data copying, runtime artefact declaration and content-panel construction are largely hard-coded independently of the plan. | Layer boundary exists but is not yet controlling assembly. |
| P1 | `artifact_model.py` is substantial and useful, but artefact kinds/metadata partly mix semantic PA meaning with rendering policy and specialised implementation labels. | Good basis requiring alignment with `04.4`/`05`. |
| P1 | `site_manifest.py` hand-builds every content panel and artifact registry; runtime renderer functions repeat page-shell assembly for each PA kind. | Scaling risk identified by the design thesis. |
| P1 | All currently declared Pages are `PROMOTED`, despite uneven model/rendering maturity and unresolved policy. | Curation/status review required. |
| P1 | Local deploy clean-up deletes all content beneath any configured `local_root` without a successor-site safety validation step. | Implementation does not yet satisfy the proposed operations safety rule. |
| P2 | Heading typography, Rank-cell semantics, Notes-panel treatment and context-colour presentation remain provisional or unresolved exactly as recorded in `06`/`10`. | Documentation correctly identifies real implementation questions. |
| P2 | Build/runtime already implements useful parts of `07`/`09`, but build metadata, planned dependency resolution and long-term runtime/bootstrap policy remain absent or partial. | Appropriate deferred design with some implementation debt. |

---

## 5. Requirements Comparison (`01 Requirements.md`)

### 5.1 Areas Already Supported

The code already supports several requirements-level outcomes:

- `site_definition.py` declares a public site identity and a Page registry.
- `navigation.py` declares a substantial subject-led Navigation hierarchy rather
  than exposing output folders mechanically.
- `models.py` supplies explicit `PageStatus` values including `promoted`,
  `candidate`, `research`, `diagnostic`, `legacy`, `superseded` and `excluded`.
- `build.py` writes static output and `deploy.py` supports local and remote
  delivery without requiring a public application server.
- `runtime/site.js` supports reader controls, selected-page state, runtime data
  loading and chart/table interaction in a static browser client.

These are consistent with the core public-product intention: a static navigable
analytical website rather than a directory of raw output.

### 5.2 Concern: Promotion Has Outrun Deliberate Curation

The current `PageRegistry` declares twelve Pages and marks all twelve as
`PageStatus.PROMOTED`, including multiple chart Pages, BRB, Banzuke Changes,
Standings, Career Length and Typical Equelo Ratings.

That may ultimately be the correct public set. Under the new Requirements,
however, `promoted` now carries a stronger implication: the Page participates in
the normal coherent public contract and can be justified through the active
model/rendering path.

The current implementation contains unresolved questions for at least Notes
placement, heading presentation, public selection links, chart presentation and
certain PA-specific semantics. This does not require demoting every Page now,
but it does mean status should be reviewed rather than treated as a harmless
implementation default.

**Review action:** Once the immediate `PG` conformance corrections are underway,
review whether each currently `PROMOTED` Page is genuinely part of the intended
normal public surface or should temporarily have another explicit status.

---

## 6. Site Definition Model Comparison (`04.1`)

### 6.1 Strong Alignment

`models.py`, `site_definition.py` and `navigation.py` already provide a close
implementation basis for `04.1 Site Definition Model.md`:

```python
@dataclass(frozen=True, kw_only=True)
class SiteDefinition:
    id: str
    title: str
    navigation: NavigationTree
    pages: PageRegistry
```

The implementation distinguishes:

- site identity (`SITE.id`, `SITE.title`);
- Navigation tree nodes;
- declared Pages;
- Page titles and summaries;
- public status;
- an `ArtifactRef` pointing toward publication material.

This is materially consistent with the idea that Site Definition declares public
intent rather than rendering HTML.

### 6.2 Differences Worth Reviewing

The current model does not yet express several optional/anticipated declaration
ideas from `04.1`, including:

- a declared home/default Page;
- additional deliberate public entry points;
- declared site-level public assets;
- richer Page-level publication-source/input declarations.

Those omissions are not immediate nonconformances because the model document
permits these matters to be added as required.

More significant is that `ArtifactRef.kind` currently uses loose implementation-
shaped strings such as `"table_app"` and `"chart"`, while the more developed PA
model in `artifact_model.py` supplies different specific kinds. The seam from
Page declaration to actual PA declaration is therefore less explicit than the
new model story anticipates.

**Review action:** Retain the existing Site Definition structure as the basis of
`04.1`, but later clarify the PageDefinition-to-PA-declaration reference so the
site declaration points deliberately toward an approved PA model without
encoding renderer accidents.

---

## 7. Publication Plan Comparison (`04.2`)

### 7.1 Existing Useful Plan Layer

`publication_model.py` already defines:

```python
@dataclass(frozen=True, kw_only=True)
class PublicationPlan:
    site: SiteDefinition
    routes: Mapping[str, PageRoute]
    pages: Mapping[str, PlannedPage]
    navigation_tree: tuple[NavigationItem, ...]
```

and includes only selected statuses by default:

```python
DEFAULT_INCLUDED_STATUSES = frozenset({PageStatus.PROMOTED})
```

This is a good starting point for the model described in `04.2`: public
inclusion is explicitly filtered by status, and Navigation is resolved against
included Pages rather than generated solely from files.

### 7.2 Planning Does Not Yet Govern Build Dependencies

The current plan does not record the required data/assets/runtime inputs of
planned Pages. `build.py` instead copies or generates data for a fixed set of
Pages before creating the plan:

```python
build_basho_results_data_output(...)
copy_banzuke_changes_data_output(...)
copy_standings_by_wins_data_output(...)
...
plan = build_publication_plan(SITE)
```

Consequences include:

- changing status/inclusion does not necessarily change which data is copied or
  computed;
- a build can stage data for Pages not included by a future status policy;
- dependency failures arise from hard-coded build operations rather than from a
  resolved PlannedPage dependency contract;
- the Publication Plan cannot yet validate its promised publication inputs
  before rendering/output assembly.

This is not surprising in a first implementation, but it is a direct gap against
`04.2` and `07`.

### 7.3 Plan and Renderable-Page Filtering Are Duplicated

`site_manifest.py` constructs content panels explicitly and then creates a
`renderable_page_ids` set to filter Navigation hrefs again. That means
renderability is decided partly by the Publication Plan and partly by the
hard-coded content-panel list.

**Review action:** Move toward a single resolved planning/registration path in
which included PlannedPages carry or resolve their PA/UI dependencies, and
Navigation availability follows that resolution rather than a second hand-built
page set.

---

## 8. Central Model Mismatch: `G1` Remains in the UI Model (`02`, `03`, `04.3`)

### 8.1 Current Code

`ui_model.py` explicitly defines:

```python
ContentGrammar = Literal["G1"]

@dataclass(frozen=True, kw_only=True)
class G1Contents:
    filter_section: FilterSection
    pa: PA
    note_ids: tuple[str, ...] = ()

@dataclass(frozen=True, kw_only=True)
class PublicSiteShell:
    navigation_bar: NavigationBar
    content_panels: tuple[ContentPanel, ...]
```

This model reflects the archived design position:

```text
shell model
  plus
G1-selected-page contents model
```

It does not reflect the new specification:

```text
PG starts at PublicUI and contains Sidebar and ContentPanel as the top-level
modelled relationship.
```

### 8.2 Specific Mismatches

| New model concept | Current implementation position | Assessment |
| --- | --- | --- |
| `PublicUI` | `PublicSiteShell`, not named as a `PG` instance | Conceptually close but still framed as shell outside grammar. |
| `Sidebar` | `NavigationBar` plus `NavigationCollapseControl` | Substantial content exists, but the public model name/ownership does not follow `PG`. |
| `ContentPanel -> Heading . Contents` | `ContentPanel` with `Heading` and `G1Contents` | Close internally, but tied to obsolete grammar vocabulary. |
| `Contents -> FilterSection? . PAPanel` | `G1Contents(filter_section, pa, note_ids)` | Missing `PAPanel`; `filter_section` is mandatory rather than optional. |
| `PAPanel -> PA . Notes` | no `PAPanel`; PA id and note ids are peers in `G1Contents` | Direct model gap. |
| `Notes -> Note*` | Note definitions live on artefacts; `note_ids` link from contents | Useful material exists, but ownership is not represented through PAPanel. |
| `BooleanChoice` / `SingleFiniteChoice` | `Filter.control` as `checkbox` / `select`, with radio/dropdown selected at rendering time | Semantically mappable, but formal model is not yet aligned. |

### 8.3 Required Correction

This is the primary model correction required by the new documentation. The
current model should be refactored from `G1Contents` toward an explicit `PG`
representation, for example conceptually:

```text
PublicUIModel
  Sidebar
  ContentPanel

Contents
  FilterSection?
  PAPanel

PAPanel
  PA
  Notes
```

The exact Python refactor should be decided carefully rather than performed as a
terminology-only rename. It must support the Notes rendering correction and the
runtime manifest transition cleanly.

**Priority:** P0.

---

## 9. Confirmed Structural Rendering Nonconformance: Notes (`05`, `06`, `10`)

### 9.1 Current Runtime Structure

In each inspected runtime content-panel renderer, Notes are appended after the
whole `.content-body`. For example, the Banzuke Changes path constructs:

```javascript
'<div class="content-body">',
renderFilterSection(panel.contents.filter_section, state),
'<div class="pa-slot">',
renderBanzukeChangesTable(artifact, filteredRows, state, config),
'</div>',
'</div>',
renderNotes(artifact, state),
```

The same broad arrangement appears in indexed-table, standings and chart paths.

### 9.2 Assessment Against PG

Under the active specification:

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

The current runtime structure is effectively:

```text
Contents -> (FilterSection? . PA) . Notes
```

When Filters are visible, Notes therefore occupy the width/ownership of the
combined content region rather than the PA region. This is exactly the
structural issue already anticipated in `05`, `06` and `10`.

### 9.3 Required Correction

The runtime and UI model should introduce the explicit PAPanel relationship, so
the rendered structure is conceptually:

```html
<div class="content-body">
  <!-- optional filter section -->
  <section class="pa-panel">
    <div class="pa-slot">...</div>
    <!-- relevant Notes -->
  </section>
</div>
```

The correction should precede decisions about the exact Notes-panel max height
or overflow styling. Placement is already decided by the model; size and visual
treatment remain rendering policy.

**Priority:** P0.

---

## 10. Public Selection and Route/Runtime Mismatch (`02`, `04.2`, `07`)

### 10.1 Current Code Paths

`routes.py` derives path-like route hrefs:

```python
def route_href(parts: tuple[str, ...]) -> str:
    return PurePosixPath(*parts, "index.html").as_posix()
```

`render.py` emits those values into actual Navigation anchors:

```html
<a class="nav-link" href=".../index.html" data-page-id="..."></a>
```

But `build.py` currently writes only one HTML entry point:

```text
<output_root>/index.html
```

and `runtime/site.js` prevents ordinary left-click Navigation behaviour and
selects pages using query state:

```javascript
selectPage(link.dataset.pageId, { pushUrl: true });
...
params.set("page", pageId);
```

### 10.2 Assessment

A single-shell, query-state public site is permitted by the new documents. A
path-per-page static output is also potentially permitted if designed. The
current implementation mixes the two:

- anchor hrefs imply route-local static entry pages;
- generated output does not create those entry pages;
- JavaScript intercepts the common click path and hides the mismatch;
- opening a Navigation link in a new tab, copying the anchor destination, using
  the link without runtime interception, or navigating directly to the emitted
  href is likely to request a non-existent output file.

This is more than a deferred URL-policy question. It is a current inconsistency
between the anchor contract and generated output.

### 10.3 Required Decision and Correction

Choose one internally coherent current implementation direction:

1. **Single shell with stateful links**: emit real hrefs compatible with the
   single generated entry and selected Page state, such as the approved query/
   hash representation; or
2. **Route-local entry output**: write the route-local HTML entry material that
   the emitted hrefs promise, with runtime/bootstrap resolution consistent with
   it.

This decision should be recorded under the public selection/output policy in
`02`, `04.2` and `07` as needed. The immediate implementation must stop emitting
public anchor destinations that are not present in the built site.

**Priority:** P0.

---

## 11. Published Artifact Model Comparison (`04.4`)

### 11.1 Strong Existing Basis

`artifact_model.py` is one of the strongest alignments between the existing code
and the new documents. It already models meaningful PA concepts including:

- data sources and indexed data sources;
- table columns and column groups;
- chart traces and axes;
- sections for sectioned tables;
- Notes with application targets;
- specific PA declarations for indexed tables, charts, sectioned tables,
  Standings and Banzuke Changes.

`site_manifest.py` then constructs real PA declarations with meaningful
public-facing features. Examples include:

- BRB columns/groups and contextual Notes;
- Standings column groups and Notes;
- Banzuke Changes data/config inputs and Notes;
- chart axis/trace/source declarations;
- Typical Equelo sectioned-table structure.

This is substantial evidence that the implementation is already operating on
public analytical meaning rather than merely embedding old HTML.

### 11.2 Terminal-Form Alignment Is Incomplete

The new documentation treats the page-level PA terminals as:

```text
<table> | <indexed table> | <chart> | <sectioned table> | <prose> |
<custom artifact>
```

The current `ArtifactKind` instead contains:

```python
"indexed_table", "sectioned_table", "chart", "banzuke_changes", "standings"
```

This means:

- Banzuke Changes is already represented as specialised, which maps reasonably
  to `<custom artifact>` but is not named as such;
- Standings is a separate artefact kind even though it appears largely to be a
  table PA with specialised selected-source/group rendering;
- ordinary `<table>` and `<prose>` terminal forms are not present as general
  artefact kinds.

This is not an immediate blocker. It is a real alignment question: are
`standings` and `banzuke_changes` terminal kinds, renderer kinds beneath a
terminal form, or temporary implementation forms awaiting a more general PA
registration model?

### 11.3 Rendering Detail Embedded as `provenance`

Several chart declarations use the `provenance` dictionary to carry matters that
are not provenance in the public explanatory sense, such as:

```text
group_colours
x_tickangle
legend_title
default_visible
hover_fields
views containing chart/layout instructions
```

Some of these values express PA-visible analytical meaning; others are clearly
rendering/runtime hints. Under the new boundary, the implementation should not
call all of these `provenance`. Doing so obscures the distinction between:

- public explanation/source/method information;
- semantic PA feature declarations;
- rendering policy or runtime configuration.

**Review action:** Retain the useful artefact-model material, but split or rename
metadata categories as real PA/rendering work proceeds. Do not undertake a broad
abstract rewrite before the next real PA pressure case requires it.

---

## 12. Filter Model and Runtime Comparison (`02`, `04.3`, `05`)

### 12.1 Existing Semantic Foundation

The implementation already models Filters as declared reader-visible state:

```python
@dataclass(frozen=True, kw_only=True)
class Filter:
    id: str
    label: str
    control: ControlKind
    default: str | bool
    url_key: str
    values: tuple[FilterValue, ...] = ()
    values_source: FilterValuesSource | None = None
```

It also:

- restores Filter state from URLs;
- coerces invalid finite values to defaults;
- writes changed state back into the URL;
- uses Filters to determine visible PA content and Notes relevance;
- renders structural choice lists without bullets in current CSS.

This is broadly consistent with the new formal concept of `Filter`.

### 12.2 Model Vocabulary Difference

The Specification formalises:

```text
FilterItem -> BooleanChoice | SingleFiniteChoice
```

The current model instead identifies a generic `Filter` whose rendering control
is either `checkbox` or `select`. In runtime, finite selection is then rendered
as radio buttons when it has at most seven values and as a dropdown otherwise:

```javascript
if (values.length <= 7) {
  return renderRadioChoice(...);
}
return renderDropdownChoice(...);
```

The existing implementation therefore contains the right practical distinction,
but its model currently speaks in control/widget vocabulary rather than in the
semantic FilterItem vocabulary of the new specification.

### 12.3 Undeclared Rendering Policy

The `<= 7` radio/dropdown rule is a shared rendering policy not yet stated in
`05`. It may be a perfectly sensible policy, but it is exactly the type of
informed rendering choice the new audit discipline requires us either to adopt
explicitly or reconsider.

**Review action:** During the PG/UI-model refactor, consider representing
BooleanChoice and SingleFiniteChoice semantically while leaving radio-versus-
dropdown selection to Rendering Design; separately decide whether the current
seven-value threshold is the desired declared shared rule.

---

## 13. Rendering Design Comparison (`05` and `06`)

### 13.1 Settled Treatments Already Present in Code

The following agreed rendering rules recorded in `05` are present in
`runtime/site.css` or `runtime/site.js`:

| Rendering rule | Current implementation evidence |
| --- | --- |
| Navigation-local line height | `.nav-list { line-height: 1.45 }` |
| Structural Filter lists without bullets | `.filter-section ul { list-style: none; }` |
| Shared table cell padding | `.artifact-table th, .artifact-table td { padding: 2px 0.25em; }` |
| Alternating data-row backgrounds | `tbody tr:nth-child(odd/even)` using shared row tokens |
| Continuous row colouring | `.artifact-table { border-collapse: collapse; }` |
| Banzuke Changes direction feature | `⇅` header and `movementDirection(...)` in both table forms |

This confirms that `05` is not merely aspirational: it already records genuine
implementation decisions.

### 13.2 Open Rendering Issues Are Also Real in Code

The open matters recorded in `06` are confirmed by the implementation:

- heading typography is split between `.site-title` and generic `h2`/`h3`
  rules;
- Banzuke Changes banzuke-style Rank data is emitted as
  `<td scope="row">...</td>`, which retains a row-header attribute on a data
  cell rather than deciding the semantic question;
- Notes have no explicit PAPanel layout and are rendered outside the PA/Filter
  content-body relationship.

### 13.3 Site-Context Colour Policy Exists but Is Not Settled in Design

Runtime classifies hosts as `remote`, `local` or `preview` and CSS changes the
page background accordingly:

```css
body.site-context-local   { --page-bg: #071733; }
body.site-context-remote  { --page-bg: #3b0508; }
body.site-context-preview { --page-bg: #063819; }
```

This may be a useful operational inspection signal, but `05` currently leaves
broader site-context colour policy unsettled. It is therefore an implemented
provisional rendering choice rather than an agreed normative rule.

**Review action:** Record the context-colour treatment in `06` for deliberate
acceptance, revision or removal before treating it as settled rendering policy.

---

## 14. Page Rendering Architecture and Scaling Risk (`03`, `04.3`, `05`)

### 14.1 Runtime Repeats Page-Level Structure by PA Kind

`runtime/site.js` contains separate functions including:

```text
renderIndexedTableContentPanel
renderBanzukeChangesContentPanel
renderSectionedTableContentPanel
renderStandingsContentPanel
renderStandingWinProbabilityContentPanel
renderCareerLengthContentPanel
renderFinishByChiiContentPanel
renderStackedBarChartContentPanel
renderGroupedLineChartContentPanel
renderOrderedBarChartContentPanel
renderCategoryBarChartContentPanel
```

Each repeats the rendering of Page heading, content body, PA slot and Notes
rather than delegating common `PG` structure to one page renderer and keeping PA
renderers inside the PA position.

### 14.2 Why This Matters

This is the implementation form of the growth problem described in the new
Design Thesis. Although the functions currently produce broadly similar shell
markup, each PA-rendering addition can now accidentally change:

- where Notes are placed;
- how Filters relate to the PA;
- whether heading/framing is rendered consistently;
- whether the same shared page structure remains intact.

The Notes nonconformance is already present across these repeated paths.

### 14.3 Recommended Refactoring Direction

A future implementation correction should separate:

```text
render ContentPanel / Contents / optional FilterSection / PAPanel / Notes
  once from the UI model

render PA terminal internals
  through renderer-specific PA functions within the PAPanel PA slot
```

This is not an instruction to eliminate specialised PA renderers. Banzuke
Changes and chart renderers can remain specialised where analytically justified.
The change is to confine that specialisation to `PA`, consistent with `03`,
`04.3`, `04.4` and `05`.

**Priority:** P1 after the model/PAPanel correction is designed, or as part of
the same controlled refactor.

---

## 15. Build, Output and Runtime Comparison (`07`)

### 15.1 Existing Alignment

`build.py` and runtime support already implement several parts of `07`:

- a static output root under `files/output/make_site2`;
- clean output-root replacement at build time;
- a root `index.html` entry point;
- copied runtime CSS and JavaScript;
- a serialized `runtime/site-manifest.json`;
- static data staging for a number of PAs;
- cache-busting support in development mode;
- browser runtime restoring selected Page and Filter state;
- a `BuildOutput` describing root, entrypoint and file count.

These are useful concrete foundations for the new build/runtime design.

### 15.2 Build Is Not Yet Plan-Driven

As noted in Section 7, `build.py` stages data through a fixed series of calls and
then builds the plan. The implementation therefore has a static-output pipeline,
but not yet the resolved planned dependency pipeline described by `04.2` and
`07`.

### 15.3 Producer Computation Boundary Requires Review

`build.py` directly obtains history and `data_output.py` directly imports Basho
Results analytical build functions and rating lookup logic to generate BRB
payloads inside the `make_site2` build path. Other PAs are primarily copied from
existing outputs.

This may be an acceptable interim orchestration arrangement under `08`, because
`make_site2` may invoke producer preparation. However, the boundary is not yet
expressed cleanly as “prepare producer site-facing input, then assemble site.”
The code should be reviewed when the next producer integration task is chosen so
site build does not gradually become the owner of producer calculation details.

### 15.4 Unimplemented or Partial Design Matters

The following `07` matters remain absent or partial in current code:

- build metadata output such as `build/build-info.json`;
- dependency/runtime collection driven from the Publication Plan;
- a documented/versioned bootstrap-manifest policy;
- a coherent choice between single-shell link representation and route-local
  entry output;
- broader validation that a promoted planned Page has all required data/model/
  runtime support before site assembly.

Most of these are correctly recorded as deferred/open rather than immediate
failures. The href/output inconsistency is the exception and should be corrected
soon.

---

## 16. Producer Integration and Migration Comparison (`08`)

### 16.1 Existing Site-Facing Integration Is Real

The current implementation does not simply iframe or copy whole former HTML
pages into the shell. Instead, it consumes structured data/configuration and
constructs PAs/renders them through the current runtime. For example:

- Banzuke Changes copies a site config and CSV report, then renders its own PA;
- Standings copies its data/config outputs and models table columns/groups;
- chart PAs consume CSV data and model traces/axes;
- BRB builds an index/payload dataset and renders an indexed-table PA.

This is strongly consistent with the intention of `08`: public pages should be
built from deliberate analytical material rather than copied standalone HTML.

### 16.2 Integration Contracts Are Currently Scattered

The current input relationship is distributed among:

- `PageDefinition.artifact` declarations;
- constants and PA declarations in `site_manifest.py`;
- file-copy/build rules in `data_output.py`;
- hard-coded build orchestration in `build.py`;
- runtime renderer names and data-loading assumptions in `site.js`.

The active docs call for deliberate site-facing inputs and a clean planning/model
handoff. The current code supplies those inputs in practice, but the contract is
not yet one easily inspectable seam.

### 16.3 Migration Evidence Already Affected the Code

The restored Banzuke Changes `⇅` feature is an example of appropriate legacy
comparison: legacy evidence exposed a missing analytical visible feature, and
current runtime now represents it distinctly from optional numeric `Delta`.

That work is consistent with the active migration policy and should serve as a
pattern: retain meaningful behaviour after assessing ownership, not by copying
legacy page structure wholesale.

---

## 17. Deployment and Operations Comparison (`09`)

### 17.1 Existing Alignment

`deploy.py` and `__main__.py` already support:

- build-only operation;
- deploying existing output without rebuilding;
- local deployment;
- remote deployment by SFTP/Paramiko;
- remote password resolution external to committed source content;
- local result and remote result reporting;
- remote upload/overwrite without remote purge;
- distinction between the successor `sumo-tools2` deployment and the legacy
  site.

These are broadly consistent with `09 Deployment and Operations.md`.

### 17.2 Local Target Path Discrepancy

The active `09` document records the earlier known local-target evidence as:

```text
A:\local\htm\sumo-tools2
```

The current implementation sets:

```python
LOCAL_ROOT = Path("A:/local/html/sumo-tools2")
```

The `htm` versus `html` difference should be checked against the actual local
server target and corrected in either code or documentation. Since deployment
may clean its configured target, this is not a cosmetic discrepancy.

### 17.3 Local Clean-Target Safety Rule Is Not Implemented

The active `09` document requires safe scoping before clean local deployment.
Current `clear_local_root(local_root)` creates the passed directory and removes
all of its children without validating that it is specifically the intended
successor-site root.

The default target may be safe in current use. The CLI also accepts arbitrary
`--local-root`, so a mistaken value could cause deletion of unrelated files
beneath the supplied directory.

**Review action:** Add an explicit target-safety policy/implementation before
regarding clean local deployment as conforming to `09`.

**Priority:** P1 because of potential destructive impact.

---

## 18. Additional Specific Findings

### 18.1 Page Summary Containing Escaped HTML

`site_definition.py` supplies this summary for `first_chii_appearance`:

```python
summary="Earliest observed bout appearance at <a href=\"sumodb.de\">SumoDB</a>for each chii."
```

But runtime renders Page summaries using `escapeHtml(panel.heading.summary)`, so
this value will display literal markup rather than a working link, and it also
contains no space between `</a>` and `for`.

This is not central to `PG`, but it reveals an unmade decision about whether Page
summary/framing content supports structured links or is plain text only.

**Review action:** Treat summary as plain text for now and correct the wording, or
introduce deliberately modelled/rendered structured framing content where real
need warrants it. Do not embed HTML in a string that the runtime correctly
escapes.

### 18.2 Home/Landing Presentation Exists Outside Declared Pages

When no `page` URL parameter is present, runtime renders a `landing-panel` with a
context label such as `Local Site`, `Remote Site` or `Preview Site`, rather than
selecting a declared public Page.

This is compatible with the fact that home/landing remains open in `10`, but it
is implemented behaviour that should be reviewed before the public site is
considered stable. In particular, the landing page currently appears to serve
operational context signalling rather than public reader orientation.

### 18.3 Context Detection Is Hostname-Specific Runtime Policy

`site.js` recognises remote and local contexts through hard-coded hostnames/IP
patterns and otherwise labels output as Preview. This may be appropriate for
current inspection, but it should eventually be treated as operational/runtime
configuration rather than hidden permanent public behaviour.

---

## 19. Recommended Correction Sequence

The code should not be broadly rewritten all at once. A controlled sequence is
more consistent with the model-first intent.

### Phase 1: Correct the Central PG Structural Gap

1. Decide the minimal Python/runtime-manifest representation of `PG`, especially
   `PublicUI`, `Sidebar`, `Contents`, `PAPanel` and `Notes`.
2. Replace or retire `G1Contents`/`ContentGrammar = "G1"` in favour of that
   explicit representation.
3. Change runtime rendering so Notes are rendered inside PAPanel alongside the
   PA, not below the combined Filter/PA region.
4. Inspect Banzuke Changes and at least one chart/table Page in the browser and
   record the audit result.

### Phase 2: Correct Current Public-Link Inconsistency

1. Decide whether the present site uses a single-shell public link strategy or
   route-local entry output.
2. Bring anchor `href`s, built HTML output and runtime URL-state restoration into
   conformity with that decision.
3. Test ordinary click, copied/opened link, new-tab/direct navigation and invalid
   requested Page behaviour.

### Phase 3: Reduce Shell Assembly Duplication

1. Centralise rendering of ContentPanel, Heading, Contents, optional
   FilterSection, PAPanel and Notes.
2. Retain PA-specific renderers only for PA internals.
3. Confirm each currently promoted PA still renders through the common shell.

### Phase 4: Address High-Value Policy/Safety Items

1. Decide and implement Rank-cell semantics and heading typography ownership.
2. Decide Notes-panel visual treatment.
3. Review host-context colour policy and radio/dropdown threshold as declared
   rendering policy or provisional behaviour.
4. Check the local deployment target path and add clean-target safety guards.

### Phase 5: Mature Planning/Integration Gradually

1. Move required Page/PA data/runtime dependencies toward Publication Plan-
   driven resolution.
2. Review the promotion status of currently declared Pages.
3. Select the next real migration/integration pressure case and use it to refine
   PA/site-facing input boundaries rather than redesigning abstractly.

---

## 20. Findings to Carry into `10 Open Issues and Deferred Design.md`

Most major findings are already anticipated in `10`. The following should be
added or strengthened when that document is next updated:

1. **Public link/output inconsistency**: route-like Navigation hrefs are emitted
   although only a single root HTML entry is built; JavaScript interception
   currently masks the mismatch.
2. **Local clean-deployment safety**: implementation deletes children of any
   supplied `--local-root` without confirming successor-site scope.
3. **Local target path verification**: active documentation says `htm`, current
   code says `html`.
4. **Context-colour runtime presentation**: implemented hostname-driven red/
   blue/green context scheme awaits deliberate rendering/operations policy.
5. **Page summary content representation**: embedded link markup is currently
   escaped as text, revealing an unsettled plain-text-versus-structured-framing
   boundary.

The existing entries for Notes placement, Notes-panel treatment, heading
ownership, Rank semantics, runtime/bootstrap policy, output conventions and
producer integration remain validated by this review.

---

## 21. What Does Not Need Immediate Change

The review should not trigger unnecessary rewriting. In particular:

- the subject-led Navigation declaration is a useful owned starting point;
- explicit Page statuses and status-filtered planning are directionally right;
- structured PA declarations and site-facing data use are valuable and should
  be retained;
- the static single-shell runtime is acceptable in principle once public link
  handling is made coherent;
- clean build-output generation is appropriate;
- local/remote deployment separation is appropriate;
- legacy `make_site` need not be made an operational dependency;
- exact theme tokens, metadata schema and richer PG extensions should not be
  redesigned before current conformance work or real pressure demands it.

The objective is to bring a promising implementation under the control of the
new active design, not to start again unnecessarily.

---

## 22. Conclusion

The replacement documents expose a genuine central mismatch in the current
implementation: `make_site2` already models and renders significant public
material, but it still does so through an old `G1`-centred selected-content
model rather than through the full-page `PG` now adopted as the specification.

That mismatch is not theoretical. It explains the current Notes-placement error
and leaves repeated runtime content-panel renderers free to reproduce or extend
such structural drift. Separately, the current public-anchor/output/runtime link
strategy is not coherent: anchors promise route-local pages that the build does
not write, while JavaScript supplies a different query-state navigation path.

The encouraging conclusion is that much of the implementation can be carried
forward. Site Definition, Navigation, status-aware planning, structured PA
declarations, static runtime assembly and deployment are already recognisable
forms of the new architecture. The next work should therefore be focused and
model-led:

```text
make PG explicit in the code
  -> place Notes within PAPanel
  -> make public links/output coherent
  -> centralise page-level rendering around the model
  -> resolve the recorded semantic-rendering and operational safety issues
```

Doing that would convert the current implementation from a useful prototype with
identified drift into a credible implementation of the newly documented
`make_site2` design.