# Chii Aggregation and 6.3.1 Work Plan

## Status

Historical / deletion candidate.

This work plan records probability/matchup thinking from the fixed-v2 period.
It contains terminology and artifact references that predate the fixed-supported
Equelo replacement. Preserve only if needed for archive archaeology; do not use
it as current implementation guidance without a fresh rewrite.

The current selected-BP implementation is now understood and repaired. The
public-category aggregation design remains unsettled.

This note should be read alongside:

```text
docs/Banzuke Position Model Work Plan.md
```

That document introduces `BP` / `Banzuke Position` as the proposed conceptual
name for the formal model value currently implemented by `Chii`.

---

## 1. Problem Statement

Page 6.3.1 currently offers two views:

```text
Observed
Equelo
```

The intended purpose is to investigate how accurate Equelo ratings are as
predictors of observed bout outcomes.

Conceptually, for a Chii-like category pair `(c1, c2)`, the comparison is:

```text
p_obs(c1 beats c2)
p_rating(c1 beats c2)
```

The implementation exposed a modelling question:

```text
What exactly are c1 and c2?
```

The answer must be the same for the Observed and Equelo views. Otherwise the
chart no longer compares observed outcomes with rating-derived expectations for
the same objects.

---

## 2. Required Foundation

Any future artifact in this area, whether separate charts or a combined
delta/comparison table, requires three things to be settled.

1. `c1` and `c2` must vary over the same domain in observed and rating-derived
   measurements.
2. The observed measurement requires actual bouts between instances of `c1`
   and `c2`, with support visible rather than hidden behind an arbitrary cutoff.
3. The rating-derived measurement requires a canonical representative rating
   for every `c` in the chosen domain.

The repaired selected-BP implementation satisfies these for its current domain.
The future public-category design still needs a settled category policy.

---

## 3. Chii and Annotation Policy

`Chii` objects, not rank strings, are the formal model.

`Chii.ordinal()` is the canonical ordering key. Strings such as `M3eHD` or
`O2w` are display/input forms.

For the present probability comparison, annotations should be collapsed.

Rationale:

- most annotations are historical or data-repair artifacts;
- there is no defined rating distinction between, for example, `M3e` and
  `M3eHD`;
- treating annotations as distinct categories would create sparse categories
  without a meaningful rating interpretation.

This annotation-collapse rule applies to all Chii, including sanyaku Chii.

After annotation collapse, side may be removed for sideless analysis. Side
removal preserves level/title and number:

```text
Y1e -> Y1
Y1w -> Y1
O2w -> O2
M3e -> M3
J7w -> J7
```

It does not imply:

```text
O2 == O1
S2 == S1
K2 == K1
```

Any such grouping would be an additional aggregation/binning policy.

---

## 4. Sanyaku and Makuuchi

Sanyaku Chii have a special public-language problem.

The model represents makuuchi using `MSD` values:

```text
Yokozuna
Ozeki
Sekiwake
Komusubi
Maegashira
```

This makes `Y`, `O`, `S`, `K`, and `M` structurally similar as Chii
designators, but public sumo language does not normally speak of a "Yokozuna
division" or "Ozeki division". It speaks of the Makuuchi division, containing
sanyaku and maegashira.

The chart therefore has two distinct concepts:

- public division filter: `Makuuchi`;
- Chii-like category labels within that division: `Y1`, `O1`, `S1`, `K1`,
  `M1`, `M2`, ...

This distinction must remain explicit.

---

## 5. Rare Chii and Binning

"Rare Chii" can mean several different things.

1. Annotated Chii such as `M3eHD`.
2. Lower-division annotated Chii such as `Ms60TD` or `Sd100HD`.
3. Rare numbered sanyaku Chii such as `O3`, `S2`, `S3`, or `K2`.

The first two are handled by annotation collapse.

The third is not handled by annotation collapse. A policy decision is still
needed.

Possible policies:

```text
diagnostic sideless BP
  O1, O2, O3 are distinct categories

canonical displayed BP category
  show/use only Y1, O1, S1, K1 for sanyaku in public charts

public-category aggregation
  sanyaku map to title/designator Y/O/S/K
  non-sanyaku use sideless BP such as M10 or J7
```

Binning is an aggregation. It is acceptable only if it is explicit and
documented. It must not be an accidental conflation hidden by a display label.

If a displayed label such as `O1` actually means "all Ozeki", that label is
misleading and should be reconsidered.

The current alignment is:

```text
diagnostic sideless BP
  best diagnostic category; preserves O1/O2/O3 distinctions

canonical displayed BP category
  describes the current 6.3.1 charts; admits Y1/O1/S1/K1 and display-filters
  other numbered sanyaku categories

BP.public_category
  target public specification; maps O1/O2/O3 to O and similarly for other
  sanyaku titles, while leaving non-sanyaku sideless categories such as M10
  and J7 intact
```

The current implementation is not incoherent. Observed and Equelo use the same
effective domain in the rendered chart. `O1` means `O1` in both, and `O2` is
ignored in both. The implementation is therefore directly comparable, but it is
not implementing `BP.public_category` aggregation. It should be recorded as
current behavior, not promoted as the final public model.

This is different from excluding historical or low-support BP slots such as
`M18`-`M22` or `J13`-`J24`. Those are outside the curated comparison domain.
Numbered sanyaku slots such as `O2` and `K2` are ordinary possible BPs; choosing
not to display them is a presentation/category policy, not a rating-domain
cleaning rule.

---

## 6. Current 6.3.1 Facts

Current 6.3.1 is artifact style B:

```text
one Observed chart
one Equelo chart
human compares the shapes
```

It is not yet artifact style A:

```text
one combined artifact showing p_obs, p_rating, and/or delta
```

The current generated data is row-based. It has `selected_chii` and
`opponent_chii` fields, not one column per Chii.

The current browser display applies a canonical-numbered sanyaku display filter:

```text
Y1, O1, S1, K1
```

That filter can hide rows that exist in the CSV. For example, `O2` may exist in
the chart CSV while not appearing in the rendered Makuuchi chart.

The previous Equelo source was found to use the wrong rating kind:

```text
latest fixed_v2 process ratings averaged by current sideless chii
```

This source answered a different question: "what are the current occupants of
this BP bucket rated?" It did not answer "what rating does fixed_v2 assign to
this BP?" It created jagged Equelo curves because the latest occupants of a BP
bucket may have unusually high or low process ratings. For example, the old
source could make `K1` higher-rated than `O1`, which violates the intended
standing-rating interpretation of this chart.

The repaired current source is:

```text
fixed_v2 entrant-initial BP ratings
  -> filter to the curated fixed_v2/v5 comparison domain
  -> remove side
  -> average BP ratings by sideless BP
```

This uses the raw fixed_v2 BP rating map, not latest process ratings and not
the smoothed `Typical Equelo Ratings` public landmark table.

The curated comparison domain excludes historical or low-support slots such as
`M18`-`M22` and `J13`-`J24`, and caps the lower bound at `Jd100w`. The
`M13`-`J1` bridge region remains in the domain because its non-monotonicity is
part of the phenomenon being investigated.

For observed probabilities, the current chart is a consistent implementation of
the canonical displayed BP category approach:

```text
O1 is plotted
O2 is ignored
O2 does not contribute to O1 or O
```

The Equelo chart applies the same effective category filter. This keeps the two
rendered charts comparable even though the category choice is not the preferred
public-category aggregation model.

In other words, current 6.3.1 uses:

```text
curated sideless BP data + canonical displayed sideless BP domain
```

It does not use:

```text
public-category aggregation
```

This distinction matters because it determines whether `O2` is ignored or folded
into an `O` category.

It also matters for labels. If future work aggregates all ozeki BPs into one
public category, the label must be `O` or `Ozeki`, not `O1`. A label of `O1`
means the selected canonical sideless BP, not all ozeki.

---

## 7. Public Category Probability Semantics

