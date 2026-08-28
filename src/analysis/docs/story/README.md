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
14. [Equelo Restart: From B Prime to Full History](14%20Equelo%20Restart%20-%20From%20B%20Prime%20to%20Full%20History.md)
    recovers the shortest current route from the selected post-1988 \(B'\) to a
    new full-history Equelo. It proposes a rating-mass audit as the next bounded
    tranche, followed by a controlled comparison of historical-extension
    policies. It is a restart proposal, not a production-model decision.
15. [Tranche 1: Population Normalisation Policy](15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md)
    records the completed investigation from the dual-`k` audit through
    canonical q=400 prior production, fixed-point controls and the exact
    population-policy predictive gate. It selects fixed \(P_1\) plus
    whole-population mean preservation as Elo-89.
16. [Handoff After Tranche 1](16%20Handoff%20After%20Tranche%201.md) is the
    current restart point. It consolidates vocabulary, model contract,
    evidence, reproducible commands, code paths, qualifications and the bounded
    decisions required before the full-history tranche.
17. [Pre-1989 Bout-Data Completeness and Rating Persistence](17%20Pre-1989%20Bout-Data%20Completeness%20and%20Rating%20Persistence.md)
    records the strict literal-chii completeness audit, its quantitative
    findings and its limitations. It supplies the evidence-based rationale for
    persisting informed ratings across historical result gaps without claiming
    that the effect of missing data on rating quality has been experimentally
    measured.
18. [Preliminary Production Sanity Checks and Fan Challenges](18%20Preliminary%20Production%20Sanity%20Checks%20and%20Fan%20Challenges.md)
    records audience-facing challenges to Equelo2, including the origin and
    use of future-informed priors, the Hakuho--Taiho comparison, inflation and
    stabilisation objections, the contrasting legacy-Equelo result for Kakuryu
    and the 1958 scope boundary. It complements formal predictive evidence with
    historically intelligible production-readiness checks.
19. [Equelo2 Candidate Experiments Handoff](19%20Equelo2%20Candidate%20Experiments%20Handoff.md)
    is the current restart point for the two remaining candidate-gate
    experiments: an audit of the November-1988/January-1989 join and historical
    chii/rating maps, followed by a fixed-pool realised-outcome comparison with
    50--50. It explains the evidential gap each experiment closes and keeps
    already settled questions outside their scope.

The post-1988 model selected in Tranche 1 is named **Elo-89**, with technical
notation \(E_{89}\). It consists of canonical \(P_1\), `q=400`, divisional `k`
and whole-population mean preservation. `BKP1` remains an experimental-family
label and is not, by itself, a synonym for Elo-89.

The intended full-history model at the end of Tranche 2 is named **Equelo2**.
Equelo2 is an objective and model role, not yet a completed contract: Tranche 2
must determine how the differently incomplete pre-1989 evidence joins Elo-89.
The purpose of that extension is to place historical rikishi such as Taiho and
modern rikishi such as Hakuho in one continuous rating account. It is not an
attempt to use pre-1989 results to improve ratings or forecasts after 1988.
Post-1988 scoring of a full-history candidate is principally a compatibility
check: incorporating the earlier record must not materially damage the
established Elo-89 account. Any small improvement is incidental rather than
the benefit Tranche 2 set out to obtain.

## Interpretive rule: future-informed priors and predictive sanity checks

The use of later historical results to construct the entrant priors is
deliberate. The fixed-point process is intended to produce useful initial
values: values which, under the accepted Elo/Equelo update dynamics, lead to a
credible rating history. It is not presented as a way to make out-of-sample
claims about bouts already contained in the construction history.

Scoring the resulting historical replay against a 50--50 predictor is therefore
first a **retrospective sanity check on the constructed system**, including its
initial ratings. It asks whether the completed system extracts useful
predictive information at all. It is not a cheat used to manufacture a claim
of prospective predictive power. Failure even on this deliberately favourable
test would be evidence that the construction had gone seriously wrong; success
shows basic usefulness and coherence, but does not by itself constitute an
out-of-sample validation of the priors.

These three questions must remain separate:

1. **Construction:** do the available historical results yield initial ratings
   which lead to a credible and useful rating history?
2. **Retrospective sanity check:** does that completed historical system beat
   the neutral 50--50 predictor?
3. **Prospective validation:** after a named Equelo2 version, including its
   prior map, is frozen, how well does it predict genuinely later results?

Under this interpretation, future-informed priors are not a defect in the
construction exercise. They become a limitation only if retrospective scores
are misrepresented as prospective evidence. A frozen prior map may later be
tested prospectively; changing it should create a newly identified model
version rather than silently revising Equelo2.

## Reporting convention: when a rating is observed

The canonical published Equelo2 rating for a rikishi in a basho is the
**processed end-of-basho rating**: the value after all eligible bouts and the
post-basho population-normalisation step. Career peaks, records, comparisons
and website displays must use this `end` value. Start-state values required by
the replay implementation are internal process data, not rating observations;
they must not be used for published ratings or records.

The detailed initial inventory remains in
[Elo Documentation Rummage](../2026%2008%2014%20Elo%20Documentation%20Rummage.md).

## Current status

| Part | Status | Notes |
|---|---|---|
| Casual Elo introduction | Draft written | Suitable for further editorial review |
| STEM Elo account | Draft written | Needs editorial and source review |
| Motivation for Equelo | Drafted | Divisional `k`, normalisation and chii-informed initialisation lead into Equelo |
| STEM Equelo account | Draft updated | Distinguishes current production from the adopted 1989-onward entrant priors |
| Consolidated Elo-like account | Proposal requires revision | Its three reading routes remain useful, but its old \(B'=B_{kP}\) endpoint must be replaced by Elo-89 |
| Detailed technical account | Elo-89 portion unblocked; production Equelo blocked | Exact Elo-89 evidence exists; historical scope, anchoring/fallback, eligibility and integration remain unsettled for Equelo |
| Expert/critical account | Audit route proposed | Reproducible model-selection and calibration artifacts provide the present critical record |
| Basic Elo predictive account | Evidence exists | Needs integration into the story |
| Elo-89 predictive account | Retrospective evidence complete | Elo-89 leads log and Brier; prospective and full-history validation remain |
| Low-support/non-monotonicity account | Decision recorded | Preserve experiments; smoothing is reasonable, but the retained policy is not smoothed |
| Model lineage and package triage | Elo-89 selected | Fixed \(P_1\), q=400, divisional `k` and whole-population preservation; historical extension remains |

## Next steps

Tranche 1 is complete, and a proto-Equelo2 full-history baseline now exists.
The current continuation is specified in
[Equelo2 Candidate Experiments Handoff](19%20Equelo2%20Candidate%20Experiments%20Handoff.md).
The initial completeness measurement is recorded in
[Pre-1989 Bout-Data Completeness and Rating Persistence](17%20Pre-1989%20Bout-Data%20Completeness%20and%20Rating%20Persistence.md).
The next work is the bounded 1988/89 boundary and historical-map audit, then
the fixed-pool realised-outcome control. It is not production or website
migration.

The proposed consolidation of the Elo-like account is now specified in
[Proposal: The Consolidated Elo-like Ratings Story](13%20Proposal%20for%20the%20Consolidated%20Elo-like%20Ratings%20Story.md).
The project is deliberately moving next to the definition of full-history
Equelo rather than performing that editorial consolidation immediately.

The M12 investigation established that changing banzuke structure materially
affects empirical chii-to-rating maps. Exact monotonicity is no longer a model
or documentation blocker. Canonical \(P_1\) retains the computed anomalies and
must be described as an entrant-initialisation policy rather than a definitive
mapping from rank to skill.

### Equelo2 candidate gate: fixed-pool predictive control

When asking **“Have we got a candidate for Equelo2 nailed down?”**, include the
following outstanding experiment in the readiness check:

- simulate a fixed pool of rikishi with fixed, unequal latent abilities and no
  entry or departure;
- generate realised bouts chronologically and have Elo forecast each bout
  before applying its update;
- score those forecasts by log loss and Brier loss against the same realised
  outcomes;
- compare them directly with a 50--50 predictor, over multiple reproducible
  runs, and report the size and variability of the advantage.

**Status: experiment required.** Existing fixed-pool toy studies test recovery
of latent gaps, convergence, forecast error relative to latent probabilities
and forgetting of initial conditions. They do not score realised forecasts
against 50--50. Existing historical fair-coin and predictive tests do make
that comparison, but use a changing rikishi population.

This control is intended to demonstrate the predictive content of the Elo
update dynamics in the simplest closed setting. It is not intended to select
the best historical Equelo2 variant or to replace the historical evidence that
Equelo2 as a complete system beats the neutral predictor.

### Comparative observation: Kakuryu in legacy Equelo

All-time peak tables are a subjective diagnostic, not a proof of greatness.
They are nevertheless useful for finding results which knowledgeable readers
would regard as difficult to defend. Using processed basho-end observations,
proto-Equelo2 ranks Kakuryu eleventh, outside its top ten. The older
fixed-supported production Equelo ranks him fifth, with a peak of 2677.432
after 2016/11. The unexpectedly high top-ten position is therefore an
observation about legacy Equelo, not an Equelo2 candidate failure, and it is
not caused by the old site's use of an intrabasho peak. Preserve the contrast
as evidence that the two constructions can produce materially different elite
rankings; do not present Kakuryu's absence from Equelo2's top ten as a problem
which Equelo2 must solve.

Production still uses older Equelo artifacts. Migration remains deliberately
deferred until the historical-extension gate has selected a full-history
construction. Older documents retain their decisions and chronology, but the
handoff, rather than their former “next step” sections, is authoritative for
resuming the work.

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
