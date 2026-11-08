# Where We Got To: Expert Account and Appendix B

> **Continuation update, 8 November 2026:** The iteration-20 / epsilon-8.5
> source described below has now been reproduced exactly, compared after the
> production support-weighting rule, promoted as `2026-09/run-002`, and passed
> strict loading, full replay, site-data production and build-only site
> verification. The installed paired table now has SHA-256
> `31ba2ea5430fb6a117b80290e78570cbbb160875febb6af14664a6c64ec93cdf`.
> Appendix B and the current production documentation contain the resulting
> values. Statements below describing that promotion as outstanding record the
> state at the original handoff.

**Handoff date:** 7 November 2026

**Repository:** `X:\Sumo-Tools`

**Branch at handoff:** `dev`

**Base HEAD before the checkpoint:** `0820eb7` (`Install P1-prime-WL prior and update account`)

**First checkpoint:** `aa9f52d` (`Document P89 and checkpoint Appendix B`)

## Purpose of this handoff

This document records the state reached while developing the expert account's
Appendix B on the Elo-89 entrant prior, (P_{89}). It separates:

- the main expert account, which was considered good enough for a checkpoint
  commit while Appendix B continued;
- the substantial work already present in Appendix B;
- the remaining work identified in a seven-point review;
- clarifications reached after that review; and
- the final audit required between Appendix B and the chapters which rely on
  it.

It is a continuation document, not part of the finished expert narrative.

## Bottom line

The numbered expert account and its Research and Implementation Guide have a
coherent structure and were considered ready for a checkpoint commit. They
should not be treated as publication-final, because Appendix B is still
preliminary and several chapters make claims or promises which Appendix B must
ultimately satisfy.

Appendix B has progressed well beyond an outline. It now contains a substantive
account of:

- the first-rating problem at the January 1989 epoch;
- equal and random initialisation as alternatives;
- mean preservation as a policy separate from prior fitting;
- the complete-W/L evidence rule;
- the iterative search through literal-chii mappings;
- why exact fixed-point convergence is not the selection principle;
- the epsilon sweep and early stopping as regularisation;
- support-weighted construction of the consumer table;
- the Komusubi aggregation diagnostic;
- reproducibility and evidence boundaries; and
- entrant-prior sensitivity, selection and optimisation as future work.

It is not yet final. The remaining work is mainly interpretive rather than a
need to rediscover the construction.

## Current working-tree state

The working tree was not clean when this handoff was written. It contained the
P89 terminology and documentation revisions across the expert account,
production documentation and prior code. Appendix B and the new `Matters
Arising` directory were untracked. The principal untracked files were:

```text
src/validation/elo89-expert-account-2/Appendix B - The Elo-89 Entrant Prior.md
src/validation/elo89-expert-account-2/Matters Arising/
```

There was also a temporary spreadsheet lock file:

```text
src/analysis/equelo_prior_aggregation/results/.~lock.priors.csv#
```

That lock file is not a project artifact and must not be committed. It should
not be deleted while the corresponding application may still be using it.

This handoff, the preliminary Appendix B, the matters arising and the
coordinated P89 terminology and production-reference revisions were included
in checkpoint `aa9f52d`. The temporary spreadsheet lock file was expressly
excluded.

## The current P89 artifact

The currently installed production table contains 484 paired chii values:

```text
src/analysis/equelo_prior_aggregation/results/priors.csv
```

Its currently documented SHA-256 is:

```text
41430ce50f61bf2769ee7b37e4c964d5ecd00e78fe554a9790a869ad35955d38
```

That artifact is based on the epsilon-10 literal fit. The current producer
still declares:

```python
EPSILON = 10.0
```

The table uses every represented binary W/L bout whether or not kimarite is
present, and converts literal cells to consumer keys by direct support
weighting. It has passed strict loading, complete Elo-89 replay and the
dependent site build.

## The agreed interpretation of P89

P89 answers a narrow operational question:

> What first rating should Elo-89 assign when it has no stored rating for a
> rikishi and the information admitted by the initialisation rule is his
> represented chii?

It is not:

- the definitive rating belonging to a chii;
- a statement that all rikishi at one chii have equal ability;
- a statement about the present ability of a rikishi who happens to occupy a
  chii;
- a schedule-independent measurement of true strength;
- necessarily monotone; or
- the uniquely correct or optimal entrant prior.

