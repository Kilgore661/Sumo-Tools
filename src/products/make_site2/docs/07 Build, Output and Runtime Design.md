# 07 Build, Output and Runtime Design

## Status

Draft design document for building, writing and running the static public site
produced by `src/products/make_site2`.

This document is downstream of the public specification, model design and
rendering design. It describes how resolved and rendered public material becomes
a complete static output tree and how browser runtime behaviour realises the
already-modelled interactive public site.

It does not define public meaning, alter `PG`, decide Page inclusion, invent
Published Artifact structure or define deployment targets.

---

## 1. Purpose

The build, output and runtime layer shall turn the resolved and rendered
`make_site2` publication into a runnable static website.

It shall provide:

- a complete static output tree;
- all required entry material, assets, data and browser runtime files;
- predictable local inspection of the generated site;
- restoration and operation of declared public state in the browser;
- explicit failure when required publication material cannot be written or run
  correctly.

The design boundary is:

```text
Upstream models and Rendering Design:
  determine what public site exists and how it is visibly realised.

Build and output:
  write the files required to publish that realised site.

Browser runtime:
  activates declared interaction and state-restoration behaviour in static
  output.

Deployment:
  places completed output at a local or remote serving destination.
```

---

## 2. Position in the Pipeline

The full public-site pipeline is:

```text
Prepared producer site-facing inputs
  -> Site Definition
  -> Publication Plan
  -> Public UI Model and Published Artifact Model
  -> Rendering
  -> Static Build Output
  -> Optional Deployment
```

Build/output writing consumes rendered site material and the resolved file/data
requirements of the Publication Plan. Browser runtime consumes the files written
into the static output and applies the declared public interaction/state
behaviour.

Conceptually:

```text
RenderedSite + PublicationPlan + OutputConfig
  -> BuildOutput

BuildOutput served as static files
  -> BrowserRuntime
  -> interactive Rendered PublicUI
```

The output/runtime layer shall not use incidental filesystem contents or runtime
branching to re-decide what Pages, Navigation, Filters, PAs or Notes mean.

---

## 3. Terms

The following concepts are used in this document:

```text
BuildContext
  operational facts and choices for a particular build

OutputConfig
  configuration controlling the generated static output location and output
  writing policy

RenderedSite
  rendered site material and required static references ready to be written

BuildOutput
  completed static output tree and a record of what was written

BrowserRuntime
  static browser-executed code and data needed to activate declared public UI
  behaviour

RuntimeBootstrap
  serialized material required to initialise the public site in the browser
```

These are design concepts. Exact Python class names and serialized formats may
differ.

---

## 4. Build Context and Build Modes

`BuildContext` carries operational information required while assembling the
static site.

It may contain:

- repository and product roots;
- output root;
- build mode;
- build timestamp;
- cache/version token policy;
- diagnostics collector;
- data-instance or date-range build selection where deliberately supported;
- local/preview/public context flags needed by output or runtime presentation.

Build mode may affect planning, validation, diagnostics, assets or visible
context/status presentation only under explicit upstream policy. It shall not
silently alter the semantic public structure of promoted Pages.

Possible modes include:

```text
public build
local inspection build
preview/development build
stress-test or diagnostic build, where explicitly supported
```

Exact mode vocabulary and inclusion policy remain matters for build policy and
implementation design.

---

## 5. Build Orchestration

A normal `make_site2` build command may coordinate the entire site-assembly
pipeline:

```text
load configuration and BuildContext
  -> load/construct SiteDefinition
  -> resolve PublicationPlan
  -> load required site-facing inputs
  -> resolve Public UI and Published Artifact Models
  -> render the planned site
  -> write static BuildOutput
  -> optionally deploy or make available for local inspection
```

The term `build` shall not be used to imply that `make_site2` owns upstream
analysis computation. The ordinary responsibility of this package is to
assemble the public site from prepared, deliberate site-facing inputs.

A later orchestrated workflow may invoke upstream producers before site
assembly, but that would not transfer analytical ownership into the output
writer or browser runtime.

---

## 6. RenderedSite

`RenderedSite` is the conceptual input to static output writing.

It may contain:

```text
RenderedSite
  entry_html
  additional_entry_html*
  runtime_bootstrap_material?
  rendered_or_serialized_public_model_material?
  required_runtime_asset_references
  required_public_asset_references
  required_data_references
  build_metadata_inputs
```

The exact balance between rendered HTML and serialized model/data consumed by
runtime is an implementation choice. Whatever the balance, the output shall
implement the already-resolved public model and Rendering Design rather than
ask the browser runtime to invent it independently.

`RenderedSite` is not a filesystem tree and is not a deployment target.

---

## 7. BuildOutput

`BuildOutput` is the completed static site generated for one build.

Conceptually:

```text
BuildOutput
  output_root
  entry_points
  runtime_files
  asset_files
  data_files
  serialized_bootstrap_or_model_files?
  metadata_files?
  written_file_inventory?
  diagnostics
```

It shall be sufficient for:

- serving the site as static files;
- local inspection;
- deployment without rediscovering build intent;
- verifying which output was produced where practical.

Deployment consumes completed output; it shall not need to rerun planning or
rendering in order to identify what should be published.

---

## 8. Output Root and Clean Output Policy

The build shall write to a defined output root distinct from any deployment
root.

```text
Output root:
  directory into which make_site2 writes the completed static site

Deployment root/target:
  local or remote destination to which completed output is copied or uploaded
```

Unless a later performance requirement establishes a safe incremental strategy,
the output root shall be prepared cleanly for each build. Stale pages, assets,
data or runtime files from earlier builds shall not survive merely because the
current build no longer knows about them.

A completed output tree should describe one coherent build, not a history of
partial build results.

---

## 9. Static Output Tree

The output tree shall consist of ordinary static web material.

An initial conceptual shape is:

```text
<output_root>/
  index.html
  assets/
    ... public static assets ...
  runtime/
    ... shared CSS, JavaScript and bootstrap/model material ...
  data/
    ... PA/runtime data files ...
  build/
    build-info.json, if emitted
```

Exact folder names and serialization choices may change. The required
properties are:

- at least one browser-loadable entry point exists;
- required site/runtime CSS and JavaScript assets are present;
- required data and serialized material are present;
- asset and data references work when the output is served statically;
- declared public selections and material state can be restored according to
  the public-state contract;
- output does not depend on the developer machine's source paths.

---

## 10. Entry Point and Page Selection

The initial design permits a single application entry HTML document, for
example:

```text
/index.html
```

with selected Page and material public state restored by static browser runtime
from the approved public-selection/deep-link representation.

The specification does not require one generated HTML document per public Page.
Nor does this design prohibit additional explicit entry documents where a later
requirement or public-link design justifies them.

Whichever approach is selected:

- public Page identity shall come from Publication Plan/public-state design, not
  from incidental output filenames;
- output writing shall write explicitly planned entry material;
- runtime shall restore only modelled/specified public state;
- invalid public state shall be handled predictably under the Specification.

---

## 11. Output-Writing Responsibilities

The output writer shall write or copy exactly the static material required by
the resolved rendered site.

It owns:

- preparing the output root;
- writing entry HTML and any explicitly planned additional entry files;
- writing serialized bootstrap/model material needed at runtime;
- copying or writing runtime assets;
- copying or writing required public assets and PA data;
- writing build metadata where configured;
- reporting write-time failures and output diagnostics;
- returning or recording the resulting `BuildOutput`.

It does not own:

- public requirements;
- Page/Navigation inclusion policy;
- `PG` or Public UI structure;
- Published Artifact meaning;
- rendering policy;
- upstream producer computation;
- deployment execution.

---

## 12. Runtime Assets

The browser runtime may require shared static source assets such as:

```text
site CSS
site JavaScript
navigation and Sidebar interaction support
public-state restoration support
Filter interaction support
PA-terminal runtime support
data-loading utilities
chart-library integration or other supported renderer assets
```

The Publication Plan shall make required runtime support knowable before output
writing completes. The output writer shall stage that support in the static
output.

The initial implementation may include one standard shared runtime bundle for
all builds. A later split-bundle design shall preserve the same ownership rule:
runtime dependencies arise from planned/modelled content and shall not be
silently discovered as a side effect of an improvised renderer path.

---

## 13. Runtime Bootstrap and Serialized Material

A static interactive site may require browser-readable bootstrap material.

Runtime bootstrap may include, as applicable:

- site caption and planned Navigation material;
- included Page identities and public selection references;
- Page Heading and Contents material needed client-side;
- Filter declarations, allowed/default/current state handling;
- PA references and terminal-form metadata;
- Notes/relevance material;
- references to PA data files;
- public status information where visibly represented.

Whether this is written as one manifest, several serialized files, embedded JSON
or generated JavaScript is an implementation decision. The important boundary
is:

```text
Bootstrap/runtime material serializes or transports modelled public meaning.
It does not create new public meaning outside the models and specification.
```

Runtime material should be stable enough to inspect and diagnose during local
build review.

---

## 14. Public State Restoration and Runtime Interaction

The BrowserRuntime may restore and update declared public state in the rendered
static site.

It shall support, as required by the selected pages:

- selecting the public Page identified by a stable public selection reference;
- applying material Filter state;
- loading or selecting PA data needed for the state;
- displaying the corresponding relevant Notes;
- maintaining a reproducible public link where the Specification requires it.

The runtime shall preserve distinctions established upstream:

| State or interaction | Ownership |
| --- | --- |
| selected Page | public selection/public UI state |
| selected Filter values | Filter/public PA presentation state |
| relevant Notes shown because PA state changed | PAPanel/Notes consequence of visible PA state |
| Sidebar hidden/restored | shell/UI state, not Filter state |
| hover, ordinary scroll or other transient interaction | ordinarily not material public state |

The runtime shall not represent Sidebar hiding as a Filter, move Notes outside
their PAPanel relationship, or create alternative Page structures unknown to the
model.

---

## 15. PA Data and Assets

Interactive PAs may require static data or terminal-form assets, including:

- table and indexed-table payloads;
- chart datasets;
- PA-specific configuration or visible-feature data;
- public images or media;
- PA-local static assets required by an approved renderer kind.

The Publication Plan identifies required references. The Published Artifact
Model interprets their analytical meaning. Rendering emits the appropriate
references/containers. Output writing stages the required static files. Runtime
loads or displays those files as declared.

Output paths should be deliberate and stable within the public output design.
They shall not expose source-tree layout accidentally or determine PA/public
meaning merely by their filenames.

---

## 16. URLs, Relative References and Static Serving

The generated site shall work when served as static web content through the
supported local and public hosting arrangements.

Entry material, runtime assets, bootstrap data, PA data and public assets shall
refer to one another using URLs compatible with the selected output and
public-link policy.

This document does not choose the exact path/query/hash public-selection policy.
It does require that output writing and BrowserRuntime implement whichever policy
is specified upstream without depending on local filesystem paths or accidental
working-directory behaviour.

A file opened directly from disk is not necessarily an adequate substitute for
static serving if browser security rules or runtime data loading prevent valid
operation. Local inspection design should therefore provide a normal served
path where needed.

---

## 17. Build Metadata and Diagnostics

The build may write inspectable metadata describing the generated output, for
example:

```text
build/build-info.json
```

Metadata may include:

- site identity;
- build timestamp;
- build mode;
- included Page count or identities;
- runtime/output version information;
- source branch or commit where readily available;
- diagnostic/warning summary where appropriate.

Build metadata serves inspection and operational verification. It is not a
substitute for public PA provenance or public Notes.

Diagnostics shall distinguish matters such as:

- blocking failures preventing valid publication;
- warnings about explicitly included provisional/legacy material;
- non-blocking output observations;
- runtime/load failures observable only during local/browser inspection.

---

## 18. Failure Behaviour

The build/output/runtime layer shall fail or report clearly when it cannot
realise a valid planned public site.

### 18.1 Build-Time Blocking Failures

Examples include:

- missing required rendered entry material;
- missing required runtime asset;
- missing required public data or PA asset;
- failed write/copy operation;
- contradictory output paths or duplicate required destinations;
- failure to serialize required runtime/bootstrap material.

A public build shall not silently omit required promoted content or create an
apparently successful but unusable static site.

### 18.2 Browser-Runtime Failures

Examples include:

- an invalid requested public selection or Filter state;
- failed loading of static PA data;
- missing serialized bootstrap material;
- a declared runtime renderer unavailable in the built output.

