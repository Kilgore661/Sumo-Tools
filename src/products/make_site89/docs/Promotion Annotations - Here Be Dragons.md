# Promotion Annotations - Here Be Dragons

## Purpose

This is the guardrail document for the promotion-annotation feature. Read it
before attempting to make the annotations more predictive, more historical,
or more responsive during a basho.

The compact Ozeki32 and YokYDJ markers are deliberately less ambitious than
several apparently attractive alternatives. Their limitations are known and
accepted. Removing those limitations casually is more likely to create a
misleading feature than an improved one.

The operative behaviour is defined in
`Promotion Annotations - Final Proposal.md`. The older
`Promotion Annotations Proposal.md` remains useful historical context but is
not the current specification.

## Dragon 1: a historical percentage is not a rikishi's probability

The promotion analysis does not support a calibrated probability for an
individual current rikishi.

Historical rates are conditional on the selected population, time period,
rank-pattern definition, outcome contract, and treatment of missing data.
Promotion practice may change. Decisions may also depend on circumstances not
represented in History, including injuries, score quality, opposition,
available rank capacity, other candidates, deliberative criteria, and the
institutional context of the period.

The observations are not independent trials:

- the same rikishi may contribute several overlapping windows;
- neighbouring opportunities share tournaments and opponents; and
- sparse categories can display extreme percentages by chance.

The rule-selection work also inspected historical performance. An in-sample
F1 winner is not automatically calibrated out of sample. Even chronological
validation cannot manufacture a stable probability from a small, changing
institutional process.

Consequences:

- do not put a percentage beside a shikona;
- do not label precision as “chance of promotion”;
- do not turn an F1 score into a forecast;
- do not present a pooled historical fraction without its conditioning
  population and counts; and
- keep statistical results in the explanatory analysis, where their samples,
  exceptions and uncertainty are visible.

The annotation says only that a simple, published site-defined results
condition is open or has been achieved.

## Dragon 2: the indicators are not JSA rules

Promotion is an institutional decision. Ozeki32 and YokYDJ summarize parts of
the recorded results history; they neither bind nor reproduce the Japan Sumo
Association's complete reasoning.

Ozeki32 has both false positives and false negatives. Actual Ozeki promotions
have occurred below 32 K/S wins, and some qualifying totals were not followed
by promotion. Strong Maegashira starts have sometimes contributed to real
promotions but are excluded from the marker because a broad Maegashira rule
would identify too many unconvincing runs.

YokYDJ is supported by a particularly small modern sample: five identified
promotions and two non-promotions. Both non-promotions belong to Takakeisho,
and the modern sample contains no independently observed `YD` case. Its
apparent modern performance is encouraging but fragile.

A tick means “the site's results condition was achieved.” It must never be
defined or styled as “promotion secured.” Actual promotion is established by
the following banzuke.

## Dragon 3: do not calculate mid-basho Yokozuna impossibility

Yusho, doten-yusho and jun-yusho are relative finishing classifications. They
depend on the records of several rikishi and, potentially, a playoff.

The remaining torikumi is not generally known in advance. Future win/loss
projections for different rikishi therefore cannot be combined independently.
For example, after day 13 one might imagine candidate B winning twice while
leader A loses twice, creating a tie and playoff. One of the unknown bouts may
be A versus B, or other future pairings may make parts of the imagined joint
record incompatible.

Knowing each rikishi's arithmetic minimum and maximum score is therefore not
enough to decide the space of achievable final classifications. A calculation
which ignores the future torikumi can falsely retain or falsely eliminate a
YokYDJ route.

The safe rule is intentionally simple:

- keep `!` throughout an in-progress basho;
- wait until the final `Y`, `D`, `J`, or `N` classification is known;
- then show a tick for a qualifying pair or remove the marker.

Do not “improve” this by adding a standings heuristic. A genuine prospective
feasibility engine would require an explicit, sufficiently complete future
torikumi plus a carefully tested joint-outcome model. That is not part of this
feature.

## Dragon 4: Ozeki32 can count down because it is different