The intellectual history now needs one further clarification. The project
originally wanted informed priors in order to shorten the **initialisation
gap**: the presumed gap between a new stored rating and the rikishi's latent
ability. That gap surely exists in some sense, but it cannot be measured
directly because true ability is unobservable. The fixed-point procedure did
not measure or minimise it. At most, better early predictions can demonstrate
a smaller **observable predictive penalty associated with initialisation**;
they do not establish greater proximity to latent ability.

The positive case for adopting it has three parts:

1. **Predictive usefulness.** The existing record indicates that a configured
   Elo-89 predicts usefully and that informed initialisation was compared with
   a flat starting value. The evidence audit below must reconstruct the exact
   configurations, populations and score comparisons before the strength of
   those claims is finalised.
2. **Replay consistency.** The retained source does not change radically under
   another application of the replay-and-aggregation procedure. This is a
   necessary acceptance check: a candidate which contradicted its own
   construction would be rejected. It is not sufficient evidence of truth,
   uniqueness or predictive superiority.
3. **Plausibility inspection.** The scale and broad curve were judged usable
   and obvious pathologies were investigated. This was informed modelling
   judgement, not a formal validation criterion.

The preferred compact description is:

> P89 is a reproducible, historically informed and schedule-conditioned
> entrant prior. It is the current Elo-89 answer to the first-rating problem,
> not a recovered law connecting chii to true ability. Its construction
> supplied one useful candidate; it has not been shown to minimise the
> unobservable initialisation gap.

The phrase **historically consistent** is safe only if it is explicitly
limited to approximate consistency with the declared historical
replay-and-aggregation procedure. It must not imply consistency with
unobservable historical ability or prove cross-era comparability.

## Fixed point, mapping search and mean preservation

The code resembles a fixed-point finder for a historical reason: the project
initially expected the fixed point to be the best answer and to have a special
interpretation in the sumo setting. That expectation was not justified. The
operator (F) was designed by the project, and satisfying (P=F(P)) would
establish only self-consistency under that operator. It would not show that
the map minimises the initialisation gap.

The epsilon sweep showed that continued numerical convergence eventually made
log and Brier loss worse. The iteration is therefore now understood as one
reproducible **candidate generator**: a path through the space of
chii-to-rating mappings. It found a useful early region; it did not prove that
the limit is special. For the logically separate question of whether a
configured Elo-89 predicts successfully, it would not matter whether its P
had come from this procedure, optimisation, expert judgement or, as a thought
experiment, been picked out of a hat. The provenance of P matters for
reproducibility, interpretation and choosing among candidates, not for the
existence of a predictively useful configured model.

Mean preservation is independent of that search. Elo-89 uses it as an
intuitive inflation/deflation control for an open population. It would remain
the production policy if the entrant map were obtained by random search,
regularised optimisation, a hierarchical model or another method. There is no
simple observable definition of rating inflation which proves that preserving
the active mean solves the problem.

## The epsilon sweep: what was actually decided

The epsilon sweep has already been run. It is not an outstanding experiment.
The retained account is:

- the accepted epsilon-10 source stopped at iteration 18, with a maximum map
  change of about 9.728 points;
- iteration 20, selected by epsilon 8.5, had the lowest observed mean log
  loss;
- iteration 21, selected by epsilon 8, had the lowest observed mean Brier
  loss;
- the advantages over epsilon 10 were very small;
- by iteration 82 the proper scores were materially worse; and
- continued fitting to epsilon 0.1 reached iteration 1,171 and increasingly
  produced extreme sparse-cell values.

The two proper scoring rules therefore identify the same narrow region of the
trajectory. They do not have their exact minima at the same iteration. The
working decision is to use iteration 20 because log loss is the declared
primary selection measure. The adjacent Brier minimum corroborates that
iterations 20--21 form the best observed region.

Epsilon 8.5 is not a theoretically privileged or smoothly optimised constant.
The fitting trajectory is unchanged by epsilon; epsilon merely chooses the
first iteration at which to stop. “Epsilon 8.5” is therefore a convenient
label for iteration 20, whose maximum remaining change crossed that threshold.

The outstanding work is implementation and promotion, not deciding whether
the scan happened. To replace the current production artifact:

1. regenerate or recover the iteration-20 literal table;
2. apply the accepted support-weighted aggregation;
3. compare the final epsilon-10, epsilon-8.5 and, where useful, epsilon-8
   consumer tables and proper scores;
4. inspect sparse-cell and curve behaviour;
5. promote the chosen paired table explicitly;
6. update its hash and provenance;
7. run the complete Elo-89 replay and tests; and
8. rebuild the dependent site artifacts.

