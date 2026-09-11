# Strength, Purpose and Model Bias

## Status and intended use

Provisional lab note, recorded on 11 September 2026 from a discussion begun
on 10 September. This preserves the reasoning reached in that discussion,
including qualifications and unresolved questions. It is a yardstick against
which to examine the details of the final rating model, not a completed
appraisal of that model.

This is not approved prose for the production "about this website" documents.
It does not change the rating implementation or supersede the historical
documents discussed below. No new empirical investigation was performed for
this note.

## 1. Where the question began

Several project documents contrast an "epistemological" approach, treated as
desirable, with a "teleological" approach, treated as suspect. In practice,
the latter often means adding or adjusting mechanisms until a model produces
an expected sporting conclusion.

The concern raised in this discussion was that this opposition is too broad.
A model can serve a purpose and still be scientifically sound. Having a goal
does not itself invalidate the representation of the system. The question is
whether the attributes being represented and the grounds for evaluating the
model are sufficiently specified and supported.

Here we use "purpose-directed" for that broad idea, without attempting to
settle the philosophical meaning of teleology. "Tuning to preferred
conclusions" describes the particular danger more accurately than a general
prohibition on teleology. Epistemic justification and having a purpose are
not mutually exclusive.

## 2. The production-efficiency example

Suppose factory efficiency means time taken to produce one unit. Alternatively,
it might mean resources consumed per unit, with the relevant resources and
their units specified. Each definition gives a particular question against
which a model can be assessed.

If factory A uses less time and factory B uses fewer resources, those
observations do not settle which is more efficient in an unspecified combined
sense. A single combined ranking requires a trade-off between the attributes.
Evidence about production does not by itself determine which trade-off people
ought to value.

If that trade-off remains unresolved, a modeller can add a feature or alter a
weight because it makes the preferred factory come first, while describing
the change as a more accurate account of efficiency. A preference has then
entered the result under the appearance of improved measurement.

Lack of universal agreement is not itself disqualifying. Different investigators
can choose different explicit definitions and make defensible conditional
claims. A subjective choice can be disclosed and studied. Conversely, a
precise or widely agreed target does not guarantee sound methods. The concern
is treating an unresolved choice of definition as an empirical fact, or using
the desired answer to justify that choice.

## 3. Applying this to sumo strength and greatness

"Greatness" might combine peak performance, longevity, achievements and the
opposition faced. A formula can specify such a combination exactly without
establishing that it is the correct meaning of greatness. "Strength" sounds
narrower, but its real-world meaning also needs to be stated: strength against
whom, at what time, under what conditions, and judged by what evidence?

This led to a distinction between the exact output of an algorithm and the
real-world attribute that output is claimed to measure. Precision in the
first does not establish validity in the second.

## 4. What Elo delivers

The discussion initially proposed that Elo measures the capacity to beat an
opponent drawn from the population a rikishi "usually" faces, taking account
of "recent" performance. Both qualifications expose substantive questions.

We then refined the starting point: the principal Elo deliverable of interest
here is a rating difference and its associated estimated bout-winning
probability. Individual ratings serve as coordinates for those differences.
A common additive shift leaves all contemporaneous pairwise differences and
their implied probabilities unchanged.

The pairwise claim differs from expected success against a population of
opponents. The latter requires averaging pairwise probabilities over a
specified opponent distribution. Changing that distribution can change the
expected winning percentage without changing any rating.

Two questions should therefore be kept visible:

- What does the model assert? A specified rating difference maps to an
  estimated probability for a particular matchup.
- What supports that assertion? The realised sequence of opponents and
  outcomes, processed through the chosen update rule and other policies.

The irrelevance of a common offset to current pairwise predictions does not
make every anchoring policy inconsequential. Relationships to future entrant
ratings and comparisons across times require their own examination.

## 5. The opponent population and the torikumi

The user described an informal impression of Makuuchi scheduling: the first
eight or so bouts tend to match similar chii, while the last seven or so tend
to match similar current scores. This is recorded as a working impression,
not an established scheduling rule. Attempts to specify it precisely have
proved difficult. The discussion did not establish corresponding patterns
for Juryo or the lower divisions, nor imply that no patterns exist there.

The realised schedule is observable even when the JSA's selection process is
not fully understood. Reconstructing that process is not required to compute
Elo ratings. It does matter when assessing which comparisons the evidence
supports and whether a result extends to less frequently observed matchups.

If one scalar per rikishi cannot adequately represent all pairwise outcomes,
for example because styles interact, the opponents actually faced can affect
the scalar summary obtained. This is a modelling possibility, not a finding
about the size of such effects in sumo. It shows why the schedule may matter
to the interpretation of "strength", as well as to estimation precision.

## 6. What counts as recent?

Elo's update process is explicit, but "recent" need not mean a fixed number of
bouts, a calendar window or a universal half-life. In ordinary bout-updated
Elo, inactivity alone does not remove the influence of earlier evidence.
The persistence of that influence depends on update parameters and the
subsequent sequence of opponents and expectations.

