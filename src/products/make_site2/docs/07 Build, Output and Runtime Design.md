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
- canonical copyable links for all material public views;
- coherent staging of included promoted History-dependent material for the
  Selected History/data instance of the build; and
- explicit failure when required publication material cannot be written, run or
  shown to be coherent.

The design boundary is:

```text
Upstream models and Rendering Design:
  determine what public site exists and how it is visibly realised.

Producer integration and Publication Plan:
  identify or prepare coherent site-facing inputs for the selected build data
  instance.

Build and output:
  validate/stage the files required to publish that realised coherent site.

Browser runtime:
  activates declared interaction and canonical public-state restoration in
  static output.

Deployment:
  places completed output at a local or remote serving destination.
```

---

## 2. Position in the Pipeline

The full public-site pipeline is:

```text
Selected History/data instance where applicable
  -> coherent prepared producer site-facing inputs
  -> Site Definition
  -> Publication Plan
  -> Public UI Model and Published Artifact Model
  -> Rendering
  -> Static Build Output
  -> Optional Deployment
```

Build/output writing consumes rendered site material and the resolved file/data
requirements and coherence conditions of the Publication Plan. Browser runtime
consumes the files written into the static output and applies declared public
interaction/state behaviour.

Conceptually:

```text
RenderedSite + PublicationPlan + OutputConfig
  -> BuildOutput

BuildOutput served as static files
  -> BrowserRuntime
  -> interactive Rendered PublicUI
```

The output/runtime layer shall not use incidental filesystem contents or runtime
branching to re-decide what Pages, Navigation, Filters, PAs or Notes mean. It
shall not silently copy input for a promoted History-dependent PA from a data
instance inconsistent with the Selected History of the build.

---

## 3. Terms

```text
BuildContext
  operational facts and choices for a particular build, including any selected
  History/data instance

SelectedHistory
  the History/data instance deliberately governing History-dependent material
  in one build

OutputConfig
  configuration controlling generated static output location and output-writing
  policy

RenderedSite
  rendered site material and required static references ready to be written

BuildOutput
  completed static output tree and a record of what was written

BrowserRuntime
  static browser-executed code and data needed to activate declared public UI
  behaviour

RuntimeBootstrap
  serialized material required to initialise the public site in the browser

CanonicalPublicViewLink
  a copyable URL selecting one Page and all applicable material Filter values
  required to reproduce one visible public view of the published build
```

These are design concepts. Exact Python class names and serialized formats may
differ.

---

## 4. Build Context and Build Modes

`BuildContext` carries operational information required while assembling the
static site. It may contain:

- repository and product roots;
- output root;
- build mode;
- build timestamp;
- cache/version token policy;
- diagnostics collector;
- an explicit History object, history archive or otherwise selected data
  instance where public material depends on History;
- local/preview/public context flags needed by output or runtime presentation.

An explicit `history` or `history_zip` selection is site-wide build context. It
shall not be treated merely as an optional override for one PA that currently
has a direct implementation path.

Build mode may affect planning, validation, diagnostics, assets or visible
context/status presentation only under explicit upstream policy. It shall not
silently alter promoted Page structure or allow a successful public build to
mix incompatible History-dependent inputs.

Possible modes include:

```text
public build
local inspection build
preview/development build
stress-test or diagnostic build, where explicitly supported
```

The precise policy for including or omitting PAs whose selected-History inputs
cannot yet be prepared or validated is not yet implemented. A normal promoted
public build shall not silently publish those inputs as coherent.

---

## 5. Build Orchestration

A normal `make_site2` build command may coordinate the site-assembly pipeline:

```text
load configuration and BuildContext, including Selected History if applicable
  -> load/construct SiteDefinition
  -> resolve PublicationPlan and coherence requirements
  -> prepare, load or validate required site-facing inputs
  -> resolve Public UI and Published Artifact Models
  -> render the planned site
  -> write static BuildOutput
  -> optionally deploy or make available for local inspection
```

The term `build` shall not imply that `make_site2` owns upstream analysis
computation. Producers own computation of History-dependent analytical material.
`make_site2` owns ensuring that included planned public material is staged only
when it satisfies the selected build contract.

An orchestrated workflow may invoke upstream producers before site assembly, or
consume producer inputs carrying sufficient data-instance identity for
validation. Neither arrangement transfers analytical ownership into the output
writer or browser runtime.

---

