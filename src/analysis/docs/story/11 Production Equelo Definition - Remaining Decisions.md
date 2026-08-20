# Production Equelo Definition: Remaining Decisions

## Status

The casual and STEM accounts of Elo are not blocked. The conceptual STEM
account of Equelo is also no longer blocked by the M12 problem: it can explain
the three headline changes and distinguish current production from the adopted
next entrant-prior policy.

A finished detailed account of *production Equelo* is not yet possible,
because the project has not selected and integrated one definitive production
construction. A finished account of Equelo's usefulness also awaits
prospective comparative validation.

This document records those remaining boundaries. It distinguishes decisions
needed to define the production model from questions that can be disclosed as
limitations and evaluated later.

The agreed model lineage and the distinction between selecting a post-1988
Elo-like successor and constructing full-history Equelo are recorded in
[Elo-family Model Lineage and Analysis Triage](12%20Elo-family%20Model%20Lineage%20and%20Analysis%20Triage.md).

## Principal production question

The central unresolved questions are now ordered:

1. Which post-1988 Elo-like candidate should be selected as \(B'\)?
2. How should that chosen model be extended to define the next full-history
   production Equelo?

Current production uses the fixed-supported literal-chii initial-rating map.
The adopted next policy uses reconciled, east/west-paired contextual priors
constructed from 1989-onward experiments. Until the adopted policy is
evaluated as part of a complete candidate model, integrated, rejected or
superseded, there is no single exact answer covering both the maintained
implementation and intended next model.

The documentation can describe both accurately now. The detailed technical
account must ultimately name one maintained production version and give its
complete reproducible contract.

## Decisions required for the production construction

### 1. Historical scope

The adopted contextual priors cover simulations beginning in 1989 or later.
Current production ratings extend further back.

The project must choose one of the following, or define another explicit
policy:

- begin the next production Equelo series in 1989;
- retain the older fixed-supported initialisation for pre-1989 simulation;
- construct a separate pre-1989 completion policy and artifact.

This is not merely missing prose. Different initial ratings can affect later
process ratings, so the choice is part of the model.

#### Parked proposal: transfer the post-1988 priors backwards

One proposed way to complete the earlier history is to assume that the JSA's
assessment of rikishi ability has retained the same broad meaning since 1958.
On that view, if a chii is an institutional judgement of relative ability and
the JSA has consistently made that judgement competently, priors learned from
1989-onward results may also be defensible as priors for earlier entrants.

The useful version of this assumption is narrower than saying that every
literal chii has always represented exactly the same numerical level of
ability. Divisions, banzuke depth, schedules and the active population have
changed. The M12 investigation is directly relevant: an M12 in a larger
historical Makuuchi can occupy a different structural position, particularly
distance from the Juryo boundary, from an M12 on a modern banzuke. JSA
competence supports a claim of broadly persistent *ordinal* meaning, but does
not by itself establish literal-rank numerical invariance across eras.

A defensible modelling convention might therefore say:

> We assume that the banzuke has retained broadly stable ordinal meaning since
> 1958: higher chii normally represent a stronger assessment of a rikishi than
> lower chii. We therefore use the 1989-onward evidence to construct
> historically transferable entrant priors. These priors are a modelling
> convention, not a claim that the expected ability associated with every
> literal chii has remained numerically unchanged.

Even with that convention, ranks found only in the earlier record, including
M19--M22 and J15--J24, still require values. Two plausible completion rules
remain:

- **literal-rank extrapolation**, extending the modern curve by chii; or
- **boundary-relative completion**, relating historical tail ranks to
  comparable positions above the contemporary division boundary.

The second is more consistent with the banzuke-depth evidence behind the M12
investigation; the first is simpler and follows the stronger literal-chii
assumption. The alternatives should be compared with each other and with the
current fixed-supported historical priors, examining early sekitori ratings,
cross-boundary careers, continuity around 1989, sensitivity of later ratings
and predictive performance where the data permit it. Incomplete lower-division
results before 1989 make this choice more consequential because an entrant's
prior may persist longer before sufficient recorded bouts can revise it.

This proposal and response are recorded for later consideration. No
pre-1989 transfer or completion rule has yet been adopted, and the question is
parked while work continues on the other production issues.

### 2. Anchoring and fallback behaviour

The adopted paired priors have an unweighted mean near 1411 and are
deliberately not recentered. A common shift is immaterial when every entrant in
a complete simulation is consistently initialised from the same table, because
Elo expectations depend on rating differences.

The origin can matter when:

- an entrant's chii is missing and a fixed fallback such as 1517 is used;
- the new priors are mixed with already established ratings;
- Mae-zumo or another unrepresented category requires a fallback;
- the modern priors are joined to a separately constructed pre-1989 table.

Production therefore needs explicit rules for coverage, fallback and any
common anchoring shift. If a consumer requires a shift, its anchoring
population and provenance must be stated and tested rather than silently
changing the retained source artifact.

### 3. Bout eligibility

The current Equelo package warns that its calculation ignores approximately
5.6% of 1989-onward bouts simply because kimarite is missing. If the win/loss
result is otherwise known, absence of kimarite is not an ordinary Elo reason
to ignore the bout.

Before the production calculation is treated as definitive, the project must
either:

- rate those known results; or
- deliberately retain the exclusion and document it as part of the model's
  result-eligibility policy.

Because this affects a material fraction of the represented bouts, it is a
production-definition issue rather than a minor implementation detail.

### 4. Artifact and API transition

The public API and site products currently consume fixed-supported artifacts.
Adopting the contextual priors requires a defined transition covering:

- the canonical entrant-prior artifact;
- lookup from raw and annotated chii to paired prior values;
- unsupported, fallback and no-rating behaviour;
- input hashes, policy metadata and other provenance;
- regeneration of process and day-end ratings;
- the production API contract;
- the distinction between operational ratings and interpretive public
  landmarks;
- migration of Highest Equelo, Typical Equelo Values and other consumers.

Until this transition occurs, documentation must call the contextual priors the
*adopted next policy*, not the map used by current production Equelo.

## Required usefulness and validation work

The first missing evidential result is a prospective, like-for-like comparison
of candidate \(B'\) models with the definitive Basic Elo baseline \(B\).

The adopted priors were constructed using history from 1989 onward through the
current experimental endpoint. Applying those priors retrospectively to
forecast bouts from the same history would use future information. Such a run
could describe an in-sample construction but could not be presented as an
out-of-sample predictive test.

The validation therefore requires a temporal design, such as a training cutoff
followed by prospective evaluation or a rolling reconstruction of the prior.
It should compare at least:

- constant initialisation;
- current fixed-supported initialisation;
- the adopted contextual priors;
- a reasonable smoothed prior as a sensitivity comparator, if useful.

The comparison should otherwise align history, result eligibility,
forecast-before-update chronology, identity handling, populations, scoring
rules, reporting periods and uncertainty treatment. It should report
calibration, Brier loss, log loss and relevant population and time splits.

This work does not block an account of the research route. It blocks selection
of \(B'\), and therefore blocks a finished claim about whether its divisional
`k` and/or informed priors improve later forecasts. Once the historical
extension is defined, the resulting Equelo will require a second comparison
with an appropriate ordinary-Elo model on the same declared problem.

## Important questions that are not production blockers

The following remain legitimate subjects for evaluation, but they need not be
settled before a transparent chosen model is explained:

- whether division is the best proxy for rating confidence in the `k` policy;
- how much divisional `k` contributes to boundary irregularities;
- whether departure normalisation is the optimal scale-stability policy;
- a general proof of fixed-point convergence or uniqueness;
- residual non-monotonicity in experimental or learned ratings;
- exact causal decomposition of the former M12 problem;
- whether another reasonable entrant-prior curve performs better.

These questions should be stated as assumptions, limitations, sensitivity
questions or experiments required. A production account needs an exact and
reproducible choice; it does not need proof that every choice is uniquely
optimal.

## Minor documentation work

The casual and STEM Elo examples both produce an illustrative probability of
approximately 74%, but currently use different rating differences and values
of `q`. They should eventually be reconciled or the contrast should be used
explicitly to explain the role of `q`.

This is an editorial consistency issue, not a conceptual blocker.

## Documentation consequences

The current position by layer is:

| Account | Position |
|---|---|
| Casual Elo | Unblocked; draft requires ordinary editorial review |
| STEM Elo | Unblocked; draft requires editorial and source review |
| Conceptual STEM Equelo | Unblocked; draft distinguishes production from adopted policy |
| Detailed production Equelo | Blocked by production version, historical scope, anchoring/fallback, eligibility and integration decisions |
| Usefulness and defence | Blocked by prospective comparative validation |
| Expert/critical account | Can be outlined, but remains incomplete until production and validation are settled |

The next implementation work should therefore define production Equelo before
the detailed technical prose attempts to present one definitive calculation.
The next evidential work should then validate that implementation
prospectively.
