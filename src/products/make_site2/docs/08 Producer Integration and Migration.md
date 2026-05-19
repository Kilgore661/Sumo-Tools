# 08 Producer Integration and Migration

## Status

Initial design document for producer integration and migration in `make_site2`.

This document describes how `make_site2` obtains real analytical content from
Sumo-Tools producers, how it orchestrates producer work, and how existing
`make_site` / `ui_model` / legacy material should be treated during migration.

This document is project-specific.

It does not redefine the Site Model, Publication Plan, UI Model, Artifact Model,
Rendering, Build/Output, or Deployment designs.

---

# 1. Purpose

`make_site2` is the public-site build orchestrator.

It is responsible for producing the public site from selected Sumo-Tools
analytical material.

That includes orchestrating whatever producer steps are required for the
selected build.

The basic flow is:

```text
prepare required producer outputs
  -> build PublicationPlan
  -> resolve UI Model
  -> render
  -> write output
  -> optionally preview/deploy
```

Producer integration answers:

```text
Which producer outputs are needed?
Who computes them?
What site-facing inputs do they provide?
How does make_site2 consume those inputs?
How do existing prototype/legacy outputs migrate into the new model?
```

---

# 2. make_site2 as Orchestrator

`make_site2` owns the public-site workflow.

It may run or request producer steps needed for the selected build.

This does not make `make_site2` the owner of producer analysis logic.

The boundary is:

```text
make_site2 decides:
  this public build needs BRB, standings, career length, etc.

producer modules decide:
  how BRB, standings, career length, etc. are computed
```

`make_site2` orchestrates the publication workflow.

Producers own domain computation and domain meaning.

---

# 3. Producer Responsibility

A producer owns analysis-specific knowledge.

Producer-owned knowledge includes:

```text
what data means
how analysis is computed
which columns, traces, values, or sections are meaningful
which filters are valid
which labels should be shown
what caveats matter
what provenance matters
what site-facing output is intentionally published
```

A producer may generate:

```text
raw data
diagnostic outputs
legacy outputs
standalone reports
debug artefacts
site-facing data
site-facing artifact inputs
site-facing prose
site-facing notes
site-facing provenance
```

Not everything a producer generates is public-site content.

Promotion to the public site means the producer provides intentional site-facing
inputs.

---

# 4. make_site2 Responsibility

`make_site2` owns the public-site layer.

It owns:

```text
site definition
navigation
routes
page status
publication planning
UI Model
filter rendering conventions
shared rendering grammar
theme/layout configuration
build/output structure
deployment workflow
```

It does not own:

```text
sumo analysis computation
domain model calculations
historical data parsing
rating algorithm details
statistical method decisions
producer diagnostic output
```

The producer/builder boundary is additive.

A producer may keep old standalone outputs, diagnostics, CSVs, reports, and
debug artefacts.

`make_site2` consumes the intentional site-facing outputs needed for the public
site.

---

# 5. Site-Facing Inputs

`make_site2` consumes producer site-facing inputs.

Site-facing inputs may be:

```text
Python objects
generated JSON-like data
CSV data
table data
chart data/config
structured prose
asset references
data references
labels
notes
provenance
renderer hints
artifact kind declarations
```

The exact representation is not settled here.

The important requirement is that the input is intentional.

`make_site2` should not normally parse old generated HTML to recover public
meaning.

---

# 6. Relationship to Former Manifests

The current design does not require the former concept of a "PA Manifest" as a
first-class model entity.

In the earlier UI-model experiment, manifests were the practical carrier of
artefact truth.

In the current design, that role is split:

```text
UI Model:
  owns interface structure

Artifact Model:
  owns the analytical object displayed inside a PA slot

Producer site-facing inputs:
  supply the data, metadata, labels, notes, provenance, and renderer hints
  needed to construct those models
```

A JSON or Python "manifest" may still be a convenient serialization format.

It is not currently a separate semantic layer.

If implementation pressure later shows that manifests are the right boundary,
they can be reintroduced deliberately as a serialization of the UI Model or
Artifact Model, not inherited accidentally from the prototype.

---

# 7. Producer Execution

`make_site2` is the orchestrator, so it may run producer steps.

A producer step is a computation or preparation action that creates the
site-facing inputs needed by a build.

Examples:

```text
build BRB site-facing data
build standings site-facing data
build Banzuke Changes site-facing data
build career length site-facing inputs
build chart data for a public chart page
```

The orchestration rule is:

```text
make_site2 may call producers;
producers own what their outputs mean.
```

This allows a normal build command to do the useful thing without requiring the
user to remember a separate chain of producer commands.

---

# 8. Producer Execution versus Site Building

Producer execution and site building are distinct phases inside the
orchestrated workflow.

Conceptually:

```text
Producer preparation:
  compute or refresh site-facing inputs

Site building:
  consume those inputs to generate the static site
```

A build command may run both phases.

The model should still keep them separate.

