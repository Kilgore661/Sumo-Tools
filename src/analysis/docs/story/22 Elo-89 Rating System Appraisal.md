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

The question previously marked TBD has now been investigated in the separate
[Normalisation Investigation](../../elo89_normalisation/docs/Normalisation%20Investigation.md).
That account preserves the original question, the choices explored and the
reproducible evidence, so this appraisal need only summarise the outcome.

Normalisation can contribute appreciably to particular reported rating
changes, although positive and negative adjustments substantially cancel over
time. Across all 51 sliding 12-basho windows starting from January 2016 through
July 2024, every eligible Makuuchi and Juryo observation had a net signed
normalisation contribution within ±1% of its end rating. This covers 2,099
Makuuchi and 1,323 Juryo wrestler-window observations, with the latest windows
ending in July 2026. Windows require continuous representation and classify
division at the end; they overlap and are not independent statistical tests.

The recent cutoff is an explicit exploratory choice. The full-history,
all-division comparison remains part of the evidence: every Makuuchi and Juryo
12-basho observation was within ±5%, and only 219 of 113,500 observations
across all divisions exceeded that interval, all in Jonidan or Jonokuchi.
These percentages are practical benchmarks on the published rating scale,
not origin-independent measures of predictive distortion or whole-career
normalisation totals.

Having examined these results and their interpretation, the author and I
regard the observed effects as acceptable and find no sufficient reason in
this investigation to change Elo-89. This resolves the TBD through an informed
judgement of acceptability, rather than a claim that every effect is negligible.
Reported changes nevertheless include population normalisation and should
not be described as wholly bout-derived.

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

The normalisation contribution should be disclosed alongside reported rating
changes, supported by the completed investigation summarised above. Its detailed
interpretation and experimental choices remain in the separate account.
Prospective evaluation remains an opportunity to extend the evidence for the
frozen model; it does not undo the retrospective support for adopting Elo-89
or prevent publishing its results with their intended interpretation.

## Sources

- [Tranche 1: Population Normalisation Policy](15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md), especially the final exact predictive gate.
- [Elo-89 Website Production Handoff](21%20Elo-89%20Website%20Production%20Handoff.md).
- [Production replay](../../elo89/replay.py).
- [Rating-change producer](../../site89/rating_changes.py).
- [Peak-rating producer](../../site89/highest_rating.py).
- [Site model explanation](../../../products/make_site89/prose/Elo-89%20Ratings.html).
- [Site assumptions](../../../products/make_site89/prose/Elo-89%20Assumptions.html).
- [Site account of rating and chii](../../../products/make_site89/prose/Elo-89%20vs%20Chii.html).

## Coda: response to an outside AI appraisal

An outside AI appraisal supplied by the author endorsed Elo-89 as a useful,
well-founded system worth retaining. It praised opponent-aware updates,
rank-based initialisation, divisional update rates, retrospective evidence and
candid documentation. It also suggested qualifications concerning normalisation,
returning wrestlers, predictive validation, historical comparisons and the
visibility of individual rating evidence.

I broadly agree with that assessment. It supports the same overall conclusion
we reached: Elo-89 is useful, defensible and worth retaining. Three passages
need refinement to preserve distinctions established in this investigation.

**Normalisation.** Describing it as a small influence rather than a substantial
obstacle to interpreting rating changes slightly blurs our distinction. The
recent ±1% result concerns the contribution relative to the ending rating,
not relative to the rating change. An acceptable contribution to the rating
can still appreciably affect a particular reported change. Our conclusion was
acceptance with disclosure. The detailed reasoning remains in the separate
[Normalisation Investigation](../../elo89_normalisation/docs/Normalisation%20Investigation.md).

**Returning wrestlers.** Treating resets as an outstanding weakness repeats a
concern we resolved. Missing bouts while remaining on the banzuke does not
trigger a reset. Reinitialisation applies after leaving the represented
population and returning. The author regards that policy as appropriate for
the exceptional cases involved. Clarifying it is useful; presenting it as an
unresolved deficiency is unnecessary.

**Historical comparisons.** Caution is reasonable, but the reason should be
the assumptions needed to interpret a common rating anchor across eras. The
recent normalisation result neither establishes nor refutes those assumptions.
We also examined normalisation across the full represented history, not only
recent years.

I agree with the predictive-evidence qualification: prospective evaluation
would extend the evidence. It should remain an opportunity to strengthen
validation, rather than an implied condition for accepting the system.

Showing how much individual evidence supports a rating is a plausible
enhancement, but it was not established as a requirement by our investigation.
I would describe it as optional rather than the necessary next step.

## Further evaluation: uncertainty and comparison with FIDE

This evaluation was added on 9 September 2026 in response to two questions:
how well Elo-89 handles the vagueness of a messy human system, and how it
compares with FIDE's Elo-like chess ratings. The intended criterion is to be
as epistemological as possible, keeping teleological input to a well-reasoned
minimum. This is an interpretive assessment, not a new validation run.