`BP.public_category` is a wider BP/category modelling issue, not only a 6.3.1
charting issue. Other public pages and controls that expose BP-like values, such
as page 5.1's Chii dropdown, need the same projection question answered.

If 6.3.1 uses `BP.public_category`, then the probability question becomes:

```text
p_obs(pc1 beats pc2)
p_rating(pc1 beats pc2)
```

where `pc1` and `pc2` are values in the conceptual `PublicCategory` type, not
display strings.

`PublicCategory` is a BP-derived category. Conceptually it is the union of:

```text
PositionTitle for sanyaku
SidelessBP for non-sanyaku
```

For example:

```text
O2w -> PositionTitle(O)
K2e -> PositionTitle(K)
M10w -> SidelessBP(M10)
J7e -> SidelessBP(J7)
```

These are conceptual model values. The strings `O`, `K`, `M10`, and `J7` are
display renderings of those values, not the values themselves.

This aggregation means side-specific questions such as:

```text
p_obs(J7e beats J8e)
p_obs(J7e beats J8w)
```

are not the public-category questions. They may remain useful in diagnostic
artifacts, but they are below the public category layer.

It also means same-category probabilities are meaningful:

```text
p_obs(J7 beats J7)
p_obs(O beats O)
```

Unlike a full side-bearing BP slot, a public category can contain multiple
different rikishi and banzuke positions. Therefore `p(pc, pc)` can represent
actual bouts between different rikishi whose BPs reduce to the same public
category.

This is an important semantic consequence of public-category aggregation and
must be visible in the eventual specification.

---

## 8. Observed Probability Specification Draft

The user-facing observed question is:

```text
What is the probability that a rikishi of public category pc1 beats a rikishi
of public category pc2?
```

For each included decisive bout:

1. take each rikishi's bout-time BP;
2. collapse annotation according to the annotation policy;
3. map the resulting BP to `BP.public_category`;
4. accumulate the bout under the unordered public-category pair;
5. record wins for each public category in that pair.

Thus:

```text
p_obs(pc1 beats pc2)
  = wins by pc1 rikishi in bouts between pc1 and pc2
    / decisive bouts between pc1 and pc2
```

The same pair can be exposed in selected/opponent form for charting:

```text
selected public category: pc1
opponent public category: pc2
```

and, when `pc1 != pc2`, the reverse selected/opponent row may also be emitted.

For `pc1 == pc2`, the probability is meaningful because a public category can
contain multiple different rikishi and BP slots. The implementation must use a
clear convention for same-category rows. The expected convention is to emit one
row with:

```text
selected_public_category = opponent_public_category = pc
p_obs = 0.5
n_obs = decisive same-public-category bouts
```

or otherwise document a different convention.

Observed support must remain visible through `n_obs` and confidence intervals.
Low-support points should not be hidden by an arbitrary cutoff in the first
public-quality Makuuchi/Juryo view.

---

## 9. Rating Prediction Specification Draft

The user-facing rating-derived question is:

```text
What probability does Equelo assign to pc1 beating pc2?
```

The rating prediction is:

```text
p_rating(pc1 beats pc2)
  = EloFormula(rating(pc1), rating(pc2))
```

where each `rating(pc)` is derived from annotation-free BP ratings.

Ratings are considered to be defined at the annotation-free BP level:

```text
AFBP -> rating
```

Every AFBP maps deterministically to a public category:

```text
AFBP.public_category -> PublicCategory
```

Therefore the representative rating for a public category is:

```text
rating(pc)
  = arithmetic mean(
      rating(afbp)
      for every supported afbp
      where afbp.public_category == pc
    )
```

Examples:

```text
rating(O)
  = mean(rating(O1e), rating(O1w), rating(O2e), rating(O2w), ...)

rating(K)
  = mean(rating(K1e), rating(K1w), rating(K2e), ...)

rating(M10)
  = mean(rating(M10e), rating(M10w))

rating(J7)
  = mean(rating(J7e), rating(J7w))
```

No ambiguity is expected in which AFBPs are pertinent to a public category. The
mapping is owned by the BP/PublicCategory model.

