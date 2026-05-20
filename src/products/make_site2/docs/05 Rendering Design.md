# 05 Rendering Design

## Status

Initial design document for rendering in `make_site2`.

This document describes how the UI Model and Artifact Model become rendered
static route pages plus browser-side interactive behavior.

It does not describe route derivation, publication planning, output writing, or
deployment.

---

# 1. Purpose

Rendering realizes the UI Model.

The renderer consumes:

```text
UIModel
ArtifactModel
RenderConfig
```

and produces:

```text
RenderedSite
```

The renderer does not invent page structure.

Core rule:

```text
If rendering needs structural information that is absent from the UI Model, the
UI Model is incomplete.
```

Rendering is the realization of the model, not the discovery of the model.

---

# 2. Position in the Pipeline

Rendering is downstream of the UI Model and upstream of output writing.

```text
SiteDefinition
  -> PublicationPlan
  -> UIModel
  -> RenderedSite
  -> WrittenOutput
```

Conceptually:

```python
def render_ui_model(
    ui_model: UIModel,
    render_config: RenderConfig,
) -> RenderedSite:
    ...
```

This transformation produces rendered static-site material.

It does not copy files to the final output directory.

It does not deploy the site.

---

# 3. Hybrid Route-Page Rendering Model

`make_site2` uses a hybrid static rendering model.

Python generates one real static HTML route page per planned page.

Examples:

```text
/current/basho-results/index.html
/banzuke/changes/index.html
/history/career-length/index.html
```

Each route page uses the shared shell and is rendered from the UI Model.

Each route page contains stable UI structure such as:

```text
Sidebar
ContentPanel
Heading
Filter containers
PA / artifact container
Notes container
runtime bootstrap data
```

Browser JavaScript then handles dynamic behavior inside those prepared slots:

```text
filters
branch selection
interactive tables
charts
visible notes
URL state where required
```

The public server remains static.

It only serves generated files.

This design deliberately avoids both extremes:

```text
not:
  copied standalone HTML pages with unrelated shells

not:
  one opaque JavaScript application that replaces the whole site
```

Python owns stable public page structure.

JavaScript owns local interactivity.

The UI Model is the contract between them.

---

# 4. Renderer Inputs and Outputs

The renderer consumes model objects that have already been resolved.

Inputs:

```text
UIModel
ArtifactModel objects or artifact references
RenderConfig
runtime requirement information from the PublicationPlan
```

Output:

```text
RenderedSite
```

Conceptually, `RenderedSite` may include:

```text
route pages
shared shell fragments
runtime bootstrap data
runtime asset references
artifact renderer registrations
metadata needed by the OutputWriter
```

The exact representation is an implementation detail.

The design commitment is that `RenderedSite` is already rendered site material,
but not necessarily written to disk yet.

---

# 5. RenderConfig, ThemeConfig, and LayoutConfig

Rendering is controlled by explicit rendering configuration.

At design level:

```text
RenderConfig
  ThemeConfig
  LayoutConfig
  RuntimeConfig
```

The exact representation is deferred, but the purpose is settled.

`ThemeConfig` owns visual tokens such as:

```text
colours
font sizes
font families, if configured
line heights
border colours
background colours
link colours
table density values
status marker colours
```

`LayoutConfig` owns layout tokens such as:

```text
Sidebar width
collapsed Sidebar width
ContentPanel padding
Heading spacing
FilterSection spacing
PA spacing
Notes spacing
content max width
table viewport policy values
chart container defaults
```

`RuntimeConfig` owns browser-runtime rendering choices such as:

```text
development cache-busting mode
runtime bootstrap mode
default browser-error display style
```

The purpose of these configuration objects is to support an iterative visual tuning loop:

```text
edit config literals
  -> rebuild
  -> deploy or preview locally
  -> inspect in browser
  -> adjust config
  -> rebuild again
```

Theme and layout constants should be centralized.

They should not be scattered through page-specific renderers.

---

# 5a. Theme and Layout Boundary

The UI Model defines interface structure.

Theme and layout configuration define how that structure is visually realized.

The renderer applies the configuration to the model.

The boundary is:

```text
UI Model:
  there is a Sidebar, ContentPanel, Heading, FilterSection, PA, and Notes

Theme/Layout config:
  how wide, what colours, what spacing, what typography, what density

Renderer:
  applies ThemeConfig and LayoutConfig to the UI Model
```

