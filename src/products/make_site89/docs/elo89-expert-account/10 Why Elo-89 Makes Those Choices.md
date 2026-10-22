# 10. Why Elo-89 Makes Those Choices

> **Draft status:** First continuous-prose draft. This chapter is a decision
> account, not a claim that every component was selected by one experiment or
> that the tested alternatives exhaust the design space.

## Different choices have different kinds of support

Chapter 9 specified Elo-89 as though it were an executable contract. That is
necessary for reproduction, but the uniform presentation can conceal how the
contract was reached.

Some choices were selected by controlled retrospective comparisons. Some were
inherited from Basic Elo or earlier Equelo work and retained because the
evidence supplied no reason to change them. Some are modelling judgements
needed to make an open historical rating population well defined. Others are
engineering consequences of asking for deterministic, publishable results.

This chapter uses the following labels:

- **evidence-led selection**: declared alternatives were compared on relevant
  recorded outcomes;
- **modelling judgement**: a necessary interpretation or policy was chosen,
  with reasons but without a decisive comparative experiment;
- **inherited convention**: a prior project choice was held fixed so that
  other questions could be isolated;
- **engineering necessity**: the recurrence or publication cannot be
  reproduced without the choice; and
- **open question**: a plausible alternative has not been tested adequately.

One choice can have more than one status. Divisional K, for example, has an
inherited numerical schedule but its inclusion was also tested against
constant K.

## Decision register

| Component | Main status | Reason for the retained choice | Important qualification |
| --- | --- | --- | --- |
| January 1989 epoch | Modelling judgement and inherited research boundary | Begins the deliberately modern, sufficiently complete comparison domain used by Basic Elo | No epoch search established January 1989 as uniquely optimal; pre-1989 lower-division evidence is substantial but irregular |
| Binary fought-result domain | Modelling judgement | Uses represented W/L evidence, including known results with missing kimarite, while excluding fusen and non-binary outcomes | Alternative treatment of fusen was not selected experimentally; off-banzuke wording remains unresolved from Chapter 9 |
| `RikId` identity and forecast-before-update chronology | Engineering necessity | Preserves one career across shikona changes and prevents the result being used in its own forecast | These choices support a valid experiment; they are not empirical discoveries about ability |
| (q=400) | Inherited convention with diagnostic support | Keeps the canonical Basic Elo probability scale; mature-rating calibration supplied no compelling reason for a global change | It was not chosen by a comprehensive search and is not proved optimal |
| Divisional K | Evidence-led selection plus inherited schedule | It modestly improved retrospective log and Brier loss, and lets lower-division ratings respond faster | The exact K values were not independently optimised; division is only a proxy for rating maturity |
| P1 initialisation | Evidence-led selection plus modelling judgement | Informed initialisation supplies most of the gain over Basic Elo and avoids pretending all entrants are initially equal | P1 is future-informed, low-support chii remain problematic, and its construction contains judgement |
| Fixed P1 | Evidence-led rejection of feedback | Re-solving the prior through the production population operator recreated extreme low-support values | Fixing the artifact does not establish that P1 is timeless or uniquely correct |
| Whole-population mean preservation | Evidence-led selection plus anchoring judgement | It gave the best tested aggregate log and Brier loss and controls the coordinate carried by incumbents relative to future entrants | The old model retained slightly better aggregate calibration error; a fixed mean does not prove absolute cross-era equivalence |
| Start and end common shifts | Modelling and accounting judgement | The start shift handles turnover; the end shift exactly absorbs unequal-K mass while preserving current differences | The end correction is tiny and adds almost no tested predictive benefit |
| Departure discards; return reinitialises | Modelling judgement | Defines a clean represented-population lifecycle and uses current chii evidence on return | It was not selected against a persisted-rating return model |
| No inactivity decay while still represented | Modelling judgement | Absence alone supplies no quantified direction or magnitude of change | Confidence may become less secure even when the point estimate is retained |
| Point rating only | Inherited simplification | Keeps the system transparent and close to Elo | No uncertainty-aware production comparator has been run |
| Multiple observation stages | Engineering and publication necessity | Different tools legitimately require pre-bout, day-end or basho-boundary states | Every publication must name the stage it uses |

