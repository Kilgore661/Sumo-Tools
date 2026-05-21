# 07 Deployment Design

## Status

Initial design document for deployment in `make_site2`.

This document describes how completed build output is made viewable locally and,
optionally, published remotely.

Deployment is a first-class package capability, but it is downstream of build
and output writing.

---

# 1. Purpose

Deployment takes a completed `BuildOutput` and puts it somewhere useful.

Useful means at least:

```text
viewable in the local development environment
optionally uploaded to the remote public host
```

Deployment does not define the site.

Deployment does not derive routes.

Deployment does not render pages.

Deployment consumes build output.

---

# 2. Position in the Pipeline

Deployment is downstream of build/output writing.

```text
SiteDefinition
  -> PublicationPlan
  -> UIModel
  -> RenderedSite
  -> BuildOutput
  -> Deployment
```

Conceptually:

```python
def deploy_local(
    build_output: BuildOutput,
    deployment_config: DeploymentConfig,
) -> DeploymentResult:
    ...


def deploy_remote(
    build_output: BuildOutput,
    deployment_config: DeploymentConfig,
) -> DeploymentResult:
    ...
```

The exact function names are implementation details.

The important point is that deployment consumes `BuildOutput`.

---

# 3. Deployment Is First-Class

`make_site2` must not merely produce files that could theoretically be deployed.

The package must support ordinary workflows for viewing the generated site
locally and, where configured, publishing it remotely.

The primary feedback loop is:

```text
build
  -> local/LAN deploy
  -> view in browser
```

A secondary feedback loop is:

```text
build
  -> preview server
  -> view in browser
```

Remote deployment is useful, but it is not the immediate correctness focus.

---

# 4. Deployment and Preview Modes

The generated site may be viewed or published through several mechanisms.

## 4.1 Build Only

Build-only mode writes the static output tree and stops.

Example output root:

```text
files/output/make_site2
```

Build-only mode is useful for inspection and for manual deployment.

## 4.2 No-Build Deployment

No-build deployment skips the build step and deploys the existing output tree.

This mode is useful for UI/runtime testing when the generated output already
exists and the developer has changed only files that are already part of that
output tree.

Example command shape:

```powershell
python -m src.products.make_site2 --no-build --local-only
```

Build-shaping options such as history selection, cache mode, and payload mode do
not apply in no-build mode. A command should fail rather than silently ignore
those options.

No-build deployment is distinct from preview serving. It still copies files to
the configured server target.

## 4.3 Preview Server

Preview mode serves the build output directory directly.

Example command:

```powershell
python -m http.server 8787 --directory files\output\make_site2
```

Example URL:

```text
http://127.0.0.1:8787/
```

This is a preview mechanism, not a deployment target.

It is useful when a caller can serve and inspect the generated output directly.

## 4.4 Local / LAN Deployment

Local deployment means copying the generated site to the LAN Apache document
tree used for local browser testing.

In the current development environment, this is the primary deployment target.

Example URL:

```text
http://192.168.0.6/sumo-tools2/
```

The host at `192.168.0.6` is known as `Grond`.

From the development machine, the writable path is expected to be a mapped drive
path such as:

```text
A:\local\htm\sumo-tools2
```

The underlying physical directory on Grond is not important to `make_site2` if
the mapped drive path works.

## 4.5 Remote Deployment

Remote deployment uploads the generated site to the remote public host.

Example URL:

```text
http://68.66.241.105/sumo-tools2/
```

Remote deployment is secondary for now.

It may upload and overwrite files without cleaning stale remote files.

Manual remote purging is acceptable during the current development phase.

A future sync tool may replace or improve remote deployment.

---

# 5. Public Root Names

The successor site uses the public folder / URL fragment:

```text
sumo-tools2
```

The legacy `make_site` site keeps:

```text
sumo-tools
```

This distinction is intentional.

`sumo-tools` remains the legacy site.

`sumo-tools2` is the successor `make_site2` site.

The package name does not define the deployed public root.

---

# 6. DeploymentConfig

Deployment configuration describes deployment targets.

It may contain:

```text
local deploy root
local public URL
remote host
remote root
remote public URL
remote user
credential source
preview port
```

Deployment configuration is operational.

It is not public site structure.

It does not belong in the Site Model.

---

# 7. Credentials

Remote credentials are external configuration.

They should not be source-controlled.

The current remote deployment approach may use an environment variable such as:

```text
GEOLOCATION
```

If the password is not available, remote deployment may prompt the user or fail,
depending on implementation.

Code written for `make_site2` should not assume that an LLM or automation
environment can read the user's local environment variables.

Build-only and local deployment must remain usable without remote credentials.

---

# 8. Local / LAN Deployment Policy

Local / LAN deployment copies the completed `BuildOutput` to the configured
local site root.

The configured target must be the site root itself:

```text
A:\local\htm\sumo-tools2
```

not the parent web root:

```text
A:\local\htm
```

Local deployment cleans the configured `sumo-tools2` target folder before
copying the new build output.