A colour, spacing value, font size, or width is not part of the UI Model unless it has semantic force.

The first implementation may use simple provisional styling, including styling ideas copied from earlier experiments. Such styling is not design authority.

Provisional styling should still be centralized so that it can be changed by editing config and rebuilding.

---

# 5b. CSS Generation and Design Tokens

The renderer may realize ThemeConfig and LayoutConfig through generated CSS custom properties.

For example:

```css
:root {
  --site-bg: ...;
  --panel-bg: ...;
  --text-main: ...;
  --sidebar-width: ...;
  --content-padding: ...;
  --table-font-size: ...;
}
```

The exact CSS mechanism is deferred.

The important design point is:

```text
shared structure uses shared tokens
theme/layout changes happen in one place
page-specific CSS is exceptional
artifact-specific CSS is confined to artifact internals
```

This directly supports iterative theme and layout tuning.

---

# 5. UI Renderer Responsibilities

The UI Renderer owns shared page realization.

It owns:

```text
HTML shell
Sidebar
Navigation
ContentPanel
Heading
FilterSection
BranchSelector
PA placement
Note placement
status markers
runtime bootstrap
shared CSS class conventions
application of ThemeConfig and LayoutConfig
```

It does not own artifact internals.

If the UI Renderer starts deciding what a page means, the design boundary has
been crossed.

---

# 6. Artifact Renderer Responsibilities

Artifact renderers own only the artifact slot.

They own:

```text
table internals
indexed-table loading and rendering
chart rendering
sectioned-table rendering
prose rendering
custom artifact internals
```

They do not own:

```text
page route
Sidebar
Navigation
ContentPanel
Heading
FilterSection placement
BranchSelector
page status
site-wide theme
site-wide layout
```

A custom artifact renderer is allowed when the artifact has genuine local
structure.

A custom artifact renderer is not allowed to become a custom page renderer.

---

# 7. Rendering Pipeline

For each planned page already resolved into the UI Model, rendering proceeds
conceptually as:

```text
render route page shell
render Sidebar
render active Navigation state
render ContentPanel
render Heading
render Contents structure
render FilterSection / BranchSelector containers
render PA slot
render Artifact container and bootstrap
render Notes container
emit runtime bootstrap data
```

Artifact internals are rendered by artifact renderers.

The completed rendered material is passed to the output-writing stage.

---

# 8. Shell Rendering

The shell renders the stable public site structure.

At minimum, the shell contains:

```text
Sidebar region
ContentPanel region
runtime asset links
runtime bootstrap data
```

The shell is shared across pages.

The shell is not page-specific.

A page may have different content, filters, artifacts, or notes, but it should
not bring its own unrelated shell.

---

# 9. Sidebar and Navigation Rendering

The Sidebar renders:

```text
site identity / caption
navigation tree
quick links, if present
sidebar hider
```

Navigation rendering distinguishes:

```text
clickable page nodes
non-clickable grouping nodes
active page
quick links
collapsed or expanded groups
Sidebar hider
```

The renderer consumes planned navigation.

It does not derive routes.

It does not decide which pages are included.

Those decisions belong to the Publication Plan.

---

# 10. ContentPanel Rendering

The ContentPanel renders the selected page.

Conceptually:

```text
ContentPanel
  Heading
  Contents
```

The ContentPanel is not an arbitrary widget container.

It is the visual realization of the page's UI Model structure.

The renderer should preserve the distinction between:

```text
page Heading
FilterSection
BranchSelector
PA slot
Artifact container
Notes
```

---

# 11. Heading Rendering

The Heading provides page-level framing.

It is distinct from:

```text
site caption
navigation label
PA title
artifact-internal labels
table headings
chart labels
```

The renderer should make this hierarchy visually clear.

A page should not rely on artifact titles or chart titles to provide page-level
identity.

---

# 12. Filter Rendering

`Filter` is the model term.

A Filter is not a widget.

The renderer chooses controls to expose Filters.

Possible controls include:

```text
radio buttons
segmented controls
dropdowns
checkbox groups
toggles
tabs
```

These are rendering choices.

They are not separate UI Model concepts unless a later pressure case requires
them.

The renderer must preserve Filter scope.

Examples:

```text
G1:
  FilterSection affects the visible PA.

G2:
  BranchSelector chooses the branch.
  Selected branch FilterSection affects that branch's PA.
```

