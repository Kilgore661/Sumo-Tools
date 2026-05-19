# 06 Build and Output Design

## Status

Initial design document for build and output writing in `make_site2`.

This document describes how rendered site material becomes a concrete static
output tree.

It does not describe route derivation, UI-model resolution, rendering internals,
producer computation, or deployment execution.

Deployment is a first-class package capability, but deployment is designed
separately in:

```text
07 Deployment Design.md
```

---

# 1. Purpose

Build and output writing turns rendered site material into a complete static
site directory.

Conceptually:

```python
def write_output(
    rendered_site: RenderedSite,
    output_config: OutputConfig,
) -> BuildOutput:
    ...
```

The input is `RenderedSite`.

The output is `BuildOutput`.

The output directory should be directly inspectable and suitable for deployment.

---

# 2. Position in the Pipeline

Build/output writing is downstream of rendering and upstream of deployment.

```text
SiteDefinition
  -> PublicationPlan
  -> UIModel
  -> RenderedSite
  -> BuildOutput
  -> Deployment
```

The build/output stage consumes rendered material.

It writes files.

It does not invent page structure.

It does not decide which pages are included.

It does not deploy.

---

# 3. RenderedSite

`RenderedSite` is the conceptual input to output writing.

It represents rendered static-site material that has not necessarily been
written to disk yet.

It may contain:

```text
rendered route pages
rendered or serialized bootstrap data
runtime asset references
global asset references
page asset references
producer data references
artifact data references
build metadata inputs
```

`RenderedSite` is not the same thing as a filesystem directory.

It is the rendered material ready to be written.

---

# 4. BuildOutput

`BuildOutput` is the conceptual result of output writing.

It records the completed static output.

Conceptually, it may contain:

```text
OutputRoot
EntryPoint
RouteFiles
RuntimeFiles
AssetFiles
DataFiles
BuildMetadataFile
WrittenFiles
```

`BuildOutput` is the thing deployment consumes.

The exact representation is an implementation detail.

The design commitment is that deployment does not have to rediscover what the
build wrote.

---

# 5. Output Root

The build writes to an output root.

The output root is distinct from deployment roots.

Examples:

```text
Build output root:
  files/output/make_site2

Local deployment root:
  local browser-visible web root

Remote deployment root:
  public remote web root
```

The output root is where `make_site2` generates the static site.

Deployment later copies or uploads that output.

---

# 6. Clean Output Policy

The output root is cleared before each build.

This prevents stale generated files from surviving after pages, assets, routes,
or data dependencies are removed.

A build output directory should represent the current build, not an accumulation
of historical builds.

Incremental writing may be reconsidered only if a real requirement appears.

---

# 7. Output Tree Shape

The generated output tree should be ordinary static-site material.

A typical shape is:

```text
<output_root>/
  index.html
  current/
    basho-results/
      index.html
  banzuke/
    changes/
      index.html
  history/
    career-length/
      index.html
  assets/
    ...
  runtime/
    ...
  data/
    ...
  build/
    build-info.json
```

Exact folder names may change.

The important requirements are:

```text
route pages are real static HTML files
runtime assets are present
data required by interactive pages is present
build metadata is present
the output root can be served as static files
```

---

# 8. Route Page Output

Each canonical route is written as a real static route page.

The preferred route-page form is directory `index.html`:

```text
/current/basho-results/index.html
```

rather than:

```text
/current/basho-results.html
```

This keeps public URLs clean and makes route folders natural containers for
route-local files if needed later.

The root route is written as:

```text
/index.html
```

---

# 9. Generated Outputs

The build/output stage writes generated files.

Generated files may include:

```text
route HTML pages
serialized bootstrap data
serialized UI/artifact model data needed by the browser runtime
build metadata
generated indexes, if needed
```

Generated files come from the `RenderedSite`.

They are not copied from producer output unchanged unless the design says they
are source inputs.

---

# 10. Copied Inputs

The build/output stage copies required source files into the static output tree.

Copied files may include:

```text
runtime CSS/JS files
global site assets
page assets
producer data files
artifact data files
images or other static media
```

Copied files are explicit build inputs.

Their destination in the static output tree is part of the output design.

---

# 11. Runtime Files

Runtime files live as source assets in the package or project.

The build copies them into the output tree.

Initial runtime files may include:

```text
make_site2 CSS
make_site2 JavaScript
table runtime support
chart runtime support
navigation/sidebar support
shared utility code
```

The Publication Plan records the runtime requirements of the planned site.

The output stage writes those runtime files into the generated site.

The initial implementation may copy the standard `make_site2` runtime bundle for
all builds.

---

# 12. Data Files

Interactive pages may require data files.

Examples:

```text
indexed table payloads
chart data
table data
lookup indexes
artifact-specific JSON/CSV data
```

The Publication Plan identifies required data references.

Rendering may generate bootstrap references to those data files.

The output stage copies or writes the required data into the static output tree.

The browser runtime later loads the static data files from the generated site.

---

# 13. Asset Files

Assets may be global or page-specific.

Global assets are required by the site as a whole.

