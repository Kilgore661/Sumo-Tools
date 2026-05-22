# BCR Next Steps

## Status

Working note.

The current Banzuke Change Report is now a useful static page with a traditional
banzuke-first default view, a one-column scan view, previous-basho context,
local movement delta, and optional fixed v1 Equelo ratings.

The next fork in the project is ratings work.  Some of that work affects the
numbers BCR already shows.  Some of it probably belongs in a separate
ratings-first expert view rather than in the current BCR page.

This document is the single home for those BCR-facing rating questions.

## 1. Revisit Fixed V1 Rating Quality

The Equelo ratings currently shown by BCR are fixed v1 model values.  These
are not the hacked v5 monotone initial-rating curve.

For an established rikishi, the displayed number is the latest persisted
fixed_v1 day-end rating before the current banzuke date.  In normal use this
means the rating after the previous completed basho.  For a rikishi absent
from that snapshot, BCR falls back to the fixed_v1 scaled fixed-point entrant
rating for the rikishi's current `Chii`.

So the visible BCR value is a process rating, not merely a lookup from chii to
rating.

Known issues:

- ratings below roughly `Jd100` are likely to be weak or meaningless because
  the churn rate is very high;
- the computed fixed-point entry ratings are not entirely monotonic with
  respect to `Chii`.

The second point matters because the fixed-point entry ratings are meant to
help ratings converge faster and represent the prior information implied by a
rikishi's rank.  If the entry curve is locally non-monotonic, then the prior
can imply that a lower chii deserves a higher initial rating than a better
chii.  That may occasionally be defensible as empirical noise, but it is
awkward as a model input.

Possible responses:

1. Suck it up.

   Treat the fixed-point values as experimental derived data.  Document the
   limitations and accept that a first exposed version may have local
   irregularities, especially where the historical evidence is thin or noisy.

2. Apply a normalising or curve-fitting kluge.

   Fit or smooth the fixed-point entry values into a monotonic curve before
   scaling and using them as entrant ratings.  This is less pure, but may be a
   better product/model compromise if the purpose of the entry policy is to
   encode rank-implied prior strength rather than reproduce every wrinkle of
   an unstable estimate.

This is an Equelo/fixed_v1 model question first and a BCR display question
second.  BCR should consume the project-level rating definition rather than
inventing a BCR-specific correction.

## 2. Ranking By Chii Vs. By Rating

Once a rating is shown, it becomes tempting to ask whether the rikishi's formal
`Chii` and numerical rating agree.  That question has several possible
meanings, and they should be kept separate.

If we have a chii-to-rating map:

```text
c2r: Chii -> rating
```

then we can also define an approximate inverse:

```text
r2c: rating -> nearest Chii
```

For a rikishi with official chii `c` and rating `r`, two questions become
available:

```text
Is c2r(c) approximately r?
Is r2c(r) approximately c?
```

These are not identical questions.  The first asks whether the rating is
typical for the official chii.  The second asks which chii the rating most
closely suggests.

The inverse form is especially delicate, because it can produce an invalid
banzuke if applied independently to every rikishi.  Several rikishi may map to
the same chii, and some chii may receive no rikishi at all.

## 3. Two Candidate Interpretive Scales

At present there are two plausible candidate scales for `c2r` and `r2c`.

### Fixed V1

Fixed v1 is the result of running the fixed-point-derived entrant policy
through the rating process, then persisting the resulting rikishi ratings
through time.

It has an empirical claim behind it: the numbers come from a deterministic
rating procedure grounded in observed bouts and project-level model choices.

Its weakness, for chii interpretation, is that the fixed-point entrant map is
not fully monotone.  This is awkward if the map is used as an interpretive
`c2r` ruler, because it may imply that a worse chii deserves a higher prior
rating than a better chii.

### V5

V5 is a curated monotone curve derived from the fixed_v1 entrant values.  It
deletes some rare or non-contemporary chii, masks a small number of troublesome
points, and interpolates a strictly decreasing curve over the remaining
ordered chii domain.

Its strength is interpretability.  It gives a well-behaved `c2r` and `r2c`.

Its weakness is that it is explicitly hacked.  The hack may be defensible if
the deviations from fixed_v1 are small enough for the intended use, but it is
not raw model output.

