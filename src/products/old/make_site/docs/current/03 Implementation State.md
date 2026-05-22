# 03 Implementation State

## Purpose

This document records the current implementation state of `src.products.make_site`.

It complements:

- `01 Public Site Model.md`, which describes the intended semantic model.
- `02 Rendering Model.md`, which describes the intended rendering contracts.
- `06 UI Model Implementation Contract.md`, which describes the current model-to-renderer implementation contract.

This document is deliberately more concrete. It describes what the code currently
does, where the implementation already matches the model, and where it is still
transitional.

The current implementation should be understood as:

```text
a static-site builder with an emerging PA-manifest runtime
```

rather than as a finished semantic publication runtime.

Recent UI Model case studies clarified that the implementation already contains much of the intended model implicitly.  The main gap is therefore not absence of semantic structure, but that the structure is distributed across PA manifest classes, page-specific renderers, copied applications, JavaScript, and CSS rather than being realized through one explicit rendering contract.

---

# Current Status

`make_site` now has a real public-site package and build path.

The active package is:

```text
src/products/make_site
```

The main implementation files are:

```text
builder.py
cli.py
render.py
routes.py
site_definition.py
site_navigation.py
site_pages.py
pa_runtime.py
classes/site_model.py
classes/page_parts.py
pa_manifest/
renderers/
files/
```

The implementation already contains several important semantic structures:

- `Site`
- `NavigationTree`
- `PageRegistry`
- `Page`
- `ViewSpec`
- `OptionsModel`
- `AssetRef`
- `DataRef`
- PA manifest classes for chart/table/runtime artefacts

However, not all rendered pages are yet driven uniformly by those structures.

The current system is therefore partly canonical model and partly adapter layer.

The case-study mapping is encouraging:

```text
ChartPA      -> PA with Chart Artifact
TablePA      -> PA with Table Artifact
MultiViewPA  -> PASet
view_option  -> PASelector
```

This means the existing PA-manifest work is best understood as the most concrete precursor to the new implementation contract, even though some names and field boundaries still need normalisation.

---

# Build Entry Point

The command-line entry point is:

```text
src/products/make_site/cli.py
```

The CLI currently:

1. loads history, either from the live store or from a supplied history zip;
2. builds several analysis outputs needed by public pages;
3. writes current Equelo landmark outputs;
4. constructs a site definition using `site_with_career_lifecycle`;
5. calls `build_site`;
6. optionally deploys locally;
7. optionally deploys remotely.

Important CLI flags include:

```text
--build-only
--prod
--local-only
--no-banzuke
--one-banzuke
--history-zip
--career-history-zip
```

`--career-history-zip` is retained as a deprecated alias for older local/offline
commands.

The `--no-banzuke` and `--one-banzuke` flags control how much Basho Results
payload data is included in the generated site.

---

# Build Configuration

The main build configuration is in:

```text
site_definition.py
```

The active build config is:

```text
BUILD_CONFIG = SiteBuildConfig(
    base_route="/sumo-tools/",
    output_root=OUTPUT_ROOT / "make_site",
)
```

`SiteBuildConfig` is defined in:

```text
classes/site_model.py
```

It currently includes:

```text
base_route
output_root
cache_mode
cache_bust_param
deep_link_page_param
```

The config therefore owns build/deploy context rather than page semantics.

---

# Core Site Model Classes

The top-level site model is defined in:

```text
classes/site_model.py
```

The current core dataclasses are:

```text
SiteBuildConfig
NavigationTree
Page
PageRegistry
Site
```

Current shape:

```text
Site
    id
    title
    navigation
    pages
    global_assets

NavigationTree
    id
    label
    slug
    children
    page_id

Page
    id
    title
    summary
    view
    options
    assets
    data
```

This is a good implementation counterpart to the semantic model in
`01 Public Site Model.md`.

The important current limitation is that the model is still fairly shallow.
For example, `Page` has title, summary, view, options, assets, and data, but it
does not yet directly model `Contents`, PA ownership, notes, provenance, artefact
ownership, or selected-PA structure.

Those richer semantics currently appear mostly in PA manifests or page-specific
renderers.  This is acceptable as a transitional state: the likely direction is
not to overload `Page`, but to make the relationship between page identity,
ContentPanel, Contents, PA, PASet, and Artifact explicit in the renderer and
manifest contract.

---

# Page-Part Model

Page view sorts are defined in:

```text
classes/page_parts.py
```

The current `ViewSpec` variants are:

```text
StandaloneHtmlView
PlotlyJsonView
TableAppView
EssayView
CustomView
```

This tells us a lot about the implementation state.

The builder is currently able to handle:

- copied standalone HTML pages;
- table-app HTML entrypoints;
- Plotly JSON/template pages;
- essay pages copied from a source file;
- custom rendered pages selected by a string `kind`.

`CustomView` is currently the main escape hatch. It is useful for migration, but
it is also the clearest sign that the renderer is not yet fully semantic.

The current direction should be:

```text
CustomView(kind=...)
    -> fewer, more explicit semantic view/artefact sorts
```

where the repeated kinds prove stable.

---

# Site Definition and Navigation

The navigation tree is defined in:

```text
site_navigation.py
```

It is a subject-led tree rooted at `Root`.

The tree includes broad public-site sections such as:

- Home
- Current Sumo
- Rikishi
- Banzuke & Rank
- Performance
- Ratings & Models
- Sumo History
- Data & Notes
- Lab / Archive

Only some navigation nodes currently have `page_id` values.

This is important: the navigation tree already contains more intended public-site
structure than the current implemented page set.

In other words:

```text
NavigationTree = intended publication structure
PageRegistry   = currently backed renderable pages
```

That distinction is healthy, but it should remain explicit.

---

# Page Registry

The base page registry is defined in:

```text
site_pages.py
```

The current base registry includes pages such as:

```text
banzuke_changes
standings_by_wins
finish_by_chii
banzuke_division_by_era
makuuchi_rank_by_era
division_stability
first_chii_appearance
win_probability_by_standing
basho_results_browser
```

Additional pages are added by factory helpers, notably:

```text
site_with_career_length(...)
site_with_career_lifecycle(...)
```

`site_with_career_lifecycle` currently adds or updates:

```text
basho_results_browser
career_length
rank_at_retirement
typical_equelo_values
v5_landmark_policy
lower_rank_rating_stability
```

and attaches several of those pages to navigation nodes.

This means the current site definition is partly static and partly generated
from analysis outputs.

That is appropriate for now, but it means the implementation state depends on
the build path used by the CLI.

---

# Route Derivation

Routes are derived from the navigation tree in:

```text
routes.py
```

The important function is:

```text
derive_page_routes(site: Site) -> Mapping[str, PageRoute]
```

It walks the navigation tree, accumulating slug parts, and produces a route for
each node with a `page_id`.

A page's public route is therefore determined by its location in navigation, not
by the page registry alone.

This is a good design choice because it preserves the semantic distinction
between:

```text
Page identity
Navigation placement
Rendered route
```

Potential issue:

A page can only have one derived route in the current map. If the same `page_id`
were attached to multiple navigation nodes, the last traversal assignment would
win. The current model should therefore treat page-to-navigation placement as
effectively one canonical route unless the route model is extended.

---

# Builder Flow

The main builder is:

```text
builder.py
```

The central function is:

```text
build_site(site: Site, config: SiteBuildConfig) -> None
```

Current build flow:

1. derive page routes from the navigation tree;
2. create a build timestamp and cache-bust token;
3. clear the output directory;
4. write the site shell `index.html`;
5. copy global assets;
6. write PA manifest files into the output root;
7. write runtime assets into the output root;
8. write each routed page;
9. copy page-specific assets;
10. copy page-specific data;
11. write a parallel PA runtime skeleton.

The current builder therefore produces both:

```text
normal static site output
```

and:

```text
runtime-skeleton/
```

The runtime skeleton is explicitly experimental/transitional, but it is very
important because it exposes the intended PA-manifest direction.

---

# Page Writing

`builder.write_page` dispatches by `ViewSpec`.

Current behavior:

| View kind | Current behavior |
|---|---|
| `StandaloneHtmlView` | copy source HTML to the target route |
| `TableAppView` | copy entrypoint HTML and rewrite local asset URLs for cache busting |
| `EssayView` | copy source file |
| `PlotlyJsonView` | write a simple HTML page from data/config/template |
| `CustomView(kind="pa_runtime_page")` | write an embedded PA runtime page |
| `CustomView(kind=...)` | dispatch to page-specific renderer functions |

This is a mixed model.

Some pages are copied artefacts. Some are custom-rendered pages. One page path
uses the PA runtime. Some older table apps still behave like embedded/copy
migrations.

