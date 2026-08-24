# Proposal 1: Forgetting in a Fixed-Skill Toy World

## Status

The fixed-skill toy-world investigation is complete as a canonical exploratory
study. The canonical contract uses 10 fixed rikishi, 40-point latent spacing,
`Q=400`, `K=5`, 800 replicates, 500 events, master seed 1, and a 25-event
persistence requirement. It has been applied to `T0` (latent-skill start), `TC`
(constant-midpoint start), `TI` (inverted start), and ten reproducible centred
random maps (`TR01`--`TR10`). Each alternative has a standalone truth-relative
report and a separate paired comparison with `T0`. Raw replicate-event metrics
and replicate-level landmarks remain available for audit.

The observed result is the qualitative result anticipated by the proposal:

- paired state and forecast disagreement declined towards zero;
- all 800 replicates of every tested alternative entered the strictest declared
  probability tolerance (`0.005`) by event 87 at the latest and sustained it
  for the required 25-event window, which was confirmed by event 111;
- no later recrossing was observed through event 500;
- after paired disagreement became negligible, all models exhibited the same
  continuing non-zero fixed-`K` truth-relative regime to practical precision;
- `T0` reached settled truth-relative behaviour sooner than every alternative
  tested, consistent with the motivating intuition;
- `TI` had a later median entry event than `TC` for every declared absolute
  forecast tolerance.

An additional 3,200-replicate, 2,000-event `T0` run corroborates the settled
TRMSE and PRMSE levels and widths. It is retained as a larger-support baseline,
not as a separate forgetting experiment. Its final-rating signed-error
cancellation RMSE is below one rating point.

The implementation also produces a two-dimensional results table with one row
per model-run. TRMSE and PRMSE are each represented by settled level, settling
event, and settled 5th--95th percentile width. Cancellation is represented by
the endpoint pair `(RMSE of ensemble-mean signed errors, replicates included)`;
it is a Monte Carlo support diagnostic, not a forgetting measure or a quantity
assumed to settle at a non-zero level.

This proposal records the vocabulary, synthetic world, coupled experimental
design, measurements, completed findings, and claim boundary. It does not
prescribe a historical-sumo experiment.

## Purpose

Determine whether and how quickly a fixed-`K` Elo process loses the effect of
its initial rating map in a world where latent skills are fixed and known.

The experiment asks:

> When several Elo processes observe exactly the same bouts and outcomes but
> start from different rating maps, how quickly do their rating states and
> forecasts become practically indistinguishable?

The first experiment must demonstrate forgetting under favourable controlled
conditions before the same idea is applied to changing populations or hidden
real-world skill.

## Meaning of forgetting

Forgetting is loss of sensitivity to initial ratings.

It does not mean:

- that an individual fixed-`K` rating stops moving;
- that ratings remain at the true latent skills;
- that the rating vector is eventually confined to a finite band;
- that Elo predictions are useful;
- that a finite simulation proves a general convergence theorem.

Two Elo processes have forgotten the difference between their initializations
when the remaining disagreement in their states and forecasts is practically
negligible under a declared rule.

One trajectory cannot demonstrate forgetting. In particular, movement away
from an initial rating vector is not evidence that the vector has been
forgotten. It may show only that random results and fixed-`K` updates continue
to move ratings. Forgetting asks the counterfactual question:

> Would the current rating state or forecasts have been materially different
> if the same process had started from another rating map but observed exactly
> the same evidence?

Answering that question requires at least two naturally coupled processes.

Predictive usefulness is deliberately separate. This proposal does not compare
Elo with a 50--50 predictor and does not require Elo to be useful in order for
forgetting to be measurable.

## Why latent skill remains necessary

Coupled-process disagreement can be measured without knowing true skill.
Nevertheless, known latent skill is essential to validation because it lets the
experiment distinguish:

1. continuing error caused by random results and fixed-`K` updates;
2. additional error caused by initialization;
3. failure of Elo to represent the known skill gaps;
4. loss of initialization memory despite continuing rating fluctuation.

