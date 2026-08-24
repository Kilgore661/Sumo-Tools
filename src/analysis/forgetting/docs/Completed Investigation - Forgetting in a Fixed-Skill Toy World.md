# Completed Investigation: Forgetting in a Fixed-Skill Toy World

## Purpose of this account

This document records the completed fixed-skill toy-world investigation. It is
intended to let a future reader recover not only what was run, but why the
observations support the conclusion eventually drawn.

The design record is [Proposal 1: Forgetting in a Fixed-Skill Toy
World](Proposal%201%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md).
Exact code, run directories, commands, file schemas, and historical naming are
catalogued in the [Technical Companion](Completed%20Investigation%20-%20Technical%20Companion.md).

## Conclusion first

In the declared fixed-skill toy world, all twelve alternative initializations
tested were empirically forgotten relative to the true-skill initialization,
`T0`. Initialization materially affected the initial ratings, forecasts, and
the duration of the transient, but it had no detectable effect on the eventual
fixed-`K` stochastic regime within the observed horizon.

More precisely:

- `TC`, `TI`, and `TR01`--`TR10` were each paired with `T0` on exactly the same
  schedules and realized outcomes within every replicate.
- Every one of the 800 replicates for every alternative entered the strictest
  declared all-pair probability-disagreement tolerance, `0.005`.
- The latest first qualifying event was event 87. Because qualification
  required 25 consecutive events, that case was confirmed at event 111.
- No later recrossing was observed through event 500.
- At event 500, even the largest model-level mean paired disagreement was only
  about `1.7e-8` rating points and `2.4e-11` probability.
- Once paired disagreement was negligible, all tested models exhibited the
  same truth-relative levels, percentile widths, and cancellation result to
  practical precision.
- `T0` reached settled truth-relative behaviour sooner than every tested
  alternative. This is consistent with the motivating intuition, but it is not
  a proof that `T0` minimizes settling time over every possible initialization.

These are finite experimental findings conditional on the declared world. They
are not a theorem of convergence, a claim of predictive usefulness, or an
automatic result about changing skills, entrants, retirements, or historical
sumo.

## 1. The question

The motivating practical problem concerned initialization lag. If an Elo
system starts every competitor at the same value, competitors who are truly
strong should generally rise and those who are weak should generally fall.
That observation does not answer how long the initial ratings continue to
matter. In a real population, some competitors may leave before the system has
lost that initial influence.

The first instinct was to ask when ratings “converge” or “stabilize.” For a
fixed, non-zero `K`, that language is misleading. Random outcomes continue to
move ratings indefinitely. Even a process initialized with the true latent
skills immediately moves away from them and then fluctuates around a non-zero
truth-relative error level.

The useful question is instead counterfactual:

> If two Elo processes saw exactly the same bouts and outcomes but began from
> different rating maps, would their current ratings or forecasts still be
> materially different?

Forgetting means loss of sensitivity to the initial map. It does not mean that
ratings stop moving or converge permanently to true skill.

### 1.1 How the question was refined

The work began with a recollection that `toy_elo` had investigated how long Elo
ratings take to “stabilize” from predetermined initial ratings. That language
mixed several different ideas:

- movement of displayed ratings away from their initial values;
- error relative to latent skill;
- predictive usefulness;
- approach to a stationary fixed-`K` distribution;
- disappearance of differences caused by initialization.

The first important separation was usefulness. Whether Elo forecasts outperform
a 50--50 predictor is a separate empirical question. Initialization can be
forgotten even by a useless rating system, and a useful system can retain an
initialization effect. No usefulness criterion is needed to define the
counterfactual comparison here.

The second separation was truth. In the toy world, latent skill is known, which
makes truth-relative error observable. But truth-relative error alone cannot
measure forgetting. If `T0` moves 20 points away from latent skill, that says
that random outcomes and fixed `K` moved it; it does not say whether a process
started elsewhere would now be in the same place.

The third separation was between one trajectory and a paired counterfactual.
One initialization cannot demonstrate loss of sensitivity to initialization.
At least two processes must consume the same evidence. That led to the final
operational definition: initialization memory is the remaining paired
difference after holding the full observed history fixed.