Where a valid built site receives invalid requested reader state, it shall fall
back or report predictably as defined by the Specification/runtime policy. Where
required built material is absent, the failure should be visible and
diagnosable rather than silently producing misleading content.

---

## 19. Local Inspection

A successful build shall be inspectable through an ordinary local workflow.

Local inspection shall permit review of:

- overall PublicUI rendering;
- Sidebar and Navigation behaviour;
- selected Page/public state restoration;
- Filter behaviour;
- PA rendering and data loading;
- Notes relevance and placement;
- runtime errors and missing assets;
- context/status presentation where relevant.

Local inspection is particularly important because Rendering Audit depends on
examining visible rendered facts, not only reading model declarations or CSS.

Local serving/deployment mechanics belong in `09 Deployment and Operations.md`,
but the build output shall contain everything needed for that workflow.

---

## 20. Cache and Version Policy

Output and runtime may require cache/version handling for static assets and data.

Possible policies include:

- a development cache-bust token;
- content- or build-versioned asset references;
- stable production references with controlled invalidation;
- build metadata recording runtime/data identity.

Exact cache/version policy is deferred until required. Whatever policy is
adopted shall be owned by build/output/runtime design, shall not change public
meaning, and shall not cause stale output to appear as current publication.

---

## 21. Relationship to Deployment

Build/output and deployment are separate responsibilities:

```text
Build/output/runtime preparation:
  create a complete runnable static site directory.

Deployment:
  make that completed directory available at an intended local or remote
  serving destination.
```

Deployment shall consume `BuildOutput` or its recorded output root. It shall not
re-decide Page inclusion, regenerate PA meaning, alter the public grammar or
patch rendered output differently for different targets unless an explicit
public/context rendering policy exists upstream.

---

## 22. Relationship to Legacy Evidence

Legacy `make_site`, archived documents and existing output may provide evidence
about:

- output-tree arrangements that have worked locally or remotely;
- runtime/data-copying requirements;
- expected public-link restoration behaviour;
- cache or deployment practicalities;
- failures caused by copied HTML or ad hoc runtime assumptions.

Such evidence should inform this design where it remains relevant. It shall not
supersede the active Specification, Model Design or Rendering Design.

---

## 23. Invariants

A conforming build/output/runtime implementation shall satisfy:

1. It writes a static output tree sufficient to serve the planned public site.
2. It writes or stages all assets, data and runtime support required by included
   promoted Pages and PAs.
3. It does not include extra public Pages merely because source files exist.
4. It does not infer public Page identity or PA meaning from incidental output
   paths.
5. It does not redefine `PG` or Rendering Design in output-writing or runtime
   convenience code.
6. Browser runtime restores and applies only declared public state and preserves
   Sidebar/Filter/PAPanel/Notes ownership distinctions.
7. Required missing or invalid output fails clearly rather than creating
   misleading publication.
8. A completed BuildOutput is suitable for local inspection and optional
   downstream deployment.
9. Stale output shall not survive a normal clean build in a way that appears to
   be part of the current site.

---

## 24. Deferred Questions

The following matters remain deferred until implementation pressure requires
settled policy:

- exact default output root;
- exact output directory layout and naming;
- exact serialized runtime/bootstrap model format;
- whether one entry HTML document remains sufficient for all approved public
  link designs;
- exact path/query/hash public-state implementation;
- exact cache/version strategy;
- exact build metadata schema;
- exact local serving workflow;
- whether optional upstream producer execution is orchestrated by a wider build
  command;
- whether partial/date-limited data staging is supported for local inspection;
- whether archive/ZIP output is a build-output convenience or a deployment
  operation.

These questions shall not be resolved by allowing output or runtime code to
quietly establish new public semantics.

---

## 25. Summary

Build, Output and Runtime Design concerns the production of a complete runnable
static site from a planned, modelled and rendered public publication.

It says:

```text
how rendered site material is written as static output
what runtime/assets/data/bootstrap material must be staged
how declared public state can be restored in the browser
how builds are inspected and diagnosed
how output hands off to deployment
```

It does not say:

```text
what public site is required
what PG means
which public structure or PA meaning exists
what rendering policy should communicate to readers
where the completed site is ultimately deployed
```

The central boundary is that static output and browser runtime deliver the
specified, modelled and rendered site; they do not become a back door for
inventing a different one.