# 09 Deployment and Operations

## Status

Draft design document for deployment and operational use of
`src/products/make_site2`.

This document defines how a completed static `BuildOutput` is made available for
inspection or publication. It is downstream of:

```text
07 Build, Output and Runtime Design.md
```

Deployment is a first-class package responsibility, but it does not define the
public site, resolve models, render Pages, or alter Published Artifact meaning.

---

## 1. Purpose

Deployment shall make a completed `make_site2` static-site build useful in its
intended environments.

The required operational capabilities are:

- inspect a completed build locally in a browser;
- publish the successor site to the configured local/LAN web target used for
  ordinary review;
- support remote public publication where configured;
- report clearly which build was deployed, where it was deployed and how it can
  be viewed;
- prevent deployment activity from damaging unrelated or legacy site trees.

The core boundary is:

```text
Build/output/runtime preparation:
  creates a complete runnable static site.

Deployment and operations:
  serves, copies or uploads that completed static site to a configured target.
```

---

## 2. Position in the Pipeline

Deployment consumes completed `BuildOutput`.

```text
Site Definition
  -> Publication Plan
  -> Public UI Model and Published Artifact Model
  -> Rendering
  -> BuildOutput
  -> Deployment / Inspection
```

Conceptually:

```text
BuildOutput + DeployTarget
  -> DeploymentResult
```

A deployment operation shall know the generated output root and the intended
target. It shall not need to inspect site declarations, re-resolve Pages, parse
runtime bootstrap material or infer public content from producer outputs.

---

## 3. Deployment Is Downstream, but First-Class

`make_site2` shall not merely generate files that could theoretically be
published. Ordinary workflows shall support viewing and publishing those files.

The primary development feedback loop is:

```text
make change
  -> build
  -> deploy/serve locally
  -> inspect rendered site in browser
  -> assess against model and Rendering Design
```

This matters especially for rendering work: `06 Rendering Audit and Changes.md`
depends on being able to inspect the actual browser-visible site repeatedly and
reliably.

Remote public deployment is also an intended capability, but it shall not be a
prerequisite for routine local design and audit work.

---

## 4. Operational Modes

The following modes are distinguished.

### 4.1 Build Only

Build-only operation creates `BuildOutput` and stops before deployment.

It is useful when:

- inspecting generated files;
- testing build/output behaviour;
- preparing a later manual or automated deployment;
- retaining a build artefact without altering any served target.

### 4.2 Preview Serving

Preview serving exposes the output root directly through a local static server.

Conceptually:

```text
BuildOutput
  -> serve output_root directly
  -> inspect through a local browser URL
```

A simple manual server invocation may be sufficient during development, for
example serving the generated output directory on a local port.

Preview serving is not deployment to a persistent public target. It is an
inspection mechanism and is particularly useful where local/LAN or remote target
access is unavailable.

### 4.3 Local/LAN Deployment

Local/LAN deployment copies a completed `BuildOutput` to a configured local web
site root used for normal browser inspection on the development network.

This is the main persistent review workflow during development. It allows the
same generated successor site to be inspected through the configured local web
server rather than only through temporary preview serving.

### 4.4 Remote Public Deployment

Remote deployment copies or uploads a completed `BuildOutput` to the configured
public host/root.

Remote deployment is downstream of successful local build and normal review. It
shall use completed static output, not rerun model resolution or analytical
production implicitly as part of file transfer.

### 4.5 Deploy Existing Build Output

An operation may deploy previously generated output without rebuilding it.

This is useful where:

- a valid build already exists;
- deployment failed or was skipped;
- the user wishes to re-publish exactly the existing output.

A deploy-existing-output operation shall not accept or silently ignore options
that would have affected build content, model resolution or output generation.
If requested options imply a different build, a new build is required.

---

## 5. Successor Site Isolation

The successor `make_site2` public deployment shall remain distinct from the
legacy `make_site` deployment during development and migration.

The known intended distinction is:

```text
legacy site public root:
  sumo-tools

make_site2 successor public root:
  sumo-tools2
```

