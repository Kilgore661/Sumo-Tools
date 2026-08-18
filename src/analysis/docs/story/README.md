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
    decision that the smoothing and predictive-validation work must implement.

The detailed initial inventory remains in
[Elo Documentation Rummage](../2026%2008%2014%20Elo%20Documentation%20Rummage.md).

## Current status

| Part | Status | Notes |
|---|---|---|
| Casual Elo introduction | Draft written | Suitable for further editorial review |
| STEM Elo account | Draft written | Needs editorial and source review |
| Motivation for Equelo | Drafted | Divisional `k`, normalisation and chii-informed initialisation lead into Equelo |
| STEM Equelo account | Draft written; ready to resume | Update initialisation to describe monotone regularised priors |
| Detailed technical account | Not started | Explain exact Elo mechanics first, then exact Equelo mechanics and prior provenance |
| Expert/critical account | Not started | Evaluate foundations, sensitivity, convergence, uncertainty, support and predictive evidence |
| Basic Elo predictive account | Evidence exists | Needs integration into the story |
| Equelo predictive account | Experiment required | Must use a directly comparable protocol |
| Low-support/non-monotonicity account | Decision recorded | Preserve experiments; smoothing is an explicit entrant-prior policy, not an empirical claim |

## Next steps

Work on the explanatory prose may resume. The M12 investigation established
that changing banzuke structure materially affects empirical chii-to-rating
maps, but did not identify one model that explains or removes every reversal.
That is no longer treated as a documentation blocker.

The project will adopt a monotone entrant-prior curve as an explicit modelling
policy. The curve should be obtained reproducibly from the experimental values,
preferably by support-weighted isotonic regression, and retained with full
provenance. Public prose must distinguish these chosen monotone priors from the
non-monotone experimental estimates and from ratings subsequently learned from
bout results.

The immediate work is to implement the [Initial Rating Policy](10%20Initial%20Rating%20Policy.md),
then conduct a prospective, like-for-like predictive comparison of Equelo with
Basic Elo accompanied by sensitivity tests using reasonable alternative
monotone priors. Start with the
[consolidated M12 record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md);
[Open Questions and Experiments](05%20Open%20Questions%20and%20Experiments.md)
records the wider validation programme.

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