## 6. RenderedSite

`RenderedSite` is the conceptual input to static output writing. It may contain:

```text
RenderedSite
  entry_html
  runtime_bootstrap_material?
  rendered_or_serialized_public_model_material?
  required_runtime_asset_references
  required_public_asset_references
  required_data_references
  selected_history_or_data_instance_metadata?
  build_metadata_inputs
```

The selected current publication design uses one ordinary HTML application entry
shell. Additional entry documents are not required to represent planned Pages
or material views.

The exact balance between rendered HTML and serialized model/data consumed by
runtime is an implementation choice. Whatever the balance, the output shall
implement the already-resolved public model and staged coherent data rather than
ask runtime to invent either independently.

---

## 7. BuildOutput

`BuildOutput` is the completed static site generated for one build.

Conceptually:

```text
BuildOutput
  output_root
  application_entry_point
  runtime_files
  asset_files
  data_files
  serialized_bootstrap_or_model_files?
  selected_history_or_data_instance_metadata?
  metadata_files?
  written_file_inventory?
  diagnostics
```

It shall be sufficient for:

- serving the site as static files;
- local inspection;
- deployment without rediscovering build intent;
- restoring every material public view from its canonical Public View Link;
- determining or verifying the selected data instance used for included
  History-dependent content where practical; and
- verifying which output was produced.

Deployment consumes completed output; it shall not rerun planning or silently
replace coherent PA inputs with unrelated material.

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
partial or mutually inconsistent build results.

---

## 9. Static Output Tree

The output tree shall consist of ordinary static web material.

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

Exact supporting folder names and serialization choices may change. Required
properties are:

- the single browser-loadable ordinary entry shell exists;
- required site/runtime CSS and JavaScript assets are present;
- required PA data and serialized material are present;
- data staged for included promoted History-dependent PAs is coherent with the
  Selected History or rejected under explicit policy;
- asset and data references work when output is served statically;
- canonical Public View Links restore declared Page selection and material
  Filter state;
- Navigation destinations link to canonical default views in the shell rather
  than unwritten per-Page HTML files; and
- output does not depend on the developer machine's source paths.

---

## 10. Single Application Shell and Public View Selection

The selected current design uses one ordinary application entry HTML document:

```text
/index.html
```

Promoted Pages and their material public views are selected within that shell by
canonical Public View Links. The build shall not need to generate one HTML entry
document per Page to satisfy Page selection or copyable-view requirements.

A canonical Public View Link shall identify:

- the selected Page; and
- all applicable material Filter values for that Page, including declared defaults.

Navigation destinations shall identify their Page's canonical default view.
Runtime changes to material Filter state shall expose the new canonical view
link in the browser address bar.

The canonical link identifies a public view of the built site's published data;
it does not normally freeze the underlying Selected History. A Banzuke Changes
link may correctly continue to mean “latest changes” after a later coherent
site deployment. Where a History value, basho or data instance is itself a
reader-selected Filter, that selection is part of the link.

The exact query parameter names, ordering and Boolean encoding are implementation
details provided they are consistent, deterministic and preserve the public
contract. Canonical link output shall not intentionally rely on omitted Filter
parameters whose meaning depends on current defaults.

The shell root URL may continue to identify the current landing view while
home/default Page policy remains unsettled. It shall not form an alternative
canonical link for a material selected-Page view.

---

## 11. Output-Writing Responsibilities

The output writer shall write or copy exactly the static material required by
the resolved rendered site.

It owns:

- preparing the output root;
- writing the application entry HTML;
- writing serialized bootstrap/model material needed at runtime;
- copying or writing runtime assets;
- staging required public assets and PA data only from validated/resolved inputs;
- writing build/data-instance metadata where configured or required;
- reporting write-time and coherence-validation failures and diagnostics;
- returning or recording the resulting `BuildOutput`.

It does not own:

- public requirements;
- Page/Navigation inclusion policy;
- `PG` or Public UI structure;
- Published Artifact meaning;
- rendering policy;
- upstream analytical computation;
- deployment execution.

The output writer shall not make an incoherent site appear complete by copying a
convenient producer-output directory without the derivation or validation
required by the plan.

---

## 12. Runtime Assets and Bootstrap

The browser runtime may require shared static source assets such as site CSS,
site JavaScript, Navigation and Filter interaction support, canonical
public-state restoration/writing support, data-loading utilities and supported
PA renderer assets.

