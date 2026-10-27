# P1-WL website build

## Status

Completed. The P1-WL website was generated, served through the shared preview
and inspected by the user without any obvious problem. The retained result and
final decision are recorded in [`Findings.md`](Findings.md).

The controlled site-bundle comparison accepted P1-WL for progression to an
assembled, non-deployed web site. This folder will retain that build, its
provenance and the inspection record.

The detailed plan is in [`docs/Proposal.md`](docs/Proposal.md).

The Kimarite-owned entry point is
`src.validation.kimarite.p1_wl_website`. It verifies the retained P1-WL input,
uses the unchanged `make_site89` assembler as a dependency, and writes only
beneath this work package. It does not invoke deployment code.

## Purpose

Build the real `make_site89` static site from the accepted P1-WL candidate
bundle without using the production deployment target on `A:`. Serve the
workspace-local output over the standard shared preview URL:

```text
http://localhost:8766/
```

This gives the user and Codex the same working site to inspect. It is a local
validation preview, not a deployment.

## Fixed input

The initial build will consume the candidate bundle retained by the accepted
comparison run:

```text
../P1-WL Site Bundle Comparison/
  output/site-bundle-comparison-2026-10-27-run3/candidate
```

That bundle was produced from P1-WL prior SHA-256
`6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486`
and the selected post-1988 History fingerprint
`46d10d006d394a146a4f0d54491741905248d3ef643ee74d05f5ee2f6543806a`.

The website build must verify those identities before assembly rather than
merely trusting the directory name.

## Boundaries

This tranche may:

- call the normal `make_site89` builder with the explicit candidate bundle;
- write a timestamped site and build manifest beneath this folder's `output/`;
- serve that output from the repository workspace on port 8766; and
- inspect the site in both automated and human browsers.

It must not:

- copy anything to `A:` or invoke a configured deployment target;
- replace the canonical P1 prior;
- overwrite the ordinary `files/output/make_site89` build;
- publish to a remote host; or
- treat a successful build as approval to deploy.

## Expected result

The tranche ends with a reproducible working P1-WL site, a shared preview URL,
and a written inspection decision. Any promotion to the production prior and
production site remains a separate explicit action.

## Build command

From the repository root:

```powershell
py -m src.validation.kimarite.p1_wl_website
```

The default selects the accepted run3 candidate bundle and creates a
timestamped directory beneath `P1-WL Website Build/output/`. An explicit new
run directory can be supplied with `--output PATH`. The command refuses to
overwrite an existing run.

On success it prints the exact `py -m http.server` command for the generated
site and the shared preview URL. Run that server command separately so its
lifetime remains under ordinary console control.

## Adopted run

The completed build is retained at:

```text
output/p1-wl-website-2026-10-27_12-06-00
```

It contains a 394-file website and a provenance manifest binding it to the
accepted P1-WL input. The output-tree SHA-256 is
`042e8929133a1f5667fc592f123eaaab31122ede136642fe210705c17854dcba`.
Deployment was not invoked.
