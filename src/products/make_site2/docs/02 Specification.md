# 02 Specification

## Status

Draft normative specification for `src/products/make_site2`.

This document specifies the public website and observable behaviour that
`make_site2` shall support. It refines the requirements stated in
`01 Requirements.md`.

This document defines public structure and public contracts. It does not
prescribe internal Python class structure, HTML element selection, CSS
selectors, JavaScript organisation, build implementation or deployment
mechanism except where observable public behaviour requires a constraint.

---

## 1. Specification Scope

`make_site2` shall generate a coherent static public website presenting curated
Sumo-Tools analytical material.

The specification covers:

- the visible structure of the public website;
- public navigation and page selection;
- public page framing and contents;
- Filters, Published Artifacts and Notes;
- curation, Page availability and public status;
- public state and reproducible public links;
- producer/site-facing input boundaries;
- coherent use of History and any compatible additional Page inputs throughout
  one build;
- required failure or unavailable-state behaviour; and
- acceptance criteria for the initial supported public page shape.

Only material deliberately included in the public site is governed as public
material.

---

## 2. Formal Vocabulary

```text
Site
PublicUI
NavigationBar
Navigation
ContentPanel
Heading
Contents
FilterSection
FilterItem
Filter
BooleanChoice
SingleFiniteChoice
Values
PAPanel
PA
Published Artifact
Notes
Note
Page
Page Availability
Public Status
Public State
Public View Link
Deep Link
History
Selected History
Data Instance
Compatible Successor Input
Site-Facing Input
Producer
Build Mode
```

`PA` means **Published Artifact**.

`Filter` is the formal term for a reader-visible control that selects,
restricts, projects or otherwise changes the visible analytical presentation.
Reader-facing UI copy may use ordinary wording such as `Options` where clearer.

A `Public View Link` is a canonical copyable URL representation of one material
public view. It identifies a selected Page and, where applicable, all material
Filter values needed to restore that view. A link identifies requested Page and
reader state; it does not by itself prove that a Page is available in a
particular build.

A `Selected History` is a History/data instance deliberately chosen for a build,
whether supplied explicitly or selected by the normal build workflow. Where a
PA's public meaning depends on History, that PA shall be coherent with the
Selected History used by the built site.

A `Compatible Successor Input` is additional data required by a Page whose
public meaning concerns a successor state not yet represented in History. It is
compatible only where its relationship to the Selected History is established
by that Page's contract.

---

## 3. Public Page Grammar: PG

### 3.1 Role of PG

Promoted public Pages in the initial supported public shape shall conform to:

```text
PG

PublicUI -> NavigationBar . ContentPanel

NavigationBar -> <hider> . NavigationContent

NavigationContent -> <site caption> . QuickLinks? . Navigation

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
      <prose> | <custom artifact> | <unavailable explanation>

Notes -> <hider> . NotesContent

NotesContent -> Note*
```

The symbols in angle brackets are terminal public forms at this level of the
specification. Their internal data or rendering structure may be specified in
later design documents where necessary.

### 3.2 Consequences of PG

- `NavigationBar` and `ContentPanel` are the two top-level visible regions.
- `NavigationBar` contains a visible hider and a hideable NavigationContent
  region.
- `ContentPanel` contains the selected Page Heading and Contents.
- `FilterSection`, where present, is a sibling of `PAPanel`.
- `PAPanel` contains the visible PA and its Notes.
- `Notes` contains a visible hider and hideable NotesContent when relevant.
- Notes do not belong to `FilterSection`.
- An unavailable Page may retain its Page Heading and use its PAPanel to explain
  why its normal PA is not available in the current build context.

### 3.3 Extension of PG

A promoted Page requiring visible structure that cannot be represented by `PG`
shall not be implemented by silently adding page-local structure. It requires an
explicit grammar/design extension or a documented restriction on promotion.

---

## 4. Site, PublicUI and Navigation Contract

A public site shall have stable identity, public caption, Navigation, a registry
of Pages eligible for public inclusion, public status information, required
site-facing inputs/assets and build/public-state defaults where applicable.

`PublicUI` contains one `NavigationBar` and one `ContentPanel`. The
`NavigationBar` provides site identity, Navigation and a control allowing the
reader to hide and restore the NavigationBar's content region. The control
remains visible when the content region is hidden. Hiding it changes shell
presentation only; it is not a Filter and shall not alter selected analytical
content.

Navigation shall be hierarchical and numbered, organised primarily by subject.
An available selectable Navigation destination shall be a valid Public View Link
to that Page's canonical default view and shall not advertise an output path the
static site does not publish.

