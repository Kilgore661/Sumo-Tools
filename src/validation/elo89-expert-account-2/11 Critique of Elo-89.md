# 11. Critique of Elo-89

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
historically fitted assumptions and work unevenly across populations.

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
| No individual uncertainty state | Ratings with very different support can have the same value; immature-versus-mature calibration is materially weaker | Deliberately outside the present point-rating model; one open subject for possible successor research |
| Divisional K is a coarse proxy | Small aggregate improvement, but exact schedule was not optimised and cross-boundary behaviour is weaker | Accepted trade-off; candidate for successor research |
| P1-WL is future-informed within its fitting period | Results through September 2026 helped construct the prior used within that history | Disclosure; the table is fixed from 30 October 2026 and later evidence cannot refit it |
| P1 omitted known W/L bouts with blank kimarite | Confirmed and repaired by P1-WL; matched comparison found no material degradation | Resolved by the selected P1-WL prior |
| Sparse and high-churn lower ranks | Earlier fixed points produced extreme rare-rank values; current lower-rank shapes and support remain difficult | Qualified publication and further research |
| Population normalisation affects displayed changes | Reconciled contribution audit; generally modest relative to end rating but sometimes decisive for the sign of a change | Accepted with disclosure |
| Fixed global mean does not stabilise each chii | Measured rank-specific movement and reversals through time | Limits cross-era and rank-level interpretation |
| Frozen return state can become stale | Persistence won the controlled comparison, but a point rating cannot express uncertainty accumulated during absence | Accepted lifecycle rule with an interpretation limit |
| Selective schedule and connectivity | Sumo bouts are not random; subgroup and toy evidence show uneven support | Limit claims to represented matchup network |
| Retrospective model selection | The final model and prior were selected on history through September 2026 | Major evidence qualification; genuinely later evidence begins after the freeze |

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
of represented bouts and the other is principally a P1-WL initialisation. The
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

P1-WL reduces this problem but cannot solve it. It supplies a better point before
personal evidence accumulates; it does not say how uncertain that point is.
Nor does Elo-89 widen uncertainty during inactivity. Retaining the point
estimate without an invented injury penalty is defensible, while continuing
to present it as equally well supported would be stronger than the model
justifies.

An uncertainty-aware Elo-family model is therefore one possible comparator,
not a requirement of the present exploration or a predetermined successor.
That investigation has not been done. Glicko-like systems belong among the
open subjects for later research, alongside alternative responsiveness,
matchup structure, population anchoring and other model choices.

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

## 4. P1-WL improves initialisation but imports the banzuke and the future

P1-WL addresses a real absurdity in equal initialisation. It also changes the
epistemic character of the model.

First, P1-WL uses chii as evidence. The rating system is therefore not wholly
independent of the banzuke at entry. This does not make later ratings numerical
copies of rank: bout results subsequently move individuals freely. It does
mean that early agreement between rating and chii is partly constructed and
cannot validate the prior independently.

Second, the frozen table was fitted using the broad historical period through
September 2026 in which it is retrospectively evaluated. Later careers within
that period help determine starting values assigned to earlier entrants. The
comparison can show internal usefulness and reject obviously bad
constructions, but it is not an unseen-future test. The table was fixed on 30
October 2026, so this criticism does not extend in the same way to results from
November 2026 onward: those results cannot alter the prior.

Third, P1-WL is a population average indexed by chii. Individuals at the same
chii can differ greatly, especially in high-churn lower divisions where a rank
may mix future retirees, long-term lower-division rikishi, rising talent and
returning competitors. A good average can still be a poor initial estimate for
a particular person.

The prior is therefore best understood as a historically fitted regulariser.
It is preferable to declared ignorance in the tested history, but it should
not be presented as the ability naturally belonging to a rank.

## 5. P1-WL repairs the known bout-eligibility defect

This issue was categorically different from the preceding qualifications. It
concerned inconsistent data semantics in the retained P1 artifact and has now
been investigated.

The Elo-89 replay rates every represented binary W/L result whether
or not kimarite is recorded. The replay which generated canonical P1 instead
skips records whose `decision` field is `blank`. In the parsed History, blank
commonly means that kimarite is missing, not that the winner and loser are
unknown.

Consequently, Elo-89 uses the intended result domain after initialisation but
uses an entrant prior estimated from an unnecessarily reduced domain. This is
not evidence that the current ratings are useless and it does not make the
rated bout ledger wrong. It is a correctable defect in a fitted input.

The whole table was therefore regenerated as P1-WL on one frozen History
snapshot using positive W/L eligibility. This admitted 33,521 additional
post-1988 results, all in Makushita and below. Like-for-like prior, predictive,
downstream-artifact and local website comparisons found changes but no material
degradation. P1-WL is the accepted replacement.