## Why begin in January 1989?

The initial purpose was to ask whether a deliberately simple Elo model could
extract information from the modern represented record. January 1989 supplied
a practical boundary after which the all-division data used by the project
were treated as sufficiently complete for a common chronological comparison.
Every subsequent candidate could then be scored on the same domain.

This is a defensible scope choice, not a discovered discontinuity in sumo. The
later completeness audit showed that the pre-1989 record is neither uniformly
complete nor generally empty. Makuuchi and Juryo are complete throughout the
audited period, while lower-division coverage improves irregularly and
contains both complete and sparse basho. There is no single date on which all
historical evidence changes character.

Elo-89 therefore says: *this is the model's modern evidence boundary*. It does
not say that relevant competition began in 1989, or that no earlier rating
system can be constructed. Elo-58 is the project's qualified attempt to ask
that different historical question.

## Why retain the binary result domain?

The model is intended to learn from represented competitive results. A W/L
pair records the evidence needed by its binary update even when kimarite is
missing. Excluding such a result merely because a technique field is blank
would discard known outcome evidence for an unrelated metadata omission.

Fusen are treated differently. They identify a winner and loser
administratively, but not the outcome of a fought bout under the same
competitive process. Excluding them avoids silently treating non-contest
events as ordinary performance evidence. Other non-binary outcomes likewise
fall outside the two-outcome model.

This is principally a semantic modelling choice. The project has not shown
by controlled comparison that every possible numerical treatment of fusen is
worse. Chapter 9 also identified a prospective ambiguity about off-banzuke
W/L records; that needs an explicit contract decision rather than a rationale
invented after the fact.

## Why (q=400)?

The value (q=400) came from the canonical Basic Elo baseline. Holding it
fixed made the later factorial comparison answer clear questions about K and
initialisation instead of changing the probability scale at the same time.
When P1 was rebuilt, its maintained producer was also moved to (q=400), so
the prior and replay no longer mixed the Basic Elo scale with legacy
(q=900) machinery.

Calibration analysis gave a reason not to interrupt the model-selection story
for a global q search. Apparent aggregate overconfidence was concentrated
mainly in contests where an immature rating faced a mature one. Once both
ratings had more evidence, calibration on the (q=400) scale was much closer.
Changing q globally might improve one weakly supported population while
damaging mature comparisons.

That is support for retention, not optimisation evidence. The project did not
compare a declared grid of q values under otherwise identical final Elo-89
conditions. A later study could still ask whether another expectation curve
or scale improves prospective forecasts.

## Why divisional K?

The substantive idea is that lower-division ratings often belong to newer or
more rapidly developing rikishi and should respond faster, while upper-
division ratings usually have more evidence and should be less volatile.
Division is used as an observable proxy for those differences. It is not an
individual measurement of uncertainty or rate of development.

The controlled two-by-two comparison separated constant versus divisional K
from constant versus informed initialisation. Divisional K improved mean log
loss by 0.000738 under constant initialisation and by 0.001110 with the older
informed prior. The effects were favourable but much smaller than the effect
of informed initialisation. Brier loss agreed with the aggregate ordering.

This supports including a variable K policy. It does not show that the exact
schedule 10/15/25/35 is uniquely or locally optimal. Those values were an
inherited FIDE-style schedule, held fixed during model selection. Nor does it
show that division is better than direct experience, age, estimated
uncertainty or another responsiveness model.

The cost is also explicit. When opponents have different K values, their
updates are not zero-sum. The cumulative audit found this mass flow small
relative to turnover effects, and Elo-89's post-basho common shift accounts
for it exactly at population level. That makes it manageable, not
mathematically nonexistent.

## Why use an informed prior at all?

Equal initialisation is simple only in notation. At the January 1989 epoch it
would give an established Yokozuna and a low-ranked newcomer the same prior
state; on later entry it would discard information already present in chii.
The relevant question was therefore not whether to pretend ignorance, but how
to use rank evidence without forcing subsequent ratings to reproduce the
banzuke.

The original factorial comparison provided strong retrospective support for
informed initialisation. Relative to Basic Elo, the older prior improved mean
log loss by 0.004698 with constant K; with divisional K, most of the combined
improvement still came from the prior. The benefit was concentrated where it
should be: new and immature ratings.