Where a promoted Page is unavailable in a production build, Navigation shall not
present it as an ordinary available destination. It may remain visible as a
disabled/unavailable item where that communicates useful public structure.

---

## 5. Page, Heading and Contents Contract

A Page is a curated public publication unit selectable within the site. It shall
have, as applicable, a stable identity, title, optional summary/framing text,
public status, availability resolution, deliberate public entry treatment,
Contents conforming to approved grammar, required PA/data/assets, Filter
defaults and Notes.

A promoted Page renders as a `ContentPanel` containing `Heading` and `Contents`.
`Heading` contains a main heading and optional sub heading. It is distinct from
the site caption, PA-internal framing, chart/table labels and Notes.

`Contents` contains optional `FilterSection` followed by `PAPanel`. Filters may
control row/data selection, visible features, representation or other declared
material public state. They shall not own Notes.

A Page is not defined by an HTML file, incidental producer output filename or a
copied legacy report.

---

## 6. PAPanel, Published Artifact and Notes Contract

`PAPanel` is the visible public region containing one PA and its Notes. The
relationship is material: Notes accompany and explain the PA or its visible
features; they are not an extension of Filters.

A PA shall have, as applicable, stable identity, public artefact form,
site-facing inputs, meaningful visible features, public labels, Notes/caveats or
provenance, and consistency/availability requirements required for truthful
public presentation.

Table-like PAs shall support ordinary column sorting as part of their PA-local
reader interaction where a sortable table is the approved PA form. Row-number
columns are reference columns and shall not be sortable. Ordinary data columns
shall be sortable unless the PA model explicitly declares them unsortable.
Clicking a sortable column heading shall sort by that column; clicking the
active sorted heading again shall toggle sort direction. The active sorted
column and direction shall be visible to the reader.

For table-like PAs with hierarchical headings, a sortable column is a visible
leaf heading that corresponds to exactly one data column. Group headings are not
sortable unless a later PA-specific model explicitly gives them single-column
sort meaning.

A Note may explain or qualify a PA, a visible feature, a selected representation
or a relevant caveat/provenance fact. A change in Filter state may change Note
relevance only because it changes visible PA state.

---

## 7. Page Availability Contract

A Page may be declared/promoted as part of the product yet unavailable in a
particular production build because its required input condition is not met.

For an availability-sensitive Page:

```text
available
  the Page's required compatible inputs exist and its normal PA may be shown;

unavailable
  the Page exists as part of the product, but its normal PA must not be
  presented as valid in this build context.
```

In an unavailable production state:

- Navigation shall not invite ordinary available selection of the normal PA;
- a direct Page request shall display a clear unavailable-state explanation;
- the explanation may direct the reader to a different Page serving a related
  but distinct public question; and
- unavailable treatment shall not silently substitute a different PA meaning.

Development builds may deliberately expose an otherwise unavailable Page for
regression testing only under an explicit development policy and conspicuous
visible warning. Such an affordance is not valid production output.

---

## 8. Specified Semantics of 2.1 Banzuke Changes

### 8.1 Public Question

**2.1 Banzuke Changes** is a **new-banzuke change report**. It answers:

```text
A new banzuke has been published before that basho has results of its own.
How does it differ from the preceding represented basho?
```

### 8.2 Required Inputs

Its normal production PA requires:

```text
predecessor context
  the latest relevant BashoState in the site's History, providing the previous
  banzuke and previous-result context;

successor subject
  a compatible separately available newly published banzuke whose basho has not
  yet entered History with results of its own.
```

### 8.3 What Banzuke Changes Is Not

It is not:

```text
a general adjacent-historical-basho comparison Page;
a Page which automatically compares the final two bashos contained in an
arbitrary Selected History; or
a Page permitted silently to display unrelated current/live output inside an
archive or explicitly historical publication.
```

For bashos represented in History, readers use **Basho Results** to inspect
results and comparisons with preceding represented bashos.

### 8.4 Production Availability

Banzuke Changes is available in a production build only where its compatible
successor-banzuke input exists relative to that build's History and the
successor has not yet entered History with results of its own.

When no compatible newly published banzuke is available, its unavailable-state
explanation shall be materially equivalent to:

```text
No newly published banzuke is currently available.
Use Basho Results to compare a represented basho with its predecessor.
```

### 8.5 Temporary Development Exception

Outside its short normal production availability window, developers need to
inspect and regress the Banzuke Changes UI. Until production availability
enforcement is implemented, development builds may therefore leave 2.1 enabled
and render its existing prepared/live report even where the production
availability condition has not been established.