There is also a consistency objection.  BCR currently shows fixed_v1 process
ratings.  If those ratings are interpreted through the v5 monotone scale, then
the process that produced the number and the scale used to interpret the
number are not identical.

That may be acceptable.  V5 is close to fixed_v1 on most of the shared domain,
and the interpretive error may be small relative to the full rating range.  For
example, if the average absolute v5-v1 difference is only a handful of rating
points, it is probably insignificant for ordinary BCR display.

The current audit tool for this claim is:

```text
src/analysis/equelo/fixed_v1/compare_initial_ratings.py
```

It compares the Expt2 raw fixed-point ratings, the fixed_v1 scaled entrant
ratings, and the v5 monotone curve on their shared domain.  Its output should
be treated as part of the evidence for whether v5 is a tolerable interpretive
scale for fixed_v1-derived BCR ratings.

The cleaner model would be a new rating series, perhaps fixed_v1a, which uses
the v5 monotone curve as its entrant initialiser.  Then BCR would display
ratings and interpret them using the same underlying chii-to-rating scale.

Again, this should remain an Equelo model question, not a BCR-specific patch.

## 4. Two Interpretive Postures

One possible view is ratings-first:

> Equelo ratings are derived in a meaningful, deterministic, and relatively
> objective way.  Initialisation issues aside, they may be the better measure
> of current strength.

Under this interpretation, the rating has primacy.  If a rikishi has rating
`r`, BCR could report the chii implied by `r2c(r)`, or some displacement from
the rikishi's official chii to that rating-implied chii.

This is attractive when the goal is to find places where the banzuke seems
conservative, generous, or slow to reflect recent rated performance.

The danger is tone and semantics.  Sumo ranks are not assigned by rating.  This
is especially true for yokozuna, ozeki, and sanyaku, where status, promotion
requirements, demotion rules, and institutional conventions are not reducible
to ordering by strength.

Another possible view is chii-first:

> Chii are assigned by people with enormous experience, within a long-running
> institutional system.  They are the primary object.  Ratings are only one
> model-derived context value.

Under this interpretation, the official chii has primacy.  If a rikishi has
chii `c`, BCR could report `c2r(c)` as the rating normally associated with that
chii, then treat the rikishi's actual rating as high or low relative to that
slot.

This is safer for a banzuke-first report.  It lets the rating add context
without implying that Equelo knows the "correct" rank.

The danger is that it can make the rating look like a subordinate diagnostic
of chii rather than an independent model output.

## 5. Independent R2C Is Not A Banzuke

A naive ratings-first display might say:

```text
rating r -> nearest chii c
```

for every rikishi.  This is not a banzuke.

It may place a non-yokozuna at `Y1e`.  It may assign multiple rikishi to the
same chii.  It may leave holes.  It may ignore structural features of the
actual banzuke, such as absent ranks, sanyaku status, division boundaries, and
special promotion/demotion conventions.

This does not make `r2c` useless, but it means it should be presented as an
approximation or diagnostic, not as an alternative banzuke.

## 6. Logical Banzuke

A more constrained ratings-first idea is to preserve the shape of the published
banzuke, then fill that shape by rating order.

Example:

```text
Actual banzuke:
Y1e: A
Y1w: B
O1e: empty
O1w: C
S1e: D

Rating order:
D, C, B, A

Logical banzuke:
Y1e: D
Y1w: C
O1e: empty
O1w: B
S1e: A
```

This keeps the JSA's published slot structure but asks where the same rikishi
would go if ordered by Equelo rating.

For sanyaku this is probably too literal, because those ranks are statusful and
rule-bound.  For maegashira and below it is more plausible, because most of the
banzuke behaves much more like an ordered list of occupied slots.

A first version should probably be computed within bands rather than across
the whole banzuke:

- maegashira only;
- juryo only;
- makushita only;
- sandanme only;
- jonidan only;
- jonokuchi only.

Cross-division and sanyaku-aware versions can come later if the simpler idea
proves useful.

## 7. Slot Error

The most BCR-friendly form may not be to show an alternative chii at all.
Instead, preserve the official row and report how far the rikishi's official
slot is from their rating-order slot.

Example:

