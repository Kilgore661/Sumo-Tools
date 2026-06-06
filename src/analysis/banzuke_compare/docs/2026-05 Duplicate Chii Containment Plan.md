# 2026-05 Duplicate Chii Containment Plan

## Status

This note records the agreed state immediately before temporary BCR tolerance
work for the `2026/05` duplicate-chii anomaly.

The issue is not treated here as part of public shikona disambiguation. Public
shikona display is keyed by `RikId`. The anomaly concerns JSA/SumoDB source
data, parser recovery, and the Sumo-Tools internal `Chii` model.

## Observed Facts

Live-store History currently reports both:

- `RikId(13003)` as `Ms60eTD` in `2026/05`;
- `RikId(13004)` as `Ms60eTD` in `2026/05`.

During BCR source loading, parser recovery logs the corresponding rank as
`Ms60TD`.

Fresh BCR generation for `2026/05` now gets past Equelo rating lookup. Before
the temporary tolerance change, it failed in the two-column row builder because
the row builder assumes at most one east rikishi and one west rikishi for each
displayed banzuke row:

```text
ValueError: Duplicate east rikishi for Ms60TD
```

The temporary tolerance change now warns and continues by preserving the
existing output shape and allowing the later duplicate side value to overwrite
the earlier one.

## Downstream Symptoms

Observed downstream behaviour is not uniform:

- Before regenerating BCR, 2.1 Banzuke Changes did not show either
  `RikId(13003)` or `RikId(13004)` in the then-current generated banzuke-style
  or scan-style table.
- After the temporary BCR tolerance and regeneration, 2.1 Banzuke Changes shows
  the surviving overwritten row. This is sufficient for continuing the
  public-shikona rollout, but it is not a proper duplicate-chii solution.
- 3.3 Career Comparisons can select Omori (`RikId(13003)`) with Equelo ratings
  enabled without raising an error, although the visible chart trace is empty.
  That may be a one-point trace/rendering issue rather than a duplicate-chii
  issue.
- 7.1 Basho Results shows both rikishi as `Ms60eTD` with ratings.

These symptoms are evidence for the JSA/SumoDB/parser/chii investigation, but
they are not to be solved as part of the immediate shikona-disambiguation work
unless they block publication.

## Deliberate Non-Decision

SumoDB appears to display `Ms60TD` after `Ms60w`, as if the exceptional rank is
outside the ordinary east/west pair while still being attached to the Makushita
60 boundary. The current Sumo-Tools `Chii` model does not represent a side-free
`Ms60TD`; parser recovery currently represents the case as `Ms60eTD`.

That internal representation can produce arguable ordering, for example placing
`Ms60eTD` before `Ms60w` where SumoDB displays `Ms60TD` after `Ms60w`.

We are deliberately not changing `Chii` ordering, broadening `Chii` to represent
side-free TD ranks, or inventing a general duplicate-rank display policy in this
work. This remains a rare JSA/SumoDB/source-data modelling issue, not part of
the public-shikona rollout.

## Open Modelling Questions

The unresolved questions are:

1. Is `Ms60TD` a real JSA/sumo/source-data case, or an artefact of SumoDB markup
   or parser recovery?
2. If `Ms60TD` is real, which module owns projecting it into the Sumo-Tools
   `Chii` model?
3. Is `Ms60eTD` the correct internal representation, or is the assignment of an
   east side an artefact introduced by parser recovery?
4. Have comparable cases occurred before `2026/05`?
5. If comparable cases occurred before `2026/05`, did the parser handle them
   successfully, and what representation did it produce?
6. If no comparable case occurred before, is this the first genuinely duplicate
   represented chii in the data, a rare JSA ranking exception, or the result of
   a recent SumoDB HTML-format change?

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

This sequence has now been carried out far enough to validate the immediate
public-shikona work: BCR regenerates with a warning, make_site2 builds, and the
checked public shikona displays follow the `get_bios` policy.

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
continuation hack. It is a JSA/SumoDB/source-data/parser/chii-model task.