My judgement is that Elo-89 handles the messiness of sumo well for a compact,
evidence-based account of performance. Its treatment of uncertainty is sensible
but incomplete. Compared with FIDE, it is more consistently directed towards
understanding performance, although that does not establish greater predictive
accuracy.

### Handling a messy human system

Here, "epistemological" means estimating what the evidence supports, and
"teleological" means shaping the calculation to produce some desired sporting
or institutional outcome. On that distinction, Elo-89 does well.

Several choices show appropriate restraint:

- Results supply evidence without becoming verdicts. An upset changes the
  estimates; it does not establish that the winner is now the stronger
  wrestler. Probabilistic predictions accommodate inconsistency.
- Chii supplies informed starting evidence. This uses existing knowledge when
  bout evidence is scarce, while allowing subsequent results to move the
  rating. It does not continually force ratings back into agreement with
  official rank.
- Inactivity does not attract an invented penalty. Retaining a rating while
  a wrestler remains represented avoids assigning a numerical decline merely
  because a plausible story suggests one.
- The model is tested against outcomes. The reported log-loss improvement
  over Basic Elo, 0.675629 versus 0.682753, is modest but relevant evidence
  that the additional machinery earns its place. This remains retrospective
  evidence, as explained above.

Using institutional rank as evidence is not inherently teleological. The
distinction is between "rank contains information about likely performance"
and "the ratings ought to reproduce rank". Elo-89 largely observes that
distinction.

Its limitations become clearer if we separate three kinds of messiness.

**Unpredictable outcomes** are handled explicitly through probabilities.
However, unexplained variation includes both chance and omitted influences:
injury, form, styles and circumstances. The model does not distinguish these.

**Uncertainty about the estimate** is handled only indirectly. Two wrestlers
can have the same rating despite very different amounts or recency of
supporting evidence. The production model maintains point estimates, rather
than individual uncertainty distributions. A 60% forecast does not tell us
how securely that 60% has been estimated.

This matters particularly for inactivity: holding the estimate steady need
not mean holding confidence steady. The existing policy is defensible without
treating an inactive wrestler's rating as an equally well-supported estimate
of present condition.

**Vagueness about what "strength" means** is handled through an operational
definition. Elo-89 provides a particular account of competitive performance.
It cannot settle every reasonable meaning of ability, dominance or greatness.
A precise peak-rating table answers a precise question; it does not eliminate
the ambiguity of "greatest".

The fixed population mean is its most consequential interpretive convention.
Uniform shifts preserve current rating differences, but the anchor also
affects relationships with future entrants and the interpretation of
comparisons across eras. This is a justified modelling choice, not something
bout results uniquely establish.

I would therefore describe Elo-89 as disciplined simplification with candid
assumptions. Its precision is computational; the knowledge expressed remains
conditional. Making individual evidential support more visible could
strengthen that communication, but this review does not establish it as a
prerequisite for accepting the system.

### Comparison with FIDE

Both systems compress changing human performance into a single rating and
update it from results relative to expectations. Neither basic approach fully
represents uncertainty about each estimate, contextual effects or the
ambiguity of cross-era strength.

The clearest difference is their purpose. Elo-89 can concentrate on an
explanatory account alongside the banzuke. FIDE must also administer a
consequential competitive system. Its published justifications explicitly
combine accuracy with fairness and institutional concerns.

For example, FIDE's October 2025 amendment removed the 400-point
rating-difference cap for players rated 2650 and above while retaining it
below that threshold. FIDE justified the change through accuracy, fairness
and competitive integrity. That introduces an institutional boundary into
the update rule that Elo-89's continuous probability formula does not have.
See [FIDE's amendment announcement](https://www.fide.com/fide-council-approves-targeted-amendment-to-rating-regulation/).

It would nevertheless be unfair to classify every FIDE intervention as
teleological distortion. Its 2024 reform responded to evidence of rating
deflation and included changes to initial ratings and the rating floor.
An intervention intended to correct a demonstrated measurement problem can
be epistemically justified. See [FIDE's explanation of the 2024 reform](https://www.fide.com/new-fide-rating-and-title-regulations-come-into-effect/).

| Criterion | Assessment |
|---|---|
| Keeping institutional goals out of the estimate | Elo-89 has the clearer separation. |
| Accommodating variable results | Both have the fundamental strength of probabilistic Elo modelling. |
| Expressing uncertainty about individual ratings | Neither basic approach provides a complete account. |
| Making assumptions explicit | Elo-89's appraisal is particularly strong. |
| Demonstrated predictive superiority | Not established by the available comparison; its tests concern other sumo models, not FIDE on comparable evidence. |

For the stated aim, I prefer Elo-89's design philosophy. Its strongest
epistemic virtue is that it makes a useful, testable claim of limited scope
and explains the conventions supporting it. FIDE faces additional
institutional demands; those demands can justify its choices without making
them the best choices for this website.
