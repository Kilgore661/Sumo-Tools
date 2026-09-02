# make_site89 Implementation Plan

## Status

This is the current implementation plan for replacing the production site's
Equelo-dependent path with a new post-1988 site built from Elo-89. It records
the agreed work, not a proposal to revisit the selected model.

## Objective

Build `make_site89` as a site assembler for the post-1988 record. A separate
production chain will run the required analyses and give `make_site89` a
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
  before it can replace `make_site2`.

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

The existing exact replay is currently arranged for evaluation rather than
production. It will be given a production publisher which exposes the rating
observations required by the website, including complete daily population
snapshots as well as its bout and basho-boundary results. This is an output
change, not a change to the model.

The run output will preserve the P1 input and record the inputs and policies
used sufficiently clearly for the run to be reproduced and understood.

## Publication-data producers

Seven site-facing producers currently depend directly or indirectly on the old
production Equelo model. Each will be changed to consume the Elo-89 production
output explicitly rather than load fixed-supported Equelo from a global
default location.

| Publication tool | Present relationship to `make_site2` | make_site89 work |
|---|---|---|
| Basho Results | Invoked during the site build | Make independently runnable and consume Elo-89 ratings |
| Career Comparisons | Implemented under and invoked by the site package | Move production code under `src/analysis` and consume Elo-89 ratings |
| Rating Changes | Invoked during the site build | Make independently runnable and consume the Elo-89 rating and bout outputs |
| Highest Rating | Highest Equelo producer is invoked during the site build | Produce the Elo-89 record independently |
| Banzuke Changes | Produced separately and copied | Replace its fixed-supported Equelo input with Elo-89 |
| Typical Rating Values | Produced separately and copied | Produce the corresponding Elo-89 values |
| Win Probability by Standing | Produced separately and copied | Replace its fixed-supported prior and scale inputs with Elo-89 |

The model-independent Longest Careers view is also currently derived during a
site build. Its derivation will move upstream so that the new assembler has no
exception to its produced-files-only rule. Other model-independent producers
need no analytical migration; their existing outputs will be collected with
the new rating-dependent outputs.

## Site-data bundle

Production orchestration will:

1. obtain the post-1988 History and established basic inputs;
2. run the Elo-89 producer once;
3. run the seven rating-dependent publication producers against that output;
4. run or collect the required model-independent publication outputs; and
5. gather the complete result into one site-data bundle.

The bundle will identify Elo-89, the represented History and the files it
contains. It exists to give the assembler one coherent input and to prevent it
from reaching into a collection of unrelated producer output directories.

## make_site89 package

The new package will be `src/products/make_site89`, with generated output under
`files/output/make_site89`.

It will begin from a private fork of the necessary `make_site2` presentation
code. Deliberate duplication protects the existing site from changes made
during the migration. `make_site89` will not import `make_site2`.

`make_site89` will:

- accept an explicit site-data bundle;
- verify that its required produced files are present;
- copy those files into the static-site tree;
- generate the site shell and copy its presentation assets and prose;
- describe rating data as Elo-89; and
- perform no History loading, rating calculation or other analysis.

The new presentation will remove Equelo-specific names from rating fields,
tables, charts, filters, links, notes and prose where they describe the model
being published. The site remains limited to the post-1988 period supported by
Elo-89.

## Implementation sequence

1. Add the Elo-89 production publisher and verify it against the retained exact
   implementation.
2. Move Career Comparisons production and the Longest Careers derivation to
   appropriate locations under `src/analysis`.
3. Adapt Basho Results, Career Comparisons, Rating Changes and Highest Rating,
   the four rating-dependent products currently generated during a site build.
4. Adapt Banzuke Changes, Typical Rating Values and Win Probability by
   Standing, the three rating-dependent products already generated separately.
5. Add orchestration which produces the complete site-data bundle.
6. Create the isolated, produced-files-only `make_site89` package.
7. Update the forked presentation to use Elo-89 data and terminology.
8. Run model, producer, integration and browser checks, then build the site for
   human visual acceptance.

## Verification

Verification will establish that:

- the production Elo-89 replay agrees with the accepted exact replay;
- its established population and rating-update behaviour is unchanged;
- all seven producers consume the same Elo-89 run and post-1988 History;
- none of them retains a fixed-supported Equelo dependency;
- the site-data bundle is complete;
- `make_site89` invokes no producer and loads no History;
- `make_site2` remains unaffected;
- every site page and data source loads; and
- navigation, tables, charts, filters and URL state behave correctly.

The final acceptance step is inspection of the generated site by the Mark I
Human Eyeball. Until that has happened, `make_site89` is a candidate and does
not replace the existing production site.

## Future extraction record

As work proceeds, this document and its supporting inventory will record the
actual inputs, outputs and transitive production dependencies of the seven
publication tools. This creates a positive list of what a future clean package
or repository would require without attempting that extraction during the
migration.

After `make_site89` has been accepted, a separate investigation may ask what
would be required to substitute Elo-58 for Elo-89. That question does not
affect this plan.