The expected qualitative result is:

```text
disagreement between differently initialized coupled runs
    approaches zero

while

error between an Elo run and latent skill
    continues to fluctuate in a non-zero regime
```

The experiment fails its conceptual validation if these two behaviours cannot
be distinguished.

## Synthetic world

### Population and latent skills

The first declared world contains ten permanent players:

```text
P0, P1, ..., P9
```

Their fixed latent skills are evenly spaced by 40 Elo points and centred at
zero:

```text
180, 140, 100, 60, 20, -20, -60, -100, -140, -180
```

The zero centre is only a normalization. Elo probabilities depend on rating
differences.

### Outcome model

For players `i` and `j`, the true probability that `i` wins is:

\[
P(i\text{ beats }j)
=
\frac{1}{1+10^{(S_j-S_i)/q}},
\qquad q=400.
\]

Each bout outcome is sampled once from this probability and then supplied to
every coupled Elo process. Initialization must never influence the generated
world, its schedule, or its outcomes.

### Schedule and clocks

One event is a complete round robin containing all 45 unordered pairs in a
new seeded random order. This retains the most interpretable connection with
the original `toy_elo` experiment while ensuring equal long-run exposure.

Outputs must record both:

- complete round-robin events;
- global bouts.

Player exposure is `9 * event` at completed-event snapshots. Later proposals
may replace the complete round robin with uniformly sampled pairs, but the
first experiment must not mix the two schedules.

### Elo update

Every process uses ordinary zero-sum Elo with:

```text
q = 400
K = 5
```

For current displayed ratings `R_i` and `R_j`:

\[
E_i
=
\frac{1}{1+10^{(R_j-R_i)/q}},
\]

and, for score \(Y_i\in\{0,1\}\):

\[
R_i' = R_i + K(Y_i-E_i),
\]

\[
R_j' = R_j - K(Y_i-E_i).
\]

The update rule, parameters, schedule, and realized outcomes are identical in
all coupled processes.

## Initial rating maps

The primary comparison uses two maps with the same mean:

### True start

```text
R_i(0) = S_i
```

This starts with zero skill-gap error. It is not stationary: random outcomes
and fixed-`K` updates immediately move the displayed ratings.

### Flat start

```text
R_i(0) = 0
```

This supplies no initial ordering information.

### Inverted start

```text
R_i(0) = -S_i
```

This supplies a completely wrong ordering at the correct overall scale and is
reserved as a post-freeze positive control for slow forgetting. It is not part
of the first true-versus-flat development comparison.

The first implementation may additionally support seeded noisy, compressed,
and exaggerated maps, but those maps must not delay or alter the primary
two-map experiment. They belong to later controls or follow-on surveys.

All maps must have the same mean. The implementation must nevertheless centre
rating vectors before calculating state distances so that the metric remains
explicitly translation invariant.

## Natural coupling

For each replicate, every initialization receives the same ordered pair and
the same outcome at every bout. Replicates use independently derived,
recorded seeds.

For two coupled processes `A` and `B`, the score term cancels directly when
their updates are subtracted. Their difference evolves through the difference
between their expected scores, rather than through different realized
evidence. This coupling isolates the memory of initialization and reduces
avoidable Monte Carlo noise.

The experiment must never compare separately generated histories as though
their difference were caused only by initialization.

## Primary measurements

Measurements are taken at event zero and after every complete round robin.

### Centred state distance

For processes `A` and `B`, define:

\[
C_t(A,B)
=
\sqrt{
\frac{1}{n}
\sum_i
\left[
(R_{i,t}^A-\bar R_t^A)
-(R_{i,t}^B-\bar R_t^B)
\right]^2
}.
\]

This directly measures the remaining difference between their rating states.

### All-pair forecast distance

For every unordered pair, calculate the probability implied by the current
ratings. Define:

\[
F_t(A,B)
=
\sqrt{
\operatorname{mean}_{i<j}
\left(p_{ij,t}^A-p_{ij,t}^B\right)^2
}.
\]

This is the primary forgetting measure because it expresses remaining
initialization memory in the quantities Elo uses to forecast bouts. It does
not score those forecasts against outcomes.

All-pair measurement is used at event snapshots so that the diagnostic is not
made noisy by which pair happened to fight next.

### Truth-relative error

For each process, record centred rating-gap error against latent skill and
all-pair probability error against the true outcome probabilities.

These truth-relative metrics diagnose what happens after initialization has
been forgotten. They are not part of the primary coupled-distance definition.

### Ensemble summaries

At every event, report at least:

- mean;
- median;
- standard deviation;
- 5th, 25th, 75th, and 95th percentiles;
- minimum and maximum;
- replicate count.

The paired replicate-level observations must remain available for audit.

## Descriptive model-results table

For compact presentation, define:

\[
\operatorname{results}(T)
=
\bigl(\mathrm{TRMSE}(T),\mathrm{PRMSE}(T),\mathrm{Cancel}(T)\bigr).
\]

The truth-relative components are triples:

\[
\mathrm{TRMSE}(T)=(L_T,\tau_T,W_T),
\qquad
\mathrm{PRMSE}(T)=(L_P,\tau_P,W_P),
\]

where `L` is the median of the ensemble-mean curve over the final 100 events,
`W` is the median 5th--95th percentile width over those events, and `tau` is
the first event beginning 25 consecutive observations during which both the
mean and width remain within 5% of their terminal values. A missing qualifying
window is reported as right-censored rather than assigned an event.

Cancellation is an endpoint pair:

\[
\mathrm{Cancel}(T;N)=(C_N,N),
\]

where `C_N` is the RMSE between the ensemble-mean final rating vector and
latent skill after `N` replicates. The cancellation curve may rise and fall as
replicates are added. The table does not assign it a non-zero settled level or
a settling coordinate; it reports the observed endpoint and its support.

The rectangular CSV has one row per model-run and records replicate and event
counts explicitly so runs such as 800 by 500 and 3,200 by 2,000 can be shown
together. These quantities describe standalone truth-relative charts. They do
not replace the paired state and forecast distances that define forgetting.

## Forgetting summaries

No single threshold is an intrinsic Elo boundary. The experiment therefore
reports both complete curves and several declared summaries.

### Fractional decay

For each comparison, report the first persistent time at which forecast
distance has fallen by:

```text
50%
90%
99%
```

relative to its event-zero value.

The true-versus-flat and true-versus-inverted comparisons have different
initial distances. Fractional results describe the rate at which each process
loses its own starting disagreement; absolute curves must accompany them.

### Absolute forecast tolerance

As an interpretable first diagnostic, report persistent entry below all-pair
forecast RMSE tolerances of:

```text
0.05
0.02
0.01
0.005
```

These correspond to five, two, one, and one-half percentage points of RMS
forecast disagreement. None is to be presented as the uniquely correct
definition.

### Persistence and recrossing

The observed forgetting time for a tolerance is the first event at which the
declared ensemble statistic remains below that tolerance for 25 consecutive
events.

The report must also record:

- whether the distance later recrosses the threshold;
- the fraction of later observed events below the threshold;
- the remaining observation horizon after first entry.

A finite persistence window establishes an empirical landmark, not a claim
that the threshold will hold forever.

### Integrated disagreement

Calculate the area under each forecast-distance curve through every declared
horizon. This measures the cumulative burden of initialization and reduces
dependence on one threshold crossing.

## Hypotheses

The primary hypotheses are:

1. Coupled state and forecast distances between the true and flat starts
   decline towards zero.
2. Truth-relative error does not decline permanently to zero, even for the
   true-start process.
3. Once coupled forecast disagreement is negligible, differently initialized
   processes exhibit the same continuing fixed-`K` fluctuation to practical
   precision.