This establishes that informed starting information is useful in the tested
history. It does not by itself select P1.

## Why P1 rather than the older prior?

The old informed prior was a contextual construction and remained slightly
better than early P1 candidates in retrospective prediction. P1 was developed
to repair a different problem: repeated uniform recentering of a literal-chii
fixed point allowed rare low-support cells to acquire absurd values.

The support-proportional rule used for P1 materially changes differences in
the chii map. Its adoption was therefore a modelling judgement, informed by
support diagnostics and inspection of the resulting curve rather than a
neutral coordinate change. The project deliberately retained visible
discontinuities and did not smooth the table merely to make ratings descend
monotonically with rank.

The canonical (q=400) P1 then passed the existing predictive gate. With
divisional K and no population adjustment it achieved mean log loss 0.677319,
very close to the older model's 0.676945, and retained about 94% of the old
model's improvement over Basic Elo. Its remaining deficit was concentrated in
the first 30 rated bouts.

P1 was accepted as a credible, reproducible prior which repaired a known
construction pathology while preserving most measured predictive value. It
was not selected because it won every score: it did not.

Both prior artifacts use later history to initialise earlier entrants in the
retrospective evaluation. The result is model-selection evidence and an
internal coherence check, not unseen-data validation.

## Why hold P1 fixed?

It might appear tidier to produce P1 using the same whole-population operation
used by the final replay. That was tested. When the operator was allowed to
feed back into the literal-chii fixed-point loop, low-support values became
extreme again: the two-observation `Jk73w` cell rose to about 3,168, and the
solve took 71 iterations rather than 18.

Controls showed that the pathology came from feedback between turnover
correction and entrant-prior estimation, not from the small unequal-K mass
correction. Thus two individually coherent ideas did not form a coherent
self-generating loop.

The retained boundary is evidence-led:

1. P1 is an externally fitted, frozen initialisation artifact; and
2. whole-population preservation operates only during the subsequent Elo-89
   replay.

Re-estimating P1 on later data may create a new fitted release, but it is not a
step performed at every production replay.

## Why preserve the whole-population mean?

Ordinary equal-K Elo conserves rating mass within a bout. It does not prevent
the active mean moving when entrants and departures carry different ratings
into and out of an open population. Elo-89 needs an anchor if ratings printed
at different dates are to remain on one administered coordinate.

Three policies were compared with canonical P1 held fixed on the same 574,863
bouts:

| Population policy | Mean log loss | Mean Brier loss | Aggregate ECE |
| --- | ---: | ---: | ---: |
| No population adjustment | 0.677319 | 0.242086 | 0.014453 |
| Expt2 departure redistribution | 0.684196 | 0.245148 | 0.017651 |
| Whole-population preservation | **0.675629** | **0.241362** | 0.014537 |

Whole-population preservation improved log loss by 0.001690 over no
adjustment and by 0.008568 over Expt2 departure redistribution. The recorded
basho-block bootstrap intervals excluded zero, and Brier loss agreed. It also
beat the previous overall candidate, although that older model retained a
slightly lower aggregate ECE.

The improvement was concentrated in younger ratings. This matches the
mechanism: a common shift cannot change probabilities among present rikishi at
the instant it is applied, but it changes the coordinate incumbents carry
relative to fixed P1 ratings assigned to later entrants.

The policy was therefore selected on the predeclared primary log-loss
criterion with corroboration from Brier loss and a coherent mechanism. It was
not selected because a constant population mean is a theorem about constant
sumo ability. The anchor is an administered modelling convention which makes
longitudinal numbers interpretable under declared assumptions.

## Why shift both before and after a basho?

The start shift addresses the large effect: entry and departure change the
active population. The end shift addresses the much smaller net mass created
by unequal K values during the bouts.

The controlled replay found average corrections of roughly 3.975 points per
active rikishi at the start and 0.040 at the end. A start-only policy and a
start-plus-end policy had virtually identical diagnostic losses. Thus the
post-bout shift is retained mainly because it closes the accounting contract:
every published basho-end population has exactly the target mean.