The Ozeki32 target is an individual regular-win total, not a relative finishing
classification. A sekitori can gain at most one regular win per tournament
day, so current wins plus remaining days gives a safe upper bound without
knowing future opponents.

That is why the current Basho Results page may count `(n)` down, replace it
with a tick when achieved, and remove it when unreachable. This reasoning must
not be copied to YokYDJ merely because both are promotion annotations.

Use tournament days remaining, not “unrecorded bouts,” for the upper bound.
An absent rikishi may have no recorded bout on a day, but that does not create
an extra day on which a future win can occur.

## Dragon 5: do not use later knowledge on historical pages

A historical annotation is tempting because the site possesses later results
and the following banzuke. Using them would introduce lookahead into a marker
which is supposed to describe a prospect.

The settled product deliberately avoids the problem:

- The Banzuke shows only the current starting condition.
- Only current Basho Results shows the developing state.
- Past Basho Results shows no promotion annotation.

When a new banzuke becomes current, the preceding Basho Results page becomes
historical and loses its annotation. The promotion outcome remains available
through its factual next rank rather than a reconstructed prospect marker.

Do not reintroduce historical annotations merely for visual consistency. The
current results view is intentionally a current-sumo enhancement of a
historical browser.

## Dragon 6: do not mutate the shikona

Examples such as `Fred (* !)` and `Fred (* 10)` describe rendering, not stored
identity. The independent `*` new-career-high marker is rendered before any
promotion marker. It appears only the first time that ordinal is the rikishi's
career high. Appending either marker to the canonical shikona would contaminate:

- rikishi identity and links;
- alternate chart actions;
- sorting and searching;
- cross-artifact reuse; and
- later changes to the annotation typography.

Publish structured prospect fields and render the marker as a separate,
associated element with accessible text.

## Dragon 7: freshness is a production property

The live-store downloader may acquire new daily results, but the public static
site changes only after the relevant producers, bundle assembly, site build
and deployment have run.

The final system is intended to trigger that chain when new daily results are
incorporated. Until that orchestration exists, the current-results countdown
is only as current as the last manual site89 production run.

Do not compensate for stale production by calculating against external data in
browser JavaScript. That would split the source of truth and bypass the
validated site-data bundle.

## Dragon 8: preserve the narrow definitions

Several extensions are plausible but are not innocent refactorings:

- changing 32 back to the conventional 33;
- accepting a Maegashira first basho;
- requiring a minimum result in every component basho;
- adding injuries, ratings or strength of schedule;
- treating ozekiwake reinstatement as an ordinary run;
- distinguishing different numerical forms of `J` or `D`; or
- changing the modern YokYDJ evidence boundary.

Each changes the population or semantic claim. None should enter through an
implementation convenience or an apparently obvious edge-case fix. It requires
an explicit policy decision, revised analysis where appropriate, updated
public prose, and new tests.

## Evidence to retain

The following repository records explain how the narrow policy was reached:

- `src/analysis/promotion/docs/Promotion Prospects Statistical Analysis Proposal.md`;
- `src/analysis/promotion/prospects/ozeki/docs/Ozeki32.md`;
- `src/analysis/promotion/prospects/ozeki/docs/Current Banzuke Annotation Handoff.md`;
- `src/analysis/promotion/prospects/yokozuna/docs/YokYDJ.md`;
- `src/products/make_site89/prose/Ozeki32.html`; and
- `src/products/make_site89/prose/YokYDJ.html`.

The original `Promotion Annotations Proposal.md` is also retained. Its 33-win,
yusho-only and retrospective requirements are superseded, but its account of
the site surfaces, temporal questions, structured-data boundary, accessibility
needs and shikona-rendering constraints remains valuable.

## Rule for future changes

An extension is not an improvement merely because it produces more markers or
more precise-looking output. Before changing the policy, state:

1. the exact new claim shown to users;
2. the population and evidence supporting it;
3. how temporal instability and repeated observations were handled;
4. which known counterexamples remain;
5. what new producer facts are required;
6. how the public Promotion prose changes; and
7. why the additional complexity is useful enough to justify the greater risk
   of misleading readers.

If those questions cannot be answered, leave the annotation narrow.