The remaining criticism is evidential rather than eligibility: P1-WL is
future-informed within its fitting period, still inherits sparse low-rank
cells and must remain fixed after its declared fitting boundary rather than
being silently refitted as later results arrive.

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

First, later entrants arrive from fixed P1-WL. A shifted incumbent population has
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

## 9. Frozen persistence retains information but not uncertainty

If a rikishi leaves the represented active population, revised Elo-89 archives
his literal rating. A later return restores it before the ordinary population
shift. The inactive rating receives no bout update or common shift.

The rule retains personal evidence and embodies the principle that absence of
competition supplies no new directional information. A controlled comparison
found modestly better proper scores overall and clearer gains in the immediate
return windows, with no invariant failure. This supports persistence over the
former reset-to-prior rule; it does not follow from Elo mathematics alone.

The project's later historical audit also found that gaps in ranked-banzuke
representation are not necessarily permanent retirement events. Most audited
gap episodes occurred around the Jonokuchi/Banzuke-gai boundary. That makes
the active-population definition operationally clear but substantively
imperfect as a proxy for career continuity.

The unresolved problem is that a frozen point does not become less certain.
Long absence may also involve physical change which the result stream cannot
observe. Partial shrinkage, time decay and explicit uncertainty remain
possible successor models, but the evidence does not justify adding one now.

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

It is also retrospective. P1-WL was fitted using the broad period being scored;
the final population policy and diagnostics were developed after extensive
inspection of the same historical system. Bootstrap intervals quantify
sampling variation conditional on that process. They do not undo information
reuse or account for every researcher choice made before the final gate.

The model and P1-WL table are fixed from 30 October 2026. The strongest next
validation is therefore to score genuinely later basho without changing them.
Rolling-origin
experiments could supply additional historical evidence if the prior and all
choices were reconstructed using only information available at each origin.

The absence of prospective evidence does not erase the retrospective result
or prohibit publication. It limits the strength of claims such as “validated
probability” and leaves open how well the selected advantage will persist.

## What needs correction, disclosure or research?

The critique supports two different responses.

### Disclose

- P1-WL is future-informed within the retrospective fitting period through
  September 2026 and fixed thereafter.
- A rating is a point estimate whose support varies by rikishi and date.
- Rating changes include population adjustments.
- Cross-era comparisons depend on the fixed anchor and changing population.
- Lower-rank and cross-boundary interpretations have weaker support.
- A rating is frozen, not shifted or decayed, while its rikishi is inactive.

### Investigate in a successor if Elo proves applicable

- uncertainty-aware or support-dependent updates;
- matchup and contextual residuals;
- responsiveness policies more individual than division;
- lower-rank churn, connectivity and cut-point sensitivity;
- uncertainty growth or decay during long inactivity;
- prospective or rolling-origin evaluation; and
- population anchors with clearer historical interpretation.

Normalisation is not presented as a defect requiring correction. Its effects
have been investigated and accepted with disclosure. Nor is the absence of an
injury penalty such a defect: adding one without evidence would replace one
limitation with an unsupported story.

## Overall assessment

Elo-89 is a disciplined exploration of an Elo-like point-rating model, not a
definitive theory of sumo strength. It succeeds at the central tasks for which
it was built: turning unequal pairwise results into a changing opponent-
sensitive scale, making probabilistic forecasts and exposing a reproducible
modern history.

One deliberate limitation is that one point cannot express both strength and
uncertainty. Whether a Glicko-like system improves on that limitation is an
open question, as are the other possible extensions considered here. Its most
important evidential limitation is retrospective selection with a prior which
is future-informed within its fitting period. Its most important interpretive
limitation is that a fixed global mean does not create an external timeless
standard. Its clearest former data-semantic defect—the reduced bout domain
used to fit P1—has been repaired by P1-WL.

Those conclusions justify qualified use and continued investigation, not the
claim that the model has failed. Chapter 12 now separates more formally what
the project has established from what remains assumption, judgement or open
question.

## Working sources

- `../../analysis/docs/story/22 Elo-89 Rating System Appraisal.md`
- `../../analysis/elo_model_selection/docs/Results 1.md`
- `../../analysis/toy_elo/README.md`
- `../../analysis/elo89_normalisation/docs/Normalisation Investigation.md`
- `../../analysis/elo89_normalisation/docs/Per-Chii Drift Findings.md`
- `../../analysis/equelo/docs/equelo docs/lower_rank_problems.md`
- `../../analysis/docs/story/17 Pre-1989 Bout-Data Completeness and Rating Persistence.md`
- `../../analysis/docs/2026 09 26 Chii and the Measurement of Strength.md`
- `../../../docs/Elo-89 P1 Missing Kimarite Repair.md`
- `../elo89-expert-account/Matters Arising/Kimarite/P1-WL Evaluation/Findings.md`
- `../elo89-expert-account/Matters Arising/Rating Persistence/Frozen Persistence Comparison/docs/Findings.md`
