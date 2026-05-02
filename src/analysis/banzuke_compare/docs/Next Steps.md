# BCR Next Steps

## Status

Working note.

The current Banzuke Change Report is now a useful static page with a traditional
banzuke-first default view, a one-column scan view, previous-basho context,
local movement delta, and optional fixed v1 Equelo ratings.

The next fork in the project is ratings work.  Some of that work affects the
numbers BCR already shows.  Some of it probably belongs in a separate
ratings-first expert view rather than in the current BCR page.

## 1. Revisit Fixed v1 Rating Quality

The Equelo ratings currently shown by BCR are fixed v1 model values.  They are
useful enough to expose, but they are probably not the best numbers the project
can produce.

Known issues:

- ratings below roughly `Jd100` are likely to be weak or meaningless because
  the churn rate is very high;
- the computed fixed-point entry ratings are not entirely monotonic with
  respect to `Chii`.

The second point matters because the fixed-point entry ratings are meant to
help ratings converge faster and represent the prior information implied by a
rikishi's rank.  If the entry curve is locally non-monotonic, then the prior
can imply that a lower chii deserves a higher initial rating than a better chii.
That may occasionally be defensible as empirical noise, but it is awkward as a
model input.

Possible responses:

1. Suck it up.

   Treat the fixed-point values as experimental derived data.  Document the
   limitations and accept that a first exposed version may have local
   irregularities, especially where the historical evidence is thin or noisy.

2. Apply a normalising or curve-fitting kluge.

   Fit or smooth the fixed-point entry values into a monotonic curve before
   scaling and using them as entrant ratings.  This is less pure, but may be a
   better product/model compromise if the purpose of the entry policy is to
   encode rank-implied prior strength rather than reproduce every wrinkle of an
   unstable estimate.

This is an Equelo/fixed_v1 model question first and a BCR display question
second.  BCR should consume the project-level rating definition rather than
inventing a BCR-specific correction.

## 2. Create A Ratings-First Expert View

The current BCR page should remain banzuke-first.  Its default view is designed
to be familiar and readable, with optional context for users who want more
detail.

Once numerical ratings are in play, a different question becomes natural:

> Where does the banzuke disagree with the rating model?

That is not just another optional BCR column.  It is a ratings-analysis product
question and probably deserves a separate expert view.

The first expert view should be a ratings-based one-column table for a selected
division.  It should keep `Chii` and Equelo rating as primary fields, but add
derived metrics that explain the disagreement between formal banzuke order and
rating order.

Candidate fields:

- `chii_rank`: ordinal position in the current banzuke/division;
- `rating_rank`: ordinal position when the same rikishi are sorted by Equelo;
- `delta_chii`: `chii_rank - rating_rank`, so positive values mean the rating
  model would place the rikishi higher than the banzuke does;
- `equelo`: fixed v1 rating, or successor project-level rating;
- `rating_gap_above`: rating difference to the rikishi immediately above in
  rating order;
- `rating_gap_below`: rating difference to the rikishi immediately below in
  rating order;
- `division_rating_rank`: rating rank within the selected division;
- `overall_rating_rank`: rating rank across all current banzuke rikishi;
- `over_ranked` / `under_ranked`: coarse presentation buckets derived from
  `delta_chii`;
- `special_rank_flag`: yokozuna/ozeki/sanyaku marker, because rating-vs-chii
  interpretation is different around protected or exceptional ranks.

`delta_chii` is the central metric.  For example:

```text
1. Fred   Y1e  2500
2. Bill   Y1w  2510
3. Anton  O1e  2600
```

If ranked by rating, Anton would be first.  Relative to chii order, his
`delta_chii` would indicate that the model places him two slots higher than the
banzuke does.

This is not how sumo promotion works, and the expert view must not imply that
ratings determine rank.  The point is to make disagreement visible.  Outside
special cases such as yokozuna and ozeki, large disagreement may be interesting
because it can hint at things like:

- a fast-rising rikishi whom the banzuke has not yet fully caught up with;
- a rikishi whose rating remains high despite a conservative rank;
- a rikishi whose formal rank is high relative to recent rated performance;
- cases where the model and banzuke-making conventions disagree in systematic
  ways.

## Product Boundary

The current BCR page should not accumulate every rating-derived metric behind
an expanding set of checkboxes.  That would make the basic page harder to
understand and harder to maintain.

Preferred direction:

- BCR remains the banzuke-change page.
- Equelo remains optional context on BCR.
- Ratings-vs-banzuke analysis gets its own expert page or route.

The expert page may reuse BCR data-loading, publication, CSS vocabulary, and
some rendering code, but it should have its own template and product question.

## Open Questions

- Should the expert view live under the BCR publisher, or become a sibling
  ratings/banzuke-analysis publisher?
- Should `delta_chii` be computed within division only, across the whole
  banzuke, or both?
- Should yokozuna and ozeki be included in `delta_chii` without adjustment, or
  marked as special cases only?
- Should rating gaps be displayed as raw rating points, expected win
  probabilities, or both?
- Should the first expert view sort by chii by default, rating by default, or
  preserve both with an explicit sort control?
