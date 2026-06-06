# 2026-05 Duplicate Chii Containment Plan

## Status

This note records the agreed state immediately before temporary BCR tolerance
work for the `2026/05` duplicate-chii anomaly.

The issue is not treated here as part of public shikona disambiguation. Public
shikona display is keyed by `RikId`. The anomaly concerns source data, parser
recovery, and the Sumo-Tools internal `Chii` model.

## Observed Facts

Live-store History currently reports both:

- `RikId(13003)` as `Ms60eTD` in `2026/05`;
- `RikId(13004)` as `Ms60eTD` in `2026/05`.

During BCR source loading, parser recovery logs the corresponding rank as
`Ms60TD`.

Fresh BCR generation for `2026/05` now gets past Equelo rating lookup, but then
fails in the two-column row builder because it assumes at most one east rikishi
and one west rikishi for each displayed banzuke row:

```text
ValueError: Duplicate east rikishi for Ms60TD
```

The existing checked/generated BCR output still allows the site to build because
it predates this regeneration attempt.

## Downstream Symptoms

Observed downstream behaviour is not uniform:

- 2.1 Banzuke Changes does not show either `RikId(13003)` or `RikId(13004)` in
  the current generated banzuke-style or scan-style table.
- 3.3 Career Comparisons can select Omori (`RikId(13003)`) with Equelo ratings
  enabled without raising an error, although the visible chart trace is empty.
  That may be a one-point trace/rendering issue rather than a duplicate-chii
  issue.
- 7.1 Basho Results shows both rikishi as `Ms60eTD` with ratings.

These symptoms are evidence for the parser/chii investigation, but they are not
to be solved as part of the immediate shikona-disambiguation work unless they
block publication.

## Open Modelling Questions

The unresolved questions are:

1. Is `Ms60TD` a real sumo/source-data case, or an artefact of SumoDB markup or
   parser recovery?
2. If `Ms60TD` is real, which module owns projecting it into the Sumo-Tools
   `Chii` model?
3. Is `Ms60eTD` the correct internal representation, or is the assignment of an
   east side an artefact introduced by parser recovery?
4. Have comparable cases occurred before `2026/05`?
5. If comparable cases occurred before `2026/05`, did the parser handle them
   successfully, and what representation did it produce?
6. If no comparable case occurred before, is this the first genuinely duplicate
   represented chii in the data, or the result of a recent SumoDB HTML-format
   change?

## Containment Plan

The goal is to continue the public-shikona rollout without pretending the
duplicate-chii model has been solved.

The agreed sequence is:

1. Commit the clean BCR public-shikona and Equelo entrant-domain change.
2. Commit this reasoning note together with an in-repository backup of the
   current generated `files/output/bcr` output under
   `src/analysis/banzuke_compare/fixtures/bcr_before_2026_05_duplicate_chii_tolerance`.
3. Make the least invasive temporary BCR tolerance change that lets BCR
   regenerate while preserving the existing CSV/config shape if possible.
4. Rebuild BCR for `2026/05`.
5. Rebuild `make_site2` and inspect whether the public-shikona change can be
   validated in 2.1.

## Stop Condition

Stop the temporary path and solve the parser/chii problem properly if the BCR
tolerance change requires any of the following:

- changing the BCR CSV schema;
- changing the BCR standalone browser renderer;
- changing the make_site2 Banzuke Changes renderer;
- inventing a general display policy for duplicate or side-free TD ranks;
- making assumptions about whether `Ms60TD` is a real rank rather than a parser
  artefact.

If those become necessary, the anomaly is no longer a small publication
continuation hack. It is a parser/source-data/chii-model task.