Runtime bootstrap may include, as applicable:

- site caption and planned Navigation material;
- included Page identities and canonical default Public View Links;
- Page Heading and Contents material needed client-side;
- Filter declarations, allowed/default/current state handling;
- PA references and terminal-form metadata;
- Notes/relevance material;
- references to PA data files;
- public status information where visibly represented;
- selected data-instance identity where useful for inspection or diagnostics.

Bootstrap/runtime material serializes or transports already-modelled public
meaning and resolved staged material. It does not correct incoherent PA data in
the browser.

---

## 13. Public State Restoration and Runtime Interaction

The BrowserRuntime shall restore and update declared public state in the rendered
static site through canonical Public View Links.

It shall support, as required by selected Pages:

- selecting the Page identified by a canonical link;
- applying all material Filter state represented by that link;
- loading or selecting staged PA data needed for the state;
- displaying corresponding relevant Notes;
- rewriting incomplete or safely resolved invalid incoming state to the
  canonical link for the displayed valid public view; and
- writing a changed canonical link when the reader changes Page or material
  Filter state.

| State or interaction | Ownership / public-link treatment |
| --- | --- |
| selected Page | public selection state; always in a selected Page's canonical link |
| selected Filter values | material Filter/PA presentation state; all applicable values in canonical link |
| Selected History/data instance of build | build/input-coherence concern; not ordinarily in the view link |
| relevant Notes shown because PA state changed | PAPanel/Notes consequence of visible PA state |
| NavigationBar hidden/restored | shell/UI state; not part of Public View Link |
| hover, ordinary scroll or ordinary tooltip | transient; not part of Public View Link |

Runtime shall not mask incoherent build data by changing public-state semantics.

---

## 14. PA Data, Data-Instance Coherence and Assets

Interactive PAs may require static data or terminal-form assets, including table
and indexed-table payloads, chart datasets, PA-specific configuration or
visible-feature data, public media and approved renderer assets.

The Publication Plan identifies required references and coherence requirements.
Producer integration prepares or validates the site-facing data. The Published
Artifact Model interprets its analytical meaning. Rendering emits references and
containers. Output writing stages required static files. Runtime loads those
files as declared.

Where a PA depends on History:

```text
Selected History
  -> producer preparation or validation of PA input
  -> staged PA data in BuildOutput
  -> browser-rendered PA
```

A PA input cannot be regarded as coherent solely because it has the expected
CSV/JSON shape or already exists in `files/output`. Under an explicit-History
build, copied History-dependent input must be derived from or validated against
the selected build History.

---

## 15. URLs, Relative References and Static Serving

The generated site shall work when served as static web content through
supported local and public hosting arrangements.

Entry material, runtime assets, bootstrap data, PA data and public assets shall
refer to one another using URLs compatible with the single-shell output design.
Canonical Public View Links shall address material selected-Page views in that
shell and shall not use route-local HTML destinations that are not written by
the build.

The public contract does not require links to be human-readable. It requires
that material views have deterministic, copyable and restorable canonical links
to the data published by the site currently being viewed.

---

## 16. Build Metadata and Diagnostics

The build may write inspectable metadata such as:

```text
build/build-info.json
```

Metadata may include:

- site identity;
- build timestamp and mode;
- included Page identities;
- Selected History/data-instance identity or interval;
- per-PA derivation/validation identity where required;
- runtime/output version information;
- source branch or commit where readily available;
- diagnostic/warning summary.

Build metadata serves inspection, validation and operational verification. It is
not a substitute for public PA provenance or Notes.

Diagnostics shall distinguish blocking failures preventing valid publication,
warnings about explicitly included provisional/non-public material, non-blocking
output observations and browser-runtime failures.

---

## 17. Failure Behaviour

The build/output/runtime layer shall fail or report clearly when it cannot
realise a valid planned public site.

### 17.1 Build-Time Blocking Failures

Examples include:

- missing required rendered entry material, runtime asset, public data or PA asset;
- failed write/copy operation;
- contradictory output paths or duplicate required destinations;
- failure to serialize required runtime/bootstrap material;
- a planned Navigation destination that cannot identify its Page's canonical
  default view in the single shell;
- a required included promoted History-dependent PA input that is inconsistent
  with or unvalidated against the Selected History of the build.

A normal public build shall not silently omit required promoted content or
create an apparently successful but materially incoherent static site.

