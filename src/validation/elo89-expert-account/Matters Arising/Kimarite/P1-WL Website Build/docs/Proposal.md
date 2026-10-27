# Proposal: build and inspect a workspace-local P1-WL website

## 1. Question

Can the accepted P1-WL candidate bundle be assembled into the actual
`make_site89` web site, served from a location visible to both the user and
Codex, without touching the production web root on `A:`?

The purpose is not another model comparison. It is to expose the propagated
P1-WL results through the real public runtime and find presentation,
interaction or integration problems which bundle-level CSV comparison cannot
show.

## 2. Constraint and proposed solution

The normal local deployment copies the generated site to:

```text
A:/local/html/sumo-tools89
```

That mapped shared drive is available to the user's production environment
but not to Codex. It is therefore unsuitable as the validation boundary.

`make_site89` already separates assembly from deployment. Its `--build-only`
mode accepts an explicit data bundle and output directory. The candidate can
therefore be built beneath this validation work package and served directly
with Python's static HTTP server:

```text
workspace candidate bundle
    -> normal make_site89 build_site
    -> timestamped validation output/site tree
    -> python -m http.server on port 8766
    -> http://localhost:8766/
```

Both parties operate on the same machine and workspace, so this URL provides
the shared inspection surface which the inaccessible `A:` mapping cannot.

## 3. Input contract

The first run must use the candidate bundle from:

```text
src/validation/elo89-expert-account/Matters Arising/Kimarite/
  P1-WL Site Bundle Comparison/output/
  site-bundle-comparison-2026-10-27-run3/candidate
```

Before building, verify:

1. the bundle passes `load_site_data_bundle` validation;
2. its History is `1989/01` through `2026/09`;
3. its rating-run manifest identifies prior SHA-256
   `6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486`;
4. its derived copied prior has the recorded paired-rank row count, unique
   rank-pair keys and valid ordinal/rating fields;
5. the bundle manifest, rating-run manifest and derived copied-prior hashes are
   recorded; and
6. the source is the candidate, not the P1 baseline or the ordinary default
   bundle.

These checks make the preview evidence about P1-WL rather than merely about a
directory believed to contain it.

The accepted source and the copied prior are different representations. The
accepted P1-WL source contains literal chii rows with support; Elo-89 loads it
into paired-rank values and writes a smaller `rank_pair,ordinal,rating` table
into the rating run. Their byte hashes must not be equated. The source identity
is checked against the accepted hash, while the transformed copy receives its
own recorded hash and structural validation.

## 4. Build arrangement

Add a Kimarite-owned validation entry point at
`src.validation.kimarite.p1_wl_website` rather than changing or copying the
product assembler. The validation package owns input selection, provenance,
output and inspection evidence. It uses the unchanged
`src.products.make_site89.build.build_site` function as a dependency so that
the experiment exercises the real product assembly rather than a fork. It
should:

1. require or default to the explicit accepted candidate bundle;
2. create a new timestamped run beneath this work package's `output/`;
3. refuse to overwrite an existing run;
4. invoke `src.products.make_site89.build.build_site` directly;
5. use development cache-busting for the interactive inspection build;
6. write the assembled files beneath `<run>/site/`;
7. record a root manifest with all input identities, build time, output file
   count, entrypoint and an output-tree fingerprint; and
8. print the exact command needed to serve the result.

The initial implementation should not start or manage a background server.
Static serving has its own lifetime: ordinary `Ctrl-C` termination is enough,
and the build must remain intact after the server stops.

The underlying equivalent product command is:

```powershell
py -m src.products.make_site89 `
  --data-bundle "<accepted-run>\candidate" `
  --output "<validation-run>\site" `
  --build-only