These distinctions explain why the completed work is a development of
`toy_elo`, but not merely another attempt to find a conventional convergence
time. `toy_elo` supplied the controlled world and known latent skills; the new
work changed the object of study from convergence of one process to forgetting
between coupled processes.

## 2. The controlled world

The experiment deliberately uses a world in which the answer is known.

There are ten permanent rikishi with fixed latent skills, centred at zero and
separated by 40 Elo points:

```text
180, 140, 100, 60, 20, -20, -60, -100, -140, -180
```

For each bout, the true winning probability is generated by the usual Elo
logistic form with `Q=400`. An event is one complete round robin: all 45
unordered pairs fight once in a seeded random order. Consequently, every
rikishi receives nine bouts per event.

Every displayed-rating process uses ordinary zero-sum Elo with `K=5` and
`Q=400`. The population, latent skills, schedule rule, outcome process, and
update parameters never change.

This is intentionally favourable terrain for forgetting. There are no
entrants, retirements, changing skills, missing observations, or schedule
imbalances. If initialization memory cannot be separated from continuing Elo
noise here, there is little prospect of doing so in historical data where
latent skill is hidden.

## 3. Initializations

The following model names were used:

- `T0`: ratings initially equal the latent skills.
- `TC`: every rating initially equals the common midpoint, zero.
- `TI`: the latent-skill vector is inverted.
- `TR01`--`TR10`: ten reproducible random maps.

Each random map began with independent raw draws from Uniform[-360, 360] and
was then translated to population mean zero. Translation does not change rating
differences or Elo probabilities; centring makes the normalization explicit.

`T0` is privileged because it begins with the correct latent gaps. It is not a
stationary process and is not assumed to remain at truth. It supplies the
counterfactual reference: an alternative initialization has been forgotten
when its ratings and forecasts become practically indistinguishable from those
of the paired `T0` process after both have consumed the same evidence.

## 4. Why the processes were paired

Within each replicate, `T0` and the alternative initialization receive the
same ordered pair and the same result at every bout. Replicates have distinct,
deterministically derived seeds, so histories are independent between
replicates but identical between the two processes being compared.

This coupling is essential. If separately generated histories were compared,
their differences would mix initialization memory with different random
evidence. Under natural coupling, the realized score term cancels when the two
Elo updates are subtracted. The remaining difference evolves through the
processes' different expected scores. The paired distance therefore isolates
the effect of initialization.

## 5. Measurements

### 5.1 Paired forgetting measurements

The direct state measurement is centred rating-state RMSE between two coupled
processes. Centring makes the distance invariant to an arbitrary common rating
translation.

The primary forgetting measurement is all-pair probability RMSE. At each event
snapshot, both rating vectors imply a probability for every one of the 45
pairs. The RMSE between those two probability vectors measures how much the
initial map still changes the forecasts Elo would make.

Four absolute probability tolerances were declared:

```text
0.05, 0.02, 0.01, 0.005
```

A replicate's first qualifying event is the first event beginning 25
consecutive observations at or below the tolerance. The output also records
right-censoring and later recrossing. No tolerance is asserted to be the one
true boundary of forgetting; they provide interpretable empirical landmarks.

### 5.2 Truth-relative measurements

For each model separately, rating-state RMSE against latent skill and all-pair
probability RMSE against the latent probabilities were recorded. These are not
forgetting measurements. They show what a process does relative to truth before
and after initialization memory has disappeared.

This distinction became central. A non-zero truth-relative RMSE can continue
indefinitely while the paired distance between differently initialized
processes becomes negligible. That is precisely the qualitative pattern the
experiment was designed to detect.

### 5.3 Signed-error cancellation

For every rikishi, the final signed rating error is averaged across replicates.
The RMSE of the ten player-specific mean errors is then calculated. Unlike the
within-run TRMSE, positive and negative errors can cancel across histories.

This is a Monte Carlo sanity diagnostic, not a forgetting metric. Its curve is
cumulative and need not decline monotonically: adding one more replicate can
move the vector of player means either towards or away from zero. The compact
summary is therefore the endpoint pair:

```text
(cancellation RMSE at N replicates, N)
```

No non-zero cancellation plateau or cancellation “settling time” is assumed.

### 5.4 The descriptive results table

For presentation, each standalone model-run is summarized as:

```text
results(T) = (TRMSE, PRMSE, Cancel)
```

`TRMSE` and `PRMSE` are triples containing a terminal level, settling event,
and terminal 5th--95th percentile width. The terminal level and width are
medians over the final 100 events. The settling event begins the first
25-event window during which both the ensemble mean and percentile width remain
within 5% of their terminal values.

These settling events describe the standalone truth-relative charts. They must
not be confused with the paired forgetting landmarks.

## 6. What was run

The canonical experiment used:

```text
10 rikishi
K = 5
Q = 400
800 replicates
500 events per replicate
history master seed = 1
25-event persistence
```

The sequence was:

1. Small deterministic and development runs verified the updater, schedule,
   replay, centring, metrics, and output audit trail.
2. A standalone `T0` ensemble established the natural fixed-`K` baseline.
3. `TC` was run alone and paired with `T0`.
4. `TI` was run alone and paired with `T0` as a deliberately adverse control.
5. Ten reproducible random maps were each run alone and paired with `T0` using
   the same canonical history ensemble.
6. A larger standalone `T0` run used 3,200 replicates and 2,000 events to check
   the baseline over substantially greater support and horizon.

The implementation lives in `src/analysis/forgetting/toy/`; generated artifacts
live in `files/output/analysis/forgetting/toy/`. The compact cross-run table is
`files/output/analysis/forgetting/toy/results_table/results_seed1.csv`. The
technical companion identifies the exact run directories and commands.

## 7. Results

### 7.1 The T0 baseline

The canonical `T0` run began with zero truth-relative error, moved away from
truth immediately, and reached a continuing non-zero regime after a short
warm-up.

Under the mechanical chart-summary rule:

| Run | TRMSE: level, event, width | PRMSE: level, event, width | Cancellation endpoint |
|---|---|---|---|
| T0, 800 by 500 | 19.416, 23, 15.067 | 0.03455, 22, 0.02702 | 1.137 at 800 |
| T0, 3,200 by 2,000 | 19.379, 23, 15.222 | 0.03445, 21, 0.02722 | 0.783 at 3,200 |

The larger run strongly corroborates the TRMSE and PRMSE levels, widths, and
warm-up times. Extending the horizon from 500 to 2,000 events revealed no
further change in the truth-relative regime. The cancellation endpoint fell
below one rating point with 3,200-replicate support, although its cumulative
path rose and fell along the way.

### 7.2 Paired forgetting landmarks

The median absolute probability-tolerance landmarks were:

| Initialization | <=0.05 | <=0.02 | <=0.01 | <=0.005 |
|---|---:|---:|---:|---:|
| TC | 23 | 41 | 55 | 70 |
| TI | 34 | 52 | 66 | 80 |
| Random maps, range | 34--40 | 49--55 | 61--67 | 73--81 |

Every tolerance was reached by all 800 replicates of every model. For the
strictest `0.005` tolerance, the latest first qualifying events were:

| Initialization | Latest first qualifying event |
|---|---:|
| TC | 74 |
| TI | 87 |
| Random maps | 76--87 |

The latest case therefore began its qualifying window at event 87 and was
confirmed after the 25-event requirement at event 111. No later recross was
observed through event 500.

In exposure terms, event 87 represents 783 bouts per rikishi in this complete
round-robin world. That does not translate directly into historical sumo time,
but it illustrates why initialization lag may be practically important even
when forgetting occurs reliably in a controlled model.

### 7.3 Continued decay after the declared tolerance

The `0.005` threshold is a practical landmark, not exact equality. Paired
disagreement continued to decay. Taking the worst model-level ensemble mean
across all tested alternatives gives:

| Event | Rating-state disagreement | Probability disagreement |
|---:|---:|---:|
| 87 | 2.56 | 0.00371 |
| 100 | 1.40 | 0.00200 |
| 125 | 0.447 | 0.000628 |
| 150 | 0.142 | 0.000201 |
| 200 | 0.0145 | 0.0000205 |
| 500 | `1.7e-8` | `2.4e-11` |

