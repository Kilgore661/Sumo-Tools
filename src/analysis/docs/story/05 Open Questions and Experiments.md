# Open Questions and Experiments

## Purpose

This note prevents expectations, established results and required experiments
from being folded into one narrative prematurely.

## Established findings

### Basic Elo

- One fixed Basic Elo procedure scored slightly better overall than a 50--50
  forecast on the represented 1989--2026 bouts.
- The aggregate improvement was modest.
- The sekitori and sub-sekitori evaluations behaved differently over time.
- The existing experiments do not identify the cause of that difference.
- Fixed nonzero-`k` Elo does not settle permanently even in an ideal stationary
  toy world; it continues to fluctuate.

### Comparison structure

- Disconnected divisions cannot identify their relative rating offset from
  within-division results alone.
- Sparse bridge comparisons can identify a common scale in the tested toy
  models.
- The tested evidence-shaped Makuuchi--Juryo schedule compresses the lower
  Makuuchi gradient but does not reproduce the nearly flat historical curve.

### Equelo and chii

- Visible non-monotonicity exists in the lower-maegashira rating surface.
- Very low-support chii can receive values substantially determined by
  normalization and completion rather than direct result evidence.
- Boundary alignment explains an important part of the apparent literal-rank
  reversal, but does not produce a complete explanation of every disagreement.
- A tightly converged full-history dual-boundary experiment retains a material
  Juryo--Makushita reversal. There is no established timeless mapping that
  removes every reversal across historically different banzuke structures.
- The project will therefore use a declared monotone regularisation for entrant
  priors while allowing ratings learned from results to be non-monotone with
  respect to chii.

## Expectations requiring care

- Equelo is intended to control open-population scale drift.
- Chii-informed initialization is intended to reduce arbitrary initialization
  and initialization lag.
- These mechanical aims do not establish predictive validity.
- It is expected that Equelo's predictive performance may be modest because
  Basic Elo's observed advantage is itself modest, but this is not an
  experimental result.
- It is plausible that sparse support and population churn affect predictive
  performance, but the existing subgroup comparisons do not isolate those
  causes.

## Required Equelo predictive comparison

The principal missing experiment is a directly comparable evaluation of Basic
Elo and the maintained Equelo model.

It should, as far as possible, hold fixed:

- the source History and date range;
- result eligibility;
- forecast-before-update chronology;
- identity handling;
- evaluation populations;
- scoring rules;
- reporting horizons;
- uncertainty method.

It should report at least:

- mean log loss;
- mean Brier loss;
- calibration by supported probability region;
- comparison with 50--50;
- Basic Elo versus Equelo differences;
- all-bout, sekitori and sub-sekitori results;
- performance through time rather than only one whole-epoch average.

The experiment must distinguish predictions available prospectively at each
bout from any Equelo construction that uses future results. A retrospectively
solved rating surface cannot be presented as an out-of-sample forecasting
system without an appropriate temporal design.

## Equelo mechanical investigations

The M12/boundary investigation is no longer a blocker to documentation. Its
artifacts should be preserved, but further mechanical work is deferred unless
predictive validation or sensitivity testing identifies a practical problem.
The canonical record is [The M12 Problem: Consolidated Research Record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md),
with reproduction details in the
[M12 Experiment Catalogue](09%20M12%20Experiment%20Catalogue.md) and the adopted
decision in [Initial Rating Policy](10%20Initial%20Rating%20Policy.md).
Questions that may be revisited include:

1. How much of each supported chii value comes from direct bout evidence,
   normalization and completion?
2. At what support level does normalization dominate?
3. How sensitive is the tail to support thresholds and completion rules?
4. Does excluding or pooling weakly supported chii materially affect
   well-supported ratings?
5. Is the visible non-monotonicity stable across time, policies and plausible
   perturbations?
6. Would a proposed refinement correct an identified defect, or merely force
   the curve toward the expected chii order?

## Decision rules

- Non-monotonicity alone is not proof of an Equelo defect.
- "Equelo is not chii" does not make every disagreement trustworthy.
- A mechanical refinement requires an independently stated problem and a
  result that could count against adopting it.
- If Equelo predicts slightly worse than Basic Elo, the lost predictive value
  must be considered against an independently demonstrated representational
  benefit.
- If Equelo predicts substantially worse, that is a serious problem,
  particularly for any probability interpretation of rating differences.
- The public entrant-prior curve may be monotone by policy, but the smoothing
  method and its status as regularisation must be explicit. It must not be
  presented as the unmodified experimental fixed-point output.

## Documentation work still required

The next documentation stage is a detailed-technical account, followed in due
course by a separate expert/critical account. Both should preserve the
Elo-then-Equelo order used by the existing STEM drafts.

- **Reconcile the illustrative Elo examples.** The casual and STEM drafts
  currently obtain approximately 74% from different rating differences and
  different values of `q`. Decide whether the two layers should use one common
  illustrative implementation, or whether the STEM account should explicitly
  use the contrast to explain `q`. Update both drafts together after the
  definitive Basic Elo example has been selected.
- Review the draft STEM accounts of Elo and Equelo for prose, sources and
  consistency of terminology.
- Write the detailed Elo account: exact formulae, parameters, chronology,
  data eligibility and worked examples.
- Write the detailed Equelo account from the maintained specifications rather
  than historical variants: divisional `k`, departure normalisation,
  fixed-point initialisation, map normalisation, convergence criterion,
  support and completion.
- In the eventual expert/critical account, address theoretical assumptions,
  convergence and uniqueness, identifiability, sensitivity, uncertainty,
  calibration, discrimination and direct predictive comparison.
- Add the Basic Elo predictive findings at the appropriate validation layer.
- Design and run the comparable Equelo predictive experiment.
- Incorporate its result without retrospectively changing the stated purpose
  of the experiment.
- Explain that initial ratings are monotone regularised priors, disclose the
  support/completion policy, and distinguish them from potentially
  non-monotone ratings learned from results.