That is a deliberate testing exception, not alternative public semantics. Its
visible sub heading shall append a conspicuous warning after `New-banzuke change
report.` materially equivalent to:

```text
DEVELOPMENT WARNING: availability is not yet validated against this build's
History. This Page is intended only for a newly published banzuke before its
first results enter History; archive or historical builds may show unrelated
live output.
```

The current build-mode distinction is appropriate for implementing the policy:
ordinary non-`--prod` output is development output; `--prod` identifies
production output. Until the production availability rule is actually enforced,
production output shall not simply conceal the warning while still displaying
unvalidated Banzuke Changes material.

---

## 9. Specified Semantics of 7.1 Basho Results

### 9.1 Public Question

**7.1 Basho Results** is a represented-basho results browser. It answers:

```text
A basho is represented in History. What were the results for that basho, and how
should selected before/current/after analytical context be inspected?
```

It covers completed historical bashos, the latest/current basho once represented
results exist, and in-progress bashos where results are represented only through
a known day.

It is not the same Page as **2.1 Banzuke Changes** and does not answer the
new-banzuke-before-results question.

### 9.2 PA Form

Basho Results is an indexed table PA. The selected basho and division determine
the visible table instance. Optional public Filters may project additional
visible context such as previous-basho context, Equelo ratings, Analysis values
or successor BP context where available.

Basho Results may use a specialised recursive presentation table because its
visible meaning requires temporal/grouped headings such as Reference,
Before Basho, Current/After Basho, Context, Result and Comparison. This is a
Basho Results PA model decision; it does not require all ordinary table PAs to
use the same recursive table shape.

### 9.3 Required Visible Meaning

The Basho Results table shall distinguish:

```text
reference values
  row number and rikishi identity;

before record
  predecessor-basho Context and Result values, visible when previous-basho
  context is selected;

selected record
  selected/current/after-basho Context and Result values, always present for the
  selected Basho Results table;

comparison context
  declared comparisons such as Division Change and Delta Equelo where available.
```

A record's Context contains non-result values. It includes Skill, where BP is
the official rank slot and Equelo is the rating value for the represented point,
and may include Analysis values derived from comparing BP order with Equelo
order.

Result values are logically decomposed into wins, losses, absences and prizes.
Compact producer result strings may remain a transitional input shape, but the
public PA model treats the visible result fields as distinct. Division Change is
not a result field; it is a comparison value.

`reference.shikona` is a rikishi identity value and may render as a link to the
corresponding public rikishi record when a valid rikishi id is supplied.

### 9.4 Rating-Order Analysis

Basho Results may expose rating-order Analysis comparing official BP order and
Equelo order for the same selected table population.

```text
banzuke position
  the rikishi's ordinal position when the selected population is ordered by
  official BP/Chii;

rating-implied position
  the rikishi's ordinal position when the selected population is ordered by
  Equelo rating;

BZ Error / DeltaBZ
  the discrepancy between those two positions;

RBBP
  the official BP slot corresponding to the rikishi's rating-implied position.
```

BZ Error / DeltaBZ is a comparison between two orderings, not a scalar rank
prediction. Its public form is direction plus absolute magnitude:

```text
direction
  whether Equelo order places the rikishi higher or lower than official BP order;

magnitude
  the number of BP slots between the official BP position and rating-implied
  position.
```

A displayed upward direction means the rating order places the rikishi higher
than the official banzuke position. A displayed downward direction means the
rating order places the rikishi lower than the official banzuke position.

RBBP is also a rating-order comparison. It means:

```text
If the selected population were placed into the same official BP slots according
to Equelo order, this rikishi would occupy this BP slot.
```

BZ Error / DeltaBZ and RBBP are not banzuke-making predictions. They do not
claim that promotion rules, rank-holding conventions, sanyaku vacancies,
committee judgment or other real banzuke constraints would produce that result.
They express how the official BP order differs from the selected rating order.

Equelo Ratings and Analysis are distinct projections. Selecting Equelo Ratings
shall not itself expose the whole Analysis subtree. The current Analysis
projection is monolithic: when selected, it shows BZ Error direction, BZ Error
magnitude and RBBP together.

### 9.5 Sorting

Basho Results shares the ordinary table sorting contract. In the recursive table,
the column identity used for sorting is the visible terminal path rather than a
flat column id.

Every visible leaf heading is sortable by default except the row-number column.
Group headings are not sortable because they do not identify a single data
column. The default Basho Results sort is selected/current BP ascending by the
emitted BP ordinal value.

Further Basho Results model details are specified in
`04.5 Basho Results Model.md`.

---

## 10. Published-Data and Publication-Context Coherence

