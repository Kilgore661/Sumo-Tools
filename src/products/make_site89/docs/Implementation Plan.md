# make_site89 Implementation Plan

## Status

The first implementation is complete. It has been deployed to the separate
local-server path, and a broad human sanity check of its links and displayed
results passed.
This document now records both the agreed plan and the production contract
which resulted from it; it is not a proposal to revisit the selected model.

## Objective

Build `make_site89` as a site assembler for the post-1988 record. A separate
production chain runs the required analyses and gives `make_site89` a
complete set of produced files. `make_site89` will validate, copy and present
those files; it will not run analyses or construct ratings.

The existing `make_site2` remains unchanged as the current production site and
as a behavioural and visual reference during the migration.

## Scope

- Elo-89 is the only rating model in scope.
- The represented History begins in January 1989.
- Work remains in the existing repository.
- New and adapted producers remain under `src/analysis`, following the
  repository's present convention for analysis which is good enough to use.
- `make_site89` has its own package and output tree.
- The resulting site must pass automated checks and human visual inspection
  before any decision to replace `make_site2`.

The following are not part of this implementation:

- changing or generalising `make_site2`;
- adding Elo-58;
- supporting model selection or simultaneous models;
- reorganising the existing `src/analysis` tree; or
- extracting the production system into a separate repository.

## Production boundary

The intended flow is:

```text
post-1988 History + established basic inputs
                    |
                    v
             Elo-89 producer
                    |
                    v
       seven publication-data producers
                    |
                    v
          complete site-data bundle
                    |
                    v
              make_site89
                    |
                    v
             static website tree
```

The production orchestration may invoke analyses. `make_site89` may not. Its
input is a coherent collection of already-produced, site-facing files.

## Elo-89 production output

The accepted Elo-89 definition is retained: canonical P1 entrant ratings,
`q = 400`, the selected divisional-k schedule, the canonical post-1988 binary
bout domain, and common whole-population mean restoration at the start and end
of each basho.

The production publisher is `src.analysis.elo89`. It exposes entrant priors,
basho-start ratings, raw day-end ratings, normalised basho-end ratings, a bout
ledger and basho-boundary adjustments. This is an output layer around the
accepted model, not a change to the model.

The run output preserves the P1 input and records the inputs and policies
used sufficiently clearly for the run to be reproduced and understood.

## Publication-data producers

Seven site-facing producers depended directly or indirectly on the old
production Equelo model. Their `make_site89` versions now consume the Elo-89
production output explicitly rather than load fixed-supported Equelo from a
global default location.

| Publication tool | Relationship to `make_site2` | Implemented make_site89 producer |
|---|---|---|
| Basho Results | Invoked during the site build | `src.analysis.site89.basho_results` |
| Career Comparisons | Implemented under and invoked by the site package | `src.analysis.site89.career_comparisons` |
| Rating Changes | Invoked during the site build | `src.analysis.site89.rating_changes` |
| Highest Rating | Highest Equelo producer is invoked during the site build | `src.analysis.site89.highest_rating` |
| Banzuke Changes | Produced separately and copied | `src.analysis.site89.banzuke_changes` |
| Typical Rating Values | Produced separately and copied | `src.analysis.site89.typical_rating_values` |
| Win Probability by Standing | Produced separately and copied | `src.analysis.site89.win_probability` |

The model-independent Longest Careers derivation also moved upstream. The
remaining model-independent site outputs are reproduced from the selected
post-1988 History by `src.analysis.site89.model_independent`; standings are
produced by `src.analysis.site89.standings`.

## Site-data bundle

`python -m src.analysis.site89` performs the production orchestration. It:

1. obtains the post-1988 History and established basic inputs;
2. runs the Elo-89 producer once;
3. runs the seven rating-dependent publication producers against that output;
4. runs the required model-independent publication producers; and
5. gathers the complete result into one site-data bundle.

The bundle identifies Elo-89, the represented History and the files it
contains. It exists to give the assembler one coherent input and to prevent it
from reaching into a collection of unrelated producer output directories.

## make_site89 package

The new package is `src/products/make_site89`, with generated output under
`files/output/make_site89`.

It began from a private fork of the necessary `make_site2` presentation code.
Deliberate duplication protects the existing site from changes made during the
migration. `make_site89` does not import `make_site2`.

`make_site89`:

- accepts an explicit site-data bundle;
- verifies that its required produced files are present;
- copies those files into the static-site tree;
- generates the site shell and copies its presentation assets and prose;
- describes rating data as Elo-89; and
- performs no History loading, rating calculation or other analysis.

The new presentation removes Equelo-specific names from rating fields,
tables, charts, filters, links, notes and prose where they describe the model
being published. The site remains limited to the post-1988 period supported by
Elo-89.

## Implemented production sequence

The normal live-store-first entry point is:

```powershell
.\_boot89.ps1
```

It refreshes the structural Banzuke Changes input, produces the coherent
site-data bundle from the live History selected from `1989/01`, assembles the
site, and deploys it to the configured local target. It forwards the existing
`make_site89` flags unchanged; `--build-only` supports restricted test
environments and `--no-build` deploys the existing generated tree without
rerunning production.

1. `src.analysis.site89` loads the post-1988 History and runs
   `src.analysis.elo89` once.
2. The seven rating-dependent producers consume that run explicitly.
3. The post-1988 model-independent producers, including Longest Careers, run
   upstream of the site builder.
4. The orchestrator writes and validates the coherent bundle at
   `files/output/analysis/site89_bundle`.
5. `src.products.make_site89` validates and copies the bundle, then adds only
   its presentation shell, runtime and prose.
6. The generated HTTP-served static tree is written to
   `files/output/make_site89`.
7. Unless `--build-only` is supplied, that tree is copied to the configured
   local Apache directory `A:/local/html/sumo-tools89`. `--local-only` has the
   same target-selection meaning as in `make_site2`; `--no-build` deploys an
   existing generated tree. The target is configured in
   `distro/make_site89_targets.json`.

The site must be viewed through HTTP. Opening `index.html` through `file://`
shows the shell but prevents the fetch-based pages from loading their produced
JSON and CSV data.

## Verification

Automated verification establishes that:

- the production Elo-89 replay agrees with the accepted exact replay;
- its established population and rating-update behaviour is unchanged;
- all seven producers consume the same Elo-89 run and post-1988 History;
- none of them retains a fixed-supported Equelo dependency;
- the site-data bundle is complete;
- `make_site89` invokes no producer and loads no History;
- `make_site2` remains unaffected;
- the tested site pages and data sources load over HTTP; and
- navigation, tables, charts, filters and URL state behave correctly.

The Mark I Human Eyeball sanity check passed after local deployment: most links
were exercised and produced reasonable-looking results. This establishes the
requested production sanity gate; it does not itself replace the existing
production site.

## Future extraction record

This document and its supporting inventory record the actual inputs, outputs
and transitive production dependencies of the seven publication tools. This
creates a positive list of what a future clean package
or repository would require without attempting that extraction during the
migration.

After `make_site89` has been accepted, a separate investigation may ask what
would be required to substitute Elo-58 for Elo-89. That question does not
affect this plan.
