# Temporary Note: Historical Scope and `site89` Production

## Purpose

This note preserves an architectural issue discovered while scoping the
fastest/slowest progression producer. It is stored here temporarily so that the
analysis work can continue without expanding into a redesign of the website
production chain.

It is not part of the progression calculation and does not propose an immediate
implementation.

## Observed production arrangements

`make_site2` has a mixed build model. The repository-root `_boot.ps1` is the
effective from-scratch production sequence when cached downloads are already
available. It:

1. creates the canonical History;
2. starts or relies on the live store;
3. invokes a series of independent producers; and
4. finally runs `src.products.make_site2`, which generates some remaining data
   and copies the prepared artifacts into the site.

Historical producers such as First Chii Appearance normally use the full
History beginning in 1958. `make_site2` copies their prepared outputs rather
than forcing them to share the History used by a rating calculation.

`src.products.make_site89`, by contrast, is deliberately only a site
assembler. It loads no History and performs no analysis. It validates and
copies a prepared site-data bundle and adds the presentation shell and runtime.

The relevant restriction is upstream in `src.analysis.site89`. That bundle
producer currently accepts a single History beginning at `1989/01`, runs the
Elo-89 replay, and passes the same truncated History to its model-independent
publication producers.

## Consequence

The single-History design applies the Elo-89 evidence boundary to artifacts
that do not use ratings.

The deployed First Chii Appearance artifact demonstrates the problem. Its
served data contains no observation before 1989 and assigns `1989/01` as the
first appearance of hundreds of ordinary ranks already present at that
boundary. Its chart nevertheless draws an axis from 1958, making the truncation
easy to miss.

Other non-rating artifacts require the same scope audit. For example, a
six-basho running average of wins has no Elo dependency and should not acquire
a `1989/01` boundary merely because it is published on the Elo-89 site. A
producer may still need its own boundary because of source-data completeness,
but that is a producer-specific decision rather than a site-wide rating rule.

## Intended separation

The intended conceptual pipeline is:

```text
complete History (supporting boundary 1958/01; analysis from 1958/03)
    -> model-independent historical producers

post-1988 History (1989/01 onward)
    -> Elo-89 replay
    -> rating-dependent producers

declared outputs from both branches
    -> site-data bundle
    -> make_site89 assembler
```

The bundle ultimately needs to preserve producer- or artifact-specific source
provenance instead of presenting one global History range as applicable to
every artifact.

## Deferred architectural decision for `fastest`

Do not solve the site-production architecture as part of the progression
artifact. For the first `make_site89` version, prefer consistency with its
current post-1988 artifact set over complete historical scope.

The `fastest` package will:

- expose an explicit command-line epoch, defaulting to `1989/01`;
- use that epoch banzuke only to exclude left-boundary incumbents;
- admit career starts from `1989/03` onward under the default;
- produce self-contained, inspectable analytical outputs; and
- remain independent of `src.analysis.site89` and
  `src.products.make_site89`.

The analytically preferable `1958/01` epoch remains supported as a CLI choice,
but is deferred for website publication. A later production-architecture repair
can select it without changing the progression calculation or UI contract.

## Additional bootstrap issue confirmed during implementation

The Fastest Risers site build exposed a second consequence of the same
experimental production arrangement. The selected History contained seven
new rikishi whose raw and parsed biographies had not yet been refreshed.
`FullShikonaStore.from_sources()` therefore stopped an existing model-independent
producer with `KeyError: 13006` before the complete site89 bundle could be
created.

The repository already has both stages needed to repair the prerequisite:

```text
src.infra.get_bios
    -> missing raw Rikishi.aspx pages

src.infra.get_bios.parser
    -> files/output/infra/get_bios/rikishi_bios.json
```

Running those stages brought the bio store into closure with History and the
complete site89 bundle then built successfully. This confirms that the problem
is not a missing analytical producer. It is the absence of a product-level
site89 bootstrap which orders and validates all required producers.

`make_site2` acquired such an entry point in repository-root `_boot.ps1` when
it was treated as the distributable product. `make_site89` began as an
experiment, so `src.analysis.site89` was allowed to assume that established
inputs such as History and parsed bios had already been refreshed by hand.
Now that `make_site89` is the deliverable, it needs its own equivalent outer
orchestration while preserving the existing boundary that the
`src.products.make_site89` package itself is only an assembler.

The intended eventual layering is therefore:

```text
site89 bootstrap
    -> obtain or select coherent source data
    -> build the required History branches
    -> refresh and validate bio coverage
    -> run site89 analytical producers
    -> create and validate the site-data bundle
    -> invoke the make_site89 assembler
    -> optionally deploy
```

Cached/offline development and explicit refresh modes are an operational
requirement of that future bootstrap. The Fastest Risers implementation does
not attempt this repair; the bio stages were run manually to verify and build
the artifact.
