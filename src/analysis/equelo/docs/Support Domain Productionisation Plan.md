# Support Domain Productionisation Plan

## Status

Historical / deletion candidate after archive.

This handoff plan recorded the transition from the accepted support-domain
feasibility study to the fixed-supported production implementation. The
current normative docs are the fixed-supported requirements, design,
implementation target and regression test design. Preserve this plan only if
needed for archive archaeology.

## Aim

Replace the old fixed-point Equelo v2 path with a production support-domain
Equelo path.

The production path should preserve the existing `make_site2` shape: site
producers should consume canonical rating artifacts and should not know about
experiment directories, temporary paths, or one-off feasibility-study commands.

## Working Conclusions From The Feasibility Study

The old raw fixed-point entrant-rating path can create spurious extreme ratings
for rarely supported low ranks. The visible failure case was the Highest Equelo
table, where low-ranked rikishi could appear with ratings near 3000 despite
short lower-division careers.

The accepted replacement shape is:

1. Select a support domain for chii whose empirical support is strong enough.
2. Run the fixed-point solver over that support domain.
3. Complete the initial-rating table for every chii required by the fixed-v2
   simulation, using nearest supported chii where direct support is absent.
4. Build day-end/process ratings from the completed initial-rating table.
5. Generate downstream public artifacts from those process ratings.

The provisional support threshold accepted for productionisation work is
`min_app=60`. This is accepted as the feasibility-study choice, not as a final
mathematical theorem.

The additive base constant has been adjusted downward by 53 so the Yokozuna
landmark returns to the intended 2500 scale when the new pipeline is rerun.

## Productionisation Sequence

### 1. Write The Waterfall Docs

Write the intended product/design first. These docs should describe the desired
Equelo replacement, not the current code.

They should answer:

- what problem the support-domain replacement solves;
- what counts as supported and unsupported chii;
- how unsupported chii receive initial ratings;
- what artifacts are canonical;
- what invariants the artifacts must satisfy;
- what commands or APIs produce those artifacts;
- what downstream consumers are allowed to depend on;
- what decisions remain policy choices rather than data facts.

### 2. Compare The Experiment To The Docs

After the desired design is documented, compare the existing experiment to that
design.

Record any gaps, including:

- experiment-only names or paths;
- missing metadata;
- unclear APIs;
- hard-coded assumptions that need to become explicit policy;
- output files whose meaning is ambiguous;
- places where downstream code depends on temporary wiring.

### 3. Change The New Code To Match The Docs

Move, rename, wrap, or rewrite the support-domain code so the production API
expresses the documented design.

This may involve keeping some experimental modules for archaeology, but the
production path should not require consumers to import from an `experiments`
package.

### 3a. Regression-Test The Tidied New Code

Before touching app plumbing, regression-test the tidied support-domain path in
isolation.

Minimum checks:

- the completed initial-rating table covers every chii required by the
  fixed-v2 simulation;
- unsupported chii are completed from documented nearest-supported sources;
- no low-rank chii retains a spurious near-3000 initial rating;
- the Highest Equelo output has Hakuho first and only Hakuho above 3000;
- the Typical Equelo landmarks are on the intended scale, with Yokozuna near
  2500 after the base adjustment;
- generated metadata identifies the production source and policy.

### 4. Remove Temporary App Plumbing

Remove the temporary `make_site2` wiring that points directly at experimental
support-domain outputs.

Regression-test the old app path after this removal so any failure is known to
come from removing temporary wiring, not from the later production switch.

### 5. Wire The Definitive Production Path

Connect `make_site2` and its producers to the new production Equelo API or
canonical production artifacts.

At this point, downstream code should not refer to feasibility-study output
directories. It should depend on production names and documented contracts.

### 6. Regression-Test The Final App Path

Run the site/data checks again after definitive plumbing.

The goal is to confirm that public pages consuming Equelo ratings use the new
production artifacts while retaining the existing UI/data-output shape.

### 7. Archive Legacy v2

After the new path is production and tested, move the legacy v2 code to a clear
archive location.

Do this after, not before, final integration testing. The legacy code remains a
useful reference while the replacement is being validated.

## Handoff Notes

The most important sequencing rule is:

> Specify the wanted system first, then test whether the experiment is that
> system, then tidy the code.

Do not let the experiment become production merely because it currently works.
The production boundary should be deliberate, named, documented, and regression
tested before `make_site2` is permanently switched over.

## Current Conformance Notes

The waterfall target is now split across:

- `src/analysis/equelo/docs/Fixed Supported Requirements.md`
- `src/analysis/equelo/docs/Fixed Supported Design.md`

The current implementation is not yet production-shaped. Known gaps:

- The accepted production name is `fixed_supported`, but the working code still
  lives mostly under `experiments/support_domain_fp` and patched `fixed_v2`
  entrypoints.
- The support-domain experiment can produce the accepted `min_app=60` result,
  but the production API for that result does not yet exist.
- The master chii initial-rating map is currently produced by an experimental
  completer with hard-coded latest-sweep lookup and experiment output paths.
- The completed map still uses legacy file names such as
  `entrant_initial_ratings.csv`, which can obscure that the artifact is keyed by
  chii rather than rikishi.
- Metadata exists, but it does not yet fully express the production support
  rule, support collapse policy, completion rule, tie-break rule, and base
  convention as a stable contract.
- `fixed_v2` has temporary hooks to accept a completed initial-rating CSV.
  Those hooks proved feasibility, but they are not the final production
  boundary.
- `make_site2` contains temporary wiring to experiment outputs. That must be
  removed before final production wiring.
- Regression checks need to be written around the production API, not around
  manually chosen experiment folders.

The next implementation task is to create the `fixed_supported` production
boundary and move only the conforming pieces of the experiment behind it.

Implementation should be guided by:

- `src/analysis/equelo/docs/Fixed Supported Implementation Target.md`
- `src/analysis/equelo/docs/Fixed Supported Regression Test Design.md`