This separation matters because it prevents producer logic from leaking into the
site builder and prevents site rendering concerns from leaking into producer
analysis code.

---

# 9. Live Store and History Inputs

Some producers may require domain data sources such as:

```text
live store
history zip
precomputed output tree
legacy compatibility data
```

Those data-source choices belong to the producer or producer-orchestration
boundary.

`make_site2` may expose command-level choices needed to run the required
producer steps.

But the public-site builder should not become the owner of historical parsing,
rating computation, or domain source selection logic.

If a producer requires a history source, the producer step owns how that source
is used.

---

# 10. Promotion

Promotion is the process by which a producer output becomes a normal public site
page.

A promoted page should have:

```text
PageDefinition
canonical navigation placement
canonical route
explicit page status
site-facing producer input
UI Model representation
Artifact Model representation
shared rendering path
local/LAN deployable output
```

A promoted page should not rely on:

```text
iframe rendering
copied standalone HTML
page-specific shell ownership
reverse-engineering generated HTML
hard-coded page-specific theme/layout styling
```

Promotion does not require deleting old producer outputs.

It requires adding or identifying intentional site-facing inputs.

---

# 11. Legacy and Prototype Outputs

Legacy/prototype outputs are evidence.

They may provide:

```text
public question clues
data lineage hints
example tables/charts
visual examples
migration pressure cases
old explanatory wording
examples of what not to preserve
```

They should not define:

```text
public routes
page grammar
site theme
CSS architecture
data contract
producer/builder boundary
```

A legacy or prototype output may remain available under explicit status if
needed.

It should not silently become a promoted page.

---

# 12. Existing make_site as Evidence

The existing `make_site` package is evidence.

Useful evidence includes:

```text
current page list
current navigation tree
producer calls
data path knowledge
deployment details
known runtime needs
known cache-busting pain
known styling drift
known page-specific hacks
```

`make_site` is not design authority for `make_site2`.

In particular, `make_site2` should not inherit:

```text
view-type dispatch as architecture
iframe/page-shell dependence
copied standalone HTML as promoted-page contract
ad hoc custom page renderers as page structure
repeated CSS as local page styling
```

Code may be copied only after deciding that the copied code implements a
responsibility that still exists in the new design.

---

# 13. Existing ui_model as Evidence

The previous UI-model experiment is evidence.

Useful evidence includes:

```text
G1 / G2 grammar pressure
BRB as G1 indexed-table case
Career Length as G2 selected-alternative case
Banzuke Changes as custom artifact case
direct rendering inside a shared ContentPanel
note/filter/branch interactions
the value of confining custom renderers to artifact slots
```

The previous experiment is not production authority.

Code may be copied or adapted only after deciding that the copied code
implements a responsibility that still exists in the new design.

---

# 14. Theme and Layout Boundary

Producer site-facing inputs may supply semantic presentation metadata.

Examples:

```text
column role
value kind
trace role
preferred ordering
default visible series
public label
help text
note target
provenance
```

Producer site-facing inputs should not supply site-theme or site-layout
decisions.

Producers should not own:

```text
site colours
Sidebar width
page padding
global font sizes
navigation styling
standard table chrome
standard chart container styling
standard note styling
```

The boundary is:

```text
producer supplies semantic roles
renderer/theme decides visual realization
```

This supports the intended visual tuning loop:

```text
edit theme/layout config
  -> rebuild
  -> deploy or preview locally
  -> inspect in browser
  -> adjust config
  -> rebuild again
```

The ability to tune theme and layout centrally is a design goal.

---

# 15. Labels, Notes, and Provenance

Labels, notes, and provenance are usually producer-owned in meaning.

The producer knows what a column, trace, row category, or analytic caveat means.

`make_site2` renders those meanings consistently.

Producer site-facing inputs should provide public-facing labels and explanatory
material where generic rendering cannot know the domain meaning.

Examples:

```text
column display label
column help text
note explaining a table column
note explaining a chart trace
provenance for an observed/modelled data source
caveat about sample size or model assumptions
```

The renderer should not invent domain explanation by guessing.

---

# 16. Artifact-Specific Semantics

Producers may need to supply artifact-local semantics.

Examples:

```text
this column is a chii value
this value is a rating
this trace is observed data
this trace is modelled data
this series should be ordered by division order
this row is a subtotal
this link is a shikona link
```

These are not theme decisions.

They are semantic inputs.

The renderer can use them to produce consistent visual behavior.

---

# 17. First Vertical Slice

The first vertical slice should be narrow.

A suitable first target is:

```text
Basho Results / BRB
```

Reasons:

```text
important public page
G1 structure
indexed table artifact
filterable
data-driven
known runtime needs
meaningful user interaction
```

The first slice should demonstrate:

```text
producer preparation
site-facing input consumption
PublicationPlan
UI Model
Artifact Model
Rendering
BuildOutput
local/LAN deploy
```

The goal is not to migrate every page.

