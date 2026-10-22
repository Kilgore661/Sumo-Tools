# 11. Critique of Elo-89

> **Draft status:** First continuous-prose draft. The chapter distinguishes
> known defects, measured limitations, structural assumptions and plausible
> but untested objections. It does not treat every criticism as a reason to
> withdraw the model.

## The standard of criticism

Elo-89 should be judged against the purpose stated in Chapter 3: a
reproducible, opponent-sensitive numerical account of changing bout-winning
strength in the represented modern record. It is not a numerical banzuke, an
injury report, a measurement of physical ability in isolation, or a complete
definition of greatness.

On that narrower standard, Elo-89 is credible. It improves retrospective log
and Brier loss over Basic Elo and the other tested candidates, its rules are
explicit, and its visible complexities answer real problems of initialisation
and open populations. Those successes make critique more exacting, not less
necessary. A useful model can still misrepresent uncertainty, depend on
historically fitted assumptions, work unevenly across populations and contain
correctable implementation defects.

The criticisms below therefore ask four different questions:

1. What does the model necessarily leave out?
2. Where has the omission or policy produced a measured weakness?
3. Is the present response correction, disclosure, further research or simple
   acceptance of a trade-off?
4. Which conclusions remain safe while the issue is unresolved?

## Criticism register

| Issue | Present evidence | Current disposition |
| --- | --- | --- |
| One scalar state | Structurally cannot express persistent non-transitive or context-specific effects; their size in sumo is unmeasured | Research question and interpretation limit |
| No individual uncertainty state | Ratings with very different support can have the same value; immature-versus-mature calibration is materially weaker | Important limitation; comparator still TBD |
| Divisional K is a coarse proxy | Small aggregate improvement, but exact schedule was not optimised and cross-boundary behaviour is weaker | Accepted trade-off; candidate for successor research |
| P1 is future-informed | The evaluation history helped construct the prior used within that history | Disclosure; prospective evidence still absent |
| P1 omitted known W/L bouts with blank kimarite | Confirmed producer/replay semantic mismatch | Known defect; bounded repair required |
| Sparse and high-churn lower ranks | Earlier fixed points produced extreme rare-rank values; current lower-rank shapes and support remain difficult | Qualified publication and further research |
| Population normalisation affects displayed changes | Reconciled contribution audit; generally modest relative to end rating but sometimes decisive for the sign of a change | Accepted with disclosure |
| Fixed global mean does not stabilise each chii | Measured rank-specific movement and reversals through time | Limits cross-era and rank-level interpretation |
| Departure and return reset state | Deliberately discards earlier rating evidence; no controlled alternative comparison | Accepted modelling judgement, not established optimum |
| Selective schedule and connectivity | Sumo bouts are not random; subgroup and toy evidence show uneven support | Limit claims to represented matchup network |
| Retrospective model selection | Final model and prior have not yet been scored prospectively as a frozen choice | Major evidence qualification, not a publication veto |
| Off-banzuke contract and manifest identity | Code/prose mismatch and incomplete source hashing identified in Chapter 9 | Engineering and documentation work |

## 1. One number may not be enough

Elo-89 represents each active rikishi by one scalar rating. The difference
between two such ratings is sufficient for its forecast. This is powerful
compression, but it imposes a transitive ordering of favourites and treats
everything not represented by that ordering as residual variation.

If A has a persistent advantage over B, B over C and C over A because of
style, handedness, body type or another matchup interaction, no scalar can
represent all three tendencies. Injury, surface condition, tactical change,
stable-specific preparation and tournament situation are likewise absent.
The model cannot distinguish a random upset from evidence of one of those
omitted effects. Both appear as an unexpected result and generate the same
kind of update.

This is a structural criticism, but its practical size is unknown. The
project has not conducted a systematic residual-interaction study with
out-of-sample protection. Memorable head-to-head records and sumo narratives
do not establish a stable effect. The defensible conclusion is conditional:

> Elo-89 gives the best one-dimensional account selected by this project. It
> has not established that one dimension captures every predictively useful
> feature of sumo.

A richer model would earn its complexity only if its contextual terms improve
later forecasts or another declared measurement objective.

## 2. A point rating conceals how well it is known

Two rikishi can have the same Elo-89 rating when one value rests on hundreds
of represented bouts and the other is principally a P1 initialisation. The
printed number contains no confidence interval, rating deviation, effective
sample size or age-of-evidence measure.

This is not the same as uncertainty about the next bout. A 60% matchup
probability already allows either result. The missing quantity is uncertainty
about whether the two point ratings support that 60% estimate securely.