The user recalled a possible half-life investigation. A relevant investigation
was found in this repository:
[Completed Investigation: Forgetting in a Fixed-Skill Toy World](../forgetting/docs/Completed%20Investigation%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md).

That work defines forgetting as loss of sensitivity to an initial rating map.
It compares differently initialised processes receiving identical subsequent
schedules and outcomes. Its completed findings concern a fixed-skill,
round-robin toy world. They do not establish a half-life for historical sumo
or a universal effective window of recent performance.

It offers a way to investigate the persistence of an earlier state. Translating
that into a claim about the age of performance evidence in the final model
would require further work.

## 7. Conclusion reached in the discussion

When "strength" means a real-world attribute rather than merely the output of
a declared formula, both "what do Elo ratings measure?" and "what do Elo
rating differences measure?" remain insufficiently specified unless that
interpretation is independently developed.

Without such a specification, there is no clear criterion for distinguishing
a better measurement of strength from a more agreeable result. Any feature
or adjustment is consequently highly susceptible to bias: an expected ranking
can motivate a change that is then justified as capturing a neglected aspect
of strength.

This applies to the original model as well as subsequent changes. A single
scalar, update rate, initialisation policy and population anchor already
embody commitments. Leaving them unchanged does not make them neutral.

The qualification is that not every choice is equally unsupported. A change
may improve predictions under a declared evaluation, repair a demonstrated
data problem or follow from independently supported assumptions. These are
grounds for particular claims. They do not automatically establish improved
measurement of an unrestricted real-world notion of strength.

The working principle is:

> Where the real-world attribute is insufficiently defined, neither a model's
> plausibility nor agreement with expected rankings establishes measurement
> validity. Every modelling choice is susceptible to importing preferences
> into the result. Choices should therefore be justified against explicit,
> independently assessable claims, and any broader interpretation as
> "strength" or "greatness" should remain conditional.

The objection is therefore to an undefined target permitting preferred
conclusions to guide model design. It is not an objection to a model having
a purpose.

## 8. A yardstick for reviewing the final model

For each significant feature or adjustment, ask:

1. What particular claim is this feature intended to support? Is it about
   pairwise probabilities, historical representation, an institutional use,
   or a broader interpretation of strength?
2. Which parts define the chosen measure, and which are empirical assumptions
   about sumo? What supports those assumptions independently of the rankings
   we would like to obtain?
3. What evidence could count against the choice? If prediction is the
   criterion, are the evaluation population and procedure specified?
4. How do the actual schedule and persistence of earlier evidence limit the
   interpretation? Are "usual opponents" or "recent performance" being used
   without sufficient definition?
5. Would we retain the justification if the resulting ranking were surprising
   or unwelcome? Is a proposed repair supported beyond its effect on favoured
   rikishi, chii or eras?
6. Does the reported conclusion stay within what was tested, while exposing
   conventions and unresolved interpretations?

These questions are an aid to judgement, not a new mechanical acceptance
test or a demand to reconstruct the entire scheduling process. The present
note has not applied them to every detail of the final model and does not
declare that model valid or invalid.

## 9. Documents that prompted or inform this note

- [Analysis README](../README.md), "Epistemic Guardrail": the central
  epistemological/teleological contrast.
- [What Ratings Might Say About Grand Sumo](../toy_elo/docs/What%20Ratings%20Might%20Say%20About%20Grand%20Sumo.md),
  "Anti-Teleology Guardrail": the useful warning against adding mechanisms
  until an interpretation feels satisfying.
- [Elo-89 Rating System Appraisal](story/22%20Elo-89%20Rating%20System%20Appraisal.md),
  "Further evaluation: uncertainty and comparison with FIDE": minimises
  teleological input and separately recognises the ambiguity of strength.
- [Divisional Averages](../divisional_averages/README.md),
  "The epistemological and teleological boundary": asks whether a correction
  has independent grounds or simply obtains desired numbers.
- [GOAT comparison framework](../../products/GOAT/docs/comparison-framework.md):
  specifies individual factors without claiming their ordering settles
  greatness.
- [Foundations: What Is This About?](../../../docs/Foundations/01-what-is-this-about.md):
  treats the model as an explicit, selective lens for an investigation.
- [teleological.txt](../../../teleological.txt): an earlier conversation about
  the production-efficiency example. It is background, not an authority for
  philosophical terminology. Its categorical claims about subjective targets
  and mathematical precision are qualified in this note.

The historical wording is preserved in those sources. This lab note records
the refinement to use when reviewing them and the final model later.

## 10. Subsequent discussion: comparison with FIDE, deferred

### The present assessment stands independently

The author clarified that the work establishing the soundness of Elo-89 was
done without reference to FIDE. The informal assessment the author takes from
that work is:

> As far as it goes, it seems OK. There are some attack surfaces, but it is
> not clear, given the inherent messiness of data pertaining to humans, how
> anyone else might handle this in a quantifiably different, better way.