Where a PA's public meaning depends on History or a compatible successor input,
its visible data shall be coherent with the build context required by that Page.

For directly History-derived Pages this means deriving from or validating
against the Selected History. For Banzuke Changes this means either validating a
compatible successor-banzuke relationship to History, resolving the production
Page as unavailable, or exposing only an explicitly warned development testing
exception.

A completed production build shall not silently combine Pages drawn from
mutually inconsistent or inapplicable publication contexts.

This is a build/PA requirement, not a requirement that a Public View Link freeze
all future published data. A later coherent deployment may legitimately serve
newer data through the same Page/Filter link.

---

## 11. Public Status, Public State and Public View Links

Every Page candidate shall have explicit public status or be excluded. Initial
status terms may include:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

Availability is distinct from status: a promoted availability-sensitive Page
may be unavailable in a particular production build.

The public site uses one static application shell for ordinary promoted Page
presentation. Every material available public view shall have a canonical
Public View Link which serializes selected Page and every applicable material
Filter value, including defaults. A direct link to an unavailable Page may
resolve to that Page's declared unavailable explanation.

Public View Links do not ordinarily encode the build's Selected History or
availability evidence unless represented as declared reader-selectable state.
They shall not derive Page identity from incidental file paths or legacy output
locations.

Invalid or incomplete public state shall degrade predictably and shall not leave
a promoted Page blank or misleading.

---

## 12. Static Publication and Producer Contract

The generated website shall be publishable as static output without Python,
database, application server, user accounts or dynamic public API. Client-side
JavaScript may realise interaction and restore canonical public state.

Producer modules own analysis-specific computation and meaning. For promoted
material they shall provide deliberate site-facing inputs sufficient to publish
the intended PA, including labels, meaningful visible fields/traces, valid
Filters, caveats/provenance and required data-instance or compatible-successor
identity/validation material.

`make_site2` owns public organisation, page structure, Filter/PAPanel/Notes
presentation, public state, availability resolution, publication assembly and
refusing to publish required public material whose input relationship cannot be
shown to meet the Page contract.

Legacy output and code may provide evidence, but are not normative merely
because they exist.

---

## 13. Error and Missing-State Contract

A promoted Page shall not silently render blank, structurally invalid or
materially misleading production content when required inputs, availability or
public state are missing or invalid.

The product shall handle, as applicable:

- missing required PA inputs or data;
- missing or unvalidated Selected-History coherence;
- missing or incompatible successor input for an availability-sensitive Page;
- invalid selected Page or Filter values;
- unavailable Page selection;
- failed client-side data load; and
- unsupported or contradictory public model structure.

Build-time invalidity of required ordinary promoted material shall be reported as
a build failure or explicit blocking error. A promoted availability-sensitive
Page whose input condition is not met may instead be explicitly represented as
unavailable under its declared production contract.

Development-only exposure of unavailable/unvalidated material shall be plainly
labelled as such and shall not be mistaken for normal production publication.

---

## 14. Initial Conformance Criteria

A first conforming production slice shall demonstrate:

- one generated static public site and one ordinary static application shell;
- visible `PublicUI` conforming to `PG`;
- a NavigationBar containing identity, Navigation and working hider;
- subject-led hierarchical numbered Navigation;
- canonical default Public View Links for available selected Pages;
- a Heading and Contents structure with optional Filters and PAPanel;
- PA and Notes ownership correctly represented;
- copied/pasted/restored Page and material Filter state;
- coherent use of History and any compatible Page-specific additional input;
- explicit unavailable handling for a promoted Page where required;
- site-facing inputs rather than copied legacy HTML; and
- working local build and inspection.

Before replacing the legacy public product, `make_site2` shall additionally
demonstrate promoted table and chart PAs, required Filter forms, a specialised PA
which does not redefine surrounding `PG`, explicit status/availability handling,
and no successful production build silently mixing incompatible publication
contexts.

---

## 15. Relationship to Design Documents

This specification establishes public website structure and observable public
behaviour. Subsequent design documents shall explain how the implementation
satisfies it, including:

- model-first architecture and auditable rendering of `PG`;
- Page inclusion and availability planning;
- Published Artifact and rendering policy;
- Basho Results recursive table modelling;
- build/runtime support for canonical links and unavailable states;
- producer integration for Selected History and compatible successor inputs;
- deployment and operational policy.

These design choices may refine implementation and rendering policy, but they
shall not silently alter `PG`, the specified semantics of 2.1 Banzuke Changes,
the specified semantics of 7.1 Basho Results, or the distinction between
production publication and explicitly warned development testing output.