```text
A is M1e in the official banzuke.
In the current occupied-slot order, M1e is position 9.
Sorted by Equelo rating, A is position 11.

Display: 2 down
```

This means the rikishi is two occupied slots lower by rating order than by
official banzuke order.  In a compact UI this might be shown as:

```text
2v
```

or, if symbols are available and encoding is reliable:

```text
2 down-arrow
```

The reverse case would mean the rikishi's rating order is higher than the
official banzuke slot, so the display would indicate upward pressure.

This avoids saying that a non-yokozuna "should be Y1e".  It also avoids
constructing an invalid banzuke.  The official banzuke remains primary, and the
rating model supplies only a displacement.

## 8. Advanced Options Proposal

The BCR option panel should distinguish ordinary context from advanced context
without changing shape when advanced mode is toggled.

The proposed option structure is:

```text
Division

Previous Basho
[ ] Results
[ ] Chii
[ ] Equelo Ratings

[ ] Show Delta

Advanced [off/on]
```

When advanced mode is off:

- `Results` and `Chii` remain normal controls;
- `Equelo Ratings` and `Show Delta` remain visible but muted and disabled;
- the panel layout does not jump when advanced mode changes.

When advanced mode is on:

- `Equelo Ratings` and `Show Delta` become enabled and unmuted;
- the user may choose either, both, or neither;
- future advanced controls, such as slot error, can follow the same pattern.

This preserves the temporal organisation: ratings are still previous-basho
context, because BCR shows the fixed_v1 rating after the previous completed
basho.  At the same time, the advanced toggle marks ratings and delta as
analytical/model-derived context rather than plain banzuke facts.

## 9. Possible BCR Displays

The current BCR page is banzuke-first.  Any rating-derived display should be
small, optional, and not require users to accept a ratings-first worldview.

Possible displays:

1. Rating only.

   This is the current behaviour.  It is simple and low-interpretation.

2. Rating plus slot error.

   This adds a compact displacement such as `2 down` or `3 up`.  It answers:
   "Within the relevant comparison set, how far away is this rikishi from their
   rating-order position?"

3. Rating-implied chii.

   This uses `r2c(r)` directly.  It is easy to explain but can be misleading
   because independent inverse mapping is not a valid banzuke.

4. Separate logical-banzuke view.

   This is probably too much for the main BCR table, but it may be valuable as
   a separate expert page.

5. Separate rating-vs-chii audit page.

   This would expose both official order and rating order, with sortable
   columns and larger explanatory space.

## Product Boundary

The current BCR page should not accumulate every rating-derived metric behind
an expanding set of checkboxes.  That would make the basic page harder to
understand and harder to maintain.

Preferred direction:

- BCR remains the banzuke-change page.
- Equelo remains optional context on BCR.
- BCR should not show a rating-implied chii in the main table for now.
- BCR may add an optional slot-error indicator once the comparison set is
  clearly defined.
- Ratings-vs-banzuke analysis gets its own expert page or route.

The slot-error indicator fits BCR because it is banzuke-relative.  It does not
claim to replace the banzuke.  It only says how far the rating order disagrees
with the official position.

The expert page may reuse BCR data-loading, publication, CSS vocabulary, and
some rendering code, but it should have its own template and product question.
It can contain the logical banzuke, rating rank, official rank, rating gaps,
and r2c diagnostics without overloading the main report.

## Open Questions

- Should the expert view live under the BCR publisher, or become a sibling
  ratings/banzuke-analysis publisher?
- Should slot error be computed across the whole banzuke, within division, or
  within smaller bands such as maegashira-only?
- Should yokozuna and ozeki be included in rating-order comparisons without
  adjustment, or marked as special cases only?
- Should rating gaps be displayed as raw rating points, expected win
  probabilities, or both?
- Should the first expert view sort by chii by default, rating by default, or
  preserve both with an explicit sort control?
- Should the current BCR Equelo values remain fixed_v1, or should a fixed_v1a
  series be created using the v5 curve as the entrant initialiser?
- If v5 is used only as an interpretive scale, how should that be described to
  users?
- What threshold makes a slot error worth displaying?  Is `1` meaningful, or
  should only larger movements be highlighted?
- Should the UI show direction from the point of view of the rikishi, the
  official slot, or the rating model?  The convention must be unambiguous.