This records the author's present judgement, not final wording for readers.
It neither establishes that no better method exists nor requires such a method
to be ruled out before the model can be useful. It expresses a bounded
acceptance based on the work already done, with remaining limitations visible.

The current purpose is to arrive at an honest assessment of Elo-89 for
interested readers. Comparison with FIDE does not presently help that task.
It is not a prerequisite for accepting Elo-89, a proposed defence of its
limitations, or an additional investigation now required for publication.

### How the comparison arose

The discussion imagined a reader who understands the broad win/loss update
idea but suspects that detailed choices were "picked out of a hat". K policy
was one concrete example. The author subsequently emphasised that the question
concerned all modelling choices, including initialisation and boundary cases.

One possible reply initially considered was to ask whether chess's established
Elo implementation handles these matters any better. We distinguished choices
derived from explicit requirements, choices supported by empirical comparisons,
examined practical conventions, and choices made to obtain preferred rankings.
The existence of judgement does not itself establish arbitrariness. Equally,
the amount of research is not a substitute for explaining what it supports.

For K, explaining the purpose of responsiveness and justifying exact numerical
values are separate tasks. The same distinction applies more widely: a reason
to have a policy does not uniquely establish its particular implementation.
Evidence may support several reasonable choices rather than one exact value.

The author separated two questions that the initial hypothetical had combined:

1. How does Elo-89 compare with FIDE for soundness?
2. Is a perceived weakness present in one system, the other, or both?

The systems share an Elo-family construction and face related questions about
limited evidence, responsiveness, entry, departure and eligible results. That
does not establish equal soundness, identical problems, or equally effective
responses. A shared challenge, a policy addressing it and an evidenced defect
are different things. In chess the expected score also includes draws; in the
binary sumo setting expected score is winning probability.

### What was checked, and what was not established

A limited check of FIDE's published regulations confirmed explicit policies
for K, initial ratings, unplayed games, inactivity and the rating floor. This
was enough to show that practical choices also exist there. It was not an
audit of their derivation, implementation, empirical success or applicability
to sumo, and did not establish comparative soundness.

Population drift prompted a further correction. The author had understood the
2024 FIDE revision as a response to long-term inflation, illustrated by the
loss of exclusivity of Fischer's historically exceptional 2700-plus rating.
The contemporary reform announcement instead describes deflation. Its one-off
adjustment increased ratings below 2000 by 40% of their distance from 2000,
leaving ratings of 2000 and above unchanged. The supporting Sonas report also
describes deflation. A later FIDE anniversary article calls the issue
"inflation", creating a discrepancy in FIDE's published wording.

The author questioned whether this inconsistency prevented us from knowing
the motivation. The assistant's qualification was that contemporary technical
and policy documents provide stronger evidence of the published rationale
than a later retrospective summary. This did not establish all institutional
motivations, the correctness of the diagnosis or the soundness of the remedy.
No attempt to resolve those larger questions was completed.

The Fischer example raised a separate issue of comparisons across eras.
More players exceeding a historical threshold does not by itself distinguish
scale drift from changes in population size or playing ability. Nor does an
earlier rise at the top exclude a later deflationary effect elsewhere. Entry
and departure can create drift, but its direction and mechanism should not
be assumed identical in chess and sumo.

Sources consulted in this limited discussion, retained for future retrieval:

- [FIDE Rating Regulations](https://handbook.fide.com/chapter/B022024),
  particularly sections 5, 7 and 8. The page inspected included the October
  2025 amendment despite its March 2024 title.
- [New FIDE Rating and Title Regulations come into effect](https://www.fide.com/new-fide-rating-and-title-regulations-come-into-effect/),
  the contemporary reform announcement.
- [Sonas final report, 11 January 2024](https://qc.fide.com/wp-content/uploads/2024/03/Sonas-Final-Report-as-of-11-JAN-2024.pdf),
  supporting technical material identified during the discussion; not fully
  appraised here.
- [Anniversary of Arpad Elo](https://www.fide.com/anniversary-of-arpad-elo-rating-system-that-changed-chess-world/),
  the later article containing the conflicting "inflation" description.
- [FIDE History](https://museum.fide.com/fide-history), recording Fischer at
  2760 and Spassky at 2690 on the first official 1971 list.

### Decision and future use

The author decided not to pursue a FIDE comparison now. It is a difficult
investigation in its own right and would distract from assessing Elo-89 on
its own evidence. The initially considered response, "FIDE uses Elo and its
model is no better", is not the intended argument and was never established
by this discussion.

The assistant's earlier preference for Elo-89's philosophy, including wording
in the existing appraisal, must not be treated as a demonstrated finding of
greater soundness. This note records that limit without rewriting the older
appraisal or production prose.

The discussion is retained because the author may later want to investigate
further, and readers may make claims such as "FIDE doesn't have this problem".
If that happens, the useful starting point is the specific alleged problem:
whether it arises in each system, how each responds, what evidence supports
the response and what uncertainty remains. An overall judgement of comparative
soundness would require substantially more work. Neither investigation is an
active commitment arising from this note.