This separation allows the new product to be evaluated, changed and deployed
without overwriting the legacy public site prematurely.

A deployment target for `make_site2` shall therefore be configured at the
successor-site root, not inferred from the legacy product or from package names.

---

## 6. Deployment Configuration

Deployment configuration is stored outside the Python code as named deployment
targets. The current default file is:

```text
deploy/make_site2_targets.json
```

Conceptually:

```text
DeploymentPlan
  default_targets
  targets[name] -> DeployTarget

DeployTarget
  method
  location
  url?
  host?
  user?
  credential_source?
```

Deployment configuration may contain:

- local filesystem or mapped-drive target paths;
- local/LAN inspection URLs;
- remote host and target-root details;
- transport choice or transport-specific settings;
- credential lookup/configuration details;
- policy for whether the target is cleaned or incrementally updated;
- optional operational safety guards.

The implemented transfer methods are currently:

- `win_copy`: copy the completed output tree to a local, mapped, or UNC-style
  filesystem location;
- `sftp`: upload the completed output tree to a remote host.

Passwords are method-specific. A `win_copy` target shall not require or request
a password. An `sftp` target may name an environment variable such as
`GEOLOCATION`, or request an interactive password when configured to require
one.

Deployment configuration is operational. It is not part of `SiteDefinition`,
`PG`, Public UI Model or Published Artifact Model.

---

## 7. Current Environment Evidence and Configuration

Earlier implementation/documentation identifies the following current working
assumptions for the development environment:

```text
successor public root fragment:
  sumo-tools2

local/LAN served URL:
  http://192.168.0.6/sumo-tools2/

known local/LAN target form from the development machine:
  A:\local\html\sumo-tools2

known remote public URL:
  http://68.66.241.105/sumo-tools2/
```

These values should be treated as current operational configuration/evidence,
not as public-site model concepts. If the hosting environment changes, this
document or the deployment configuration should be updated without affecting
`PG`, Page meaning or Rendering Design.

The local host previously referred to as `Grond` is an operational detail only.
Its name is not required by the public site design.

---

## 8. Local/LAN Deployment Policy

Local/LAN deployment shall copy the completed static output to the configured
successor-site target root.

The local deployment target shall be the site root itself, for example:

```text
A:\local\html\sumo-tools2
```

It shall not be the containing web-document root, for example:

```text
A:\local\html
```

### 8.1 Clean Local Deployment

The intended local/LAN policy is a clean replacement of the configured
`sumo-tools2` target for each deployment:

```text
clean configured successor-site target
  -> copy completed BuildOutput into that target
```

This ensures that the locally served site represents the current build and does
not retain stale removed pages, runtime files, data files or assets.

### 8.2 Safety Boundary

Local deployment shall never clean or overwrite:

- the parent web root merely because it contains the configured target;
- the legacy `sumo-tools` deployment;
- unrelated sibling sites;
- source/input directories;
- any destination not positively identified as the configured successor-site
  target.

Any implementation that supports clean deletion should validate the target
scope before removing files.

---

## 9. Preview Serving Policy

Preview serving shall make a completed output root viewable without copying it
into a persistent deployment target.

A typical manual development pattern is:

```powershell
python -m http.server 8787 --directory files\output\make_site2
```

followed by inspection at a local browser URL such as:

```text
http://127.0.0.1:8787/
```

The exact command, port and default output path are operational choices and may
change. The design requirement is that preview serving operates on completed
static output and provides a reliable browser context for runtime behaviour,
data loading and rendering audit.

Opening generated HTML directly from the filesystem is not a required supported
inspection mechanism where static data loading or browser-origin restrictions
make it unreliable.

---

## 10. Remote Deployment Policy

Remote public deployment shall publish completed `BuildOutput` to the configured
successor-site remote target.

The initial remote-deployment policy may support:

- ensuring required target directories exist;
- uploading/copying files from the output root;
- overwriting files at matching paths;
- reporting transfer failures and the resulting public URL.

A full remote mirror/delete-stale-files policy is not yet required. During the
current development phase, stale remote files may be managed manually or by a
later sync mechanism, provided this limitation is understood and does not lead
to mistaken verification of removed Pages/assets.