For explicit-history inspection/development workflows, unsupported promoted PAs
may be rejected or omitted only under a deliberately adopted policy that makes
the resulting scope/status clear. That enforcement policy remains to be
implemented.

### 17.2 Browser-Runtime Failures

Examples include invalid requested public selection or Filter state, failed
loading of staged PA data, missing bootstrap material or an unavailable declared
runtime renderer.

The browser runtime may normalise invalid reader state, but it cannot repair a
build which staged data from incompatible History instances.

---

## 18. Local Inspection

A successful build shall be inspectable through an ordinary local workflow.
Local inspection shall permit review of:

- overall PublicUI rendering;
- NavigationBar and Navigation behaviour;
- selected Page/public state restoration;
- canonical link copy/paste, reload and new-tab behaviour;
- Filter behaviour and link updates;
- PA rendering and data loading;
- Notes relevance and placement;
- visible or inspectable selected-History/data-instance coherence;
- runtime errors and missing assets;
- context/status presentation where relevant.

Restricted-history builds are particularly useful conformance tests: a small
History makes unvalidated copied material visible when it displays results from
a different period.

---

## 19. Cache, Version and Deployment Boundaries

Output and runtime may require cache/version handling for static assets and data.
Possible policies include a development cache-bust token, versioned asset
references, stable production references with controlled invalidation, and build
metadata recording runtime/data identity.

Build/output and deployment remain separate responsibilities:

```text
Build/output/runtime preparation:
  create a complete coherent runnable static site directory.

Deployment:
  make that completed directory available at an intended local or remote
  serving destination.
```

Deployment shall consume `BuildOutput` or its recorded output root. It shall not
re-decide Page inclusion, regenerate PA meaning, patch rendered output, or mix
data instances differently for different targets unless explicit upstream policy
exists.

---

## 20. Invariants

A conforming build/output/runtime implementation shall satisfy:

1. It writes a static output tree containing the one ordinary application shell
   required to serve the planned public site.
2. It writes or stages all assets, data and runtime support required by included
   promoted Pages and PAs.
3. Where an explicit Selected History governs the build, each included promoted
   History-dependent PA is derived from or validated against it, or the build
   reports/restricts the Page under explicit policy.
4. It does not include extra public Pages merely because source files exist.
5. It does not infer public Page identity or PA meaning from incidental output paths.
6. Navigation destinations and runtime-selected material views expose canonical
   Public View Links addressed into the single shell.
7. It does not redefine `PG` or Rendering Design in output/runtime convenience code.
8. Browser runtime restores only declared public state and preserves
   NavigationBar/Filter/PAPanel/Notes ownership distinctions.
9. Required missing, invalid or incoherent output fails clearly rather than
   creating misleading publication.
10. A completed BuildOutput is suitable for local inspection and deployment.
11. Stale output shall not survive a normal clean build in a way that appears to
    be part of the current site.

---

## 21. Deferred Questions

The following matters remain deferred until implementation pressure requires
settled policy:

- exact default output root and supporting directory naming;
- exact serialized runtime/bootstrap format;
- exact canonical query parameter ordering and Boolean encoding;
- long-term compatibility for previously published canonical Public View Links;
- exact cache/version and build-metadata schema;
- exact local serving workflow;
- general producer-orchestration API;
- whether restricted-history builds block unsupported promoted Pages or omit
  them only under an explicit inspection/non-public policy;
- whether archive/ZIP output is a build-output convenience or deployment operation.

The decisions to use one static shell, to use canonical Page-plus-material-
Filter links, and to require coherent Selected-History staging are not deferred.

---

## 22. Summary

Build, Output and Runtime Design concerns production of a complete runnable
static site from a planned, modelled and rendered public publication.

It says:

```text
one ordinary static application shell hosts selected public Page views
canonical Public View Links identify Page plus material Filter state
Navigation links identify canonical default Page views
browser runtime restores and writes canonical public state
an explicit Selected History governs included History-dependent material
only coherent validated/resolved PA data is staged into BuildOutput
builds are inspected and diagnosed
output hands off to deployment
```

It does not say:

```text
what public site is required
what PG means
how producers compute History-dependent analysis
what rendering policy should communicate to readers
where the completed site is ultimately deployed
```

Static output and browser runtime deliver the specified, modelled and coherently
prepared site; they do not become a back door for inventing a different one or
for combining mutually inconsistent public data instances.