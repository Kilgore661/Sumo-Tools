# make_site2 Specification

## 0. Status

This is the initial specification for `src/products/make_site2`.

`make_site2` is the successor public-site builder for Sumo-Tools. It is not a
refactor of `make_site`, and it is not a continuation of the previous
`make_site2` experiment. The previous UI-model experiment is now treated as
`ui_model` evidence.

This specification defines what `make_site2` must do.

It does not prescribe final implementation details except where required to
constrain behavior.

---

# 1. Package Purpose

`make_site2` shall generate the public Sumo-Tools website.

The package shall consume:

```text
site definition
navigation definition
page definitions
producer-generated site-facing artefacts
data files
producer site-facing inputs
shared runtime assets
deployment/build configuration
```

and produce:

```text
a coherent static website
suitable for local inspection and public deployment
```

The generated site shall present curated professional sumo analysis to a mixed
audience:

```text
casual readers:
  clear defaults
  ordinary-language framing
  low cognitive load
  official-looking tables where appropriate

expert/statistical readers:
  richer filters
  caveats
  provenance
  methodology
  research material
  deeper analytical controls
```

The public site shall be organized by subject, not by user type.

---

# 2. Non-Goals

`make_site2` shall not be:

```text
a general web framework
a CMS
a live application server
a dashboard framework
a database-backed public API
a repository-wide artefact browser
a compatibility wrapper around old generated HTML
a clone of make_site
```

The first production version does not need to migrate every legacy idea or every
existing generated page.

---

# 3. Static Site Contract

`make_site2` shall generate a static output tree.

The public server shall not require:

```text
Python
a database
an application server
server-side computation
user accounts
a dynamic public API
```

Client-side JavaScript is allowed for interactive pages.

The generated output shall include, as needed:

```text
HTML
CSS
JavaScript
data files
serialized page/artifact data, where required
images/assets
runtime support files
```

Build and deployment shall be separable operations.

---

# 4. Curation Contract

`make_site2` shall distinguish public content from internal project artefacts.

The package shall not publish content merely because it exists or is
browser-readable.

The following are non-public unless deliberately promoted:

```text
raw downloaded HTML
parser diagnostics
warning reports
cache files
source-data archives
debug artefacts
stale experiments
internal audit outputs
legacy generated pages
```

Every page candidate shall have an explicit public status.

Initial status vocabulary:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

Only `promoted` pages are required to conform fully to the normal public
rendering contract.

`legacy`, `diagnostic`, and `candidate` pages may exist only if their status is
explicit.

---

# 5. Site Definition Contract

A `make_site2` site definition shall declare:

```text
site id
site title
navigation tree
page registry
global assets
build defaults
```

The site definition is the public structure of the site.

It is distinct from:

```text
producer source layout
legacy file paths
runtime filter state
build output paths
deployment targets
```

When the site definition conflicts with incidental producer output layout, the
site definition wins.

---

# 6. Navigation Contract

Navigation shall be a rooted labelled tree.

A navigation node shall have:

```text
stable id or key
human-facing label
slug or route component
zero or more children
optional page reference
optional status/readiness metadata
```

A navigation node need not be a page.

Navigation shall be organized primarily by subject.

Navigation shall not expose every implementation subdivision merely because it
exists.

The site may also provide quick entry points for casual readers. Quick entry
points shall link into the canonical subject structure rather than define a
second navigation system.

---

# 7. Route Contract

`make_site2` shall derive or validate stable public routes from navigation and
page definitions.

Routes shall be public concepts.

Routes shall not be derived from incidental source filenames, legacy output
paths, or producer implementation details.

Each promoted page shall have exactly one canonical public route.

Route changes after publication shall be deliberate compatibility decisions.

---

# 8. Page Contract

A page is a public publication unit.

A page definition shall include:

```text
stable page id
title
summary or framing text
navigation placement or navigation reference
public status
content model
data dependencies
asset dependencies
producer site-facing input references
filter/default state where applicable
```

A page is not merely:

```text
an HTML file
a route
a copied generated artefact
```

