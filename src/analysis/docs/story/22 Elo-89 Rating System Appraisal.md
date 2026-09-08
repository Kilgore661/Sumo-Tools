# Elo-89 Rating System Appraisal

## Purpose and assessment

This is Codex's assessment of the rating system published by `make_site89`,
following inspection of the production implementation, the model-selection
record, the website explanations, and discussion with the author. It records
the resulting assessment rather than the sequence of objections and replies.
It is an appraisal, not a new validation run or an experiment specification.

Elo-89 is a credible, thoughtfully developed rating system and a good fit for
the site's purpose: giving readers a numerical account of sumo performance
alongside the banzuke. Its model choices have stated purposes and empirical
support. I support retaining the core model. The main opportunity is to make
the interpretation of its numbers as clear as the calculation, so readers do
not mistake a modelling convention for a defect or attribute more meaning to
a number than the model gives it.

## Evidence for the chosen model

The final declared retrospective comparison covers 574,863 eligible bouts.
Elo-89 achieves mean log loss of 0.675629, compared with 0.682753 for Basic Elo
and 0.693147 for a constant 50–50 forecast. Its Brier loss is 0.241362. The
recorded paired bootstrap comparisons support its improvement over the tested
alternatives, including the previous retrospective winner. These are modest
but meaningful improvements; they are not percentages of prediction accuracy.

The evidence supports the selection without establishing superiority on every
measure. The previous informed-prior model has slightly lower aggregate
calibration error. The selection is supported by the declared log-loss
criterion and the agreeing Brier-score result.

The fixed P1 entrant map was constructed using the historical period being
evaluated. These results are therefore retrospective evidence, not an
out-of-sample validation claim. That is a qualification of the evidence, not
an objection to operational use. Once the model and its inputs are frozen,
subsequent bouts can supply prospective evidence. The site's explicit
disclosure of this distinction is a strength.

## What a rating represents

Elo-89 expresses competitive relationships through rating differences. Its
probability formula uses those differences, not an independently meaningful
absolute rating origin.

Imagine listing every active rikishi in rating order, labelling the leader
zero, and recording each subsequent rikishi's gap from the wrestler above.
That table contains enough information to reconstruct all ratings up to a
common additive constant, and hence all Elo matchup probabilities. Adding a
common constant to the individual ratings changes none of this information.

Individual rating numbers are a convenient presentation of those relationships.
They give each wrestler a readable label instead of requiring the reader to
sum adjacent gaps. Whether a typical yokozuna is labelled 2500, 3000, or 10000
does not matter if the difference is solely a common shift of origin. The
rating units and the probability parameter remain fixed in this argument;
multiplying the gaps would be a different operation.

This also clarifies the use of the word "strength". Operationally, the model's
account of strength is its rating and the matchup probabilities derived from
rating differences. A separate notion of underlying ability would mean a
hypothetical propensity to win under comparable conditions. It is not a
directly observed quantity against which the model has been independently
verified.

The fixed population mean supplies an anchor. Bout results alone cannot
identify a common absolute level, because shifting all ratings leaves their
probabilities unchanged. This does not show that underlying ability is
unrelated to mean rating, or that the chosen anchor is wrong. Historical
comparisons are substantive conclusions conditional on the model's common
anchor and other assumptions. They should be presented as such, rather than
dismissed merely because the anchor is a convention or presented as independent
measurements of absolute ability across eras.

## Chii and initialisation

Using chii as informed starting evidence is sensible. When individual bout
evidence is scarce, starting everyone equally would discard useful information
already available in the banzuke. A chii-based prior does not assert that every
wrestler at that rank has identical ability.

The fixed-point work constructs the entrant-rating map. Once adopted, that map
is fixed: its construction adjustments are not ongoing chii-based adjustments
to individual wrestlers' ratings. It enters the production calculation when a
wrestler is initialised, including reinitialisation after leaving and later
returning to the represented population.

Rating and chii are consequently related but not interchangeable. The banzuke
also incorporates institutional rules, promotion decisions and available
places. Disagreement between rating and rank invites interpretation; it does
not automatically establish an error in either. The site's treatment of
ratings as a complementary account of performance is appropriate.

## Inactivity and the absence of new evidence

Two different kinds of absence must be distinguished explicitly:

- Missing bouts, or an entire basho, while remaining on the banzuke does not
  trigger reinitialisation. The existing rating is retained, subject to common
  population normalisation. No eligible bouts means no individual bout update.
- Leaving the represented population and subsequently returning does trigger
  reinitialisation from the fixed P1 map at the returning chii.

Thus "returning rikishi" in the entrant policy means a return to the represented
population, not simply a return to competition after missing bouts.

I do not regard the absence of an explicit injury penalty or inactivity decay
as a deficiency. No appearance means no new bout information; the absence
itself does not determine a numerical change in ability. Introducing a decay
rule would add assumptions about its direction, magnitude and timing. Such a
rule would need its own evidential justification. It should not be inserted
simply to make an inactive wrestler's rating follow an expected story.

I also accept reinitialisation after leaving and returning to the represented
population as an intentional policy for this model. The author considers it
appropriate for the exceptional returns at issue; identifying that behaviour
in the code does not establish a defect requiring correction. Both policies
are deliberate, and neither requires a code change or regeneration of the
published outputs on this account. The appropriate interpretation remains an
account supported by the available record, rather than a claim to observe an
inactive wrestler's present physical condition.

## Population normalisation and reported changes

The production replay restores the active population's fixed mean before and
after each basho. Each operation adds the same constant to every active
wrestler and therefore changes neither their order nor their pairwise rating
differences at that instant. It also anchors the ratings carried by survivors
relative to the fixed prior assigned to future entrants. This is separate from
the fixed-point construction of the entrant map.

Reported changes in an individual's rating are consequently not 100%
bout-derived. That should be stated clearly. Whether the normalisation
contribution is practically important is a question of measured magnitude,
not something established by constructing a hypothetical small sign reversal.

The author's expectation, which I regard as reasonable but not yet established,
is:

> Population normalisation contributes little to reported rating changes
> compared with variation generated by competition over the same period. Its
> effect is unlikely to materially alter readers' interpretation, including
> in Makuuchi, where the comparison deserves particular attention.

The small numerical examples used in discussion were illustrative, not
measurements of the production effect. They do not establish either its
significance or its insignificance.

**Experiment: TBD.** A subsequent experiment will frame and test this
expectation using production data. The metric, comparison periods and criteria
for practical importance remain to be decided. This appraisal does not adopt
an experimental design or claim that the expectation has already been tested.

## Peak rating and greatness

A peak is deliberately a momentary maximum. That is a legitimate quantity to
publish; its failure to measure sustained excellence is not a defect in the
peak measure. Longevity, sustained dominance and other conceptions of greatness
answer different questions. The author reports that a separate GOAT package
explores those questions; this appraisal does not assess that package.

The site's implementation records maximum day-end Elo-89 ratings. If the table
uses the word "greatest", the following definition would make its claim clear:

> For this table, we define “greatest” by peak Elo-89 rating: the rikishi who
> reached the highest recorded day-end rating in the period covered by the site.

That is a clear, conditional definition with a calculable answer. It leaves
room for other definitions without weakening this one. Cross-era conclusions
retain the model assumptions described above.

## Implications for the account of the work

The explanation should state the relational meaning of ratings, the role of
the fixed mean, and the distinction between an entrant prior and subsequent
bout evidence. It should describe inactivity as an intentional no-new-evidence
policy and peak rating as a deliberate definition of one kind of greatness.
These are clarifications of what the model does, not proposals to replace its
choices.

The normalisation contribution needs a brief disclosure now and a quantitative
statement once the proposed experiment exists. Prospective evaluation remains
an opportunity to extend the evidence for the frozen model. Neither issue
undoes the retrospective support for adopting Elo-89 or prevents publishing
its results with their intended interpretation.

## Sources

- [Tranche 1: Population Normalisation Policy](15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md), especially the final exact predictive gate.
- [Elo-89 Website Production Handoff](21%20Elo-89%20Website%20Production%20Handoff.md).
- [Production replay](../../elo89/replay.py).
- [Rating-change producer](../../site89/rating_changes.py).
- [Peak-rating producer](../../site89/highest_rating.py).
- [Site model explanation](../../../products/make_site89/prose/Elo-89%20Ratings.html).
- [Site assumptions](../../../products/make_site89/prose/Elo-89%20Assumptions.html).
- [Site account of rating and chii](../../../products/make_site89/prose/Elo-89%20vs%20Chii.html).