Appendix B currently says that the sweep did not settle whether epsilon 8.5
should replace epsilon 10. That wording is stale. It should instead record the
iteration-20 decision and distinguish it from the still-unperformed production
promotion.

## What “looked about right” should mean

Elo ratings have no intrinsic origin, and the project deliberately chose a
familiar chess-like numerical presentation. The intended broad scale placed a
Yokozuna near 2500, with other chii located relative to that level. Earlier
work found that a flat starting value of 1517, with (q=400) and the then-used
responsiveness policy, produced approximately that scale. The later divisional
K policy produced a similar broad result.

The current epsilon-10 P89 table begins at approximately:

| Chii | Rating |
| --- | ---: |
| Y1 | 2525.42 |
| O1 | 2400.89 |
| S1 | 2359.51 |
| K1 | 2323.05 |
| M1 | 2301.52 |
| J1 | 2141.95 |
| Ms1 | 2016.07 |
| Sd1 | 1700.27 |
| Jd1 | 1478.13 |

The curve broadly declines through the banzuke and remains intelligible well
into the lower divisions. “Looked about right” means that this overall scale,
broad ordering and common-rank behaviour were plausible for an entrant prior.
It does not mean that every adjacent chii is monotone, every tail value is well
estimated, or every local irregularity has an explanation.

A final Appendix B would benefit from a legible chart of the full map, ideally
with support or uncertainty information available alongside it. The chart
should not imply a precision which the construction does not possess.

## The Makuuchi--Juryo boundary

The most conspicuous questionable feature is the reversal at the
Makuuchi--Juryo boundary. In the current table J1, at about 2141.95, exceeds
M15, M16, M17 and M18, although it remains below M13 and M14. Similar local
boundary relationships occur elsewhere, for example Ms1 above low Juryo.

The deepest literal Maegashira positions also have declining support:

| Chii | Support |
| --- | ---: |
| M12 | 450 |
| M13 | 450 |
| M14 | 444 |
| M15 | 393 |
| M16 | 277 |
| M17 | 90 |
| M18 | 6 |

This support pattern is relevant to precision and stability. It does **not**
explain the direction of the ratings: greater support does not imply a greater
rating.

Possible substantive mechanisms include selective interdivision scheduling,
promotion only when space is available, and the possibility that a strong
Juryo rikishi must remain strong while waiting for a Makuuchi vacancy.
Changing banzuke depth and composition also make literal M16--M18 labels
historically selective. These are plausible stories, not identified causes.
True strength is unobservable, and the project has not isolated which, if any,
of these mechanisms explains the fitted values.

The defensible position is therefore to disclose the reversal, retain the
empirical output rather than impose monotonic smoothing, and avoid claiming
that the reversal is either a discovery about true ability or a proven model
failure. These are the best values produced by the adopted method so far.

## Scheduling and “sufficient interplay”

The ratings aggregated into P89 were produced through the actual sumo
schedule. They are schedule-conditioned, not measurements obtained from an
ideal experiment.

Elo wrote that self-correction requires “sufficient interplay” within the
pool, but did not provide an operational threshold. The limiting cases are
clear:

- repeated round-robin competition would provide exceptionally strong, close
  to ideal, interplay;
- two groups whose members never meet cannot have an identified relative
  rating offset; and
- mathematical connectivity through a very small number of bridge bouts does
  not guarantee a practically precise relationship between the groups.

Sumo lies in the difficult middle. Most bouts are rank-local, interdivision
bouts are relatively sparse and selective, promotion controls movement between
pools, and later-basho torikumi can depend on earlier records.

The retained connectivity experiments established something useful but
limited. Disconnected synthetic divisions cannot identify their relative
offset. Sparse bridges can identify an offset in controlled toy worlds. An
evidence-shaped Makuuchi--Juryo bridge substantially compressed the recovered
boundary gradient, by about 153 points in the retained experiment, but did not
reproduce the nearly flat historical boundary curve. Connectivity is therefore
a plausible contributor, not an established complete explanation.

This perspective applies to chess as well as sumo. The fact that Elo was
created for chess does not make selective chess schedules harmless.

Two useful theoretical references are:

- Jabin and Junca, *A continuous model for ratings*; and
- Roberto Cortez and **Hagop Tossounian**, *Convergence and stationary
  distribution of Elo rating systems*, published in 2026 and available as
  arXiv:2410.09180.