Before remote deployment becomes the normal production publication path, the
stale-file and verification policy should be reviewed and made explicit.

---

## 11. Credentials and Secrets

Remote credentials and secrets are external operational configuration.

They shall not be committed to source control or embedded in active design
content as literal secrets.

A remote deployment implementation may use environment variables, secret stores,
interactive prompting or another configured credential mechanism. The exact
mechanism is deferred.

Build-only, preview-serving and local/LAN deployment workflows shall remain
usable without remote credentials.

Failure to obtain required remote credentials shall fail the remote deployment
operation clearly; it shall not alter or invalidate an already completed local
`BuildOutput`.

---

## 12. DeploymentResult and Verification

A deployment operation should return or report a `DeploymentResult` sufficient
for operational verification.

Conceptually:

```text
DeploymentResult
  mode
  source_output_root
  target_root_or_served_root
  public_or_preview_url
  deployment_timestamp?
  file_count_or_transfer_summary?
  build_metadata_reference?
  warnings_or_failures
```

A successful operation should tell the user where to inspect the result.

Verification should distinguish:

- build success: a complete static output was created;
- deployment success: files were served, copied or uploaded as configured;
- browser/runtime verification: the deployed site loads and behaves correctly;
- rendering audit: the visible public site conforms to model and rendering
  expectations.

A successful copy/upload alone is not proof that the public UI or runtime is
correct.

---

## 13. Local Operational Workflow

The normal local design/review workflow should be:

```text
1. Build the current make_site2 output.
2. Deploy it to the configured local/LAN successor-site root or serve it as a
   local preview.
3. Open the resulting browser URL.
4. Check public Page selection, Filters, PA rendering, Notes and runtime/data
   behaviour.
5. For visible-structure or styling changes, apply the rendering audit method in
   06 Rendering Audit and Changes.md.
6. Correct the owning model, rendering design or implementation as needed.
```

This workflow deliberately separates:

- source-code success;
- build/output success;
- deployment success;
- visible public-site correctness.

---

## 14. Remote Operational Workflow

A normal remote-publication workflow should be:

```text
1. Produce a valid intended public BuildOutput.
2. Inspect locally where practicable.
3. Deploy that exact completed output to the configured remote successor-site
   target.
4. Inspect the reported public URL.
5. Confirm that entry, assets, runtime data and important public views load from
   the remote target.
6. Record or address any stale-remote-file concern where the deployment policy
   does not yet guarantee an exact mirror.
```

Remote deployment shall not silently select different Pages, inputs, renderers
or assets from those represented in the completed build being deployed.

---

## 15. Cache and Freshness During Inspection

Browser caching and remotely cached static assets can obscure whether the latest
build or deployment is being viewed.

Build/output design may provide development cache-busting or versioned asset/data
references. Deployment shall copy/upload the resulting output consistently.

Operational verification should take cache behaviour into account where a
recent change appears not to be visible. Cache concerns shall not be mistaken
for a reason to change the public model or Rendering Design without evidence.

A production cache/freshness policy remains deferred until remote publication
requirements make it necessary.

---

## 16. Failure and Safety Behaviour

Deployment shall fail clearly when it cannot publish or expose completed output
as requested.

### 16.1 Deployment Failures

Examples include:

- build output root absent or incomplete;
- configured target absent or inaccessible;
- target-safety validation failure before cleaning;
- failure to copy or upload required files;
- missing credentials for remote deployment;
- failed preview-server startup where managed by `make_site2`;
- inability to report a usable target/preview URL.

### 16.2 Safety-Critical Failures

Operations that remove or overwrite target files require particular care. An
ambiguous, unexpectedly broad or suspiciously mismatched clean-deployment target
shall fail rather than risk deleting unrelated web content.

### 16.3 Post-Deployment Browser Failures

Runtime/data-loading or visible-rendering failures discovered after successful
transfer belong first to build/runtime/rendering diagnosis, unless caused by
incorrect transfer, stale files, URL base configuration or serving-target
behaviour.

