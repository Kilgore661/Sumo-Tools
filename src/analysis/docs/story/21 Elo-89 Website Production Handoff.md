# Elo-89 Website Production Handoff

## Status

This document records the transition from model investigation to production
website work. The first `make_site89` implementation and data-production chain
now exist, have been deployed locally, and have passed a broad human sanity
check. Earlier story documents remain the evidential and chronological record.
The implementation record is maintained in
[make_site89 Implementation Plan](../../../products/make_site89/docs/Implementation%20Plan.md).

## Decision

Elo-89 is the selected operational rating model for the sufficiently complete
record from January 1989 onward. The next tranche is to publish that model in a
new post-1988 website built by `make_site89`.

Elo-58 remains a viable and informative historical reconstruction. Its research
is on hold while Elo-89 is taken through production. The project is not waiting
for Elo-58, or for a future model worthy of the reserved Equelo2 name, before
replacing legacy production Equelo on the post-1988 site.

## Why a new site package

The existing `make_site2` both assembles a static site and invokes some of the
analyses which produce its data. It also contains Equelo-specific assumptions
in its data access and presentation. Altering it in place would remove the
working production reference before its replacement had been seen and
accepted.

`make_site2` therefore remains unchanged. `make_site89` is a separate package
with separate output. It consumes produced files rather than running analyses,
and it describes the ratings it publishes as Elo-89.

## Production surface

Seven publication-data tools carry the rating model into the current website:

1. Basho Results;
2. Career Comparisons;
3. Rating Changes;
4. Highest Rating;
5. Banzuke Changes;
6. Typical Rating Values; and
7. Win Probability by Standing.

The first four are invoked during `make_site2`; the final three are produced
separately and copied. The `make_site89` Career Comparisons producer now lives
under `src/analysis`, as does the model-independent Longest Careers derivation,
so the new builder boundary has no exception.

The seven rating-dependent tools consume one production Elo-89 run. Their
outputs, together with newly produced post-1988 model-independent outputs, are
gathered by `src.analysis.site89` into a coherent site-data bundle.
`make_site89` validates, copies and presents that bundle without loading a
History or invoking an analysis.

The generated tree is kept at `files/output/make_site89`. Its local-server
deployment target mirrors `make_site2` but remains separate at
`A:/local/html/sumo-tools89`, served as
`http://192.168.0.6/sumo-tools89/`. The local deployment completed successfully
and most site links were checked for plausible-looking output.

## Relationship to the research story

Documents 14 through 20 record the attempt to extend the selected post-1988
model into a full-history construction, culminating in the distinction between
Elo-89, Elo-58 and the reserved Equelo2 name. That distinction makes the
present production step possible: operational adoption of Elo-89 no longer
depends on adoption of a full-history successor.

This handoff does not reopen the Elo-89 model definition and does not attempt a
general multi-model website. Once `make_site89` has been produced and accepted,
the project may separately ask how difficult it would be to substitute Elo-58
data. Good production boundaries should make that later question easier, but
it is not a requirement of the current work.

## Acceptance boundary

The production chain has been tested and the generated website has passed its
initial human sanity check. `make_site89` remains separate from `make_site2`;
whether it replaces that site, and whether its production subset should be
extracted into a clean package or repository, remain later decisions.
