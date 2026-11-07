# Where We Got To: Expert Account and Appendix B

**Handoff date:** 7 November 2026

**Repository:** `X:\Sumo-Tools`

**Branch at handoff:** `dev`
**Base HEAD before the checkpoint:** `0820eb7` (`Install P1-prime-WL prior and update account`)

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
- mapping-space optimisation as future work.

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

This handoff, the preliminary Appendix B and the matters arising are intended
to be included in the requested documentation checkpoint, together with the
coordinated P89 terminology and production-reference revisions. The temporary
spreadsheet lock file is expressly excluded.

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

The positive case for adopting it has three parts:

1. **Predictive usefulness.** Controlled retrospective work established that
   rank-informed initialisation improves on a flat starting value, especially
   while individual ratings are immature. The complete-W/L fitted source
   underlying P89 passed the retained predictive evaluation before final
   aggregation.
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
> not a recovered law connecting chii to true ability.

The phrase **historically consistent** is safe only if it is explicitly
limited to approximate consistency with the declared historical
replay-and-aggregation procedure. It must not imply consistency with
unobservable historical ability or prove cross-era comparability.

## Fixed point, mapping search and mean preservation

The code resembles a fixed-point finder for a historical reason: the project
initially expected the fixed point to be the best answer. That expectation was
not justified. The operator (F) was designed by the project, and satisfying
(P=F(P)) would establish only self-consistency under that operator.

The epsilon sweep showed that continued numerical convergence eventually made
log and Brier loss worse. The iteration is therefore now understood as one
reproducible path through the space of chii-to-rating mappings. It found a
useful early region; it did not prove that the limit is special.

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

## Predictive evidence: wording that must be preserved

The existing record should not be rewritten as though P89 “was never
predictively checked”. The current understanding of the evidence chain,
subject to the audit required in the next section, is:

- informed initialisation was tested against flat initialisation;
- the complete-W/L fitted source underlying P89 passed the retained predictive
  evaluation;
- support-weighted aggregation was compared with the alternative pooling
  rules and selected because it represents the underlying observations more
  defensibly; and
- the final artifact passed strict loading, complete replay and site-build
  verification.

What was not isolated was the incremental predictive effect of replacing the
fitted source's legacy aggregation with support weighting. Support weighting
was not selected because it had been shown to improve forecasts. It was
selected because equal-cell aggregation gave arbitrary low-support cells the
same influence as heavily represented cells.

This clarification has already been applied to the preliminary Appendix B,
Chapter 12, Chapter 13, the Research and Implementation Guide and the
aggregation README.

## Predictive benchmark audit required before Appendix B is finished

Before the adoption argument is treated as complete, the retained experiments
must be audited to establish exactly which configurations and evaluation
populations were compared. Two separate tests are required because they answer
different questions:

1. **Official Elo-89 with P89 versus 50--50.** This asks whether the complete
   model contains useful predictive information at all. For the eligible
   binary outcomes, 50--50 has log loss \(\log 2\), approximately 0.6931, and
   Brier score 0.25.
2. **Official Elo-89 with P89 versus the same model with constant entrant
   ratings.** This asks whether the additional rank-informed prior improves on
   the simpler initialisation. It should be reported over the full evaluation
   population and over an explicitly defined entrant or early-history window,
   because the effect of an initial rating dissipates as bouts accumulate.

The desired evidential position is that the exact official configuration
passes both tests on a common, clearly described evaluation set. Beating
constant initialisation would not rescue a complete model that failed to beat
50--50. Conversely, beating 50--50 would establish some predictive usefulness
for Elo-89 but would not by itself justify P89's extra complexity.

The audit should first determine whether these comparisons have already been
run; it should not assume that they are absent merely because the current
accounts describe them incompletely. Any missing comparison should then be
run using prediction-before-update values, identical bout eligibility and the
same proper-score definitions.

Results from the fitted historical period are development or model-selection
evidence, not prospective validation. The intended freeze date is 30 October
2026 and no later basho has yet supplied genuinely post-freeze evidence.
Future eligible bouts provide the strongest prospective version of the first
test and can also compare the frozen P89 and constant-initialisation variants.
Until this audit is complete, Appendix B should not imply that both nested
predictive requirements have been established.

## The seven remaining Appendix B tasks, updated

### 1. Epsilon 10 versus 8.5

The experiment is complete. Iteration 20 / epsilon 8.5 is the working choice
under the primary log-loss criterion, with iteration 21 / epsilon 8 supplying
the adjacent Brier minimum. What remains is rebuilding and promoting the final
support-weighted artifact and updating Appendix B's stale “serious candidate”
language.

### 2. State the adoption argument explicitly

Appendix B should bring together, in one place:

- the predictive benchmark audit above, including both the 50--50 and flat-
  initialisation comparisons;
- approximate replay consistency as necessary but not sufficient;
- plausibility inspection as informed but informal judgement; and
- the conclusion that none of these establishes a uniquely correct map.

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
and schedule-conditioned entrant prior, not a definitive chii-to-ability
mapping or a statement about a particular rikishi.

### 7. Place future work correctly

The mapping-space programme is already recorded at:

```text
src/validation/elo89-expert-account-2/Matters Arising/
  Entrant Prior Mapping Optimisation/README.md
```

Appendix B should cross-reference it without trying to execute it. A future
Elo-89 successor should also represent rating uncertainty explicitly, probably
through a Glicko-like state. Glicko's rating deviation is pertinent to sparse
evidence, inactivity and immature ratings, but it would not by itself solve
selective scheduling, promotion bottlenecks, injuries or unobserved changing
ability. Detailed successor design belongs in the critique, alternatives or a
separate matter arising.

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

1. Inspect and checkpoint the main expert-account revisions which were judged
   commit-ready, excluding temporary lock files.
2. Complete the predictive benchmark audit: recover the exact retained
   comparisons, identify their populations and configurations, and run only
   the missing 50--50 or constant-initialisation comparisons.
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
- Mapping-optimisation matter: [`Matters Arising/Entrant Prior Mapping Optimisation/README.md`](Matters%20Arising/Entrant%20Prior%20Mapping%20Optimisation/README.md)

## Guardrails for the next session

- Do not say that greater support causes a greater rating.
- Do not say that both proper scores have their exact minimum at epsilon 8.5.
- Do not say that P89 was never predictively evaluated.
- Do not imply that the exact official P89 configuration has passed both the
  50--50 and constant-initialisation benchmarks until the evidence audit has
  established that result.
- Do not present replay consistency as sufficient validation.
- Do not present (P=F(P)) as proof of correctness.
- Do not claim that connectivity, promotion congestion or changing banzuke
  depth has been established as the cause of a boundary reversal.
- Do not describe Glicko as solving schedule selection or unobserved ability
  changes.
- Do not silently smooth the prior or silently replace the persisted artifact.
- Do not commit the temporary spreadsheet lock file.
- Do not delete the superseded HTML artifacts without a new explicit decision.