That mixed state is expected during migration, but it is the main implementation
gap relative to the desired model.

---

# Standard Site Shell

The standard shell is rendered by:

```text
render.write_site_index
```

It writes:

- document head;
- shared CSS;
- shell CSS;
- body cache/deep-link attributes;
- left navigation panel;
- main content area;
- welcome panel;
- iframe content panel;
- shell JavaScript.

The current shell uses an iframe for selected site pages:

```text
<iframe id="content-frame" title="Selected site page"></iframe>
```

This is practical for integrating heterogeneous page outputs, but it is also a
sign that the public site is not yet one fully unified semantic renderer.

The iframe approach is currently serving as a compatibility boundary.

---

# Navigation Rendering

Navigation rendering is handled by:

```text
render.render_navigation
render.render_navigation_node
```

Current behavior:

- non-page nodes render as `<span>`;
- page nodes render as links;
- nested children render as nested ordered lists;
- page links carry data attributes used by the shell;
- `tbd_page` links receive a `nav-link-tbd` class.

This already supports the semantic distinction between labels and links.

The current navigation renderer also determines whether a page accepts shell
parameters via:

```text
shell_param_mode_for_page(page)
```

Current modes are:

```text
pa-runtime
adapter
adapter-cache
none
```

These modes are transitional. They encode how different legacy/current page
types accept URL parameters.

A cleaner future model would move this from hard-coded page-id checks toward
semantic page/view capabilities.

---

# Page Renderers

Page-specific renderers live in:

```text
renderers/
```

Current renderer modules include:

```text
banzuke_division_by_era.py
career_length.py
division_stability.py
first_chii_appearance.py
makuuchi_rank_by_era.py
rank_at_retirement.py
standing_win_probability.py
tbd.py
typical_equelo_values.py
```

These are dispatched from:

```text
render.write_custom_page
```

using `CustomView.kind`.

This is currently an acceptable migration mechanism.

However, the string-dispatch model should not become the final abstraction.
When page-specific renderers converge, their common structures should be lifted
into PA manifests or explicit semantic view classes.

---

# PA Manifest Runtime

The PA-manifest runtime is implemented in:

```text
pa_runtime.py
pa_manifest/
files/pa-runtime.css
files/pa-runtime.js
```

The runtime is described in code as an experimental skeleton.

Current behavior:

- writes manifest JSON files for active PA manifests;
- writes a manifest index;
- copies runtime CSS/JS assets;
- can write a parallel runtime shell under `runtime-skeleton/`;
- can write an embedded runtime page inside the normal site output;
- copies page data needed by runtime pages.

The active manifest registry is:

```text
pa_manifest/active_instances.py
```

It currently validates active manifests at import time.

Active PA manifest ids include:

```text
banzuke_changes
basho_results_browser
standings_by_wins
finish_by_chii
banzuke_division_by_era
makuuchi_rank_by_era
division_stability
first_chii_appearance
win_probability_by_standing
career_length
rank_at_retirement
typical_equelo_values
v5_landmark_policy
lower_rank_rating_stability
```

This is the strongest sign that the implementation is moving from page-specific
rendering toward semantic artefact manifests.

---

# PA Manifest Classes

The PA manifest classes live in:

```text
pa_manifest/table_pa.py
pa_manifest/chart_pa.py
```

Important current classes include:

```text
TablePA
IndexedTablePA
ChartPA
MultiViewPA
EssayPA
ExcludedPA
```

The table model includes concepts such as:

- data sources;
- indexed data sources;
- columns;
- column groups;
- group visibility presets;
- sections;
- options;
- notes;
- default sort;
- provenance;
- renderer.

The chart model includes concepts such as:

- data sources;
- axes;
- traces;
- options;
- default trace;
- notes;
- provenance;
- renderer;
- consumed options.

This is already much richer than the top-level `Page` model.

The PA manifests are therefore currently the most concrete implementation of the
semantic publication grammar.

The four UI Model case studies confirm that these classes were already close to
the desired model:

```text
Banzuke Division by Era       -> ChartPA / PA with Chart Artifact
Win Probability by Standing   -> optioned ChartPA
Career Length                 -> MultiViewPA / PASet
Standings by Wins             -> rich TablePA
```

The main normalisation work is to align names and boundaries with the explicit
model:

```text
MultiViewPA        -> PASet
view_option        -> PASelector
ChartPA            -> PA with Chart Artifact
TablePA            -> PA with Table Artifact
Note               -> PA Note, possibly with relevance targets
DataSource         -> DataBinding / dataSources
provenance bucket  -> split into provenance, parameters, render policy, display policy, and ordering where appropriate
```

---

# Data and Assets

Assets and data references are defined using `AssetRef`, `DataRef`, and
`ViewRef`.

Reference construction helpers live in:

```text
site_refs.py
```

Site data references live in:

```text
site_data_refs.py
```

Site asset references live in:

```text
site_assets.py
```

The builder copies declared assets and data into the output tree.

This is a good pattern because pages declare what they need instead of forcing
the builder to infer dependencies from generated HTML.

Current limitation:

Some copied HTML/table-app pages still bring legacy assumptions about their own
asset layout. `TableAppView` handles this partly by rewriting local asset URLs
for cache busting.

---

# Cache Busting

The current build uses a timestamp-derived cache-bust token in dev mode.

Cache-busting support appears in:

```text
builder.AssetUrlRewriter
site_urls.cache_busted_url
render.write_site_index
pa_runtime.write_embedded_runtime_page
```

The builder rewrites local `link href` and `script src` attributes for copied
table-app entrypoints.

External URLs, data URLs, mailto links, anchors, and protocol-relative URLs are
not rewritten.

This is a pragmatic mechanism and should remain implementation-level. It should
not leak into the semantic model.

---

# Deployment

Deployment logic is in:

```text
deploy.py
```

Current deployment supports:

- local deployment by copying the output tree;
- remote deployment using `ssh`/`scp` style operations;
- remote directory creation;
- password prompting.

The CLI prints the final public URL after remote deployment.

Deployment is operational infrastructure, not part of the semantic publication
model.

---

# Current Page Implementation Categories

The current pages fall into several implementation categories.

## Copied or adapted legacy pages

Examples:

```text
banzuke_changes
standings_by_wins
finish_by_chii
```

These are useful public pages, but they are not yet fully expressed through the
new semantic renderer.

## Custom-rendered generated pages

Examples:

```text
banzuke_division_by_era
makuuchi_rank_by_era
division_stability
first_chii_appearance
win_probability_by_standing
career_length
rank_at_retirement
typical_equelo_values
```

These pages are closer to the desired direction because the builder controls the
public rendering, but many are still page-specific renderers.

## PA-runtime page

Example:

```text
basho_results_browser
```

This is the clearest active example of the PA-manifest/runtime direction.

## Placeholder pages

Examples:

```text
v5_landmark_policy
lower_rank_rating_stability
```

These are represented as `tbd_page` custom views.

---

# Current Equelo Position

The currently implemented public Equelo page is:

```text
Typical Equelo Ratings
```

It is backed by fixed-v2/v5 landmark outputs generated during the CLI build.

The page id is:

```text
typical_equelo_values
```

The broader documentation policy should continue to distinguish public Equelo
model names from diagnostic chart-stage names. In implementation terms, the
current public page is the fixed-v2/v5-landmark path, not the older fixed-v1
diagnostic sequence.

---

# Known Transitional Areas

## 1. `CustomView` is doing too much

`CustomView(kind=...)` currently handles:

- real custom renderers;
- PA runtime pages;
- placeholders;
- future/unknown views.

This is useful while migrating, but it should gradually shrink.

Stable cases should become explicit semantic view types or PA manifest renderers.

## 2. Shell parameter mode is hard-coded

`shell_param_mode_for_page` currently uses a mixture of view-kind checks and
page-id checks.

This works, but it is not a semantic contract.

A future model should probably attach this to the page/view definition as an
explicit capability.

## 3. The iframe shell is a compatibility layer

The iframe shell allows heterogeneous pages to coexist.

It should be treated as transitional infrastructure, not as the final expression
of the rendering model.

## 4. PA manifests and page registry overlap

The page registry defines pages.

The PA manifest registry defines published artefacts by page id.

This is acceptable for now, but the ownership relation should become clearer.

The current working model resolves the main conceptual shape as:

```text
ContentPanel
  = Heading + Options? + Contents

Contents
  = PA | PASet

PASet
  = PASelector + PA+
```

The implementation still needs to make this relationship explicit in code and
manifest layout.

## 5. Top-level `Page` is less expressive than PA manifests