The calibration evidence shows that support matters. In the earlier
four-model comparison, the informed divisional-K model's expected calibration
error was 8.38 percentage points when the less experienced rating had fewer
than 30 prior bouts, compared with 1.12 points at 30--59 and between 0.39 and
2.26 points in the later broad bands. The worst pattern was not simply two new
rikishi: it occurred when an immature rating faced a much more established
one.

P1 reduces this problem but cannot solve it. It supplies a better point before
personal evidence accumulates; it does not say how uncertain that point is.
Nor does Elo-89 widen uncertainty during inactivity. Retaining the point
estimate without an invented injury penalty is defensible, while continuing
to present it as equally well supported would be stronger than the model
justifies.

An uncertainty-aware Elo-family model is therefore a natural comparator.
That investigation has not been done. It remains unknown whether the added
parameters and assumptions would improve sumo forecasts enough to justify the
complexity.

## 3. Divisional K is useful but crude

The 10/15/25/35 schedule lets lower-division ratings move more quickly and
upper-division ratings move more slowly. Controlled comparison found a small
aggregate benefit, so this is not merely decorative complexity.

Nevertheless, division is a blunt proxy. A long-serving Makushita rikishi and
a rapidly rising newcomer receive the same K; a newly promoted Juryo rikishi
changes K at a categorical boundary even though his evidence did not change
discontinuously. The schedule does not respond directly to bout count,
recency, estimated volatility or uncertainty.

Cross-K bouts also cease to be zero-sum. The population correction handles the
resulting mean accounting, but it does not prove that both participants had
the right responsiveness. In the earlier comparison, cross-sekitori-boundary
bouts were a weak subgroup for the informed divisional-K model: its point log
loss was worse than Basic Elo's, although the direct interval included zero
and the group was only about 0.44% of scored bouts.

The appropriate verdict is not that divisional K failed. It improved the
declared aggregate scores. It is that the inclusion of variable K has better
evidence than the exact boundaries and values through which variability is
implemented.

## 4. P1 improves initialisation but imports the banzuke and the future

P1 addresses a real absurdity in equal initialisation. It also changes the
epistemic character of the model.

First, P1 uses chii as evidence. The rating system is therefore not wholly
independent of the banzuke at entry. This does not make later ratings numerical
copies of rank: bout results subsequently move individuals freely. It does
mean that early agreement between rating and chii is partly constructed and
cannot validate the prior independently.

Second, the frozen table was fitted using the broad historical period in which
it is retrospectively evaluated. Later careers help determine starting values
assigned to earlier entrants. The comparison can show internal usefulness and
can reject obviously bad constructions, but it is not an unseen-future test.

Third, P1 is a population average indexed by chii. Individuals at the same
chii can differ greatly, especially in high-churn lower divisions where a rank
may mix future retirees, long-term lower-division rikishi, rising talent and
returning competitors. A good average can still be a poor initial estimate for
a particular person.

The prior is therefore best understood as a historically fitted regulariser.
It is preferable to declared ignorance in the tested history, but it should
not be presented as the ability naturally belonging to a rank.

## 5. P1 contains a known bout-eligibility defect

This criticism is categorically different from the preceding qualifications.
It concerns inconsistent data semantics in the retained artifact.

The Elo-89 production replay rates every represented binary W/L result whether
or not kimarite is recorded. The replay which generated canonical P1 instead
skips records whose `decision` field is `blank`. In the parsed History, blank
commonly means that kimarite is missing, not that the winner and loser are
unknown.

Consequently, Elo-89 uses the intended result domain after initialisation but
uses an entrant prior estimated from an unnecessarily reduced domain. This is
not evidence that the current ratings are useless and it does not make the
production bout ledger wrong. It is a correctable defect in a fitted input.

The repair cannot be made by patching selected P1 rows. P1 is the result of an
iterative replay, aggregation and recentering process, so the whole table must
be regenerated on one frozen History snapshot with positive W/L eligibility.
The old and corrected semantics then need like-for-like prior-map and
predictive comparisons. Adoption should create a newly identified prior
artifact and rebuild Elo-89; routine website builds should not silently refit
it.

This is presently the clearest item in the chapter which calls for corrective
work rather than disclosure alone.

## 6. The lowest ranks remain the least secure

Elo-like ratings acquire meaning through a connected network of persistent
competitors. Jonokuchi and low Jonidan have high churn, short careers, rapid
risers, weak long-stayers, returning rikishi and historically changing banzuke
depth. Many entrants leave before their personal rating becomes mature.

The prior-construction history demonstrates the danger. Literal-chii fixed
points have assigned spectacularly implausible values to rare deep-Jonokuchi
cells; feedback from whole-population normalisation recreated an approximately
3,168 rating for the two-observation `Jk73w` cell. P1's support-proportional
construction avoids adopting that failed feedback loop, but it does not make
every retained low-rank value strongly evidenced.

