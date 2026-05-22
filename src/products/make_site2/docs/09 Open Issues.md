# 09 Open Issues

## Status

Initial open-issues register for `make_site2`.

This document records unresolved decisions, implementation pressure points, and questions deliberately deferred from the requirements, specification, and design documents.

It is not a second design notebook.

Each item should remain short, actionable, and linked back to the relevant design area where possible.

---

# 1. Purpose

The purpose of this document is to keep unresolved work visible without scattering decision notes across the design documents.

An issue belongs here when:

```text
the project has identified the question
the answer is not yet settled
the answer is not required to continue the current design pass
the question may matter during implementation
```

An issue should be removed once the decision has been made and the relevant requirements, specification, design, or implementation document has been updated.

---

# 2. Issue Statuses

Use these statuses when maintaining this file:

```text
Open
  Known issue with no settled answer yet.

Decided
  Decision made, but docs or implementation may still need updating.

In progress
  Active implementation or design work is underway.

Blocked
  Cannot proceed until another issue is resolved.

Done
  Completed and ready to remove during the next docs tidy.
```

Default assumption: if an issue appears here without an explicit status, it is **Open**.

---

# 3. Status and Inclusion Policy

## 3.1 Final Page Status Vocabulary

Current working statuses are:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

Decision needed:

```text
Is this the final vocabulary?
Are any statuses redundant?
Do we need separate development-only status?
```

## 3.2 Inclusion by Build Mode

Decide which statuses are included in which build modes.

Possible build modes:

```text
development
public
local preview
stress test
```

Current direction:

```text
promoted:
  included in ordinary public builds

candidate / research / diagnostic / legacy:
  included only when build mode requests them or public structure justifies them

superseded / excluded:
  excluded by default
```

Precise policy remains open.

---

# 4. Route and Slug Policy

## 4.1 Slug Derivation

Routes are derived from canonical navigation placement.

Decision needed:

```text
How exactly are slugs generated from navigation nodes?
```

Examples:

```text
Current Sumo / Basho Results
  -> /current-sumo/basho-results/

or

Current Sumo / Basho Results
  -> /current/basho-results/
```

## 4.2 Route Stability

Decide when a route becomes stable enough that renaming requires compatibility handling.

Questions:

```text
When is a route public?
Do early make_site2 routes need redirect support?
Can route changes be ignored during dev-ui work?
```

## 4.3 Home Route

Decide whether the home route is:

```text
a normal PageDefinition selected by HomePageId
generated from quick links and navigation
some other special page
```

Current preference: home is a normal page selected by `HomePageId`.

---

# 5. Quick Links

Quick links are accepted as useful casual-reader shortcuts into the canonical navigation tree.

Open questions:

```text
Where are quick links rendered?
Are they in the Sidebar, home page, or both?
Are quick links required in the first implementation?
What are the first quick links?
```

Candidate first quick links:

```text
Basho Results
Standings
Banzuke Changes
```

---

# 6. First Vertical Slice: BRB

BRB / Basho Results is the leading candidate for the first vertical slice.

The first slice should demonstrate:

```text
producer orchestration
site-facing input consumption
PublicationPlan
UI Model
Artifact Model
Rendering
BuildOutput
local/LAN deployment
```

Open questions:

```text
What exact BRB producer step should make_site2 call?
What site-facing input does BRB expose first?
What is the minimal BRB artifact contract?
What filters are required in the first slice?
What data payloads are required?
What useful result proves the slice works?
```

---

# 7. Producer Orchestration API

`make_site2` is the public-site build orchestrator.

Decision needed:

```text
How does make_site2 call producers?
```

Possible forms:

```text
producer prepare functions
a producer registry
direct imports for the first slice
a small orchestration module
command-line subprocesses
```

Current preference:

```text
simple direct orchestration first
formal producer API only when needed
```

But this remains open.

---

# 8. Site-Facing Input Representation

The former first-class “PA Manifest” concept has been superseded.

Current design says producer site-facing inputs may be:

```text
Python objects
generated JSON-like data
CSV data
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

Open questions:

```text
What representation is used first?
Python objects?
JSON files?
Generated files consumed by Python?
Some mixture?
```

Decision should be driven by the first BRB slice.

---

# 9. ThemeConfig and LayoutConfig

Rendering design now includes:

```text
RenderConfig
  ThemeConfig
  LayoutConfig
  RuntimeConfig
```

Open questions:

```text
Where does the config live?
Python file?
JSON/YAML?
Dataclass literals?
How are CSS custom properties generated?
What are the first tokens?
```

The goal is the visual tuning loop:

```text
edit config literals
  -> rebuild
  -> deploy/preview locally
  -> inspect in browser
  -> adjust config