A page shall render into a `ContentPanel`.

---

# 9. Public UI Contract

The generated public UI shall have the following conceptual shape:

```text
PublicUI
  Sidebar
  ContentPanel
```

`Sidebar` contains:

```text
site caption / identity
navigation
sidebar visibility control
```

`ContentPanel` contains the selected page:

```text
ContentPanel
  Heading
  Contents
```

`Heading` provides page-level framing.

`Contents` is the structured public content selected by the page.

The public UI shall not use an iframe as the normal promoted-page content
mechanism.

---

# 10. Filter Contract

`make_site2` shall use **Filter**, not **Option**, as the public UI-model term.

A filter is reader-visible state that restricts, selects, projects, or otherwise
narrows what part of the available analytical view is shown.

A filter may internally correspond to:

```text
row filtering
column projection
source selection
measure selection
representation selection
branch selection
PA selection
visibility preset selection
```

The public meaning remains:

```text
show this slice or view of the available analytical content
```

A filter shall have, where applicable:

```text
stable id
label
allowed values
default value
URL-state participation
help text
presentation hint
```

Filters may have concise help text.

Filters do not own Notes.

---

# 11. Content Grammar Contract

`make_site2` shall support the G1 content grammar for current promoted pages.

## G1: Single Visible Artefact

G1 describes ordinary pages whose contents expose one visible published
artefact, optionally controlled by filters and accompanied by notes.

```text
ContentPanel
  Heading
  Contents

Contents
  FilterSection?
  PA
  Note*

FilterSection
  FilterItem*

FilterItem
  BooleanChoice | SingleFiniteChoice

BooleanChoice
  label
  default

SingleFiniteChoice
  label
  value+
  default
```

G1 is the default promoted-page shape.

This is not the only possible way to model a content panel.

In particular, G1 does not currently accommodate nested or hierarchical lists of
filters, choices, or options. This is deliberate. The current navigation tree
mostly contains items that do not need this sophistication.

There are a few items that might benefit from structured filters, but
`make_site2` has decided to keep the current model simple for now even though
this can lead to awkward displays. For example, in 6.3.1 Win Probability by
Standing, `Error bars` semantically applies only to the observed source, but it
is currently rendered as a flat peer control alongside `Source`.

Richer content-panel and artifact-view models are deferred. See:

```text
A Appendix - Better Models.md
```

---

# 12. Published Artefact Contract

A Published Artefact, or PA, is the analytical object a public page presents.

A PA shall have:

```text
stable id
artifact kind
renderer kind
data references
optional title/framing
optional filters consumed by the PA or artifact
notes/caveats/provenance where applicable
consistency requirements where applicable
```

A PA renders one artifact.

Initial artifact kinds:

```text
table
indexed_table
chart
sectioned_table
prose
custom_artifact
```

Custom artifact renderers are allowed.

However, a custom artifact renderer may render only the artifact slot. It shall
not redefine the surrounding page structure.

---

# 13. Notes Contract

Notes explain visible analytical content.

Notes belong to PAs or visible artefact features, not to filters.

A note may pertain to:

```text
the PA as a whole
a table column
a column group
a visibility preset
a chart trace
a data source
a visible artifact feature
```

A note shall render only when relevant to the currently visible PA/state.

Notes are general explanatory annotations attached to PAs or visible artifact features.
The first implementation may exercise table notes first, but the model is not table-only.

---

# 14. Producer Contract

Producer modules own analysis-specific knowledge.

A producer may generate:

```text
raw data
diagnostic outputs
legacy outputs
standalone reports
site-facing artefacts
site-facing artifact inputs
site-facing data files
```

Promotion to the public site means the producer provides intentional site-facing
inputs.

`make_site2` shall not normally parse old generated HTML to recover public
meaning.

Producer-owned knowledge includes:

```text
what the data means
how the analysis is computed
which columns/traces are meaningful
what filters are valid
what caveats/provenance matter
what labels should be shown
```

`make_site2` owns:

```text
navigation
routes
page framing
shared rendering grammar
filter rendering conventions
public status handling
static output assembly
deployment shape
shared styling/runtime behavior
```