Nor is the broad rank curve strictly monotone. That may reflect real population
mixtures, changing banzuke structure, sparse support, model failure or several
of these at once. Silently smoothing the curve would hide the evidence;
treating every reversal as a discovery about sumo would overinterpret it.

The lowest-division normalisation results are also the least reassuring. In
the full-history 12-basho contribution study, the 219 observations outside
the author's ±5% practical band all belonged to Jonidan or Jonokuchi.

Current inclusion is a pragmatic judgement. It allows whole careers to be
represented and makes model strain visible. Claims at the bottom of the
banzuke should nevertheless be weaker, and experiments on churn,
connectivity, alternative cut points and later sekitori impact remain
justified.

## 7. Normalisation is invisible in a gap but visible in a history

At the instant a common shift is applied, every active rating gap, ordering
and Elo probability is unchanged. It is therefore tempting to call
normalisation cosmetic. That is incomplete for two reasons.

First, later entrants arrive from fixed P1. A shifted incumbent population has
different gaps from those future entrants, so subsequent forecasts and updates
can differ.

Second, published individual rating changes include every common shift
received while represented. A displayed increase is not necessarily the sum
of positive bout evidence. In May 1992, for example, Konishiki's recorded bout
contribution was about -26.1 points and his normalisation contribution about
+30.4, producing a displayed increase of about +4.2.

The contribution audit prevents exaggerating this criticism. Across all 51
recent sliding 12-basho windows, every eligible Makuuchi and Juryo observation
had a net normalisation contribution within ±1% of end rating. Across the full
history, every Makuuchi and Juryo observation was within ±5%. Positive and
negative shifts substantially cancel.

Those percentages use the chosen rating origin and are practical benchmarks,
not probability-invariant measures. Nor does subtracting the recorded shifts
simulate a counterfactual no-normalisation model, because later bout updates
would also change.

The accepted conclusion is proportionate: normalisation does not presently
undermine the usefulness of Elo-89, but rating-change products must not
describe their values as wholly bout-derived.

## 8. A fixed population mean does not fix historical meaning

Elo-89 holds one global active-population mean constant. That controls one
coordinate, not the composition, schedule or rating distribution within the
population.

The per-chii drift study makes the distinction concrete. Among 382 numbered
groups with at least 60 represented basho over ten years, full-history
post-basho slopes ranged from -104.5 to +92.3 points per decade. M1 period
means rose from about 2,293 in 1989--1993 to 2,512 in 2004--2008 and were about
2,452 in the partial 2024--2026 period. Y1 rose from about 2,515 to 2,939 and
then fell to about 2,633 across the corresponding periods.

These movements are not estimates of causal inflation. Occupants, banzuke
depth, division sizes, schedules and support change over time; Hakuho alone
accounted for 22.1% of the Y1 observations. A single linear slope can also
conceal rises and reversals.

The finding is nevertheless important: identical chii and identical printed
rating values do not acquire timeless meaning merely because the global mean
is fixed. Cross-era comparisons are model-conditional comparisons within an
anchored changing population, not direct measurements against an external
constant standard.

## 9. Departure and return discard information

If a rikishi remains on the banzuke while missing bouts, Elo-89 retains his
rating. If he leaves the represented active population, it discards the
rating; a later return is initialised from P1 at the returning chii.

The rule is clear and accepted for the model, but it is not information-
neutral. A long personal bout history can be replaced by a group prior because
of one population-boundary event. Conversely, archiving the old rating would
assume that old evidence remains the better estimate after an exceptional gap.
Neither answer follows from Elo mathematics.

The project's later historical audit also found that gaps in ranked-banzuke
representation are not necessarily permanent retirement events. Most audited
gap episodes occurred around the Jonokuchi/Banzuke-gai boundary. That makes
the active-population definition operationally clear but substantively
imperfect as a proxy for career continuity.

No controlled modern-domain comparison has measured the predictive effect of
reset, restoration, partial shrinkage toward P1 or uncertainty growth. The
present rule should therefore be described as a lifecycle policy, not a
discovery that prior personal evidence has ceased to matter.

## 10. The observed schedule limits what has been learned

Elo-89 adjusts for the strength of opponents actually faced. It does not turn
sumo into a random round robin.

Torikumi are strongly structured by division and rank and can react to results
within a basho. Unscheduled matchups provide no direct evidence. A connected
path through the bout graph can identify a relative coordinate in principle,
but sparse bridge bouts may leave that relationship weakly supported.

This matters most when extending claims across divisions, distant ranks or
eras. The earlier model comparison found only 2,533 sekitori--sub-sekitori
cross-boundary bouts in its 574,863-bout domain. Toy experiments show that
realistically shaped bridges can identify a divisional offset in controlled
worlds; they do not establish that every historical comparison in the real
network is equally secure.