```

First implementation should be simple.

---

# 10. Runtime Bootstrap Format

Each route page may include runtime bootstrap data.

Open questions:

```text
Inline JSON script tag?
External page JSON file?
Generated JavaScript assignment?
Per-page bootstrap or shared index?
```

Bootstrap may include:

```text
page id
route
status
filters
default filter state
branch definitions
artifact references
data URLs
note relevance data
build metadata
```

Exact format is open.

---

# 11. URL State Policy

Meaningful public state should be serializable where useful.

Open questions:

```text
Query string or hash?
Which filter states are shareable?
Are default values omitted?
How are invalid values handled in browser runtime?
Does ordinary table sort become URL state?
```

Current direction:

```text
route identifies page
query/hash identifies meaningful non-default state
transient UI state is not serialized
```

---

# 12. Output Tree Defaults

Current typical output shape:

```text
<output_root>/
  index.html
  current/
    basho-results/
      index.html
  assets/
  runtime/
  data/
  build/
    build-info.json
```

Open questions:

```text
Exact output root default
runtime folder name
assets folder name
data folder layout
whether route-local data folders are needed
whether to generate sitemap or route index
```

---

# 13. Build Metadata

Build metadata should be written.

Open questions:

```text
Exact filename?
Exact schema?
Include git branch/commit?
Include build mode?
Include route/page counts?
Include runtime bundle identity?
```

Current placeholder:

```text
build/build-info.json
```

---

# 14. Deployment Commands and Targets

Deployment design recognizes:

```text
build only
preview server
local/LAN deployment
remote deployment
```

Open questions:

```text
Exact CLI flags
Exact default local deploy path
Exact default remote root
Whether preview server is launched by make_site2 or documented as manual
Whether remote deploy is included in first implementation
```

Known current environment:

```text
LAN Apache URL:
  http://192.168.0.6/sumo-tools2/

Likely mapped local target:
  A:\\local\\htm\\sumo-tools2

Remote URL:
  http://68.66.241.105/sumo-tools2/
```

## 14.1 Best CLI Vocabulary and Options

Status: Open.

The word "build" is ambiguous.

It can mean:

```text
build everything from scratch
  rebuild the whole project data world from raw/source inputs

build the data we need
  run selected producers and write site-facing CSV/JSON/etc.

build the site
  assemble the static public site from prepared site-facing inputs
```

The first meaning exists at the wider project/pipeline level but is not a
`make_site2` responsibility. `make_site2` should not present its ordinary CLI as
if it can rebuild the whole analytical world from scratch.

Possible clearer pipeline vocabulary:

```text
rebuild-world
  run the full upstream project pipeline from raw/source inputs; outside
  make_site2's normal scope

produce
  run analysis/producers and write site-facing CSV/JSON/etc.

assemble
  turn site definition + produced artefacts into the static site tree

deploy
  copy/upload the completed site tree to the server and/or remote server

preview
  serve an existing site tree with the preview server
```

Under this vocabulary, the default full workflow is:

```text
produce -> assemble -> deploy server -> deploy remote server
```

The wider project workflow, outside make_site2's normal CLI scope, would have an
earlier stage:

```text
rebuild-world -> produce -> assemble -> deploy server -> deploy remote server
```

The current `--no-build` option is useful but may be poorly named because it
depends on the ambiguous word "build". A possible clearer future name is:

```text
--deploy-existing
```

Decision needed:

```text
What are the best CLI options?
Should no-build deployment be renamed before the CLI settles?
Should command names distinguish produce/assemble/deploy/preview explicitly?
```

---

# 15. Remote Deployment / Future Sync

Remote deployment is secondary for now.

Current accepted behavior:

```text
ensure directories exist
upload/overwrite files
do not delete stale remote files
manual remote purge is acceptable
```

Open questions:

```text
Will a future sync tool replace make_site2 remote deployment?
Should remote clean deploy ever be implemented?
What remote upload mechanism should be used long-term?
```

---

# 16. Notes and Note Targeting

Notes are general, not table-only.

Open questions:

```text
How are note targets represented?
How much target taxonomy is needed for the first slice?
How are relevant notes selected in browser runtime?
Are PA-level notes enough initially?
```

Possible note targets:

```text
PA
table column
column group
chart trace
chart source
data source
prose section
visible artifact feature
```

Do not invent a large taxonomy before examples require it.

---

# 17. Artifact Metadata Details

Initial artifact kinds:

```text
table
indexed_table
chart
sectioned_table
prose
custom_artifact
```

Open questions:

```text
Exact table column metadata vocabulary
Exact chart semantic metadata vocabulary
Exact sectioned-table structure
Exact prose representation
Exact custom artifact renderer registration
```

Decision should be driven by actual migrated pages.

## 17.1 Finish by Chii Checkpoint

Status: In progress.

The next planned implementation target is:

```text
5.1 Finish by Chii
```

Current decision:

```text
Do not migrate the legacy standalone HTML page.
Do not use an iframe.
Represent Finish by Chii as a normal Artifact in the make_site2 shell.
```

Target artifact shape:

```text
Artifact
  TitleBlock
    title
    subtitle
  Payload
    Plotly chart
  Notes, optional