---

# 15. Rendering Contract

Promoted pages shall render through the shared `ContentPanel` model.

The renderer shall own:

```text
page shell
sidebar
navigation
heading layout
filter section layout
branch selector layout
PA placement
notes placement
shared table/chart/prose containers
shared CSS classes
shared runtime initialization
```

Artifact renderers shall own:

```text
table internals
chart internals
indexed table loading
sectioned table layout
custom artifact internals
```

Artifact renderers shall not own:

```text
page title
site navigation
route
global shell
ContentPanel structure
page-level status
```

---

# 16. Legacy / Prototype Contract

Legacy or prototype content may be included only under explicit status.

A legacy/prototype inclusion shall not silently count as a promoted page.

Legacy/prototype content shall not define:

```text
public route policy
site navigation policy
page grammar
CSS architecture
filter model
data contract
producer contract
```

A promoted page shall not require:

```text
iframe content rendering
copied standalone HTML
page-specific shell ownership
reverse-engineering generated HTML
```

---

# 17. URL State Contract

Meaningful public filter state shall be serializable into the URL where
shareability matters.

Default state may be omitted from the URL.

Non-default state that materially changes interpretation should be
representable.

The route identifies the page.

Query/hash state may identify:

```text
selected filter values
selected branch
selected data instance
selected representation
visible table preset
```

Transient interaction state need not be shareable unless promoted into the
public model.

Examples of transient state:

```text
temporary hover
scroll position
open tooltip
ordinary table sort, unless declared meaningful
Plotly zoom, unless declared meaningful
```

Invalid URL state shall degrade predictably.

---

# 18. Output Contract

A successful build shall produce a complete static output tree.

The output tree shall include:

```text
site entry HTML
route HTML or route data as required
runtime CSS
runtime JavaScript
serialized page/artifact data, where required
data files
assets
build metadata where useful
```

A promoted page with missing required inputs, unsupported artifact kind, or contradictory model structure is a build error.

---

# 19. Deployment Contract

`make_site2` shall support at least:

```text
build only
build and local deploy
build and remote deploy
```

Build and deploy shall be separable.

Deployment targets shall be configuration, not hard-coded public semantics.

The deployed public root shall not be determined by the package name.

---

# 20. Error and Missing-State Contract

The generated site shall handle non-happy paths explicitly.

Examples:

```text
missing data
empty table
invalid filter
unknown route
missing required producer input
unsupported artifact renderer
failed data load
excluded page selected
legacy page not available
```

A promoted page shall not silently render blank space when a required artefact is
missing.

---

# 21. Acceptance Criteria for First Production Slice

The first useful `make_site2` vertical slice shall demonstrate:

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

# 22. Acceptance Criteria for Model Coverage

Before replacing `make_site`, `make_site2` shall demonstrate:

```text
at least one G1 table page
at least one G1 chart page
flat FilterSection handling for BooleanChoice and SingleFiniteChoice controls
one custom artifact renderer inside a shared page structure
explicit handling of legacy/prototype/excluded pages
shared filter vocabulary
shared route/navigation behavior
no promoted iframe pages
no promoted copied-HTML pages
```

---

# 23. Design Freedom

This spec does not require a particular Python class structure.

It does not require that the grammar names become class names.

It does not require that site-facing inputs be JSON rather than Python objects or dataclasses.

It does require that implementation preserve the specified ownership boundaries
and observable behavior.

---

# 24. Vocabulary Decisions

The following terms are part of the `make_site2` specification:

```text
Site
Navigation
Route
Page
Sidebar
ContentPanel
Heading
Contents
Filter
FilterSection
FilterItem
BooleanChoice
SingleFiniteChoice
PA
Artifact
Note
Producer
SiteFacingInput
Status
```

The following term is not part of the `make_site2` public model:

```text
Option
```

This restriction applies to the `make_site2` requirements, specification, design,
model, public terminology, and implementation-facing vocabulary.

It does not prohibit using the ordinary English word "option" in conversation,
planning notes, or informal discussion.