```

The validation wrapper exists for provenance, fixed-input checks and
timestamped retention, not to duplicate `make_site89`.

## 5. Shared preview

After a successful build, serve the generated `site` directory from the
repository root:

```powershell
py -m http.server 8766 --directory "<validation-run>\site"
```

The shared URL is:

```text
http://localhost:8766/
```

The server process must remain running during inspection. If port 8766 is
already serving the correct directory, refresh that preview rather than start
another process. If it is occupied by an unrelated service, identify that
fact before choosing and recording a different port.

The site must be served over HTTP. Opening `index.html` through a `file:` URL
is not an adequate test because module imports and data fetches can behave
differently.

## 6. Inspection plan

### 6.1 Build and runtime integrity

Confirm:

- the shell and default page load;
- navigation resolves every declared page;
- no browser console errors or failed data requests occur;
- the served bundle metadata matches the source candidate;
- JavaScript modules, CSS, prose and static assets load over HTTP; and
- refreshes and query-string page links work from the shared preview URL.

Use automated browser checks where useful, but retain a human-readable
inspection record. Passing Python tests or JavaScript syntax checks is not a
substitute for loading the site.

### 6.2 Rating-dependent pages

Inspect every page identified by the bundle comparison as a P1-WL consumer:

- Typical Elo-89 ratings;
- win probability by standing;
- current or future torikumi;
- Banzuke Changes;
- Basho Results;
- Career Comparisons;
- Rating Changes; and
- Highest Ratings.

For each, check headings, explanatory text, filters, sorting, chart scales,
tooltips, table formatting, empty states, links and responsive behaviour.

### 6.3 Numerical spot checks

Trace selected visible values back to the candidate bundle, including:

- Hakuho's 3070.311 career peak before display rounding;
- at least one early large sekitori change near the 1989 initialization;
- a current-era sekitori value;
- a lower-division case with a large ordering movement;
- one career peak whose selected chii crosses a division boundary; and
- representative prior-derived typical-rating values.

The aim is not to reproduce the complete CSV comparison in the browser. It is
to prove that the UI reads, rounds, labels and orders the candidate data as
intended.

### 6.4 Chii watch point

The preceding tranche found 43 cases where the historical observation chosen
as a rikishi's career peak moved across a division boundary. Raw
`chii_ordinal` subtraction usefully identified these cases but did not provide
a principled distance measure.

During website inspection, look for a concrete presentation or interpretation
problem arising from those changed peak ranks. Do not begin a general chii
metric investigation unless the site reveals such a problem. If it does, open
a separate bounded analysis based on division, rank number, side and special
rank status rather than arithmetic on the encoded ordinal.

## 7. Acceptance criteria

This tranche passes when:

1. the retained manifest proves that the site was built from the accepted
   P1-WL candidate bundle;
2. the normal `make_site89` assembler completes without deployment;
3. both user and Codex can load the same site through the shared HTTP preview;
4. automated browser inspection finds no unexplained console or network
   errors;
5. affected pages render and behave correctly under focused human inspection;
6. sampled displayed values trace to candidate bundle values; and
7. all findings and any deferrals are recorded.

A defect may be in the candidate data, the product assembly, the browser
runtime or the prose. Record that boundary before fixing it.

## 8. Retained outputs

Each run should retain beneath this work package:

```text
output/<timestamped-run>/
  manifest.json
  site/
  inspection/
```

`inspection/` should contain the final checklist or findings and any compact
machine-readable browser report. Screenshots should be retained only when they
demonstrate an issue or materially support a decision.

Validation output in this package is evidence and should not be silently
discarded. If the complete generated site is judged too large for repository
retention, make that an explicit documented decision while preserving its
manifest, tree fingerprint, exact reproduction command and inspection record.

## 9. Non-goals

This tranche will not:

- deploy to `A:` or any remote host;
- alter the deployment configuration;
- change P1-WL, epsilon or Elo-89 replay policy;
- promote P1-WL to the canonical prior merely because the preview works;
- redo the complete bundle comparison;
- design a general chii-distance measure without a downstream problem; or
- revise the public Elo-89 narrative beyond defects discovered during the
  inspection.

## 10. Decision after inspection

If the preview passes, the evidence will support a separate production change
which installs P1-WL as the canonical fixed prior and regenerates the ordinary
production bundle and site. Deployment would still require explicit approval.

If it fails, retain the preview and identify whether the correction belongs in
the analytical bundle, product assembler/runtime, or documentation. Rebuild a
new timestamped validation run after the bounded fix; do not overwrite the
failed evidence.
