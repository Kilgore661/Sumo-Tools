# Proposed Next Steps after Proposal 1

## Status

Proposed research sequence following the completed fixed Basic Elo experiment
in `Proposal 1.md`. Each item requires its own experimental specification
before implementation.

## Starting point

Proposal 1 remains the frozen baseline:

```text
epoch = 1989/01
eligible results = W/L, irrespective of kimarite
rating population = all represented rikishi
q = 400
k = 35
initial rating = equal 1500
reference forecast = 50%
```

The equal-rating state is an externally imposed initial condition. The common
numerical value 1500 is arbitrary: translating every rating by the same
constant changes no prediction.

Follow-on experiments should change one conceptual component at a time and
retain Proposal 1 as a named comparator. Chii and `RikId` are domain values;
chii strings and shikona remain presentation affordances and must not drive a
calculation.

## 1. Evaluate sekitori bouts only

**Implemented as `Proposal 2.md`, with the complementary sub-sekitori
evaluation in `Proposal 2b.md`.**

Calculate Basic Elo ratings from every eligible represented bout exactly as in
Proposal 1, but evaluate predictive loss only for sekitori bouts. This changes
the evaluation population without depriving the rating producer of
lower-division evidence.

The experiment must define a sekitori bout from the participants' pre-bout
`Chii` values. The proposed primary definition is that both participants are
sekitori on that basho's banzuke. Juryo–Makushita contests should be reported
separately rather than silently assigned to either population.

The existing pre-bout forecasts should be reused. Chii may select evaluation
rows but cannot alter the Proposal 1 predictions. The output should compare:

- all-bout loss from Proposal 1;
- sekitori-only loss;
- the 50% reference within the same sekitori bouts;
- rolling and cumulative behaviour under the same windows.

This is the next experiment because the all-bout aggregate is dominated by
lower-division contests, while the sekitori population is the main setting in
which the predictive interpretation is of interest.

## 2. Initialize ratings from chii

**Implemented as the retrospective diagnostic in `Proposal 3.md`.**

Replace equal initialization with an explicit function from an unseen
rikishi's pre-bout `Chii` value to an initial Elo rating. Retain the 1989 epoch,
the complete post-1988 rating population, q=400, k=35, eligibility rules and
evaluation framework.

This directly tests whether rank supplies a useful prior at the epoch and when
later entrants first appear. It also tests whether the long early period of
underperformance is substantially attributable to equal initialization.

The experiment must specify:

- the mapping from `Chii` to an initial rating;
- whether the mapping is externally fixed or estimated from a declared
  training period;
- the pre-bout chii used for an entrant;
- how the mapping treats divisions, numerical levels, annotations and sides;
- whether the same mapping is used for epoch incumbents and later entrants.

The mapping must not treat a chii string as data. Nor should it assume without
testing that numerical distance between chii ordinals is a distance in
ability. If the mapping is estimated, its evaluation data must not be used to
fit it.

Once initial rating differences are expressed in Elo points, q has a meaning
relative to that mapping's scale. The constant-K simplification that only k/q
matters under equal initialization no longer describes the whole model.

## 3. Test and reduce the Chii-prior structure

**The randomized association test is implemented as `Proposal 4.md`; its
deterministic division-only reduction is implemented as `Proposal 5.md`.**

Proposal 4 retains the exact multiset of retrospective Chii ratings while
destroying either all Chii association or only the association within actual
divisions. Its result locates most durable initialization information at the
division level. Proposal 5 assigns the unweighted mean of each division's
completed Chii values to every entrant in that division. This is the expected
within-division permutation value and tests the finding without choosing a
random mapping.

## 4. Vary the constant update rate

**Deferred until after the randomized-prior proof of concept in `Proposal
4.md`.**

Retain equal initialization and vary the responsiveness of Basic Elo. Under
equal initialization, predictions depend on k and q through their ratio k/q;
scaling both by the same factor produces identical predictions. The clearest
first comparison therefore keeps q=400 and varies constant k around 35.

Include k=0 as the exact 50% producer. Treat the result as a sensitivity curve,
not immediately as selection of an optimum. Compare each setting with k=35
using paired bout losses and basho-block uncertainty.

A later interaction experiment may apply update-rate sensitivity to the
chii-initialized producer, but it should not be folded into the first
initialization experiment.

## 5. Examine the 1958–1988 sekitori record

Run a separately labelled sekitori experiment over the earlier data regime.
The represented sekitori results may be adequate even though lower-division
results are incomplete. Consequently, Juryo ratings will usually lack evidence
from lower-division bouts; the rarity of Juryo–Makushita meetings may make the
effect small, but it is part of the information contract and must be reported.

Two distinct questions should not be conflated:

1. How predictive is Basic Elo within the represented 1958–1988 sekitori
   record?
2. What happens after 1989 if the earlier represented results are used to warm
   the rating state before evaluation begins?

The second question is a direct sensitivity test of Proposal 1's externally
imposed equal-rating condition. It must remain distinct from the post-1988
complete-data baseline because its pre-epoch information is incomplete.

## 6. Make k depend on chii

Test whether rating responsiveness should depend on a participant's pre-bout
career level. This is a change to rating dynamics, not merely initialization.

The update equation needs an explicit contract. If each participant receives
a different k, the ordinary symmetric zero-sum Elo update is lost. The
experiment must therefore choose deliberately between:

- a single bout-level k derived from both pre-bout chii values, preserving a
  zero-sum update; or
- participant-specific k values, accepting and interpreting non-zero-sum
  updates.

This experiment follows the constant-k sensitivity work so that any benefit
can be distinguished from choosing a generally faster or slower update rate.

## Interpretation common to the sequence

The 50% comparator remains substantively important. Torikumi may be formed so
that bouts are expected to be competitive, even though the exact formation
policy is unknown. A small improvement over 50% can therefore represent real
residual predictive information within deliberately balanced contests.

None of these experiments requires a renewed investigation into torikumi
formation. They evaluate predictions for the contests that were actually
arranged. Work on the distribution of final win–loss records may later help
contextualize the strength of the 50% baseline, but it is not a prerequisite
for this sequence.

## Proposed order

1. Sekitori-only evaluation of the existing Basic Elo forecasts.
2. Chii-based initialization.
3. Randomized-prior placebo for the Chii initialization.
4. Deterministic division-only initialization.
5. Constant update-rate sensitivity.
6. The 1958–1988 sekitori regime and optional pre-1989 warm state.
7. Chii-dependent update rates.

## Concrete 50–50 significance experiment

**Implemented and completed as `Proposal 6.md`.**

Before further producer sensitivity work, Proposal 6 translates the original
comparison with 50% into the bookmaker thought experiment. It uses Proposal
1's fixed producer, stakes the favourite probability at evens, and compares
the represented historical return with 2,000 complete fair-coin histories.
This supplies a direct chance comparison for the claim that Basic Elo has
directional predictive information.

The order is methodological rather than a claim about likely importance. It
first establishes the population of interest, then tests the initial condition,
then rating responsiveness, and only afterwards combines rank information with
the update mechanism.