The rating-source artifact `S'` should therefore contain at least:

```text
public_category
public_category_display
rating
support_count
support_afbps
support_ratings
rating_source
aggregation_policy
```

This replaces the current useless source:

```text
latest fixed_v2 process ratings averaged by current sideless chii
```

For the current selected-BP implementation, the replacement is already known:

```text
fixed_v2 entrant-initial BP ratings averaged to the selected sideless BP
category after applying the curated fixed_v2/v5 comparison domain
```

For a future public-category implementation, the same fixed_v2 BP rating source
should be aggregated to `BP.public_category` instead of to sideless BP. The
shared PublicCategory mapping should be owned outside this specific matchup
producer if other pages, such as 5.1, also need it for public controls.

---

## 10. Scope Decision

The first public-quality target should work well for:

```text
Makuuchi
Juryo
```

Lower divisions are lower priority. If the code has known limitations below
Juryo, it is acceptable for now to document those limitations rather than fix
them immediately.

---

## 11. Work Plan

### Step 1: Audit Current Aggregation

Status: current behavior understood for 6.3.1.

Determine exactly how the current observed data preparation handles:

- annotations;
- side removal;
- `O2`, `O3`, `S2`, `S3`, `K2`;
- lower-division annotations;
- display-domain filtering versus data-domain filtering.

The output should say whether `O2wHD`, for example, currently contributes to:

```text
O2w
O2
O1
O
```

or is excluded.

Current finding: the rendered chart uses selected sideless BP categories. It
does not aggregate numbered sanyaku BPs into title bins. `O1` is plotted as
`O1`; `O2` is not folded into `O1` or `O`.

### Step 2: Decide the Public Domain

Decide the category domain for page 6.3.1.

Candidates:

```text
diagnostic sideless BP domain
  Y1, O1, O2, S1, S2, K1, K2, M1...

canonical displayed sideless BP domain
  Y1, O1, S1, K1, M1...

public-category / title-bin domain
  Y, O, S, K, M1...
```

The choice must apply to both Observed and Equelo.

Current alignment: the public-category domain is the target public
specification. The canonical displayed sideless BP domain describes the current
implementation and can remain a diagnostic or transitional behavior, but it is
not the model to persist as the public explanation of 6.3.1.

### Step 3: Specify S'

Status: specified for the current selected-BP implementation; still open for
the future public-category implementation.

Specify the canonical representative rating source for every public category in
the chosen domain.

For the current selected-BP implementation, S' is generated from fixed_v2
entrant-initial BP ratings, filtered to the curated fixed_v2/v5 comparison
domain and averaged by sideless BP. It is not generated from the latest
day-end process ratings and it is not generated from the public landmark table.

Open questions for the future public-category implementation include:

- whether a public-category rating artifact should be persisted as its own
  producer output;
- what provenance metadata that artifact must carry;
- whether public-category labels should use abbreviations (`O`) or title text
  (`Ozeki`) in the site UI.

Settled direction:

- ratings are defined at annotation-free BP level;
- each annotation-free BP maps to one public category;
- each public-category rating is the arithmetic mean of its supported
  annotation-free BP ratings;
- support must be recorded.

### Step 4: Update 6.3.1 Generation

Status: implemented for the current selected-BP implementation.

The current generator now:

- removes the latest-current-occupant source;
- uses fixed_v2 entrant-initial BP ratings;
- applies the curated fixed_v2/v5 comparison domain to both Observed and
  Equelo;
- records the rating source and domain policy in metadata;
- keeps confidence intervals visible for observed support.

Future public-category work would revisit this generation step.

### Step 5: Reconsider Artifact A

Once B is coherent, reconsider a combined comparison artifact:

```text
p_obs
p_rating
delta
support
confidence interval
```

This should reuse the same domain and S' rather than invent a second policy.

---

## 12. Non-Goals for Now

Do not attempt to solve all lower-division presentation issues before fixing
Makuuchi and Juryo.

Do not make public labels hide aggregation decisions.

Do not use current process-rating bucket averages as the representative
standing-rating source for 6.3.1.