The goal is to prove the full path.

---

# 18. Provisional Migration Order

A possible migration order is:

```text
1. Basho Results / BRB
   G1 indexed table

2. Banzuke Changes
   G1 custom table artifact

3. Standings by Wins
   G1 table

4. One ordinary chart page
   G1 chart

5. Career Length
   G2 selected alternative

6. Typical Equelo Ratings
   sectioned table and/or prose-adjacent artifact

7. Remaining pages by artifact family
```

This order is provisional.

It should change if implementation pressure reveals a better path.

---

# 19. Page Migration Criteria

A page is migrated to the normal `make_site2` path when it has:

```text
PageDefinition
canonical navigation placement
explicit status
site-facing producer input
UI Model structure
Artifact Model structure
shared rendering path
build output
local/LAN deployable result
```

For promoted pages, migration also means:

```text
no iframe content rendering
no copied standalone HTML as the primary content
no page-specific shell
no hard-coded page-specific theme/layout values
```

---

# 20. Non-Migrated Pages

Not every existing output needs migration.

Some outputs should remain:

```text
candidate
research
diagnostic
legacy
superseded
excluded
```

Non-migrated pages must not appear as promoted public content by accident.

A non-migrated page may be listed or preserved only if its status is explicit.

---

# 21. Current Candidate Producer Areas

Known or likely producer areas include:

```text
Basho Results / BRB
Banzuke Changes
Standings by Wins
Career Length
Rank at Retirement
Typical Equelo Ratings
Banzuke Division by Era
Makuuchi Rank by Era
Division Stability
First Chii Appearance
Win Probability by Standing
Finish by Chii
future prose/method/glossary pages
```

This list is not a commitment to migrate every item.

It records known integration pressure.

---

# 22. HTML Outputs

Generated HTML may continue to exist as producer output or legacy output.

However, promoted `make_site2` pages should not depend on old generated HTML as
their public contract.

Acceptable uses of existing HTML:

```text
visual reference
legacy page under explicit status
diagnostic page under explicit status
temporary comparison during migration
evidence for requirements/spec/design
```

Non-acceptable promoted-page use:

```text
copy old HTML and treat it as the real page
parse old HTML to recover model meaning
let old HTML define page shell or route
```

---

# 23. Data Files and Existing Outputs

Existing JSON, CSV, or other data files may be used if they are intentional
enough for the new producer/builder boundary.

If an existing file is merely an incidental intermediate, the project should not
pretend it is a stable contract without deciding so.

The question for each existing output is:

```text
Is this a site-facing input, or is it an implementation artifact?
```

Site-facing inputs can be consumed.

Implementation artifacts should not define public contracts.

---

# 24. Integration with Build Modes

Producer orchestration may vary by build mode.

Examples:

```text
development build:
  prepare enough producer output for local inspection

public build:
  prepare only promoted/public material

stress build:
  prepare candidate or diagnostic material as well
```

Build mode may affect which producers run.

The Site Model and Publication Plan determine what the build needs.

Producer orchestration prepares those needs.

---

# 25. Integration with Deployment

Producer integration is upstream of deployment.

The flow is:

```text
run producers
  -> build site
  -> write output
  -> deploy or preview
```

Deployment should not run producers.

Deployment consumes completed `BuildOutput`.

---

# 26. Relationship to Offensive Programming

Producer integration should not hide contradictory internal states.

Examples that should fail directly:

```text
planned page requires producer output that was not produced
producer declares artifact kind unknown to make_site2
producer site-facing input lacks required semantic information
quick link targets a page that the build excluded
```

External input failures may occur at producer boundaries.

The design does not require graceful recovery from broken producer/build
contracts.

---

# 27. What Producer Integration Does Not Own

Producer integration does not own:

```text
site requirements
public navigation policy
route derivation
UI rendering
theme/layout configuration
deployment execution
browser runtime behavior
```

It owns how analytical content enters the public-site build workflow.

---

# 28. Deferred Questions

The following questions are deferred:

```text
exact producer orchestration API
exact command-line flags for running producer steps
whether each producer exposes a standard prepare function
exact location of site-facing producer outputs
exact representation of producer site-facing inputs
exact first BRB producer integration shape
whether legacy make_site producer calls are copied or rewritten
whether live-store/history-zip selection is exposed by make_site2 CLI
how much producer output is cached between builds
whether build mode selects producer subsets automatically
```

These should be resolved when they become implementation pressure points.

---

# 29. Summary

`make_site2` is the public-site build orchestrator.

It may run required producer steps.

Producers own analytical computation and domain meaning.

`make_site2` owns the public-site workflow, model resolution, rendering,
output, and deployment.

The new builder should consume intentional site-facing producer inputs rather
than reverse-engineering old generated HTML.

Existing `make_site` and `ui_model` code are evidence, not authority.

The first integration target should be narrow enough to prove the whole pipeline.

BRB / Basho Results is the leading candidate for that first vertical slice.