There is no unique event of exact coalescence. The strict threshold supplies
an operational forgetting time; event 500 merely demonstrates that the
remaining difference later became numerically negligible.

### 7.4 Standalone settled behaviour

For all canonical 800 by 500 runs, the terminal descriptive quantities were
the same to numerical precision:

```text
TRMSE level       approximately 19.416
TRMSE 5--95 width approximately 15.067
PRMSE level       approximately 0.03455
PRMSE 5--95 width approximately 0.02702
Cancel endpoint   approximately 1.137 at 800 replicates
```

Only the truth-relative settling events differed materially. `T0` settled at
events 23 and 22 for TRMSE and PRMSE respectively. The alternatives settled
later under the rule requiring both the mean and percentile width to be within
5% of their terminal values.

The table's later PRMSE settling events for some models should be read exactly
as defined. They are not paired forgetting times and can be driven by the time
taken for the replicate percentile width to resemble its terminal width, even
after the ensemble mean visually appears near its eventual level.

The complete rounded presentation table is:

| Model | Replicates | Events | TRMSE level | TRMSE event | TRMSE width | PRMSE level | PRMSE event | PRMSE width | Cancel level | Cancel N |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| T0 | 800 | 500 | 19.416 | 23 | 15.067 | 0.03455 | 22 | 0.02702 | 1.137 | 800 |
| T0 | 3,200 | 2,000 | 19.379 | 23 | 15.222 | 0.03445 | 21 | 0.02722 | 0.783 | 3,200 |
| TC | 800 | 500 | 19.416 | 52 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TI | 800 | 500 | 19.416 | 67 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TR01 | 800 | 500 | 19.416 | 110 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TR02 | 800 | 500 | 19.416 | 110 | 15.067 | 0.03455 | 127 | 0.02702 | 1.137 | 800 |
| TR03 | 800 | 500 | 19.416 | 111 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TR04 | 800 | 500 | 19.416 | 110 | 15.067 | 0.03455 | 69 | 0.02702 | 1.137 | 800 |
| TR05 | 800 | 500 | 19.416 | 110 | 15.067 | 0.03455 | 127 | 0.02702 | 1.137 | 800 |
| TR06 | 800 | 500 | 19.416 | 118 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TR07 | 800 | 500 | 19.416 | 118 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TR08 | 800 | 500 | 19.416 | 110 | 15.067 | 0.03455 | 127 | 0.02702 | 1.137 | 800 |
| TR09 | 800 | 500 | 19.416 | 118 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |
| TR10 | 800 | 500 | 19.416 | 110 | 15.067 | 0.03455 | 119 | 0.02702 | 1.137 | 800 |

The repeated terminal numbers are not rounding away substantive model
differences. In the underlying CSV, the canonical model levels agree to about
eight or more decimal places. This is expected once the paired processes have
coalesced on the common histories.

### 7.5 What the random maps added

The random models began with state RMSEs from about 187 to 279 and probability
RMSEs from about 0.274 to 0.461. Their median strict forgetting times ranged
from 73 to 81 events. Initial error magnitude was associated with forgetting
time in this small sample, especially for stricter thresholds, but ten maps do
not justify a predictive relationship or general law.

The important contribution of the random experiment was broader coverage. The
same qualitative result was not confined to the special constant and inverted
maps. A survey of thousands of additional maps could characterize a declared
random-map distribution more precisely, but it would not prove forgetting for
every possible initialization and is not needed for the completed conclusion.

## 8. How the observations support the conclusion

The inferential chain is straightforward:

1. The paired processes differ only in their initial ratings. They receive the
   same evidence thereafter.
2. Their initial rating and forecast disagreements are substantial and vary by
   initialization.
3. Those paired disagreements decay across every tested model and every
   replicate.
4. Every replicate enters the strictest declared practical tolerance, with no
   observed recross through the remaining horizon.
5. Paired differences subsequently shrink to numerical insignificance.
6. The standalone truth-relative error does not disappear. Instead, all models
   exhibit the same continuing fixed-`K` fluctuation after paired differences
   have disappeared.

