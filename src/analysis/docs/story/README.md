# Elo and Equelo Story Workspace

## Purpose

This folder records how the project intends to explain Elo and Equelo to
different readers. It is a working documentation plan, not yet the finished
site prose and not a defence of conclusions that the experiments have not
established.

The immediate purpose is to keep four things separate:

1. how Elo works;
2. the problems Equelo was designed to address;
3. how Equelo works;
4. evidence about the utility and limitations of either system.

This separation is important because a mechanical improvement, such as
controlling rating-scale drift, does not by itself establish predictive
validity. Equally, disagreement between Equelo and chii is not automatically
either a defect or an insight.

## Documents

1. [Reader Layers](01%20Reader%20Layers.md) defines the casual, STEM,
   detailed-technical and expert/critical layers and the
   progressive-disclosure policy.
2. [Narrative and Validation Structure](02%20Narrative%20and%20Validation%20Structure.md)
   records the agreed route from Elo to Equelo and keeps construction separate
   from validation.
3. [Elo Introduction for the Casual Reader](03%20Elo%20Introduction%20for%20the%20Casual%20Reader.md)
   is the current first-layer draft.
4. [Draft: A Standard Account of Elo](06%20Draft%20Standard%20Elo%20Account%20for%20the%20STEM%20Reader.md)
   is the current STEM-layer draft of the ordinary Elo mechanics and their
   historical-sumo complications. It is rendered to HTML by
   `render_stem_account.ps1`, along with every other Markdown document in this
   folder.
5. [Draft: How Equelo Changes Elo](07%20Draft%20Equelo%20Account%20for%20the%20STEM%20Reader.md)
   is the current STEM-layer construction account. It explains divisional
   `k`, normalisation and chii-informed initialisation; exact implementation
   details belong in the planned detailed-technical account.
6. [Evidence and Source Map](04%20Evidence%20and%20Source%20Map.md) points to the
   existing research record and identifies what each source contributes.
7. [Open Questions and Experiments](05%20Open%20Questions%20and%20Experiments.md)
   distinguishes established findings, expectations and work still required.
8. [The M12 Problem: Consolidated Research Record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md)
   is the single entry point for the question, chronology, evidence and final
   position.
9. [M12 Experiment Catalogue](09%20M12%20Experiment%20Catalogue.md) records the
   reproducible code paths, commands, matched artifacts and headline results.
10. [Initial Rating Policy](10%20Initial%20Rating%20Policy.md) is the normative
    decision that the next integration and predictive-validation work must
    implement.
11. [Production Equelo Definition: Remaining Decisions](11%20Production%20Equelo%20Definition%20-%20Remaining%20Decisions.md)
    distinguishes the decisions still needed to define one maintained
    production model from later evaluation questions and minor editorial work.
    It also records, without adopting, the proposal to treat the 1989-onward
    priors as historically transferable under a stable-ordinal-meaning
    assumption, together with the qualifications and completion choices that
    this would require for pre-1989-only ranks.