```

The title and subtitle should follow the existing `make_site` / legacy
Finish-by-Chii behavior. They belong to the Artifact, not to Plotly and not to
the chart payload itself.

Options should use the existing page grammar:

```text
FilterSection
  FilterControl*
```

No new options layout rule is currently expected for this page.

The immediate design pressure is data loading.

Existing `make_site` evidence shows these data-loading patterns:

```text
single CSV
CSV plus metadata
option-selected CSV
indexed CSV family
view-selected CSV
```

Finish by Chii exposes another needed pattern:

```text
csv_set
  top_thresholds CSV
  bottom_thresholds CSV
```

Working definition:

```text
DataSource
  one copied resource

DataBinding
  the artifact-level rule for how one or more DataSources become payload data
```

For Finish by Chii, the implementation should introduce only the binding needed
for the page:

```text
DataBinding(kind=csv_set)
  source role: top_thresholds
  source role: bottom_thresholds
```

Do not hide the two-source requirement inside bespoke chart-loading code.

Deferred pressure:

```text
7.3.1 Career Length
```

Career Length may be understood through a more general artifact-view model, but
that model is not part of the current implementation plan. See:

```text
A Appendix - Better Models.md
```

Current executive decision:

```text
Career Length / Longest will have no local options for now.
```

Before implementing Finish by Chii, inspect Career Length enough to avoid
choosing a DataBinding shape that assumes:

```text
one artifact = one CSV = one payload kind
```

The Finish by Chii implementation should remain independent of Career Length,
but the DataBinding vocabulary should not block Career Length later.

## 17.2 Mutually Exclusive Filter Widget Choice

Some filters expose a mutually exclusive range of values.

Current examples include:

```text
dropdown
radio group
segmented control
```

The model currently records the existence of the filter and its values, but it
does not fully answer who decides which widget should render that choice.

Open questions:

```text
Should make_site2 infer the widget from the option count and filter role?
Should the model explicitly say dropdown, radio group, or segmented control?
If the artifact model should not own this, where should the decision live?
Should House Style provide defaults that the model may override?
Should the renderer ever decide, or should it only implement a prior decision?
```

Related questions:

```text
When is a checkbox preferable to a two-value exclusive choice?
When is a segmented control preferable to a radio group?
When is a long option list too long for visible choices?
Which widget decisions affect layout strongly enough to be model-owned?
Which widget decisions are merely chrome?
```

Current direction:

```text
The renderer should not make this decision ad hoc.
The eventual design should distinguish filter meaning from filter presentation.
```

---

# 18. JavaScript Runtime Boundaries

Rendering design says JavaScript handles local interactivity but must not own public site structure.

Open questions:

```text
How many JS modules?
How is artifact renderer dispatch represented in JS?
How are filters bound to runtime state?
How are notes updated?
How much table rendering is generic?
How much BRB behavior is custom?
```

Current direction:

```text
shared runtime owns filters, branch switching, URL state, and common behaviors
artifact runtimes own artifact internals
```

---

# 19. Browser Error Reporting

UX failures should report useful diagnostic information simply.

Current initial direction:

```text
alert()
```

Open questions:

```text
What errors should be reported through alert?
Should a visible error panel replace alert later?
What diagnostic details should be included?
```

Build/model contradictions are not UX errors and should crash during build.

---

# 20. Cache Policy

Caching was a significant problem in the predecessor site.

Current direction:

```text
development cache-busting is enough for now
production cache policy deferred
```

Open questions:

```text
What exact cache-busting mechanism?
Asset URL query token?
Content-stamped filenames?
Data URL cache busting?
Do route pages get cache tokens?
```

---

# 21. Documentation Follow-Up

Open documentation tasks:

```text
Add or update docs index / README.
Remove stale "manifest" vocabulary from any remaining docs.
Standardize BuildOutput terminology.
Keep deferred questions centralized here.
Move decided items out of this file after docs are updated.
```

---

# 22. First Implementation Plan

After `09 Open Issues.md`, the next useful document may be:

```text
10 First Slice Implementation Plan.md
```

Likely focus:

```text
BRB-only vertical slice
minimal SiteDefinition
minimal PublicationPlan
minimal UIModel
minimal Rendering
minimal BuildOutput
local/LAN deploy
```

Open question:

```text
Do we need this document before writing code?
```

---

# 23. Current Priority Guess

Current likely priorities:

```text
P0:
  first BRB vertical slice
  ThemeConfig/LayoutConfig minimal config
  output tree defaults
  local/LAN deployment target
  runtime bootstrap format

P1:
  route slug policy
  first status inclusion policy
  notes targeting
  producer orchestration cleanup

P2:
  remote deployment sync
  production cache policy
  sitemap/redirects
```

This priority guess should be revised once implementation starts.

---
# 24 New Ideas
1. Chii v.Elo before and after/during

# 25. Summary

The major design spine is settled.

The remaining questions are mostly about:

```text
first implementation shape
exact file/config formats
first producer integration
runtime/bootstrap details
local deployment workflow
```

This file should be updated as decisions are made.

Do not let it become a second design notebook.

