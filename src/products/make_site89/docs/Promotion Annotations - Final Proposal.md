# Promotion Annotations - Final Proposal

## Status

Implemented specification, pending review of the generated site. This document
is the authoritative product and data contract for promotion-prospect
annotations in `make_site89`.

It supersedes the behavioural requirements in the earlier
`Promotion Annotations Proposal.md`, while preserving that document as a
historical design record. The analytical guardrails and rejected extensions
are recorded separately in `Promotion Annotations - Here Be Dragons.md`.

The implementation also composes the independent first-time career-high marker
described below. That marker is not a promotion claim.

## Purpose

Promotion annotations should draw attention to rikishi whose starting
position makes the current basho relevant to a possible promotion. They are a
compact aid, not a prediction of the Japan Sumo Association's decision.

The minimum and primary surface is **The Banzuke**, where users inspect the
conditions at the start of a basho. The only additional surface is **Basho
Results for the current basho**, where the Ozeki32 target may develop as daily
results arrive.

Past Basho Results pages must not display promotion annotations.

## Shared shikona annotation order

The two eligible surfaces use a shared `annotated_shikona()` rendering routine.
It renders the canonical shikona/link first, then independent annotations in
this fixed order:

1. `HIGHEST_CHII = "*"` when the current chii ordinal is strictly better than
   every ordinal the rikishi held before the displayed current banzuke;
2. the promotion annotation, separated from the preceding text by a space.

A first banzuke appearance therefore qualifies, but returning to an ordinal
previously held does not. All annotations are placed in one parenthesised group
after a space following the shikona. Examples include `Fred (* !)`,
`Bill (* 10)` and `Tom (*)`.
The asterisk applies to rikishi in every division, but only on The Banzuke and
current Basho Results. It does not appear on historical Basho Results.

Neither marker is part of the canonical shikona. The producer supplies
`highest_chii` independently of the promotion facts, and the renderer composes
them without affecting identity, links, searching or shikona sorting.

## Adopted indicators

### Komusubi or Sekiwake to Ozeki: Ozeki32

For a rikishi on the current banzuke, create an Ozeki32 prospect when:

1. the current rank is Komusubi or Sekiwake;
2. the immediately preceding two held basho both exist;
3. the rikishi was Komusubi or Sekiwake in both of them;
4. regular-win totals are available for both basho; and
5. those two totals sum to at least 17, so 32 wins remain achievable with at
   most 15 wins in the current basho.

Define:

```text
required_wins_at_start = 32 - previous_two_basho_wins
```

There is no additional component-basho minimum. Wins include fusensho and
exclude playoff wins. Consecutive means consecutive tournaments which were
actually held. Immediate ozekiwake reinstatement is a different mechanism and
is not represented.

The rule deliberately excludes a Maegashira first basho even though some real
promotions have used such a result. This keeps the annotation sparse and gives
it the precise meaning explained by the public Ozeki32 account.

### Ozeki to Yokozuna: YokYDJ

For an Ozeki on the current banzuke, create a YokYDJ prospect when:

1. the immediately preceding held basho exists;
2. the rikishi was Ozeki in that basho; and
3. the preceding result was a yusho (`Y`), doten-yusho (`D`) or jun-yusho
   (`J`).

The result required in the current basho depends on the preceding result:

| Previous result | Current qualifying result |
|---|---|
| `Y` | `Y`, `D`, or `J` |
| `D` | `Y` |
| `J` | `Y` |

This accepts the completed pairs `YY`, `YD`, `YJ`, `DY`, and `JY`.

## The Banzuke presentation

The Banzuke records the starting conditions. Its annotations remain fixed for
the life of that banzuke.

- Render an Ozeki32 prospect as the required number in the annotation group, for
  example `Fred (10)`.
- Render a YokYDJ prospect with `POSS_YOK`, initially displayed as `!`, for
  example `Fred (!)`.

The rendered marker is adjacent to the shikona but is not part of the
canonical shikona value. It must not affect identity, links, alternate actions,
search, or shikona sorting.

Accessible text must give the semantic meaning. For example:

```text
Ozeki32 prospect: needed 10 wins at the start of this basho.
Yokozuna prospect: previous Ozeki result was a yusho; a Y, D or J result
in this basho would satisfy YokYDJ.
```

The precise YokYDJ wording changes after `D` or `J` to say that a yusho is
required.

## Current Basho Results presentation

Promotion annotations appear only when Basho Results is displaying the
current basho represented by the production snapshot. Selecting any past
basho removes them.

This is an intentional current-sumo enhancement of an otherwise historical
results browser.

### Ozeki32 countdown

Let:

```text
R = required_wins_at_start
W = regular wins recorded in the current basho
D = latest completed tournament day, from 0 through 15
remaining_days = 15 - D
```

Render the prospect as follows:

| Condition | Presentation |
|---|---|
| `W >= R` | tick |
| `W + remaining_days < R` | no annotation |
| otherwise | `(R - W)` |

The tick means that the site-defined Ozeki32 results target has been achieved.
It does not mean that promotion has been announced or guaranteed.

The countdown is safe without advance knowledge of the torikumi because it
depends only on this rikishi's individual win total and the number of
tournament days remaining.

