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

## Temporary decision for `fastest`

Do not solve the site-production architecture as part of the progression data
producer.

The `fastest` package will:

- use complete banzuke History;
- use `1958/01` only to exclude left-boundary incumbents;
- admit career starts from `1958/03` onward;
- produce self-contained, inspectable analytical outputs; and
- remain independent of `src.analysis.site89` and
  `src.products.make_site89`.

After the producer contract is settled, a separate artifact-design document
will determine the required publication payload. The broader production issue
can then be repaired before the artifact is integrated into `make_site89`.

