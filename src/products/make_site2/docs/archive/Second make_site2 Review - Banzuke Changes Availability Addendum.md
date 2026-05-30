# Second `make_site2` Review — Banzuke Changes Availability Addendum

## Status

Focused correction to the current review following investigation of the apparent Selected-History failure in Page 2.1.

This addendum governs over any statement in `Second make_site2 Review.md` which describes the next Banzuke Changes correction as generating an ordinary final-two-bashos report from `resolved_history`.

The normative contract is in `02 Specification.md`; detailed design refinement is in `08.1 Banzuke Changes Availability.md`; evidence/status are in `10.1 Selected History Coherence Audit.md` and `10 Open Issues and Deferred Design.md`.

## Corrected Finding

The restricted-history test remains evidence of misleading publication context:

```text
Basho Results
  showed selected historical material ending at 1980_11.

Banzuke Changes
  showed copied current/live new-banzuke material from 2026.
```

However, Banzuke Changes is not properly repaired by redefining it as a comparison of `1980_11` with `1980_09`.

Its production meaning is:

```text
A new banzuke has been published before its basho has results of its own.
Show how it differs from the preceding represented basho.
```

It therefore requires predecessor History context plus a compatible separately available successor banzuke.

## Corrected Implementation Sequence

The immediate correction is:

```text
Keep Banzuke Changes available in development output for UI regression testing.
Add a conspicuous subheading warning that its availability is not validated
against the build's History and archive/historical builds may show unrelated
live output.
```

The later production correction is:

```text
Resolve whether a compatible successor banzuke exists relative to History.
When it does, expose the ordinary Banzuke Changes PA.
When it does not, make the Page unavailable in production, disable or mark its
Navigation treatment accordingly, and direct direct-request readers to Basho
Results for represented historical comparison.
```

The broader Selected-History coherence issue for ordinary History-derived copied PAs remains open and separate.