---

## 17. Relationship to BuildOutput

Deployment consumes `BuildOutput` as the complete generated site intended for a
particular deployment operation.

It may read enough output metadata to support reporting or validation. It shall
not use deployment as an occasion to:

- scan producer material for extra public content;
- alter the included Page set;
- modify Navigation;
- re-render PAs;
- change Filter or Notes behaviour;
- make target-specific semantic changes to the public site without an explicit
  upstream policy.

The principle is:

```text
Deploy the build that was produced; do not create a new public site while
transferring it.
```

---

## 18. Relationship to Rendering Audit

Local and remote browser inspection provide the evidence needed to audit the
rendered site.

Deployment does not decide rendering correctness. It enables observation of the
actual visible output in the relevant served context.

Where an audit finding is caused by a deployment/context issue—such as stale
remote assets, incorrect base paths or missing copied runtime files—it should be
recorded and corrected at the deployment/output boundary rather than treated as
a model or rendering-rule problem.

---

## 19. Relationship to Legacy Deployment Evidence

Legacy deployment behaviour provides practical evidence worth retaining where it
continues to serve the successor site safely.

Useful known evidence includes:

- clean replacement of a specifically configured local target supported reliable
  local review;
- upload/overwrite remote deployment provided a workable initial remote path;
- separating `sumo-tools2` from `sumo-tools` avoids overwriting the legacy site;
- caching has historically complicated browser verification.

Those observations justify provisional operational policies in this document.
They do not make legacy deployment code or paths permanently authoritative.

---

## 20. What Deployment and Operations Does Not Own

Deployment and operations does not own:

- public-site requirements;
- `PG` or any model structure;
- Page/Navigation/public-status decisions;
- Published Artifact or Note meaning;
- Rendering Design rules;
- producer analytical computation;
- build/output generation beyond validating and transporting completed output;
- browser-runtime semantics beyond diagnosing whether the deployed output runs
  as built.

Where deployment appears to need to change those things, the boundary has been
crossed and the requirement should be addressed upstream.

---

## 21. Deferred Questions

The following matters remain deferred until implementation or operating pressure
requires settled decisions:

- exact target-safety validation mechanism for configured deployment paths;
- whether preview serving is managed by `make_site2` or remains an external
  development command;
- exact remote transport implementation;
- exact credential source and prompting policy;
- whether remote deployment becomes a clean mirror/sync operation;
- exact production cache/version and rollback policy;
- whether ZIP/archive output belongs only to build-output convenience or forms a
  supported deployment interchange artefact;
- what automated post-deployment verification should be supplied;
- whether deployment operations should retain a deployment history or manifest.

Deferred operational questions shall not be resolved by letting deployment
silently change the public content or rendering of the site.

---

## 22. Invariants

A conforming deployment/operations implementation shall satisfy:

1. Deployment operates on completed `BuildOutput` or a clearly identified
   existing output tree.
2. Local/LAN deployment targets only the configured successor-site root and does
   not damage the legacy site or unrelated web content.
3. Preview serving exposes completed static output without redefining it.
4. Remote deployment publishes only the intended completed output and reports
   its limitations where stale-file cleanup is not guaranteed.
5. Operational configuration and credentials remain outside the public model.
6. Deployment does not alter Page inclusion, `PG`, PA meaning or Rendering
   Design.
7. Successful operations report a target or URL sufficient for inspection.
8. Failures are reported at the owning operational boundary rather than hidden
   by partial or misleading publication.

---

## 23. Summary

Deployment and Operations makes the completed `make_site2` static site
viewable locally and publishable remotely.

It says:

```text
how completed BuildOutput is previewed, copied or uploaded
how the successor site remains isolated from the legacy deployment
what operational configuration, safety and verification are required
how browser inspection feeds rendering audit and development workflow
```

It does not say:

```text
what the public site means
what PG contains
which Pages or PAs should exist
how visible rendering conveys meaning
how analytical producer outputs are computed
```

The governing boundary is simple: deployment shall transport or expose the
site that upstream design and build have produced, not become another place in
which the public product is improvised.