The only experimental variable capable of explaining the paired initial
difference is initialization. When that paired difference disappears while
the common process continues to fluctuate, the detectable effect of
initialization has been forgotten.

The equality of terminal standalone summaries is corroborating evidence, not
the definition of forgetting. Two unpaired models could have similar aggregate
distributions without agreeing history by history. The direct evidence is the
decay of paired state and forecast distances.

## 9. Interpretive points that matter later

Several points caused understandable confusion during development and are
worth preserving explicitly.

### 9.1 T0 is a reference process, not a motionless truth line

`T0` starts at latent skill, but random outcomes move it immediately. The
paired alternative is not expected to converge to the fixed latent vector; it
is expected to coalesce with the moving `T0` state generated by the same
history. The approximately 19-point TRMSE is the scale of ordinary realized
fixed-`K` wandering, not residual initialization memory.

### 9.2 Event 500 is not the forgetting time

Event 500 is the endpoint at which paired differences were found to be near
machine precision. Under the strictest declared practical rule, all qualifying
windows began by event 87 and were confirmed by event 111. Statements that the
models were “forgotten by event 500” are true but needlessly weak.

### 9.3 A truth-relative settling event is not a paired forgetting event

The results-table event tells us when a standalone model's mean and percentile
width resemble their terminal truth-relative regime. A paired landmark tells
us when changing the initialization no longer changes forecasts beyond a
declared tolerance. Both are observable and useful, but they answer different
questions. This is why a random model can have a strict paired forgetting
median near event 80 while its mechanical standalone PRMSE settling event is
119 or 127.

### 9.4 Cancellation does not need a plateau

The signed-error curve was initially discussed as if it might have a settled
non-zero level. The larger run made clear that a cumulative cancellation curve
can rise and fall. The pragmatic question is simply how small the endpoint is
at declared support. The experiment observed 1.137 points at 800 replicates and
0.783 at 3,200. It neither needs nor supplies a proof that the value converges
strictly to zero.

### 9.5 More random maps would change coverage, not logical status

Ten maps are enough to show that the result is not peculiar to the flat and
inverted constructions. One thousand maps would describe the selected random
map distribution more densely. No finite number would turn the experiment
into a proof for all possible initialization vectors.

## 10. Strongest defensible statements

The experiments support the following statements:

1. In every replicate examined, for every initialization examined, the effect
   of initialization became practically negligible under the declared paired
   probability rule.
2. Among the maps tested, initialization changed the size and duration of the
   transient but had no detectable effect on the later observed fixed-`K`
   regime.
3. `T0` reached settled truth-relative behaviour sooner than every tested
   alternative, consistent with the motivating intuition.
4. `TI` had a later median entry event than `TC` for every declared absolute
   paired forecast tolerance.
5. By event 500, initialization no longer had a detectable effect on the
   signed-error cancellation diagnostic among the tested 800-replicate models,
   because their final rating vectors had coalesced with `T0` replicate by
   replicate.
6. A larger `T0` ensemble produced a cancellation endpoint below one rating
   point and independently corroborated the scale and shape of the settled
   truth-relative regime.

The experiments do not establish:

- forgetting for every mathematically possible initialization;
- exact or asymptotic convergence;
- impossibility of recurrence after event 500;
- convergence of signed-error cancellation to zero;
- universal optimality of `T0`;
- predictive usefulness of Elo;
- applicability to changing populations, changing skills, or historical sumo.

## 11. Where this leaves the wider problem

The controlled experiment has supplied a workable meaning of forgetting and
shown it in the most favourable world: initialization memory can disappear
while fixed-`K` ratings continue to wander relative to truth. That resolves the
conceptual problem that `toy_elo` did not settle.

The next substantive question is not whether to generate ever more fixed-world
initial maps. It is whether the paired-counterfactual idea can be adapted to a
world with changing skills, entry, retirement, unequal exposure, and an
imperfect chii-like signal. In such a world there may be no permanent
counterfactual partner and no known latent rating vector. That requires a new
proposal rather than an extension silently folded into this one.
