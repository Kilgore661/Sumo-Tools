# Rating Statistics Work Plan

## Status

Draft proposal for the next active `make_site2` work tranche.

This document records the intended direction of work. It is not yet a product
specification or implementation design.

The rikishi-chooser defect has been implemented against
`Rikishi Chooser Interaction Model.md`; browser acceptance testing remains.

## 1. Purpose

The next tranche will:

- add further statistical information to rating-related Published Artifacts;
- correct a known defect;
- improve the usefulness of the public site without first requiring a complete
  account of the relationship between Equelo ratings and chii.

The exact statistical additions and the defect shall be recorded before
implementation begins.

## 2. Product Context

Sumo-Tools publishes a mixture of statistical material:

- rating-focused artifacts;
- chii-focused artifacts, including divisions and banzuke structure;
- artifacts in which ratings and chii appear together.

The site is therefore neither exclusively about ratings nor exclusively about
chii.

Ratings and chii may legitimately appear in the same artifact because both are
important ways of understanding rikishi and Grand Sumo. Their joint appearance
must not imply that they are interchangeable measures or that Equelo is a
numerical translation of the banzuke.

## 3. Current Understanding of Ratings and Chii

The project's present position is provisional but sufficient for this tranche:

- Equelo and chii are related to performance.
- They are not the same construction.
- Broad association is expected.
- Flawless monotonic correspondence is not assumed.
- A higher-chii rikishi need not always have a higher Equelo rating.
- The historical mean Equelo rating associated with chii \(c\) need not always
  exceed the mean associated with a lower chii \(c'\).
- A disagreement does not, by itself, establish that either Equelo or the
  banzuke is wrong.

Recent experimental work investigated imperfect correspondence using Elo-like
ratings rather than the production Equelo series. Its conceptual and
methodological conclusions are relevant to Equelo, but its numerical findings
do not automatically describe Equelo.

The project expects that this distinction can be explained coherently. That
explanation remains to be completed.

## 4. Working Decision

Imperfect rating-chii correspondence shall not block development of useful
rating-related artifacts.

This is a pragmatic decision, not a conclusion that the issue has disappeared.

The tranche may proceed on the working assumption that rating-based information
about rikishi remains useful independently of whether ratings reproduce chii
order. Examples include:

- current or historical rating;
- rating change;
- peak rating;
- rating trajectory;
- comparison of rikishi by rating;
- rating-based records.

The tranche shall not attempt to make Equelo agree more closely with chii merely
to simplify public presentation.

## 5. Artifact Classification

Each affected artifact shall be classified before its changes are specified.

### 5.1 Rating-focused

The artifact principally answers a question about ratings or rikishi rated by
Equelo.

Chii may appear as contextual information. A chii column does not by itself make
the artifact an analysis of rating-chii correspondence.

### 5.2 Chii-focused

The artifact principally answers a question about official standing, divisions,
banzuke movement or chii history.

The imperfect-correlation issue does not arise unless ratings are introduced.

### 5.3 Combined

The artifact makes ratings and chii jointly prominent or invites readers to
interpret their relationship.

Combined artifacts require explicit review. The review shall ask:

> Is chii contextual information, or is the artifact making or inviting a claim
> about the relationship between chii and rating?

The answer determines the explanatory treatment required.

## 6. Publication Guardrails

Changes made during this tranche shall observe the following rules:

- Public wording shall call the metric `Equelo` or an `Equelo rating`.
- Technical production names such as `fixed_supported` shall appear only where
  provenance requires them.
- Chii and Equelo may be shown together.
- Their juxtaposition shall not imply equivalence.
- Rating-chii inversions shall not automatically be labelled anomalies.
- The site shall not claim that average process ratings must decline
  monotonically through chii order.
- Public statistics shall distinguish individual process ratings from
  entrant-initial ratings and rating landmarks.
- Necessary qualifications should be proportionate to the claim being made.

A rating-focused table containing a contextual chii column may require only a
short note. An artifact explicitly aggregating rating by chii requires the
fuller companion account.

## 7. Typical Equelo Ratings

The present `Typical Equelo Ratings` page is no longer an adequate
uncomplicated explanation of the Equelo scale.

Its monotonic table contains constructed public rating landmarks. It is not an
empirical demonstration that historical mean process ratings are monotonic by
chii.

The table is likely to become an early exhibit in a replacement account
explaining:

- why a monotonic chii-to-rating ladder is attractive;
- how the current landmarks were constructed;
- why the ladder must not be mistaken for observed mean ratings by chii;
- what the rating-chii investigations established;
- what remains unknown;
- why Equelo can remain useful without reproducing chii.

Producing that complete account is not a prerequisite for beginning this
tranche. Changes made now must not deepen the current implication that the
landmark table is an observed correspondence.

## 8. Proposed Work

The tranche should proceed in this order:

1. Complete browser acceptance testing of the implemented rikishi-chooser
   correction.
2. Inventory the rating-related artifacts affected by the proposed statistical
   additions.
3. Classify each artifact as rating-focused, chii-focused or combined.
4. Specify each proposed statistic:
   - question answered;
   - source rating series;
   - time point or interval;
   - population and History scope;
   - aggregation;
   - visible representation;
   - required Notes or gloss.
5. Decide whether the additions change any PA model or producer contract.
6. Implement the defect correction with focused tests.
7. Implement the agreed statistical additions through their owning producers
   and `make_site2` models.
8. Build and inspect the affected pages.
9. Review every affected artifact for unintended rating-chii claims.
10. Record the remaining work required for the companion account and the
    replacement of `Typical Equelo Ratings`.

## 9. Out of Scope

Unless separately agreed, this tranche shall not:

- redesign the Equelo model;
- force Equelo into monotonic agreement with chii;
- rerun the correlation investigation using production Equelo;
- complete the definitive companion account;
- treat `Typical Equelo Ratings` as empirical mean rating by chii;
- redesign unrelated chii-only artifacts.

## 10. Risks

The principal publication risk is not that ratings and chii differ. It is that
an artifact or its wording causes readers to infer a relationship stronger than
the evidence supports.

Additional risks include:

- using rating landmarks where process ratings are required;
- mixing before-basho and after-basho rating semantics;
- presenting copied rating artifacts that are incoherent with the selected
  History;
- adding statistics without stating their population, period or aggregation;
- allowing a short caveat to substitute for a necessary methodological
  explanation.

## 11. Intended Outcome

At the end of the tranche:

- the known defect is corrected;
- the selected rating-related artifacts expose the agreed additional
  statistics;
- each statistic has a documented producer and public meaning;
- combined rating-chii presentation has been reviewed;
- no new feature depends on flawless rating-chii correlation;
- the unresolved correlation issue is recorded as companion explanatory work
  rather than hidden or treated as solved.

## Next

Identify the defect and enumerate the proposed statistical additions, then
convert each accepted addition into requirements and PA/producer contracts
before implementation begins.