Page assets are required by individual pages or artifacts.

The output stage writes all assets required by the rendered site.

Asset output paths should be stable and public-facing.

Asset paths should not expose arbitrary local source layout unless deliberately
chosen.

---

# 14. Build Metadata

The output tree includes build metadata.

A simple build metadata file should be written, for example:

```text
build/build-info.json
```

Build metadata may include:

```text
site id
site title
build timestamp
build mode
output root
route count
page count
runtime bundle identity
source branch or commit, if conveniently available
```

Exact fields are deferred.

The purpose of build metadata is to make the generated output inspectable.

It is not a substitute for public page provenance.

---

# 15. BuildOutput and Deployment

The output-writing stage returns `BuildOutput`.

Deployment consumes `BuildOutput`.

This allows deployment to know:

```text
where the generated site lives
what entry point exists
what files were written
what route pages exist
what build metadata exists
```

Deployment should not have to reconstruct the output tree by guessing.

---

# 16. Build Orchestration

A full build command may orchestrate earlier stages:

```text
load or construct SiteDefinition
make PublicationPlan
make UIModel
render UIModel
write output
```

This document focuses on the final output-writing stage, but the package build
command naturally coordinates the whole pipeline.

The output stage itself consumes `RenderedSite`.

It does not redo publication planning or UI-model resolution.

---

# 17. File Paths

The output stage translates public routes and output references into filesystem
paths.

Examples:

```text
Route:
  /current/basho-results/

Output file:
  <output_root>/current/basho-results/index.html
```

This mapping belongs to build/output design.

Public route semantics are already resolved by the Publication Plan.

---

# 18. Relative Links and Asset URLs

Generated route pages need correct links to runtime assets, data files, and
other pages.

The output design should support stable URL references from route pages to:

```text
runtime CSS/JS
data files
assets
other route pages
```

The exact URL policy is deferred.

However, generated pages should not depend on the local filesystem layout of the
developer machine.

---

# 19. Cache and Versioning

Build/output may participate in cache/version policy.

Examples:

```text
content-stamped runtime files
build-stamped asset URLs
development cache-bust tokens
stable production URLs
```

Exact cache policy is deferred.

The important distinction is:

```text
development cache convenience
  versus
public production cache policy
```

The output stage should implement whatever policy is chosen by build/render
configuration.

---

# 20. Local Inspection

The build output should be inspectable in a browser through the normal local
deployment path.

The output directory itself should also be understandable as static site
material.

A successful build should create all files needed for local serving.

Deployment design later defines how the generated output is made visible through
the local browser-visible web root.

---

# 21. What Build and Output Does Not Own

Build/output writing does not own:

```text
public site requirements
site definition
page inclusion policy
route derivation
UI Model structure
artifact model structure
artifact rendering internals
producer computation
browser interaction behavior
local or remote deployment execution
```

If output writing starts deciding any of those things, the boundary has been
crossed.

---

# 22. Relationship to Rendering

Rendering produces `RenderedSite`.

Output writing consumes `RenderedSite`.

Example:

```text
Rendering:
  creates the HTML text for /current/basho-results/

Output writing:
  writes that HTML text to <output_root>/current/basho-results/index.html
```

Rendering decides what the rendered page contains.

Output writing decides where that rendered page is placed in the static tree.

---

# 23. Relationship to PublicationPlan

The Publication Plan identifies routes, included pages, dependencies, and
runtime requirements.

Output writing uses the rendered consequences of that plan.

It does not rederive the plan.

It does not include extra pages merely because their files exist.

---

# 24. Relationship to Deployment

Deployment is first-class.

However, deployment is downstream of build/output.

Build/output creates the static site directory.

Deployment copies or uploads that directory to a target where it can be viewed
or published.

The separation is:

```text
Build/output:
  create the static site

Deployment:
  put the static site somewhere useful
```

Both are required package concerns.

They have different ownership.

---

# 25. Relationship to make_site and ui_model Evidence

Existing `make_site` and `ui_model` material may inform build/output design.

Useful evidence includes:

```text
current output tree shape
current runtime asset copying
current data-file copying
current local deployment expectations
current cache-busting behavior
current generated page routes
```

That evidence is not authoritative.

The build/output model for `make_site2` is defined by the new requirements,
specification, and design.

---

# 26. Deferred Questions

The following questions are deferred:

```text
exact output root default
exact runtime folder name
exact assets folder name
exact data folder layout
exact build metadata schema
exact cache/version policy
whether route-local data folders are ever needed
whether output should include a generated sitemap
whether output should include redirects for renamed routes
exact relation between build output root and local deploy root
```

These should be resolved when they become implementation pressure points.

---

# 27. Summary

Build and output writing turns `RenderedSite` into `BuildOutput`.

It writes a clean static output tree.

It writes real route pages using directory `index.html` form.

It copies runtime assets, global assets, page assets, and data files required by
the rendered site.

It writes build metadata.

It returns a `BuildOutput` object or report for deployment to consume.

It does not decide what the site means, what pages are included, how UI
structure works, how artifacts render internally, or where the finished site is
deployed.