### YokYDJ during the basho

Keep `!` unchanged throughout an in-progress basho. Do not attempt to remove it
because a qualifying finish appears unlikely or seems arithmetically
impossible.

Yusho, doten-yusho and jun-yusho are relative finishing classifications.
Future records are constrained by future matchups, and the complete torikumi
is not generally known in advance. Independent record projections can
therefore describe combinations which cannot jointly occur.

After the basho is complete:

- replace `!` with a tick when the completed pair satisfies YokYDJ; or
- remove the annotation when it does not.

Here too, the tick means only that YokYDJ was satisfied. The following banzuke
remains the site's evidence of an actual promotion.

## Temporal scope

An annotation belongs to the current-banzuke/current-basho product state, not
to a rikishi permanently and not to every historical occurrence of the same
results pattern.

- The Banzuke annotation is calculated as of entry to its basho.
- Current Basho Results starts with that same prospect state.
- Daily Ozeki32 presentation may change as new results are published.
- A completed current basho may show the achieved/failed terminal state until
  the next banzuke becomes current.
- Once a later banzuke is current, the earlier Basho Results page is historical
  and shows no promotion annotation.

No later promotion decision may be used to decide whether an earlier page
should have displayed a prospect.

## Producer and data boundary

`src.products.make_site89` remains an assembler and renderer. It must not load
History or reconstruct promotion rules in browser JavaScript.

An upstream site89 producer should derive structured prospect data for the
current banzuke and current Basho Results. A suitable logical shape is:

```text
highest_chii = true | false

promotion_prospect.kind
    = ozeki32 | yokydj
promotion_prospect.as_of_basho
promotion_prospect.start_annotation
promotion_prospect.status
    = open | achieved | impossible

ozeki32 fields:
    previous_basho_wins[2]
    required_wins_at_start
    current_wins
    remaining_wins_required

yokydj fields:
    previous_result = Y | D | J
    qualifying_current_results
    current_result = Y | D | J | N | unresolved
```

The exact serialization may differ, but it must preserve the distinction
between fixed starting context and current presentation state. Producer data
must carry semantic facts; punctuation, parentheses and tick glyphs belong to
the renderer.

The current-banzuke derivation may be shared by the Banzuke and current Basho
Results producers, but no historical annotation feed is required.

## Notes and links

Both surfaces require concise Notes or a legend which says:

- `*` means the rikishi is at a new career-high chii for the first time on
  this banzuke;
- the markers are site-defined promotion prospects, not JSA rules;
- `(n)` on The Banzuke is the number required at the start of the basho;
- the current-results number is the remaining Ozeki32 target;
- a tick means the relevant site-defined results condition was achieved, not
  that promotion is guaranteed;
- `!` is deliberately not recalculated from in-progress Yokozuna standings;
  and
- actual promotion is known from the following banzuke.

The Notes should direct users to the existing Ozeki32 and YokYDJ pages under
the Promotion menu. No probability should appear in the annotation or its
tooltip.

## Update and publication lifecycle

The live store is intended eventually to run continuously and download daily
results. A newly incorporated daily result should trigger regeneration of the
current Basho Results data, followed by site bundle assembly, static-site build
and publication.

This trigger belongs to the future site89 bootstrap/update orchestration. It
does not change the rule that `make_site89` itself only assembles validated,
already-produced data.

The Banzuke annotations require no daily regeneration. The current-results
countdown is useful only to the freshness of the published daily results.

## Acceptance criteria

The implementation is acceptable when tests and rendered checks establish:

1. a rikishi whose current chii is strictly better than every prior ordinal is
   shown with `*` in either eligible artifact, while a return to an equal
   career high and all historical Basho Results remain unannotated;
2. annotations appear in one parenthesised group after a space following the
   canonical shikona, with `*` before any promotion marker, without changing
   links, searching or sorting;
3. a current K/S rikishi with 22 wins across the preceding two K/S basho is
   shown as `(10)` on The Banzuke;
4. a previous two-basho total below 17 is not annotated;
5. a Maegashira-start sequence is not treated as Ozeki32;
6. current Basho Results counts `(10)` down using regular wins;
7. the Ozeki32 marker becomes a tick when the target is reached and disappears
   when the target cannot be reached in the remaining days;
8. an eligible current Ozeki is shown with `!` after a previous `Y`, `D`, or
   `J`, with accessible text stating the correct required current result;
9. `!` remains throughout an in-progress basho regardless of apparent
   standings;
10. a completed YokYDJ pair produces a tick and a non-qualifying pair removes
   the marker;
11. past Basho Results pages have no annotations;
12. canonical shikona values, links, alternate actions and sorting remain
    unchanged;
13. missing prior evidence causes omission rather than inference; and
14. annotations contain no promotion probability or claim of official JSA
    policy.

## Explicit non-goals

This proposal does not:

- predict an individual promotion decision;
- assign a promotion probability;
- infer whether an in-progress YokYDJ finish remains mathematically possible;
- annotate historical Basho Results;
- include Maegashira-starting Ozeki runs;
- represent immediate ozekiwake reinstatement;
- ingest press reports or Promotion Committee decisions; or
- redesign the live-store and site89 bootstrap architecture.