12. [Elo-family Model Lineage and Analysis Triage](12%20Elo-family%20Model%20Lineage%20and%20Analysis%20Triage.md)
    records the agreed route from the definitive post-1988 Basic Elo baseline,
    through selection of a successor \(B'\), to a new full-history Equelo. It
    also defines the classification scheme for separating current model work,
    production legacy, useful negative evidence and tangential explorations
    across the analysis packages.
13. [Proposal: The Consolidated Elo-like Ratings Story](13%20Proposal%20for%20the%20Consolidated%20Elo-like%20Ratings%20Story.md)
    defines the proposed near-publishable web account from the casual
    explanation through the selection of \(B'=B_{kP}\). It supplies a contents
    structure, three reading routes, claim boundaries, acceptance criteria and
    pointers to the supporting research and generated evidence. The proposal
    deliberately stops where the next full-history Equelo construction begins.

The detailed initial inventory remains in
[Elo Documentation Rummage](../2026%2008%2014%20Elo%20Documentation%20Rummage.md).

## Current status

| Part | Status | Notes |
|---|---|---|
| Casual Elo introduction | Draft written | Suitable for further editorial review |
| STEM Elo account | Draft written | Needs editorial and source review |
| Motivation for Equelo | Drafted | Divisional `k`, normalisation and chii-informed initialisation lead into Equelo |
| STEM Equelo account | Draft updated | Distinguishes current production from the adopted 1989-onward entrant priors |
| Consolidated Elo-like account | Proposal written | Three reading routes cover casual, STEM and technical/audit needs through \(B'=B_{kP}\) |
| Detailed technical account | Elo-like portion unblocked; production Equelo blocked | Exact \(B'\) evidence exists; historical scope, anchoring/fallback, eligibility and integration remain unsettled for Equelo |
| Expert/critical account | Audit route proposed | Reproducible model-selection and calibration artifacts provide the present critical record |
| Basic Elo predictive account | Evidence exists | Needs integration into the story |
| Equelo predictive account | Experiment required | Must use a directly comparable protocol |
| Low-support/non-monotonicity account | Decision recorded | Preserve experiments; smoothing is reasonable, but the retained policy is not smoothed |
| Model lineage and package triage | \(B'\) selected provisionally | \(B'=B_{kP}\); the historical extension and producer-level Equelo audit remain to be completed |

## Next steps

The proposed consolidation of the Elo-like account is now specified in
[Proposal: The Consolidated Elo-like Ratings Story](13%20Proposal%20for%20the%20Consolidated%20Elo-like%20Ratings%20Story.md).
The project is deliberately moving next to the definition of full-history
Equelo rather than performing that editorial consolidation immediately.

The M12 investigation established
that changing banzuke structure materially affects empirical chii-to-rating
maps, but did not identify one model that explains or removes every reversal.
That is no longer treated as a documentation blocker.

The project will retain the reproducible, east/west-paired 1989-onward
contextual curve as its entrant-prior policy. Smoothing that curve would be a
reasonable modelling choice, but not smoothing is also reasonable because the
curve is already adequate for shortening the initialisation gap. The project
therefore chose not to smooth. Public prose must distinguish these chosen
priors from uniquely estimated chii values and from ratings subsequently
learned from bout results.

The immediate work is to implement the [Initial Rating Policy](10%20Initial%20Rating%20Policy.md),
then conduct a prospective, like-for-like predictive comparison of Equelo with
Basic Elo accompanied by sensitivity tests using reasonable alternative
priors, which may include smoothed comparators. Start with the
[consolidated M12 record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md);
[Open Questions and Experiments](05%20Open%20Questions%20and%20Experiments.md)
records the wider validation programme.

Before the detailed technical account presents one definitive production
calculation, the outstanding model and integration decisions in
[Production Equelo Definition: Remaining Decisions](11%20Production%20Equelo%20Definition%20-%20Remaining%20Decisions.md)
must be resolved. In particular, current production still uses the older
fixed-supported priors, and the present calculation ignores a material number
of bouts whose win/loss result is known but whose kimarite is missing.
The possible backward transfer of the 1989-onward priors is recorded there as
a parked proposal rather than a decision, so it need not interrupt work on the
other production questions.

The current route is set out in
[Elo-family Model Lineage and Analysis Triage](12%20Elo-family%20Model%20Lineage%20and%20Analysis%20Triage.md):
first compare the post-1988 candidate models with the definitive Basic Elo
baseline and select \(B'\); then extend \(B'\) over the incomplete earlier
record to construct the next full-history Equelo. A producer-by-producer audit
will use the statuses defined there to distinguish germane code and evidence
from production legacy, retained negative results and tangential exploration.

## Working discipline

Claims in this folder and the eventual prose should be recognizable as one of:

- **Definition**: what a calculation or term means;
- **Intended property**: what a design choice is meant to achieve;
- **Established finding**: what an experiment currently supports;
- **Expectation**: what is provisionally anticipated;
- **Open question**: what is not yet known;
- **Experiment required**: what evidence is needed before making a claim.

The final account may be readable as one continuous story, but the underlying
research record should preserve these distinctions.