It must not clean the parent document root.

It must not affect the legacy `sumo-tools` folder.

The intended result is that the LAN Apache-served `sumo-tools2` tree reflects
the current build.

---

# 9. Remote Deployment Policy

Remote deployment is a secondary convenience path for now.

It may:

```text
ensure remote directories exist
upload files
overwrite files with the same path
leave stale remote files in place
```

It does not currently need to:

```text
delete stale remote files
mirror the build output exactly
guarantee remote correctness after removed files/routes
```

This is acceptable because the current focus is getting the successor site
working locally.

If the remote site is temporarily wrong because stale files remain, that is
acceptable during this phase.

The remote `sumo-tools2` folder may be purged manually if needed.

A later deployment/sync tool may make the remote target exact.

---

# 10. Clean Deployment Scope

Clean deployment applies to the configured local/LAN site root.

Clean deployment does not mean cleaning an entire web root.

Correct:

```text
clean A:\local\htm\sumo-tools2
```

Incorrect:

```text
clean A:\local\htm
```

Correctness of the configured target path is therefore important.

The deployment design assumes the target is configured as the site root, not its
parent.

---

# 11. DeploymentResult

Deployment may return a conceptual result object.

A DeploymentResult may record:

```text
deployment mode
source BuildOutput root
target root
public URL or local preview URL
file count
start/end time
```

The exact representation is an implementation detail.

The useful purpose is to tell the caller where the deployed or previewed site can
be viewed.

Example:

```text
Local deployment complete:
  http://192.168.0.6/sumo-tools2/
```

---

# 12. Preview Server Result

Preview mode may report:

```text
source build output root
port
preview URL
command used
```

Example:

```text
Serving files/output/make_site2 at:
  http://127.0.0.1:8787/
```

Preview mode is especially useful when deployment targets are unavailable.

---

# 13. Cache-Busting and Deployment

Caching was a significant problem in the predecessor site.

For now, the important supported mode is development cache-busting.

A development build may emit cache-busted asset and data URLs so that local
browser testing sees current files.

Production cache policy is deferred.

Remote deployment does not currently need to solve production cache policy.

---

# 14. Relationship to BuildOutput

Deployment consumes `BuildOutput`.

`BuildOutput` tells deployment:

```text
where the generated site lives
what entry point exists
what files were written
what route pages exist
what build metadata exists
```

Deployment should not reconstruct the build by scanning source definitions.

Deployment should operate on the completed static output tree.

---

# 15. Relationship to Build and Output Design

Build/output creates the static site directory.

Deployment copies, serves, or uploads that directory.

The separation is:

```text
Build/output:
  create the static site

Deployment:
  put the static site somewhere useful
```

Both are package concerns.

They have different ownership.

---

# 16. Relationship to Rendering

Deployment does not know or care how route pages were rendered.

Deployment should not inspect:

```text
UI Model
G1/G2 structure
filters
artifacts
notes
HTML internals
```

Deployment operates on generated files.

---

# 17. Relationship to make_site Evidence

Existing `make_site` deployment is useful evidence.

Known predecessor behavior:

```text
local deployment:
  cleared the local target folder before copying

remote deployment:
  ensured remote directories existed
  uploaded/overwrote files
  did not clear stale remote files
```

`make_site2` keeps the local clean-deploy idea for the configured `sumo-tools2`
target.

`make_site2` may keep the remote upload/overwrite behavior for now.

The successor site uses `sumo-tools2` so that it does not overwrite the legacy
`sumo-tools` deployment.

---

# 18. What Deployment Does Not Own

Deployment does not own:

```text
requirements
site definition
page inclusion policy
route derivation
UI Model structure
artifact model structure
rendering
producer computation
build output generation
cache policy beyond applying configured build outputs
```

If deployment starts deciding what the site means or which pages exist, the
boundary has been crossed.

---

# 19. Deferred Questions

The following questions are deferred:

```text
exact default local deploy path
exact default remote root path
exact SFTP implementation
whether remote upload uses Paramiko, external SFTP, rsync, or another tool
whether remote deployment eventually deletes stale files
whether a future sync tool replaces remote deployment
exact production cache policy
whether preview server is launched by make_site2 or documented as a manual step
```

These should be resolved when they become implementation pressure points.

---

# 20. Summary

Deployment is a first-class `make_site2` capability.

The primary workflow is:

```text
build
  -> local/LAN deploy
  -> view at http://192.168.0.6/sumo-tools2/
```

Preview server workflow is also useful:

```text
build
  -> python -m http.server over files/output/make_site2
  -> view at http://127.0.0.1:8787/
```

Remote deployment is secondary for now:

```text
build
  -> upload/overwrite remote sumo-tools2 files
  -> view at http://68.66.241.105/sumo-tools2/
```

Local deployment cleans only the configured `sumo-tools2` target folder.

Remote deployment may leave stale files for now.

The focus is getting a locally viewable successor site working cleanly.
