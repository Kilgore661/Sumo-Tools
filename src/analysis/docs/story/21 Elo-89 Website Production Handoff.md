# Elo-89 Website Production Handoff

## Status

This document records the transition from model investigation to production
website work. Earlier story documents remain the evidential and chronological
record. The detailed implementation plan is maintained with the new product in
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

`make_site2` will therefore remain unchanged. `make_site89` will be built as a
separate package with separate output. It will consume produced files rather
than run analyses, and it will describe the ratings it publishes as Elo-89.

## Production surface

Seven publication-data tools carry the rating model into the current website:

1. Basho Results;
2. Career Comparisons;
3. Rating Changes;
4. Highest Rating;
5. Banzuke Changes;
6. Typical Rating Values; and
7. Win Probability by Standing.

The first four are currently invoked during `make_site2`; the final three are
produced separately and copied. Career Comparisons production is currently
located inside the site package and will move under `src/analysis`. The
model-independent Longest Careers derivation will also move out of the site
builder so that the new boundary has no exception.

The seven rating-dependent tools will consume one production Elo-89 run. Their
outputs, together with the existing model-independent outputs, will be gathered
into a coherent site-data bundle. `make_site89` will validate, copy and present
that bundle.

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

`make_site89` remains a candidate until its production chain has been tested
and the generated website has passed human visual inspection. Only then will
the project decide whether it replaces `make_site2` and whether the accepted
production subset should be extracted into a clean package or repository.