Filters do not own Notes.

Filters may have help text.

---

# 13. G1 Rendering

G1 is the single-visible-artefact grammar.

Conceptually:

```text
Heading
FilterSection?
PA
Notes
```

A G1 page renders one visible PA slot.

The artifact inside that slot may still be complex.

Examples:

```text
one table page
one indexed-table page
one chart page
one sectioned-table page
one prose page
one custom-artifact page
```

The renderer should not treat G1 as "simple HTML". It is a structural grammar,
not a complexity claim.

---

# 14. G2 Rendering

G2 is the selected-alternative grammar.

Conceptually:

```text
Heading
BranchSelector
selected Branch FilterSection?
selected Branch PA
relevant Notes
```

Unselected branches are not rendered as simultaneous visible content.

They may exist in runtime bootstrap data or model data, but only the selected
branch is active.

Changing the BranchSelector changes:

```text
visible branch
visible branch filters
visible PA
relevant notes
```

The renderer must make this scope clear.

---

# 15. PA Rendering

The renderer places the PA.

A PA may include:

```text
PA title / framing, if present
Artifact container
Notes container or note references
```

The PA is the boundary between shared page rendering and artifact rendering.

The renderer places the PA and delegates artifact internals to the appropriate
artifact renderer.

---

# 16. Artifact Rendering

Artifact rendering dispatches by artifact kind or renderer kind.

Initial artifact kinds include:

```text
table
indexed_table
chart
sectioned_table
prose
custom_artifact
```

The shared renderer creates the artifact slot.

The artifact renderer fills the slot.

The artifact renderer may be generic or custom.

It may not redefine the surrounding page.

---

# 17. Notes Rendering

Notes are general, not table-only.

The renderer displays Notes relevant to the visible PA and visible artifact
state.

Notes may pertain to:

```text
the PA as a whole
a table column
a column group
a table visibility preset
a chart trace
a chart source
a data source
a prose section
a visible artifact feature
a provenance fact
a caveat
```

Filters may affect note relevance by changing what is visible.

This does not make Notes belong to Filters.

The UI Model and Artifact Model provide note ownership and relevance
information.

The renderer realizes that information visually.

---

# 18. Status Rendering

Promoted pages may need no visible marker.

Other statuses may need visible treatment:

```text
candidate
research
diagnostic
legacy
superseded
```

The exact visual treatment is deferred.

However, the renderer must not silently make legacy, diagnostic, candidate, or
research material look identical to promoted public content unless the design
explicitly allows it.

Status should be visible enough to prevent accidental misinterpretation.

---

# 19. Runtime Bootstrap

Each route page may include runtime bootstrap data.

Bootstrap data may include:

```text
page id
route
status
filter definitions
default filter state
branch definitions
artifact references
data URLs
note relevance data
build metadata
theme/layout token references, if needed by the runtime
```

The exact serialization is deferred.

The important rule is:

```text
Runtime bootstrap realizes the UI Model.

It is not a second hidden model.
```

If browser JavaScript needs semantic information, that information should come
from the UI Model / Artifact Model serialization, not from page-specific
hardcoding.

---

# 20. JavaScript Runtime Policy

Browser JavaScript handles local interactivity.

It may own:

```text
filter control event handling
branch switching
table sorting, filtering, and rendering
chart initialization
note relevance updates
URL state synchronization
Sidebar collapse interaction
```

It must not own:

```text
public site structure
route derivation
page identity
canonical navigation structure
semantic page grammar
site-wide theme policy
site-wide layout policy
```

JavaScript should implement runtime behavior inside the rendered model.

It should not become a second application model that competes with the Python
side.

No Node.js runtime is required by the public site.

---

# 21. CSS and Styling Policy

CSS must express the UI Model, Artifact Model, and explicitly declared rendering
grammar.

It must not introduce semantic, structural, or visual distinctions that are not
present in those models or grammars.

This applies down to the smallest implementation choices:

```text
wrapper structure
control grouping
control layout
table alignment
spacing
muted text
note placement
responsive behavior
link treatment
form-widget treatment
```

If the rendered page looks wrong, the first question is not "what local CSS fixes
this?" The first question is "what model or grammar rule is missing?"

Fix the missing rule at the highest appropriate level:

```text
site theme
site layout
content grammar
control model
artifact model
artifact renderer
page-specific exception, only if the model really contains one
```