The current `Page` class has title, summary, view, options, assets, and data.

PA manifests contain richer semantics such as notes, provenance, columns,
column groups, traces, data sources, selected views, and consumed options.

The likely direction is not to overload `Page`, but to clarify how a page route
and page identity lead to a ContentPanel whose Contents are either a PA or a
PASet.

## 6. Some navigation nodes are intentional but not implemented

The navigation tree includes many future public-site locations.

This is fine, but the difference between:

```text
planned navigation node
implemented page
placeholder page
```

should remain visible.

---

# Implementation Direction

The implementation should move toward:

```text
Page
    owns page-level identity, route, summary, and navigation placement

ContentPanel / Contents
    own the selected page's rendered publication structure

Published Artefact
    owns analytical artefact semantics

Renderer
    realizes ContentPanel, Contents, PA, PASet, and Artifact semantics consistently
```

This suggests the following direction:

1. keep `Site`, `NavigationTree`, `PageRegistry`, and `Page`;
2. reduce `CustomView` over time;
3. promote stable page renderers into explicit view sorts or PA renderers;
4. use PA manifests as the canonical form for charts/tables/essays where
   practical;
5. make ContentPanel, Contents, PA, PASet, and Artifact ownership explicit;
6. make page-level vs artefact-level ownership explicit;
7. make shell URL/deep-link capabilities explicit rather than page-id based;
8. keep copied legacy pages only as migration adapters.

---

# Near-Term Work

## Consolidate implementation docs

This document should replace older scattered implementation notes unless they
contain facts not yet merged here.

## Review `CustomView` kinds

Inventory current `CustomView.kind` values and classify them as:

```text
stable semantic view
temporary adapter
placeholder
PA runtime
```

## Implement the ContentPanel / Contents relationship

The working model now treats the rendered page body as:

```text
ContentPanel
  = Heading + Options? + Contents

Contents
  = PA | PASet
```

Near-term work is to reflect this explicitly in manifests and renderer code,
rather than leaving the relationship implicit in `Page.view`, custom renderers,
or page-specific JavaScript.

## Move shell parameter behavior into model

Replace hard-coded page-id checks with model-level capabilities such as:

```text
accepts_shell_params
shell_param_mode
deep_link_mode
```

or an equivalent semantic option model.

## Decide the future of the iframe shell

The iframe shell is currently useful. It should be explicitly classified as:

```text
compatibility shell
```

unless the project decides it is the long-term architecture.

## Promote one more page to PA runtime

Basho Results Browser already exercises the runtime path.

Promoting one chart-like page and one table-like page would help test whether
the PA manifest model generalizes beyond BRB.

## Add conformance tests/checks

Good early checks:

- every routed page id exists in the page registry;
- every active PA id matches a page id where intended;
- every PA validates;
- every copied data source exists;
- navigation page ids are unique;
- page ids have at most one route unless aliases are explicitly supported;
- placeholder pages are visibly marked.

---

# Operational Notes

The normal development build path is through the CLI.

The builder writes output under:

```text
files/output/make_site
```

unless configuration overrides it.

The standard public base route is:

```text
/sumo-tools/
```

The generated output includes:

```text
index.html
site shell assets
page route directories
copied page assets
copied page data
manifest JSON files
PA runtime assets
runtime-skeleton/
```

In production mode, cache-busting behavior changes according to
`SiteBuildConfig.cache_mode`.

---

# Summary

The implementation is in a productive transitional state.

The most important completed pieces are:

- a real `make_site` package;
- a static-site builder;
- a subject-led navigation tree;
- a page registry;
- route derivation from navigation;
- explicit asset/data references;
- page-specific renderers;
- PA manifest classes that already encode much of the implicit UI model;
- active PA validation;
- an experimental PA runtime skeleton;
- build/deploy CLI support.

The most important remaining issues are:

- reducing `CustomView` string dispatch;
- making ContentPanel / Contents / PA / PASet ownership explicit;
- reconciling PA manifest names and fields with the implementation contract;
- replacing hard-coded shell parameter modes;
- deciding whether the iframe shell is transitional or permanent;
- moving more pages from copied/custom adapters toward semantic manifests;
- making implemented/planned/placeholder navigation states explicit.

The current code therefore already contains the outline of the desired semantic
publication system.  The case studies suggest that the old implementation was
working toward a coherent implicit model; the next implementation pass should
make that model explicit and render from it deliberately.