4. Estimated forgetting landmarks are stable across the independent histories
   within a sufficiently large canonical ensemble and a sufficiently long
   observation horizon.

An additional control expectation is that the inverted start begins farther
from the true-start process and requires longer to enter declared absolute
forecast tolerances than the flat start.

The experiment must report contrary or ambiguous evidence without redefining
the primary paired measurements to manufacture the anticipated result.

## Experimental sequence

The work is divided into exploratory development and a reproducible canonical
experiment. The forgetting definition may be revised while inspecting small
development runs. The canonical configuration and every later change must be
recorded, but a predictive-model-style principal/holdout hierarchy is not
required for this completely specified synthetic data-generating process.

### Stage 0: deterministic verification

Use hand-checkable two- and three-player histories to verify:

- Elo updates;
- preservation of rating mean;
- translation invariance;
- common outcomes across initializations;
- centred state distance;
- all-pair forecast distance;
- exact event-zero values;
- deterministic seeded replay.

### Stage 1: illustrative true-start run

Generate and persist one seeded synthetic history. Run the true-start process
alone and inspect:

- its departure from zero truth-relative error;
- its continuing fixed-`K` fluctuation;
- its rating and forecast trajectories;
- the event and bout clocks;
- the audit artifacts needed to replay the history exactly.

This stage establishes the natural-noise baseline. It does not yet measure
forgetting because there is no differently initialized process to compare.

The Stage 1 interpretation must be limited to:

- departure from a perfectly informed initial state;
- continuing truth-relative rating and forecast error;
- fluctuation rather than permanent settlement;
- preservation or inversion of latent-skill ordering in the displayed ratings;
- the empirical scale of natural fixed-`K` variation in this one history.

It must not describe distance from the initial latent-skill vector as a
forgetting metric. Distance from the initial vector measures departure from
truth in this world; it does not identify whether the current state still
depends on that initialization.

Stage 1 must have a standalone baseline report or a clearly self-contained
first report section. That presentation shows only the true-start trajectory,
latent skills, truth-relative rating error, and truth-relative forecast error.
No flat-start comparison or forgetting landmark belongs in the Stage 1 view.

After the illustrative run is understood, Stage 1 may be repeated as an
ensemble of independent true-start histories. For this aggregate baseline, the
implementation must calculate truth-relative errors separately within each run
before summarising them by event. It must report distributions of per-run error
rather than calculate one error from ensemble-mean ratings. At minimum, report
the mean, median, standard deviation, and 5th, 25th, 75th, and 95th percentiles,
along with the fraction of runs containing ordering inversions. The run must
record and print its total wall-clock duration.

### Stage 2: flat replay of the identical history

Run the flat-start process through the exact schedule and realized outcomes
persisted by Stage 1. Do not regenerate an equivalent history from the same
parameters when the recorded history itself can be replayed.

The model-family notation is `T0` for true latent-strength initialization, `TC`
for constant-midpoint initialization, and `TI` for inverted latent-strength
initialization.

First report the flat-start process, `TC`, on its own relative to latent skill.
This Output 1 must show how its truth-relative state and probability errors
develop from constant initialization. It is a description of `TC`, not a
forgetting measurement.

Compare the two processes using:

- truth-relative error for each process;
- centred state distance;
- all-pair forecast distance;
- fractional decay;
- provisional absolute tolerances;
- provisional persistence and recrossing diagnostics.

Stage 2 must also have a separate paired report, Output 2. It may place the
true-start and flat-start paths in the same view, but
must identify coupled state and forecast disagreement as the first actual
forgetting measurements. It must not retrospectively relabel Stage 1's
truth-relative error as forgetting.

### Stage 3: exploratory metric development

Use the illustrative history and additional small development runs to decide
whether the measurements give a coherent account of forgetting. In particular,
ask:

- whether coupled disagreement begins positive and generally decays;
- whether state and forecast distances tell compatible stories;
- whether continuing fixed-`K` noise is visibly distinct from initialization
  memory;
- whether threshold crossings are unstable or frequently reversed;
- whether fractional decay and integrated disagreement remain interpretable;
- how long a canonical horizon must be to observe strict tolerances and later
  recrossing.

Metrics, outputs, tolerances, and presentation may be corrected during this
stage. Every development run must remain reproducible and must be labelled as
exploratory rather than canonical.

### Stage 4: declare the canonical contract

Record the configuration used for the canonical experiment:

- the primary and secondary metrics;
- event and bout clocks;
- world and Elo parameters;
- simulation horizon and replicate count;
- deterministic seed derivation;
- fractional and absolute forgetting summaries;
- persistence and recrossing rules;
- aggregation and uncertainty summaries;
- required artifacts and interpretation language.

Later descriptive additions must be documented and must not silently replace
the primary paired forgetting definition. In particular, the later
`results(T)` table summarizes truth-relative charts; its settling events are
not substitutes for paired forgetting landmarks.

### Stage 5: canonical replicated pairwise experiment

Run many independent synthetic histories. Within every replicate, run `T0` and
the alternative start through identical ordered bouts and outcomes. Histories
are independent between replicates.

Report both:

1. ensemble disagreement curves and their uncertainty;
2. the distribution of replicate-level forgetting landmarks.

At minimum, aggregate:

- mean, median, and quantile bands by event;
- fractional and absolute forgetting times;
- integrated disagreement where used;
- recrossing frequency;
- the fraction right-censored at the canonical horizon;
- Monte Carlo support as the included replicate count increases.

The result must not be reduced to an average rating trajectory or a single
ensemble threshold crossing. The implemented 800-replicate, 500-event runs for
`TC`, `TI`, and `TR01`--`TR10` satisfy this stage.

### Stage 6: robustness checks and extensions

Robustness checks are useful but are not a predictive holdout requirement. The
completed checks include:

- deterministic translation invariance;
- an inverted initialization as a deliberately adverse control;
- ten reproducible random initial maps spanning a range of initial errors and
  orderings;
- a longer, larger-support `T0` run confirming the settled truth-relative
  regime.

A further paired ensemble generated from another master history seed remains
available as an optional check against an unusual canonical seed bank or an
implementation error. It is not required to establish the present conditional
claim. A nearly-correct initialization was considered but is no longer
required: the broader random-map experiment already demonstrates that the
measurement responds coherently to varied initial conditions.

### Stage 7: assess the established claim

The canonical experiment supports a defensible statement about initialization
forgetting in the declared toy world. Every tested alternative entered the
strictest persistent forecast-disagreement tolerance, while truth-relative
fixed-`K` error continued in a non-zero regime. `T0` settled sooner than every
tested alternative, and `TI` had later median entry events than `TC` for the
declared absolute tolerances.

These are conditional empirical findings, not a theorem that `T0` minimizes
settling time among every possible map and not a universal forgetting time.

### Stage 8: choose the next experiment

The fixed-world question is sufficiently answered for present purposes.
Thousands of additional random initializations could increase coverage of a
declared map distribution but would not prove universal optimality and are not
required for completion. Candidate later experiments include:

- controlled variation in initial error magnitude and direction;
- random-pair rather than round-robin scheduling;
- changing latent skill;
- entry, retirement, and right-censored careers;
- an imperfect chii-like signal;
- historical replay.

Random-pair schedules, changing skill, entry, and retirement require later
proposals because they change the experimental world rather than merely a
parameter.

## Development and canonical run identification

Development and canonical artifacts must be written to distinguishable run
directories and identified in their manifests. The intended roles are:

```text
verification
development
canonical
robustness
```

`Canonical` means the standard reproducible reference configuration. It does
not imply a predictive principal/holdout experiment. Historical manifests may
use `development` for the standalone canonical-size `T0` run; the run identity
block and explicit replicate/event columns in the results table remove any
practical ambiguity.