Shared UI structure gets shared CSS.

Page-specific CSS is exceptional.

Artifact-specific CSS is allowed only for artifact internals.

UI-level CSS includes:

```text
shell
Sidebar
Navigation
ContentPanel
Heading
FilterSection
BranchSelector
PA placement
Notes
status markers
theme/layout tokens
```

Artifact-level CSS includes:

```text
table internals
chart container internals
sectioned-table internals
prose internals
custom artifact internals
```

The old failure mode was CSS drift caused by repeated page-specific rendering.

`make_site2` should avoid that by making shared structure share styling and by centralizing theme/layout constants.

Until a theme or layout rule is declared, browser/default rendering is preferred
over bespoke CSS.

---

# 22. URL State and Browser State

The UI Model identifies meaningful public state.

Rendering/runtime serializes and restores it where needed.

Examples:

```text
selected filters
selected branch
selected representation
selected data instance
visible table preset
```

Default state may be omitted from the URL.

Non-default meaningful state should be shareable where useful.

Exact route/query/hash policy is deferred.

Transient browser state need not be public URL state unless promoted into the
model.

Examples of normally transient state:

```text
hover state
open tooltip
scroll position
ordinary chart zoom
ordinary table sort, unless declared meaningful
```

---

# 23. Error and Missing States

Offensive programming applies to internal build and model errors.

UX is different.

Browser-side failures should report useful diagnostic information simply.

Initial browser-side error reporting may use `alert()`.

The point of using `alert()` is simplicity, not vagueness. Error messages should
still be diagnostically useful.

Examples of browser-side failures:

```text
failed data fetch
missing runtime data file
unsupported browser-side artifact state
invalid restored URL state
```

Examples of build/model failures that should crash rather than degrade
gracefully:

```text
missing promoted page route
unknown artifact kind in generated UI Model
contradictory G2 branch structure
missing required producer input during build
```

The user-facing site should not silently show blank space when interactive data
fails to load.

---

# 24. What Rendering Does Not Own

Rendering does not own:

```text
site definition
page inclusion policy
route derivation
producer computation
artifact data generation
deployment
output copying
```

If rendering starts making these decisions, the boundary is wrong.

Rendering owns realization of already-modeled structure.

Rendering must not imply a hierarchy, grouping, emphasis, status, alignment, or
relationship that is absent from the model.

---

# 24a. Relationship to Producers

Producer-owned site-facing inputs may supply semantic presentation metadata such as:

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

Producers should not supply site-theme or site-layout decisions such as:

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

This preserves the ability to tune layout and theme by changing centralized configuration and rebuilding.

---

# 25. Relationship to make_site and ui_model Evidence

Existing `make_site` and `ui_model` material may inform rendering design.

Useful evidence includes:

```text
old shell behavior
old iframe/page switching limitations
old CSS drift
known table rendering needs
known chart rendering needs
BRB runtime behavior
Career Length G2 behavior
Banzuke Changes custom artifact rendering
provisional theme/layout ideas
```

That evidence is not authoritative.

Rendering in `make_site2` is defined by the new requirements, specification, and
design.

Styling ideas copied from previous experiments must be centralized as theme or
layout configuration. They must not become hard-coded page-renderer accidents.

---

# 26. Deferred Questions

The following questions are deferred:

```text
exact RenderedSite representation
exact HTML template strategy
exact runtime bootstrap serialization
exact URL query/hash policy
exact CSS class naming
exact JavaScript module organization
exact ThemeConfig representation
exact LayoutConfig representation
exact CSS custom property generation
exact status marker visuals
exact browser-side error display beyond initial alert()
exact client-side data loading conventions
exact chart renderer implementation
exact table renderer implementation
```

These should be resolved when they become implementation pressure points.

---

# 27. Summary

`make_site2` uses hybrid route-page rendering.

Python renders stable route pages from the UI Model.

JavaScript handles dynamic behavior inside prepared slots.

The server remains static.

The renderer realizes the model; it does not invent it.

Artifact renderers fill artifact slots; they do not own page structure.

Theme and layout constants are centralized so the visual design can be tuned by editing configuration and rebuilding.

The core rendering invariant is:

```text
No promoted page is rendered until it has first been represented in the UI Model.
No rendered structure, styling, or runtime behavior introduces distinctions that
are absent from the UI Model, Artifact Model, or declared rendering grammar.
```
