# Torikumi Lifecycle Repair Proposal

## Problem

The first Torikumi implementation equates the latest basho represented in
`History` with the basho whose torikumi the public site should show.  That is
true during a basho but false in the pre-basho interval.  On 2026-11-01,
`History` ended at the completed 2026/09 basho while the independently
published New Banzuke identified 2026/11 as the upcoming basho.  The updater
therefore re-requested all fifteen 2026/09 pages.

The updater also treated HTTP absence, transport failure and unrecognised HTML
as the same `None` result and replaced a valid snapshot with an empty one.  A
live check on 2026-11-01 established that an unpublished 2026/11 day returns
HTTP 200 with a valid SumoDB Results page shell but without the results heading
or torikumi table.  Normal unpublished state therefore cannot be inferred from
HTTP status alone.

## Required lifecycle

The target is selected from two coherent inputs:

1. an incomplete latest History basho is the active target;
2. otherwise, an independently published New Banzuke which is the immediate
   successor of History is the upcoming target; and
3. otherwise there is no current Torikumi target.

November-to-January rollover is an ordinary immediate-successor transition,
not a terminal date special case.

Acquisition distinguishes:

- a positively recognised, published torikumi;
- a positively recognised SumoDB Results shell for an unpublished day;
- HTTP 404, also treated as unpublished;
- transport and HTTP failures; and
- unrecognised or malformed HTML.

Only a complete successful probe of the bounded Days 1 through 15 replaces
the persisted snapshot.  A failed refresh leaves the prior snapshot and raw
cache unchanged.  The command may reuse a retained snapshot only when it has
the selected target date; it must fail rather than silently publish a snapshot
for a different basho.

## Upcoming-basho ratings

An upcoming basho has no `History` state and therefore no ordinary
`basho_start_ratings` artifact.  Elo-89 projects the exact next start state:

- use each active rikishi's latest persisted end rating, including a returning
  rikishi's frozen rating from his most recent appearance;
- initialise a genuinely unseen rikishi from the accepted P1WL chii prior; and
- shift the selected active population to the run's fixed target mean, exactly
  as the normal replay does at the start of a represented basho.

This is model logic and belongs to `src.analysis.elo89`, not to acquisition or
website code.

## Package boundaries

- `src.infra.torikumi` owns target selection, acquisition classification and
  atomic persistence.
- `src.infra.new_banzuke` remains the source of the upcoming typed banzuke.
- `src.analysis.elo89` owns projected next-basho start ratings.
- `src.analysis.site89` accepts either the represented History banzuke or the
  matching New Banzuke and produces the public Torikumi artifact.
- product orchestration produces New Banzuke before refreshing Torikumi and
  passes the same artifact into site-data production.

## Verification

Tests cover active, upcoming, absent-target and November-to-January selection;
published and unpublished HTML; preservation after network or parse failure;
new and returning rating projection; upcoming-basho publication; mismatched
input rejection; and product wiring.  The real schedule-only 2026/11 page will
be checked when SumoDB publishes it, because that transient state did not yet
exist on 2026-11-01.