The spelling is **Tossounian**, not “Toussounian”. Cortez and Tossounian prove
convergence for a pure Elo process in a technical idealisation with a fixed
population, fixed true skills, uniformly random pair selection, a correctly
specified expected-score function, constant K and a zero-sum pool. For fixed
K the process converges to a stationary distribution; as K tends to zero that
distribution concentrates around the assumed true-skill vector. This is
valuable theory, but it does not remove the modelling choices required by
historical sumo.

The detailed theory of scheduling and convergence probably belongs in the
main account's chapters on ordinary Elo, problems and critique. Appendix B
needs enough of it to explain why P89 is schedule-conditioned and why boundary
irregularities cannot simply be read as true ability.

## Predictive evidence: the two axes

The discussion after the first checkpoint exposed two logically distinct axes
on which the project has evaluated the model.

1. **Absolute performance for a given P.** Does
   \(\operatorname{Elo}_{89}(P)\) predict better than 50--50? This establishes
   that a configured Elo-89 contains useful predictive information. For the
   eligible binary outcomes, 50--50 has log loss \(\log 2\), approximately
   0.6931, and Brier score 0.25. For this question, the provenance of P is not
   material: a P obtained by fixed-point iteration, optimisation, judgement or
   even an arbitrary draw can demonstrate the existence of a working
   configuration.
2. **The effect of changing P.** Holding the remainder of Elo-89 fixed, what
   changes when constant, P89, random or otherwise constructed entrant maps
   are substituted? This measures the contribution and sensitivity of the
   prior choice. It is a separate question from whether Elo-89 works at all.

These are not two independent gates which every candidate P must separately
pass. On the same bouts and scoring rule, if P89 performs better than constant
initialisation and the constant-initialisation model performs better than
50--50, the ordering already implies that P89 performs better than 50--50.
The 50--50 benchmark belongs principally to model-level validation; the
constant and alternative-P comparisons belong to prior attribution and
selection.

The existing record should not be rewritten as though P89 “was never
predictively checked”. The current understanding, subject to the audit below,
is that informed initialisation was tested against flat initialisation and
that the complete-W/L fitted source underlying P89 passed a retained
predictive evaluation. Support-weighted aggregation was selected because it
represents the observations more defensibly, not because its incremental
forecast effect had been isolated. The final artifact separately passed strict
loading, complete replay and site-build verification.

## Predictive evidence audit required before Appendix B is finished

The retained experiments must be audited before the adoption argument is
finalised. The audit should reconstruct rather than prejudge:

- which P was used in each predictive experiment;
- whether the configured model was compared with 50--50;
- which informed priors were compared with constant initialisation;
- the evaluation population and whether scores covered all bouts or an
  entrant or early-history window;
- whether prediction-before-update values, bout eligibility and proper-score
  definitions were consistent; and
- whether candidate selection and evaluation reused the same historical data.

Any missing comparison can then be run within one common framework. For each
candidate P, that framework should ideally report absolute log and Brier loss,
improvement over 50--50, improvement over constant initialisation and results
for both the full evaluation population and an explicitly defined early-rated
period. The latter matters because the influence of an entrant prior
dissipates as bout evidence accumulates.

Results from the fitted historical period are development or model-selection
evidence, not prospective validation. The intended freeze date is 30 October
2026 and no later basho has yet supplied genuinely post-freeze evidence.
Future eligible bouts provide the strongest prospective test of the frozen
official configuration. Until the audit is complete, Appendix B should not
overstate either the absolute evidence for Elo-89 or the incremental evidence
for P89.

## The seven remaining Appendix B tasks, updated

### 1. Epsilon 10 versus 8.5

The experiment is complete. Iteration 20 / epsilon 8.5 is the working choice
under the primary log-loss criterion, with iteration 21 / epsilon 8 supplying
the adjacent Brier minimum. What remains is rebuilding and promoting the final
support-weighted artifact and updating Appendix B's stale “serious candidate”
language.

### 2. State the adoption argument explicitly

Appendix B should bring together, in one place:

- the two-axis distinction between absolute model performance and the
  incremental effect of changing P;
- the evidence audit above, without treating the 50--50 and
  flat-initialisation comparisons as redundant gates for every candidate;
- approximate replay consistency as necessary but not sufficient;
- plausibility inspection as informed but informal judgement; and
- the conclusion that none of these establishes a uniquely correct map or a
  minimum unobservable initialisation gap.

### 3. Complete the account of “looked about right”