## Required outputs

The proposed implementation location is:

```text
src/analysis/forgetting/toy/
```

Its default output root must therefore be:

```text
files/output/analysis/forgetting/toy/
```

Each run should create an auditable child directory containing at least:

```text
manifest.json
event_summary.csv
replicate_distances.csv
truth_error.csv
forgetting_summary.csv
true_start_report.md
true_start_report.html
paired_report.md
paired_report.html
```

During development, a combined `report.md` or `report.html` may additionally be
written for convenience. It does not replace the required conceptual separation
between the Stage 1 baseline and Stage 2 coupled comparison.

The manifest must record:

- all world and Elo parameters;
- every initial map;
- seed derivation;
- schedule and clock definitions;
- event and bout horizons;
- replicate count;
- metric definitions;
- thresholds and persistence rules;
- run role and experimental-contract version;
- start and completion timestamps;
- implementation version when available.

The Stage 1 report should show:

- latent skills and the true-start rating trajectories;
- truth-relative state and forecast error;
- selected rating snapshots and any local ordering inversions;
- continuing fluctuation without language implying forgetting.

The Stage 2 paired report should show:

- state- and forecast-distance decay for the primary true/flat pair;
- absolute and normalized forecast-distance curves;
- truth-relative error for both initializations as contextual diagnostics;
- forgetting landmarks, recrossing, and persistence diagnostics;
- integrated disagreement through declared horizons.

Control and extension reports should add true/inverted and random-map
comparisons where applicable.

## Required verification

Automated tests must establish that:

- latent skill affects outcome generation but is invisible to Elo updating;
- each sampled outcome is reused by every coupled initialization;
- schedules are identical within a coupled replicate;
- independent replicates use deterministic, distinct random streams;
- adding a constant to an initial map does not change forecasts or centred
  distances;
- all rating sums remain constant under the zero-sum updater;
- true initialization has zero truth-relative error at event zero;
- flat and inverted event-zero distances match direct calculations when those
  maps are exercised;
- metrics use predeclared event snapshots consistently;
- persistence and recrossing calculations handle right-censored runs;
- output rows can be traced to the manifest configuration.

## Interpretation contract

If supported, the experiment may say:

> In the declared fixed-skill toy world, Elo processes exposed to identical
> evidence progressively lost the detectable effect of every alternative
> initialization tested relative to a true-skill start. Individual fixed-`K`
> ratings continued to fluctuate after this initialization disagreement became
> negligible.

The completed control experiment may additionally say that the inverted start
had a later median entry event than the flat start for every declared absolute
forecast-disagreement tolerance.

It may also say that `T0` reached settled truth-relative behaviour sooner than
every tested alternative, consistent with the motivating intuition. It must not
turn that observation into a claim that `T0` minimizes settling time over every
possible initialization map.

It must not say:

- that ratings converge permanently to true skill;
- that the observed forgetting time is universal;
- that a finite run proves pathwise convergence;
- that forecast agreement demonstrates predictive usefulness;
- that the result automatically applies to changing skills, entrants,
  retirements, chii-shaped schedules, or historical sumo.

## Completion criterion

This proposal is complete when reproducible canonical runs can report:

1. the full decay of state and forecast disagreement for paired true and flat
   starts;
2. declared fractional and absolute forgetting landmarks with persistence and
   recrossing evidence;
3. continuing truth-relative fluctuation after coupled disagreement becomes
   negligible;
4. uncertainty across replicated coupled histories;
5. coherent controls spanning constant, inverted, and reproducible random
   initializations;
6. a rectangular results table that applies the declared chart-summary rules
   consistently while retaining paired forgetting as the primary definition;
7. a documented basis for either selecting the next forgetting experiment or
   stopping the fixed-world investigation.

These criteria have been met. Optional fresh-seed robustness checks or larger
random-map surveys may be performed later without reopening the completed
fixed-world conclusion.
