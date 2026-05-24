# 02 Specification

## Status

Draft normative specification for `src/products/make_site2`.

This document specifies the public website and observable behaviour that
`make_site2` shall support. It refines the requirements stated in
`01 Requirements.md`.

This document defines the public structure and public contracts. It does not
prescribe the internal Python class structure, HTML element selection, CSS
selectors, JavaScript organisation, build implementation or deployment
mechanism except where an observable public behaviour requires a constraint.

---

## 1. Specification Scope

`make_site2` shall generate a coherent static public website presenting curated
Sumo-Tools analytical material.

The specification covers:

- the visible structure of the public website;
- public navigation and page selection;
- public page framing and contents;
- Filters;
- Published Artifacts;
- Notes;
- curation and public status;
- public state and reproducible public links;
- producer/site-facing input boundaries;
- required failure behaviour;
- acceptance criteria for the initial supported public page shape.

The specification does not require every potentially useful analytical page to
be promoted immediately. Only material deliberately included in the public site
is governed as public material.

---

## 2. Formal Vocabulary

The following terms are formal concepts in this specification:

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
Public Status
Public State
Deep Link
Site-Facing Input
Producer
```

`PA` means **Published Artifact**.

`Filter` is the formal term for a reader-visible control that selects,
restricts, projects or otherwise changes the visible analytical presentation.
Reader-facing UI copy may use ordinary wording such as `Options` where that is
clearer.

The term `Option` is not a formal model term for a Filter.

---

## 3. Public Page Grammar: PG

### 3.1 Role of PG

The public website shall conform to the page grammar `PG` for promoted pages in
the initial supported public shape.

`PG` specifies the visible semantic structure of the public page. It begins at
the full visible public UI, including the NavigationBar and the selected page
ContentPanel.

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

The symbols in angle brackets are terminal public forms at this level of the
specification. Their internal data or rendering structure may be specified in
later design documents where necessary.

### 3.2 Consequences of PG

The following are specified structural relationships:

- `NavigationBar` and `ContentPanel` are the two top-level visible regions of
  the public UI.
- `NavigationBar` contains site identity, Navigation and a NavigationBar-visibility control.
- `ContentPanel` contains the selected page Heading and Contents.
- `FilterSection`, where present, is a sibling of `PAPanel`.
- `PAPanel` contains the visible Published Artifact and its Notes.
- `Notes` may be empty because it expands to zero or more `Note` items.
- Notes do not belong to the FilterSection.
- The initial supported page shape presents one visible PA in its PAPanel.

The specification does not require a separate visible Notes region when no Note
is relevant or present.

### 3.3 Extension of PG

A promoted page requiring visible structure that cannot be represented by `PG`
shall not be implemented by silently adding page-local structure.

Such a page requires one of:

- an explicit extension to `PG`;
- a declared additional public page grammar;
- a documented restriction preventing promotion until the public model is
  extended.

Possible future needs include multiple simultaneously visible Published
Artifacts, nested Filters, conditional Filter structure or more complex
presentation relationships. These are not specified by this initial `PG`.

---

## 4. Site Contract

A public site shall have:

- a stable site identity;
- a public site caption or title;
- a Navigation structure;
- a registry of pages eligible for public inclusion;
- public status information;
- the assets and site-facing inputs needed to realise included pages;
- build and public-state defaults where applicable.

The public site definition shall express intended public organisation. It shall
not be inferred from producer directory structure, old generated pages or the
presence of output files.

---

## 5. PublicUI and NavigationBar Contract

`PublicUI` is the visible public website surface for a selected page.

It shall contain one `NavigationBar` and one `ContentPanel` in accordance with `PG`.

The `NavigationBar` shall provide:

- the site caption or identity;
- the public Navigation;
- a control allowing the reader to hide and restore the NavigationBar.

The NavigationBar-visibility control changes the public shell presentation; it
is not a Filter because it does not change the visible analytical content of the
selected page.

Hiding the NavigationBar shall not remove, replace or alter the selected page or
its material analytical state.

---

## 6. Navigation Contract

Navigation shall present the public information structure as hierarchical,
numbered navigation items.

A Navigation item shall have, as applicable:

- a stable identity;
- a reader-facing label;
- zero or more child items;
- an optional public page destination;
- status or readiness information where exposed publicly.

A Navigation item need not itself select a page; it may group child items.

Navigation shall be organised primarily by subject and shall not expose every
producer output, implementation category or repository directory merely because
it exists.

The selected available page shall be identifiable in Navigation where it has a
navigation destination.

---

## 7. Page and ContentPanel Contract

A Page is a curated public publication unit selectable within the site.

A Page shall have, as applicable:

- a stable page identity;
- a public title;
- optional public summary/framing text;
- public status;
- a public entry route through Navigation or another deliberate public link;
- Contents conforming to an approved public grammar;
- required Published Artifact, data and asset references;
- Filter and default-state declarations where applicable;
- Notes declarations where applicable.

A promoted page supported by the initial implementation shall render as a
`ContentPanel` conforming to `PG`.

`ContentPanel` shall contain:

- a `Heading` representing page-level reader framing; and
- `Contents` representing the selected analytical public material.

A Page is not defined by an HTML file, an incidental producer output filename or
a copied legacy report.

---

## 8. Heading Contract

`Heading` provides page-level framing for the selected Page.

It shall contain:

- a main heading; and
- an optional sub heading.

The Heading is distinct from:

- the site caption in the NavigationBar;
- Published Artifact framing within the PAPanel;
- table headings, chart labels or other artefact-internal labels;
- Notes headings or note content.

The precise visual hierarchy and HTML realisation of these distinct roles belong
to rendering design, subject to preserving their public meanings.

---

## 9. Contents and FilterSection Contract

`Contents` shall contain an optional `FilterSection` followed by a `PAPanel`.

A `FilterSection`, where present, shall contain zero or more `FilterItem`
instances. It shall present Filters that affect the visible analytical content
or representation within the associated PAPanel.

Filters may control matters including:

- row selection;
- source/data-instance selection;
- visible column groups;
- measure selection;
- representation selection;
- PA visibility presets or views where later specified.

The initial `PG` permits flat FilterItems only. Nested or hierarchical Filter
structure is not specified.

A FilterSection shall not contain or own Notes. A Filter may affect whether a
Note is relevant because it changes visible PA state, but Note ownership remains
with the Published Artifact or visible Published Artifact feature.

---

## 10. FilterItem Contract

A `FilterItem` shall be either a `BooleanChoice` or a `SingleFiniteChoice` in the
initial supported page grammar.

A Filter shall have, where applicable:

- a stable identifier;
- a reader-facing label;
- a default value;
- allowed values;
- participation in reproducible public state;
- concise help text or presentation hints.

### 10.1 BooleanChoice

A `BooleanChoice` shall represent a labelled true/false Filter with a declared
default value.

### 10.2 SingleFiniteChoice

A `SingleFiniteChoice` shall represent a labelled Filter selecting one value
from one or more declared values, with a declared default value.

The specification does not require any particular HTML widget for either
FilterItem form. Widget selection belongs to rendering design so long as the
specified meaning and state are preserved.

---

## 11. PAPanel Contract

`PAPanel` is the visible public region containing one Published Artifact and its
Notes.

A PAPanel shall contain:

- one `PA`; and
- `Notes`, which may contain zero or more visible Notes.

The PAPanel relationship is material: Notes accompany and explain the Published
Artifact or visible Published Artifact features. They are not an extension of
the FilterSection and shall not be presented as belonging to it.

A rendering of `Contents` in which Notes visibly span the FilterSection as well
as the Published Artifact does not conform to this specified relationship unless
an amended grammar or explicit public exception is adopted.

---

## 12. Published Artifact Contract

A Published Artifact is the analytical object deliberately presented to the
reader within a PAPanel.

A PA shall have, as applicable:

- a stable identity;
- a public artefact form;
- a public label or framing where needed;
- site-facing data or artefact inputs;
- meaningful visible features;
- Notes, caveats or provenance declarations where needed;
- consistency requirements required for public presentation.

The initial PA terminal forms in `PG` are:

- `<table>`;
- `<indexed table>`;
- `<chart>`;
- `<sectioned table>`;
- `<prose>`;
- `<custom artifact>`.

The internal structure and rendering rules for those forms may be refined by
Published Artifact model and rendering design documents.

A custom artefact may provide specialised visible analytical presentation, but
it shall occupy the PA position in the PAPanel and shall not silently redefine
`PublicUI`, `NavigationBar`, `ContentPanel`, `Heading`, `Contents`,
`FilterSection`, `PAPanel` or `Notes` structure.

---

## 13. Notes Contract

`Notes` consists of zero or more `Note` items accompanying a PA in a PAPanel.

A Note explains or qualifies visible analytical material. A Note may pertain to:

- a PA as a whole;
- a visible table column or column group;
- a visible chart trace or data source;
- a representation or visibility preset;
- a visible artefact feature;
- relevant caveat or provenance information.

A Note shall be visible only when relevant to the visible PA and material visible
state.

A Note does not belong to a Filter. A change in Filter state may change Note
relevance only because it changes the visible state of the PA.

---

## 14. Public Status and Curation Contract

Every page candidate shall have an explicit public status or be excluded from
public publication.

The initial status vocabulary may include:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

Only `promoted` pages are required to satisfy the normal public page grammar and
rendering contract in full.

Legacy, diagnostic or candidate content may be exposed only where its status and
limitations are explicit. Such content shall not silently establish the public
site's normal page grammar, navigation, styling, Filter behaviour or data
contracts.

---

## 15. Public Selection and Deep-Link Contract

The site shall support stable public selection of promoted pages.

Where material analytical state changes the public view, a public link shall be
capable of restoring that state where shareability is required.

Public state may include:

- selected Page;
- selected Filter values;
- selected data instance;
- selected representation;
- visible table or chart view where declared material.

Transient browser interaction need not form part of public state unless it is
explicitly promoted into the public contract. Examples of normally transient
state include:

- hover state;
- scroll position;
- an open tooltip;
- ordinary table sort, unless declared material;
- chart zoom, unless declared material.

Public page identities and public state shall not be derived from incidental
source filenames or legacy output locations.

Invalid requested public state shall degrade predictably and shall not silently
leave a promoted page empty or misleading.

---

## 16. Static Publication Contract

The generated website shall be publishable as static output.

The public server shall not require:

- Python;
- a database;
- an application server;
- server-side computation;
- user accounts;
- a dynamic public API.

Static output may contain, where required:

- HTML;
- CSS;
- JavaScript;
- data files;
- serialized page, PA or runtime data;
- images and other public assets;
- build metadata useful for verification.

Client-side JavaScript may realise interactive public behaviour and restore
public state from stable links.

Build and deployment shall remain separable operations.

---

## 17. Producer and Site-Facing Input Contract

Producer modules own analysis-specific computation and meaning.

For promoted public material, producers shall provide deliberate site-facing
inputs sufficient to publish the intended PA, including where applicable:

- data values;
- labels;
- meaningful visible columns or traces;
- valid Filter values;
- caveats;
- provenance;
- consistency requirements.

`make_site2` owns the public organisation, public page structure, Filter
presentation, PAPanel relationship, Notes presentation, public state,
publication assembly and shared site behaviour.

`make_site2` shall not normally parse legacy generated HTML to recover the
meaning of a promoted PA.

---

## 18. Legacy Evidence Contract

Legacy `make_site` output and code may be used as evidence of behaviour that
might need to be retained, restored, corrected or deliberately rejected.

Legacy material is not normative merely because it previously existed.

A retained legacy behaviour shall be justifiable against current requirements,
this specification or an explicitly recorded pending design decision.

The active `make_site2` product shall not depend operationally on legacy
`make_site` code or output for normal promoted-page publication.

---

## 19. Error and Missing-State Contract

A promoted page shall not silently render blank, structurally invalid or
materially misleading public content when required inputs or required public
state are missing or invalid.

The product shall handle, as applicable:

- missing required PA inputs;
- missing required data;
- invalid selected Page;
- invalid Filter values;
- unsupported PA terminal form;
- contradictory public model structure;
- excluded or unavailable page selection;
- failed client-side data load.

Build-time invalidity of required promoted material shall be reported as a build
failure or explicit blocking error. Invalid reader-requested state in an
otherwise valid built site shall degrade predictably to an available public
state or a clear public error presentation.

---

## 20. Initial Conformance Criteria

A first conforming production slice shall demonstrate:

- one generated static public site;
- one visible `PublicUI` conforming to `PG`;
- a NavigationBar containing site identity, Navigation and a working hider;
- one subject-led hierarchical numbered Navigation structure;
- one promoted Page rendered in a ContentPanel;
- one Heading and one Contents structure;
- optional/actual FilterSection behaviour using supported FilterItems;
- one PAPanel containing one PA and Notes;
- one table or indexed-table PA terminal;
- stable selected-page public state;
- site-facing inputs rather than copied legacy HTML for the promoted page;
- working local build and inspection;
- explicit public status handling.

Before replacing the legacy public product, `make_site2` shall additionally
demonstrate:

- promoted table and chart PAs conforming to the public page grammar;
- `BooleanChoice` and `SingleFiniteChoice` FilterItems;
- a specialised/custom PA terminal that does not redefine surrounding PG
  structure;
- explicit handling of candidate, legacy or excluded material where included;
- shared public state and public navigation behaviour;
- no normal promoted-page dependence on iframe rendering or copied generated
  legacy HTML.

---

## 21. Relationship to Design Documents

This specification establishes the public website structure and public
behaviour required of `make_site2`.

Subsequent design documents shall explain how the implementation satisfies this
specification:

- `03 Architecture and Design Thesis.md` shall explain the model-first
  architecture and how it supports coherent, auditable rendering of `PG`;
- model design documents shall specify semantic representations of the concepts
  and relationships defined here;
- rendering design shall specify how those concepts are realised visually and
  interactively without inventing unowned public structure;
- build, runtime, producer-integration and deployment documents shall specify
  the supporting machinery.

These later design choices may refine implementation and rendering policy, but
they shall not silently alter the public relationships specified by `PG` or the
public contracts in this document.