Add the deliberately familiar chess-like scale, the 1517 origin choice, the
approximately 2500 Yokozuna level, the broad full-banzuke curve and a candid
account of its local and lower-tail irregularities. Add a better chart if it
materially aids the explanation.

### 4. Disclose the Makuuchi--Juryo reversal

Name it as the clearest questionable artifact. Report it accurately, separate
low support from rating direction, list possible mechanisms only as
speculation, and explain why monotonic smoothing was not imposed.

### 5. Explain schedule dependence

Add a concise account of sufficient interplay, disconnected groups, sparse
bridges and why P89 inherits the structure of the historical torikumi network.
Cross-reference the fuller treatment elsewhere rather than turning Appendix B
into a general monograph on Elo convergence.

### 6. Give the final interpretive statement

End with a compact statement that P89 is a reproducible, historically informed
and schedule-conditioned entrant prior under which Elo-89 performs usefully.
It is one selected candidate, not a definitive chii-to-ability mapping, a
statement about a particular rikishi or a demonstrated minimum of the
unobservable initialisation gap.

### 7. Broaden and place future work correctly

The existing mapping-optimisation proposal is recorded at:

```text
src/validation/elo89-expert-account-2/Matters Arising/
  Entrant Prior Mapping Optimisation/README.md
```

That proposal should be broadened into an **entrant-prior sensitivity and
selection** programme. Holding Elo-89 fixed, it should compare:

- constant with non-constant priors;
- P89 with a distribution of appropriately constrained random priors;
- P89 with other constructed maps, including relevant epsilon iterations,
  smoothing or monotonic variants and aggregation choices; and
- P89 with maps produced by optimisation-based searches.

Random P should be a family of meaningful null maps, not one pathological
draw. Useful designs include permutations of P89 values across chii, random
smooth maps with comparable mean, range and roughness, and controlled
perturbations around constant or P89. The common framework should report
absolute performance, the effect relative to constant, P89's position in the
random-map distribution and uncertainty across evaluation periods. “Best P”
must always mean best for a stated score, population, historical period and
set of constraints; it does not mean the true map.

Appendix B should cross-reference this programme without trying to execute all
of it. The narrower evidence audit is required before Appendix B is final;
the full random-prior and optimisation programme remains prominent future
work.

A future Elo-89 successor should also represent rating uncertainty explicitly,
probably through a Glicko-like state. Glicko's rating deviation is pertinent
to sparse evidence, inactivity and immature ratings, but it would not by
itself solve selective scheduling, promotion bottlenecks, injuries or
unobserved changing ability. Detailed successor design belongs in the
critique, alternatives or a separate matter arising.

## One lower-tail caution

An older experimental curve contained an extreme low-rank spike, remembered as
a Jk73 rating above 3000. That spike did not disappear because of the accepted
support-weighted aggregation. It belonged to a rejected feedback variant in
which whole-population preservation was fed back into the literal-prior loop;
the two-observation Jk73w cell rose to roughly 3168. In the accepted literal
source, Jk73e and Jk73w were approximately 906 and 1544 before pairing, and
support weighting made little difference because both had support two.

Do not describe the present lower-tail shape as an unanticipated benefit of
the aggregation correction without new evidence.

## Return pass through the main expert account

When Appendix B is complete, audit every place in the main account which
introduces P89, relies on Appendix B or promises evidence that Appendix B must
deliver. At minimum review:

```text
src/validation/elo89-expert-account-2/README.md
src/validation/elo89-expert-account-2/00 Contents.md
src/validation/elo89-expert-account-2/09 The Exact Elo-89 Model.md
src/validation/elo89-expert-account-2/10 Why Elo-89 Makes Those Choices.md
src/validation/elo89-expert-account-2/11 Critique of Elo-89.md
src/validation/elo89-expert-account-2/12 What Has and Has Not Been Established.md
src/validation/elo89-expert-account-2/13 Other Choices Are Possible.md
src/validation/elo89-expert-account-2/Appendix - Research and Implementation Guide.md
```

The audit should check:

- that Appendix B actually supplies the construction, evidence and
  qualifications promised by the chapters;
- that the chapters do not repeat technical detail better left in the
  appendix;
- that “historically consistent” is used only in the narrow declared sense;
- that predictive evidence is neither understated nor attributed to the
  aggregation correction;
- that absolute Elo-89 performance is distinguished from the incremental
  effect of changing P;
- that no reduction in the unobservable true-ability initialisation gap is
  claimed from fixed-point consistency or predictive scores;