Both shifts are common additions. They preserve current ranking, gaps and
matchup probabilities at application time. Over a longer history they are not
causally inert, because later entrants arrive from fixed P1.

The later normalisation audit found that common shifts can contribute
appreciably to a particular displayed rating change, even though signed
effects substantially cancel. Across 51 recent sliding 12-basho windows, all
eligible Makuuchi and Juryo observations had a net normalisation contribution
within one per cent of end rating. The full-history record contains larger
low-division exceptions. The retained judgement is acceptance with
disclosure, not a claim of zero effect.

## Why these lifecycle rules?

A rikishi who remains on the banzuke remains in the active population even if
he records no eligible bout. Elo-89 leaves his individual point estimate
unchanged apart from the common population shifts. An injury or absence may
matter, but absence alone does not state the size or even the direction of an
ability change. Adding automatic decay would turn a plausible story into an
unmeasured numerical rule.

When a rikishi leaves the represented population, Elo-89 discards the rating;
on return it uses P1 at the new chii. This was accepted as a clean policy for
the exceptional returns in the modern domain. It was not selected in a
controlled comparison with archiving and restoration, time decay or an
uncertainty-widening model.

That distinction must remain visible. “No update during absence” and
“reinitialise after leaving the represented population” are different rules.
Neither claims direct knowledge of current physical condition.

## Why select by log loss?

The model is used to attach probabilities to binary outcomes, so the primary
comparison used mean log loss calculated from forecasts made before their
results were processed. Log loss is a proper scoring rule and strongly
penalises confident errors. Brier loss was retained as an independent proper-
score check; calibration diagnostics examined whether nominal probabilities
matched observed frequencies in important subgroups.

The project declared log loss as primary before inspecting the model ordering.
That matters because different summaries did not choose exactly the same
winner. Elo-89 had the best tested aggregate log and Brier loss. The older
informed-prior model had slightly better aggregate ECE, and alternatives were
slightly better in the longest-career bands. Changing the decision rule after
seeing those results would obscure rather than resolve the trade-off.

The resulting claim is deliberately bounded:

> Elo-89 is the selected model among the tested candidates under the declared
> retrospective primary criterion, with agreeing Brier evidence and recorded
> calibration qualifications.

It is not “the true model of sumo” or the winner of every possible evaluation.

## What evidence could change these decisions?

The model is frozen for production, not insulated from criticism. A serious
alternative would need an exact contract and a like-for-like comparison. The
most informative new evidence would include:

- prospective or rolling-origin results for the frozen P1 model;
- a declared q or expectation-curve comparison which protects the already
  good calibration of mature ratings;
- a responsiveness policy based directly on rating support or uncertainty,
  compared with divisional K;
- an uncertainty-aware model which improves forecasts and communicates stale
  or immature estimates better;
- a controlled comparison of persistence, reinitialisation and decay across
  genuine departures and returns;
- a population anchor with clearer historical interpretation and equal or
  better predictive behaviour; or
- evidence that a subgroup regression is large enough to outweigh aggregate
  gains.

Until such evidence exists, the present choices are defensible. Their status
must nevertheless remain attached to them: tested selection where comparison
was performed, judgement where it was not, and open question where the
project's work is still thin.

Chapter 11 now critiques Elo-89 on those terms rather than criticising it for
failing to prove claims it does not make.

## Working sources

- `../../../../analysis/elo_model_selection/README.md`
- `../../../../analysis/elo_model_selection/docs/Results 1.md`
- `../../../../analysis/prediction/docs/experiments/Findings.md`
- `../../../../analysis/equelo_bkp1/README.md`
- `../../../../analysis/equelo_population_policy/README.md`
- `../../../../analysis/docs/story/07 Draft Equelo Account for the STEM Reader.md`
- `../../../../analysis/docs/story/15 Tranche 1 - Population Normalisation Policy.md`
- `../../../../analysis/docs/story/16 Handoff After Tranche 1.md`
- `../../../../analysis/docs/story/17 Pre-1989 Bout-Data Completeness and Rating Persistence.md`
- `../../../../analysis/docs/story/22 Elo-89 Rating System Appraisal.md`
- `../../../../analysis/elo89_normalisation/docs/Normalisation Investigation.md`