The rating is consequently opponent-sensitive, not schedule-free. It
describes performance through the matchups sumo supplied and relies on the
scalar model when extrapolating beyond densely observed regions.

## 11. Validation remains retrospective

Elo-89 led a declared, reproducible comparison. Its mean log loss of 0.675629
was better than Basic Elo's 0.682753 and neutral prediction's 0.693147, and
Brier loss supported the same selection. That is genuine evidence.

It is also retrospective. P1 was fitted using the broad period being scored;
the final population policy and diagnostics were developed after extensive
inspection of the same historical system. Bootstrap intervals quantify
sampling variation conditional on that process. They do not undo information
reuse or account for every researcher choice made before the final gate.

The strongest next validation would freeze the model, prior and evaluation
rules and score genuinely later basho without refitting. Rolling-origin
experiments could supply additional historical evidence if the prior and all
choices were reconstructed using only information available at each origin.

The absence of prospective evidence does not erase the retrospective result
or prohibit publication. It limits the strength of claims such as “validated
probability” and leaves open how well the selected advantage will persist.

## 12. Reproducibility is good but not yet complete

The production outputs expose detailed ledgers and snapshots, and the
research comparisons preserve substantially stronger provenance than many
informal rating projects. Chapter 9 nevertheless found two contract-level
weaknesses.

The named-model prose says off-banzuke results are excluded, while the retained
selector would rate a represented off-banzuke W/L result and initialise the
participant through its fallback. The current production ledger contains no
such case, so published values are unaffected, but the prospective policy is
ambiguous.

The production manifest also does not hash every source needed to identify a
run: it copies the P1 table but does not bind the prior source manifest, K
configuration, History snapshot and code version through stable identities.
These are fixable engineering and documentation defects. They do not require a
new statistical model.

## What needs correction, disclosure or research?

The critique supports three different responses.

### Correct

- Regenerate and evaluate P1 with outcome-based W/L eligibility so that known
  results with missing kimarite are no longer discarded.
- Resolve the off-banzuke eligibility contract before such a case affects a
  production run.
- Strengthen production artifact identity and hashing.

### Disclose

- P1 is future-informed in the retrospective evidence.
- A rating is a point estimate whose support varies by rikishi and date.
- Rating changes include population adjustments.
- Cross-era comparisons depend on the fixed anchor and changing population.
- Lower-rank and cross-boundary interpretations have weaker support.
- Return after leaving the represented population triggers reinitialisation.

### Investigate if the project seeks a successor

- uncertainty-aware or support-dependent updates;
- matchup and contextual residuals;
- responsiveness policies more individual than division;
- lower-rank churn, connectivity and cut-point sensitivity;
- alternative departure, return and inactivity policies;
- prospective or rolling-origin evaluation; and
- population anchors with clearer historical interpretation.

Normalisation itself does not currently sit in the “correct” list. Its effects
have been investigated and accepted with disclosure. Neither does the absence
of an injury penalty: adding one without evidence would replace one limitation
with an unsupported story.

## Overall assessment

Elo-89 is a disciplined and useful point-rating model, not a definitive theory
of sumo strength. It succeeds at the central tasks for which it was built:
turning unequal pairwise results into a changing opponent-sensitive scale,
making probabilistic forecasts and exposing a reproducible modern history.

Its most important scientific limitation is that one point cannot express
both strength and uncertainty. Its most important evidential limitation is
retrospective selection with a future-informed prior. Its most important
interpretive limitation is that a fixed global mean does not create an
external timeless standard. Its clearest known defect is the reduced bout
domain used to fit canonical P1.

Those conclusions justify correction and continued investigation, not the
claim that the model has failed. Chapter 12 now separates more formally what
the project has established from what remains assumption, judgement or open
question.

## Working sources

- `../../../../analysis/docs/story/22 Elo-89 Rating System Appraisal.md`
- `../../../../analysis/elo_model_selection/docs/Results 1.md`
- `../../../../analysis/toy_elo/README.md`
- `../../../../analysis/elo89_normalisation/docs/Normalisation Investigation.md`
- `../../../../analysis/elo89_normalisation/docs/Per-Chii Drift Findings.md`
- `../../../../analysis/equelo/docs/equelo docs/lower_rank_problems.md`
- `../../../../analysis/docs/story/17 Pre-1989 Bout-Data Completeness and Rating Persistence.md`
- `../../../../analysis/docs/2026 09 26 Chii and the Measurement of Strength.md`
- `../../../../../docs/Elo-89 P1 Missing Kimarite Repair.md`