- that the epsilon-8.5 promotion, new hash, iteration count and artifact date
  are consistent everywhere;
- that local reversals are disclosed without invented causal explanations;
- that P89 is never described as the natural ability of a chii; and
- that the prospective evidence boundary is dated consistently.

The intended freeze date is **30 October 2026**. It was chosen because it was
the then-current date and lay cleanly between the September and November
basho. That is the model's prospective boundary: results after that date are
later evidence and must not refit the table. The date on which a document was
written, the artifact was renamed or a decision was recorded is a separate
provenance fact and does not move that boundary. Some current chapters instead
say 6 November 2026; the final return pass should restore 30 October
consistently and, where useful, distinguish the freeze date from the later
documentation or promotion date. Rebuilding the selected epsilon-8.5 artifact
also must not silently change the freeze date.

The old website-account HTML files were reinstated after an earlier mistaken
deletion request and are marked as superseded. They should remain available as
historical artifacts unless a later explicit decision removes them.

## Recommended continuation order

1. Complete the predictive evidence audit: recover the exact retained
   comparisons, identify their populations and configurations, separate
   absolute model performance from the effect of P, and run only comparisons
   which are actually missing.
2. Broaden the existing mapping-optimisation matter into the entrant-prior
   sensitivity and selection programme described above; this records future
   work and need not be executed before Appendix B is finished.
3. Implement the already-decided iteration-20 / epsilon-8.5 entrant-prior
   build, apply support-weighted aggregation and run the full verification
   chain.
4. Update Appendix B with the promoted artifact's exact values, hash,
   iteration, scores and date.
5. Add the adoption argument, scale account, Makuuchi--Juryo disclosure and
   schedule-conditioned interpretation described above.
6. Decide whether a full-map chart materially improves the appendix and, if
   so, create a legible retained artifact.
7. Complete the return pass through Chapters 9--13, the contents, README and
   research guide.
8. Remove the word “Preliminary” only after those checks pass, then commit the
   finished Appendix B and coordinated account changes.

## Key local references

- Current preliminary appendix: [`Appendix B - The Elo-89 Entrant Prior.md`](Appendix%20B%20-%20The%20Elo-89%20Entrant%20Prior.md)
- Expert-account contents: [`00 Contents.md`](00%20Contents.md)
- Research guide: [`Appendix - Research and Implementation Guide.md`](Appendix%20-%20Research%20and%20Implementation%20Guide.md)
- Current paired P89: [`../../analysis/equelo_prior_aggregation/results/priors.csv`](../../analysis/equelo_prior_aggregation/results/priors.csv)
- Aggregation account: [`../../analysis/equelo_prior_aggregation/README.md`](../../analysis/equelo_prior_aggregation/README.md)
- P89 producer account: [`../../analysis/elo89/prior/README.md`](../../analysis/elo89/prior/README.md)
- Epsilon-sweep account: [`../elo89-expert-account/Matters Arising/P1 Epsilon Sweep/README.md`](../elo89-expert-account/Matters%20Arising/P1%20Epsilon%20Sweep/README.md)
- Boundary-monotonicity experiment: [`../../analysis/toy_elo/boundary_monotonicity/README.md`](../../analysis/toy_elo/boundary_monotonicity/README.md)
- Existing mapping-optimisation matter, to be broadened into entrant-prior
  sensitivity and selection: [`Matters Arising/Entrant Prior Mapping Optimisation/README.md`](Matters%20Arising/Entrant%20Prior%20Mapping%20Optimisation/README.md)

## Guardrails for the next session

- Do not say that greater support causes a greater rating.
- Do not say that both proper scores have their exact minimum at epsilon 8.5.
- Do not say that P89 was never predictively evaluated.
- Do not treat 50--50 and constant initialisation as two independent gates
  which every candidate P must separately pass.
- Do not confuse evidence that a configured Elo-89 predicts with evidence
  about the incremental contribution of P.
- Do not say that P89 reduces the true-ability initialisation gap; only an
  observable early-prediction penalty can be compared.
- Do not present replay consistency as sufficient validation.
- Do not present (P=F(P)) as proof of correctness.
- Do not claim that connectivity, promotion congestion or changing banzuke
  depth has been established as the cause of a boundary reversal.
- Do not describe Glicko as solving schedule selection or unobserved ability
  changes.
- Do not silently smooth the prior or silently replace the persisted artifact.
- Do not commit the temporary spreadsheet lock file.
- Do not delete the superseded HTML artifacts without a new explicit decision.
