# Proposal: The Consolidated Elo-like Ratings Story

## Status and purpose

This is a proposal for a near-publishable internet account of the work from
ordinary Elo through the selection of the post-1988 Elo-like model
\(B'=B_{kP}\). It does not attempt to write that account now, and it does not
define the next full-history Equelo.

The proposed account should consolidate material that is currently spread
across the casual draft, the STEM drafts, the initial-rating research and the
model-selection package. Its endpoint is a defensible answer to:

> What Elo-like rating model do we use for the sufficiently complete
> post-1988 sumo record, how does it work, and why is that choice reasonable?

The next document can then begin from that answer and ask how \(B'\) should be
extended over the incomplete 1958--1988 history to produce the next Equelo.

## Proposed form

The preferred form is one navigable web document with progressive disclosure,
rather than three independent accounts that can silently drift apart. A short
contents panel near the beginning should offer three reading routes:

1. **Just tell me what the ratings mean** -- the casual account;
2. **Show me how the model works** -- the STEM account; and
3. **Show me exactly what was tested** -- the technical and critical record.

The first route should be readable without formulae. The second should be a
self-contained technical explanation with formulae and worked examples. The
third need not reproduce every experiment in prose: it should give exact model
contracts, summarize the decisive evidence, state limitations and link to the
reproducible research record.

This three-route presentation is a practical consolidation of the four layers
in [Reader Layers](01%20Reader%20Layers.md). The former detailed-technical and
expert/critical layers become one public audit section with links out to code,
artifacts and fuller research documents. Nothing prevents a later academic
treatment, but the web account should not be delayed while an audience and
requirements for such a treatment remain hypothetical.

## Proposed contents

### Opening: what this page is about

State briefly that the project uses bout results to maintain numerical ratings
for rikishi. Explain that the page begins with how to read those ratings, then
opens the calculation for readers who want more detail, and finally records
why one particular Elo-like model was selected.

The opening should not begin with Equelo, fixed points, calibration or model
notation.

### Part I: Reading an Elo rating

#### 1. Ratings are comparative

Explain that a rating is a running summary derived from earlier results. An
isolated rating is not an amount of strength; comparisons and rating
differences are what matter.

#### 2. Expected and surprising results

Explain informally that beating a lower-rated opponent changes little, while
an upset changes more. The same rating difference has the same consequence
wherever it occurs on the numerical scale.

Use the paired examples already developed for the casual draft: a yokozuna
against an M1 and a low maegashira against a mid-Juryo rikishi. The first
example should mention the 400-point difference explicitly. The second should
reinforce that differences, not absolute values, drive the calculation while
quietly giving intuition for ratings near 2500, 2100, 1900 and 1500.

#### 3. Estimated probabilities are not promises

Explain that a rating difference can be converted into an estimated chance of
winning, that an underdog can still win, and that the empirical usefulness of
such probabilities is a separate question. The illustrative percentage must
be made consistent with the STEM worked example, or the contrast must be used
deliberately to explain the probability-scale parameter.

#### 4. The short answer about usefulness

Give only the result needed by a casual reader: the selected model extracts
more information from historical bouts than treating every contest as an
independent 50--50 event, but it is not perfect. Avoid log loss, ECE and model
subscripts here.

Suggested tone:

> The calculation does not make sumo predictable. It does, however, describe
> later results better than assuming that every bout is an even contest.

### Part II: How the Elo-like model works

#### 5. Elő and the standard idea

Introduce Arpad Elő as a person, explain that he developed a chess rating
system at FIDE's request, and record FIDE's use of the system from 1970. The
historical paragraph should be sourced during editorial consolidation.

Explain why opponent-sensitive ratings are useful where competitors do not
all face one another equally often. Also state the ideal assumptions often
associated with simple accounts--unchanging abilities and a fixed
population--and note that neither chess nor sumo satisfies them literally.

#### 6. Define Basic Elo \(B\)

Present the expected-score equation, the update equation and one worked bout
example. Define the project's baseline rather than speaking about an
unspecified Elo implementation:

```text
epoch = 1989/01
q = 400
k = constant 35
initialisation = one common rating
chronology = forecast before update
identity = RikId
rating persistence = permanent within the run
eligible result = represented W/L, irrespective of kimarite
```

Cover:

- why only rating differences matter;
- the role of \(q\) in converting a difference to an expected score;
- the role of \(k\) in controlling responsiveness;
- translation invariance and the arbitrary common rating origin;
- equal-\(k\) zero-sum updates; and
- chronological predict-before-update calculation.

The worked example may use real rikishi and a real basho, but numbers must be
backed by the declared model or explicitly introduced as what an illustrative
Elo model *might* assign.

#### 7. Why Basic Elo is not the end of the story

Explain the practical sumo difficulties without implying that every one is
solved:

- equal entrant ratings produce an initialisation gap;
- entrants and retirees make the rating population open;
- fixed \(k\) balances responsiveness against stability;
- scale drift can arise in an open population;
- ability changes with development, injury and age;
- the earlier historical record is incomplete; and
- fixed nonzero \(k\) produces continuing fluctuation rather than permanent
  convergence.

This section should distinguish mechanical problems, modelling assumptions
and empirical questions. It should also distinguish two ideas that are easily
conflated: a fixed-\(k\) rating path need not settle permanently, while the
effect of its initial rating can nevertheless become negligible. The
fixed-skill `forgetting` experiment supports that conceptual distinction by
comparing differently initialized processes on exactly the same subsequent
evidence. It does not establish a forgetting time for historical sumo.

#### 8. Divisional \(k\)

Introduce the first modification to \(B\). Use the agreed compact account:

> In the Elo update formula, \(k\) controls how strongly a new result changes
> the rating. A larger \(k\) makes the rating respond more quickly, while a
> smaller \(k\) makes it more stable. From a teleological perspective, it
> makes sense for new rikishi to have a larger \(k\) so they can find their
> position quickly, and for strong rikishi to have a small \(k\) so that their
> ratings do not unduly reflect a winning or losing streak.

Add the epistemic interpretation: a larger \(k\) expresses less confidence in
the present rating and a smaller \(k\) greater confidence. State that division
is a useful proxy chosen by the model, not a proof that every rikishi in a
division has the same rating uncertainty.

#### 9. Informed entrant priors

Motivate the change before describing its construction. Giving a yokozuna and
a Jonokuchi rikishi the same rating is deliberately simple but ignores
relevant information already present in the banzuke. An informed prior is
intended to shorten the initialisation gap; it is not a claim that chii and
ratings are identical.

Give the fixed-point idea at STEM resolution:

1. start with provisional initial ratings;
2. replay the history;
3. derive typical ratings associated with the represented chii;
4. feed those values back as the next initial-rating map; and
5. repeat.

State only the demonstrated convergence claim: in the implementations tested,
successive maps converge to stable fixed points. Then explain why the adopted
prior is a declared reconciliation of contextual post-1988 experiments rather
than a timeless, uniquely true or necessarily monotone chii-to-ability table.

The fixed-skill toy investigation may be cited here only as limited supporting
background. In its deliberately favourable world, an initialization at known
latent skill reached meaningful truth-relative behaviour sooner than flat,
inverted and random alternatives, while all tested initializations were
eventually forgotten. This is consistent with the intuitive purpose of an
informed prior: shortening the initial transient. It is not direct evidence
for the adopted prior \(P\). The toy world has ten permanent rikishi, fixed
abilities, complete round robins, no divisions and \(k=5\); historical sumo
has a much larger open population, changing abilities, unequal schedules,
divisions and a different update policy. Its numerical forgetting times should
therefore not appear in the main narrative as though they transferred to sumo.

The public account should say that the retained paired priors are unsmoothed
because smoothing was not required for their purpose. The source simulations
and final reconciliation should be deferred to the audit section.

#### 10. The four-model comparison

Introduce the controlled two-by-two comparison:

| Model | \(k\) policy | Entrant initialisation |
|---|---|---|
| \(B\) | constant 35 | constant |
| \(B_k\) | divisional | constant |
| \(B_P\) | constant 35 | informed prior \(P\) |
| \(B_{kP}\) | divisional | informed prior \(P\) |

Explain why the comparison is fair: all four process the same 574,863 bouts,
use \(q=400\), forecast before updating and vary only the two policies under
investigation.

#### 11. Why we use \(B'=B_{kP}\)

Lead with the conclusion rather than the research chronology:

> We use \(B'=B_{kP}\). It is not a perfect model, but it predicts outcomes
> better than treating every bout as an even contest. Its design is grounded
> in evidence about previous results, while informed initial ratings and
> divisional update rates address the practical problems of placing new
> rikishi and balancing responsiveness against stability.

Then give the STEM-level evidence:

- \(B_{kP}\) has the lowest declared aggregate log loss;
- Brier loss gives the same ordering;
- most of the improvement over \(B\) comes from informed initialisation;
- divisional \(k\) adds a smaller aggregate improvement;
- \(B_k\) and \(B_{kP}\) are the two strongest candidates, with little to
  choose between them under some calibration summaries; and
- the predeclared primary criterion supports retaining \(B_{kP}\) as \(B'\),
  while \(B_k\) remains the serious alternative.

The origin of \(P\) should be recorded as methodological provenance. It should
not repeatedly reappear as an objection to using the fitted model. Using all
available results through the latest basho and then forecasting the next is an
ordinary past-to-future application.

#### 12. Calibration and limitations

Define calibration in ordinary language before naming ECE: when the model
says 70% for a class of forecasts, that class should win about 70% of the
time. If ECE is shown, define it as the participant-weighted mean absolute gap
between predicted probability and observed win rate across the declared
probability bins.

The body text need not reproduce the whole calibration investigation. It
should say:

- the aggregate curves initially suggested substantial overconfidence in
  some probability ranges;
- pairing ratings by their prior bout counts showed that the principal defect
  is concentrated when a rating with fewer than 30 prior bouts faces a more
  established rating;
- two immature ratings can nevertheless be well calibrated against one
  another, possibly because their forecasts remain cautious and near 50--50;
- for \(B_{kP}\), 83.8% of bouts outside the less-than-30 row fall in
  support-pair cells with ECE below three percentage points; and
- good calibration is not the same as strong discrimination, so the proper
  scoring results remain the primary model-selection evidence.

Use the coarse triangular heatmap in the story. Link the uniform 30-bout
heatmap and CSV as the detailed exploratory view.

State the known limitations proportionately: early rating formation is hard,
cross-boundary performance is a disappointing subgroup result, ratings are
not chii, and no selected parameter policy is uniquely true. These are reasons
for care, not reasons to withhold \(B'\).

#### 13. Where Equelo begins

End the consolidated account at the newly clarified boundary:

\[
B \longrightarrow B'=B_{kP} \longrightarrow
\text{Equelo over the represented 1958--present history}.
\]

Initialisation and divisional \(k\) are now part of the chosen Elo-like model,
not sufficient definitions of Equelo. The remaining distinctive Equelo task
is to extend \(B'\) over the incomplete pre-1989 record using explicit
historical initialisation, completion, normalisation, eligibility and
integration policies. Link to the Equelo account rather than attempting to
settle those choices here.

### Part III: Technical and critical record

This part should be concise and link-heavy. Its purpose is auditability, not a
second continuous tutorial.

#### A. Exact model contracts

Record the parameters, input histories, eligibility rules, divisional \(k\)
configuration, adopted-prior artifact, fallback policy and forecast chronology
for \(B\), \(B_k\), \(B_P\) and \(B_{kP}\).

#### B. Initial-rating construction

Record the contextual source experiments, convergence criteria, support,
reconciliation, east/west pairing, absence of final recentering and decision
not to smooth. Distinguish experimental fixed points from the adopted prior.

#### C. Model-selection protocol and results

Link the proposal, manifest, forecast ledger, log-loss and Brier comparisons,
factorial contrasts and subgroup results. Explain why log loss was primary and
why calibration is diagnostic rather than the post-hoc selection rule.

#### D. Calibration views

Provide the aggregate chart, one-dimensional maturity chart, story-facing
coarse paired-maturity heatmap, fine 30-bout heatmap and their CSVs. Define
participant-level duplication and the rotational symmetry of the calibration
curves.

#### E. Interpretive limits

Link the chii-disagreement and M12 records, fixed-\(k\) fluctuation work,
the fixed-skill forgetting study, the cross-boundary result and the distinction
between calibration, discrimination, retrospective fit and future
forecasting. Preserve the distinction between continuing stochastic
fluctuation, truth-relative error and sensitivity to initialization. Record
explicitly that the forgetting experiment clarifies these concepts but does
not validate \(P\), divisional \(k\), or a forgetting claim for historical
sumo.

#### F. Reproduction

Give the canonical command, input hashes and output directory. Do not require
the reader to infer which of the many older Equelo and probability packages
defines the selected model.

## Claim discipline

The consolidated account should continue the existing discipline of labelling
claims internally, even if those labels are not printed in the final prose:

| Kind | Example in this account |
|---|---|
| Definition | \(B'\) uses divisional \(k\) and adopted prior \(P\) |
| Intended property | informed priors are intended to shorten initialisation lag |
| Established finding | \(B_{kP}\) has the best declared aggregate log loss |
| Interpretation | larger \(k\) can be read as less confidence in a rating |
| Limitation | calibration is poor for many immature-versus-established pairings |
| Open question | whether another reasonable policy would perform better |

The account must not turn an intended property into an established result, a
modelling convention into a fact about true ability, or a small empirical
advantage into a claim of decisive superiority.

## Research and source map

### Narrative design and existing drafts

- [Reader Layers](01%20Reader%20Layers.md) supplies the progressive-disclosure
  principle.
- [Narrative and Validation Structure](02%20Narrative%20and%20Validation%20Structure.md)
  separates construction from validation.
- [Elo Introduction for the Casual Reader](03%20Elo%20Introduction%20for%20the%20Casual%20Reader.md)
  supplies the current first-layer prose and paired illustrative examples.
- [Draft: A Standard Account of Elo](06%20Draft%20Standard%20Elo%20Account%20for%20the%20STEM%20Reader.md)
  supplies the formulae, history, worked-example template, parameter account
  and discussion of open populations.
- [Draft: How Equelo Changes Elo](07%20Draft%20Equelo%20Account%20for%20the%20STEM%20Reader.md)
  supplies concise explanations of divisional \(k\), normalisation and
  informed initialisation. Its old three-feature definition of Equelo must be
  revised in light of the new \(B'\)/Equelo boundary.

### Basic Elo and model selection

- [Prediction README](../../prediction/README.md) and
  [Prediction Findings](../../prediction/docs/experiments/Findings.md) record
  the earlier Basic Elo predictive work.
- [Elo Model Selection README](../../elo_model_selection/README.md) defines the
  controlled four-model tranche and its current conclusion.
- [Model-selection proposal](../../elo_model_selection/docs/Proposal%201.md)
  records the predeclared questions, primary metric and comparison design.
- [Controlled retrospective results](../../elo_model_selection/docs/Results%201.md)
  records the proper scores, factorial effects, calibration analysis,
  maturity-band interpretation and selection of provisional \(B'\).

The canonical generated evidence is beneath:

```text
files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/
```

Important artifacts include `manifest.json`, `summary.csv`,
`comparisons.csv`, `factorial_contrasts.csv`, `calibration_summary.csv`, the
coarse `calibration_ece_by_support_pair_coarse.html`, the fine
`calibration_ece_by_support_pair.html`, and their separate CSVs.

### Initialisation and chii

- [Initial Rating Policy](10%20Initial%20Rating%20Policy.md) is the normative
  source for the adopted 1989-onward paired priors.
- [The M12 Problem](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md)
  and [M12 Experiment Catalogue](09%20M12%20Experiment%20Catalogue.md) record
  why literal monotonic chii maps are not required and how the contextual
  source experiments were evaluated.
- [Fixed-Boundary Equelo](../../equelo/fixed_boundary/README.md),
  [Continuous Lower-Banzuke Equelo](../../equelo/fixed_lower_banzuke/README.md)
  and [Initial-Rating Reconciliation](../../equelo/smoothing/README.md) define
  the source and reconciliation producers.
- [Clean Elo README](../../clean_elo/README.md) and
  [Rating Probe Findings](../../clean_elo/docs/Rating%20Probe%20Findings.md)
  supply the retained negative evidence about treating chii agreement as a
  simple validity test.

### Behaviour, limitations and the transition to Equelo

- [Toy Elo README](../../toy_elo/README.md) and
  [What Ratings Might Say About Grand Sumo](../../toy_elo/docs/What%20Ratings%20Might%20Say%20About%20Grand%20Sumo.md)
  provide interpretive guardrails.
- [Elo Bottom Line 2](../2026%2008%2010%20Elo%20Bottom%20Line%202.html) records
  continuing fixed-\(k\) fluctuation.
- [Forgetting package README](../../forgetting/README.md) defines
  initialization forgetting as a paired-counterfactual property and separates
  it from convergence, truth-relative error and predictive usefulness.
- [Completed Investigation: Forgetting in a Fixed-Skill Toy World](../../forgetting/docs/Completed%20Investigation%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md)
  supplies the completed experiment and its strict claim boundary. It supports
  the limited proposition that initial conditions can be forgotten despite
  continuing fixed-\(k\) fluctuation, and that better initialization can
  shorten the transient in the declared toy world. Its ten-rikishi,
  fixed-skill, divisionless round-robin results are not direct validation of
  the adopted prior or transferable numerical evidence about historical sumo.
- [Forgetting Technical Companion](../../forgetting/docs/Completed%20Investigation%20-%20Technical%20Companion.md)
  records the exact model, pairing contract, artifacts and reconstruction
  checks for readers auditing that limited result.
- [Production Equelo Definition: Remaining Decisions](11%20Production%20Equelo%20Definition%20-%20Remaining%20Decisions.md)
  identifies the historical-scope, anchoring, eligibility and integration
  choices that belong to the next chapter.
- [Elo-family Model Lineage and Analysis Triage](12%20Elo-family%20Model%20Lineage%20and%20Analysis%20Triage.md)
  supplies the decisive boundary between generic initialisation work,
  selected \(B'\) and the full-history Equelo extension.
- [Evidence and Source Map](04%20Evidence%20and%20Source%20Map.md) remains the
  wider inventory for sources not repeated here.

Older probability and Equelo experiments may supply methods or retained
negative evidence, but their different \(q\), \(k\), epoch, normalisation and
eligibility policies must not silently enter the definition or validation of
\(B'\).

## Editorial decisions required during consolidation

1. Reconcile the casual and STEM illustrative probabilities and rating
   differences.
2. Source-check the short Elő/FIDE historical paragraph.
3. Decide whether the real-rikishi worked example uses exact \(B\) values or
   remains explicitly illustrative.
4. Use one notation and capitalization policy for \(q\), \(k\), \(P\),
   \(B_k\), \(B_P\), \(B_{kP}\) and \(B'\).
5. Introduce model notation only after the casual route.
6. Keep estimated probability, calibration and predictive information
   distinct.
7. Use the coarse paired-maturity heatmap in the narrative and link the fine
   chart for exploration.
8. Remove stale text saying that \(B'\) has not been selected or that a general
   \(q\) investigation blocks progress.
9. Reframe the present STEM Equelo draft so divisional \(k\) and informed
   initialisation belong to \(B'\), while the historical extension begins the
   new Equelo chapter.

## Acceptance criteria

The consolidated account is ready for internet publication when:

- a casual reader can stop before formulae and still interpret a displayed
  rating correctly;
- a STEM reader can reproduce the mechanics of \(B\) and explain why
  \(B_{kP}\) was selected;
- every numerical claim about model performance points to a declared model
  and reproducible artifact;
- intended purposes, established findings and limitations remain distinct;
- the account does not imply that ratings are chii or true ability;
- the HTML renders all mathematics through the existing MathJax/CDN process;
- the 74% example is internally consistent or its inconsistency is explicitly
  instructive; and
- the final section hands off to Equelo without pretending that the
  pre-1989 construction has already been decided.

## Out of scope

This consolidation should not wait for:

- proof that \(B_{kP}\) is uniquely optimal;
- a general theorem about Elo convergence;
- further searching over \(q\);
- a monotone chii-to-rating map;
- an academic-paper treatment for an unspecified expert audience; or
- resolution of the full-history Equelo construction.

It should also not decide the latter accidentally. Historical transfer of the
post-1988 priors, completion of pre-1989-only chii, normalisation, fallback,
bout eligibility and product migration belong to the Equelo work that follows.
