# Baseline Elo Toy Model

This note defines the normalized toy model for studying what it means for Elo
ratings to approach, stabilize around, or fail to stabilize around a fixed
underlying skill scale.

The model separates three ideas that are often tangled together:

- The hidden world: fixed player skills and fixed win probabilities.
- The rating scale: how skill differences are converted into probabilities.
- The learning rule: how strongly Elo reacts to each observed result.

## Parameters

The baseline model starts from four conceptual parameters.

```text
n      number of players
m      total hidden rating span
q      certainty scale for translating rating gaps into probabilities
f      update size as a fraction of one adjacent skill gap
```

The players are indexed from strongest to weakest:

```text
0, 1, ..., n - 1
```

The nominal rating range is:

```text
0 to m
```

The midpoint of the range is:

```text
b = m / 2
```

The adjacent hidden skill gap is:

```text
gap = m / (n - 1)
```

The hidden skills are evenly spaced and centered on `b`:

```text
S_i = b + gap * ((n - 1) / 2 - i)
```

So:

```text
S_0       = m
S_(n - 1) = 0
S_i - S_(i + 1) = gap
```

The center `b` is not mathematically important to Elo probabilities. It is a
normalization choice that makes the scale readable.

## Certainty Scale

Elo converts rating differences into probabilities with:

```text
P(i beats j) = 1 / (1 + 10^((S_j - S_i) / q))
```

The parameter `q` is the certainty scale. It says how large a rating gap must
be before a result becomes highly predictable.

For a rating gap of `q`:

```text
P(stronger wins) = 1 / (1 + 10^-1)
                 = 10 / 11
                 ~= 90.9%
```

For a rating gap of `2q`:

```text
P(stronger wins) ~= 99%
```

For a rating gap of `3q`:

```text
P(stronger wins) ~= 99.9%
```

Abstractly, `q` can be chosen directly. It remains meaningful even if the
hidden skills are not uniformly spaced.

In the special case where hidden skills are uniformly spaced, we may instead
describe the same choice using `p_adj`, the probability that a player beats the
next weaker adjacent player:

```text
p_adj = 1 / (1 + 10^(-gap / q))
```

Solving for `q`:

```text
q = gap / log10(p_adj / (1 - p_adj))
```

So for uniformly spaced hidden skills, choosing `q` and choosing `p_adj` are
equivalent once `gap` is known. For non-uniform hidden skills, `q` is the more
general parameter, while `p_adj` becomes a derived diagnostic for whichever
adjacent gap is being discussed.

## Learning Scale

Elo ratings are initialized at the scale midpoint:

```text
R_i(0) = b
```

The initial value could be anything, including random values, because Elo
probabilities depend only on rating differences. Starting everyone at `b` is
the cleanest test because it gives Elo no initial ordering information.

The update size is chosen as a fraction of one adjacent hidden skill gap:

```text
k = f * gap
```

This makes `f` the learning-rate parameter.

Large `f` means a single result can move a player by a large fraction of the
spacing we are trying to recover. That learns quickly, but leaves more
stationary wobble.

Small `f` means each result has less leverage. That learns more slowly, but
settles closer to the hidden skill scale in ensemble mean.

## Match Generation

The hidden skills generate the true win probability for every matchup:

```text
P(i beats j) = 1 / (1 + 10^((S_j - S_i) / q))
```

For each simulated bout, draw a random outcome from that probability.

The Elo system does not see `S_i`. It sees only the result and its current
ratings `R_i`.

## Elo Update

For a bout between players `i` and `j`, Elo computes:

```text
E_i = 1 / (1 + 10^((R_j - R_i) / q))
```

Then:

```text
R_i <- R_i + k * (score_i - E_i)
R_j <- R_j - k * (score_i - E_i)
```

where:

```text
score_i = 1 if i wins
score_i = 0 if i loses
```

The same `q` is used in the hidden world and in the Elo updater. This makes the
model correctly specified: if the rating gaps equal the hidden skill gaps, the
expected update is zero.

## Event And History Process

An event is one complete round robin: every unordered pair of players fights
once.

A history is a consecutive sequence of events. The experiment can also repeat
the whole history many independent times, using different random seeds, to
estimate ensemble behavior.

With fixed `k`, a single run should not be expected to converge to fixed
numbers. Even when the ratings are correct, future random outcomes continue to
move them. The stable object is the ensemble behavior or a long-run stationary
distribution, not one path that freezes.

## Measuring Stability

The rating center is irrelevant, so stability should be measured using rating
gaps.

For each pair of players:

```text
rating_gap_ij = R_i - R_j
skill_gap_ij  = S_i - S_j
```

A useful all-pair error metric is:

```text
gap_rmse = sqrt(mean_over_pairs((rating_gap_ij - skill_gap_ij)^2))
```

For an ensemble of many independent simulations, compute `gap_rmse` from the
ensemble mean ratings.

The current toy script calls a state stable when:

```text
mean gap RMSE <= epsilon
and the rolling RMSE slope is close to zero
for a fixed number of consecutive events
```

Persistence is then the fraction of later events that continue to satisfy the
stable condition after it is first reached.

## Scale Invariance

The model is invariant under rescaling if all rating-like quantities are scaled
together.

If:

```text
R'_i = a * R_i
S'_i = a * S_i
q'   = a * q
k'   = a * k
```

then all win probabilities and update behavior are equivalent in normalized
units.

This means the absolute choice of `m` is a convention. The meaningful quantities
are ratios such as:

```text
gap / q
k / gap = f
k / q
```

The most general baseline parameters are therefore:

```text
n
m
q
f
```

with:

```text
b   = m / 2
gap = m / (n - 1)
k   = f * gap
```

For the uniformly spaced case, the adjacent-player win probability is:

```text
p_adj = 1 / (1 + 10^(-gap / q))
```

Equivalently, if we prefer to choose `p_adj` directly for that uniform case:

```text
q = gap / log10(p_adj / (1 - p_adj))
```

## Current Working Intuition

For a future 60-player pool with a nominal rating span of 2500:

```text
n = 60
m = 2500
gap ~= 42.37
```

Using the traditional `q = 400` implies:

```text
p_adj ~= 56%
```

So adjacent players are only slightly distinguishable, while a gap of roughly
ten ranks is very decisive.

Earlier toy runs suggest that:

```text
f = 1 / 8
```

is a plausible compromise between speed and accuracy for this kind of setup.
A smaller value such as:

```text
f = 1 / 16
```

should reduce stationary error, but should also require more events to reach
the same level of stability.

## Implementation

The current executable toy lives at:

```text
src/analysis/toy_elo/toy_elo_simulation.py
```

It exposes the normalized baseline parameters `n`, `m`, `q`, and `f` through:

```text
--players
--max-rating
--q
--learning-fraction
```

The script derives `gap` and `k`, and prints the implied `p_adj` as an
interpretive diagnostic for the uniformly spaced hidden skills.

Each invocation writes to a timestamped run directory under:

```text
files/output/toy_elo_simulation/
```

The run directory contains:

```text
ensemble_mean.csv
sample_run.csv
convergence_metrics.csv
manifest.json
```

The manifest records the input parameters, derived model values, timing, a
stability summary, and the paths of the generated output files.

## Runtime Scaling

One complete round robin is called an event. A history is a consecutive
sequence of events.

```text
n  players
h  history length, in events
r  independent runs through that history
```

One event contains exactly:

```text
n(n - 1) / 2
```

matches, so the exact number of simulated matches in a run configuration is:

```text
r * h * n(n - 1) / 2
```

This is the dominating runtime term because each match produces one Elo update.
A first benchmark on this machine measured roughly:

```text
2.13 million matches / second
4.70e-7 seconds / match
```

The helper module:

```text
src/analysis/toy_elo/runtime_model.py
```

uses this calibration to estimate one missing value from `n`, `r`, `h`, and
desired runtime `t`.

## Convergence Sweep Experiment

The first convergence sweep app is:

```text
src/analysis/toy_elo/convergence_sweep.py
```

It was written to answer the question:

```text
for a fixed number of runs r, how many events h are needed before the
ensemble mean ratings look stable?
```

For each player count `n`, the app simulates histories of increasing event
length and writes two audit files:

```text
attempts.csv
summary.csv
```

The important distinction in those files is:

```text
tested_events
first_stable_event
implied_event_bucket
```

`tested_events` is the history length actually simulated. `first_stable_event`
is the first event inside that history where the stability rule was met.
`implied_event_bucket` is `first_stable_event` rounded up to the event grid.

That distinction matters because simulating a 900-event history can reveal
that stability first appeared at event 884. The useful result is not merely
"900 was tested"; it is "the first stable event was 884, or 900 on the
50-event grid".

The first longer run used:

```text
r = 100
event_start = 50
event_step = 50
event_stop = 1000
```

and wrote output under:

```text
files/output/toy_elo_convergence_sweep/20260705_234846_seed1/
```

The useful converged part of the run was:

```text
n    first_stable_event    implied_event_bucket
10   304                   350
20   131                   150
30   197                   200
40   244                   250
50   348                   350
60   446                   450
70   563                   600
80   715                   750
90   884                   900
```

`n = 100` did not converge before the artificial ceiling of 1000 events, and
larger values of `n` were therefore not meaningfully explored by that run.
The run was later killed around `n = 200`, where each tested step was taking
on the order of tens of minutes.

Ignoring the small-`n` anomaly at `n = 10`, the observed first-stable events
were well approximated by the quadratic:

```text
f(n) = 0.106468633733679 n^2 - 1.0373921331466 n + 120.586077749013
R^2  = 0.999850449332067
```

This fit is empirical rather than a theoretical claim, but it is good enough
to use as a search heuristic.

## Why A Predictive Sweep App Was Added

The bounded sweep exposed two problems.

First, `event_stop = 1000` was an implementation guardrail, not part of the
experimental question. The user did not ask for an upper limit. Once the run
hit that ceiling, later rows became censored observations rather than
convergence measurements.

Second, the naive increasing grid wastes time when the required history length
gets large. If the first stable event for `n = 200` is expected to be around
4000 events, then testing 900, 950, 1000, and so on is mostly paying for
failed histories that the quadratic already suggests are too short.

The new app is:

```text
src/analysis/toy_elo/predictive_convergence_sweep.py
```

It keeps the old sweep app intact, but changes the search strategy:

```text
1. predict the first stable event from the quadratic
2. start 50 events before that prediction, rounded to the event grid
3. simulate that whole history from event 0
4. measure the true first_stable_event inside the simulated history
5. if not converged, keep increasing by event_step until convergence
```

By default it has no upper event limit:

```text
--event-stop
```

is optional and exists only as an explicit safety ceiling if one is wanted.

The default predictor is:

```text
0.106468633733679 n^2 - 1.0373921331466 n + 120.586077749013
```

and the default backoff is:

```text
--prediction-backoff-events 50
```

The test is deliberately modest: for the range where we already have data
apart from the anomalous `n = 10`, success means the quadratic places us close
enough that convergence is confirmed after one or two attempts.

and the app writes to a separate audit root:

```text
files/output/toy_elo_predictive_convergence_sweep/
```

The intended next command is:

```text
python -m src.analysis.toy_elo.predictive_convergence_sweep --players 20,30,40,50,60,70,80,90,100,150,200,250,300,350,400,450,500,550,600 --runs 100 --event-step 50
```

This does not prove that the quadratic law is real. It uses the current
quadratic as a practical way to spend runtime near the likely convergence
region, while preserving the auditable `first_stable_event` measurement for
each `n`.

## Predictive Sweep Progress

The first predictive run wrote output under:

```text
files/output/toy_elo_predictive_convergence_sweep/20260706_101659_seed1/
```

It used:

```text
r = 100
event_step = 50
prediction_backoff_events = 50
```

The run was stopped during the first `n = 200` attempt because the machine was
needed for other work. The completed part of the summary is:

```text
n    search_start    tested_events    first_stable_event    bucket
10   100             350              304                   350
20   100             150              131                   150
30   150             200              197                   200
40   200             250              244                   250
50   300             350              348                   350
60   400             450              446                   450
70   550             600              563                   600
80   700             750              715                   750
90   850             900              884                   900
100  1050            1100             1084                  1100
150  2350            2400             2362                  2400
```

The main pattern was:

```text
attempt 1: no convergence
attempt 2: convergence
```

This is exactly the desired behavior for the confirmation experiment. It means
that subtracting 50 events from the quadratic prediction usually starts just
before convergence, and the next 50-event step crosses the threshold.

The `n = 150` result is a useful sanity check:

```text
predicted first stable event ~= 2360.5
observed first stable event  = 2362
```

This suggests that, at least through `n = 150`, the quadratic is doing more
than merely fitting old points; it is operationally useful for choosing where
to spend runtime.

The interrupted `n = 200` attempt was:

```text
predicted first stable event ~= 4171.9
search_start = 4150
```

It had an estimated runtime of about one hour for that first attempt.

Because each `n` is independent, the experiment can be resumed by running a
new predictive sweep over the remaining player counts:

```text
python -m src.analysis.toy_elo.predictive_convergence_sweep --players 200,250,300,350,400,450,500,550,600 --runs 100 --event-step 50
```

This will create a new timestamped audit directory, but conceptually it
continues the same experiment from `n = 200`.

## Small-n Oddness

The behavior for small player counts remains odd. A fixed 500-event run over
`n = 10..20` wrote output under:

```text
files/output/toy_elo_convergence_sweep/20260706_140301_seed1/
```

The measured first stable events were:

```text
n    first_stable_event
10   304
11   192
12   169
13   163
14   179
15   198
16   158
17   175
18   135
19   164
20   131
```

This is smooth-ish, but not very. The most striking feature is still that
`n = 10` looks unlike the rest of the range. It is possible that ten players
simply do not generate enough bouts per event for the current stability rule
to behave in the same way.

To check whether the `n = 10` convergence point was just an artifact of
stopping too early, we reran `n = 10` with a much longer 5000-event history:

```text
players = 10
runs = 100
events = 5000
```

That run wrote output under:

```text
files/output/toy_elo_simulation/20260706_135519_seed1/
```

The first stable event was still:

```text
first_stable_event = 304
```

so increasing the history length from 500 to 5000 did not move the measured
convergence point down below the value seen for `n = 20`. However, the longer
run did show that `n = 10` wanders in and out of the stability rule:

```text
persistence after first stable window = 72.0%
stable_now in last 1000 events        = 750 / 1000
last-1000 mean RMSE range             = 1.04 to 5.25
```

The threshold is `mean RMSE <= 4.0`, so this supports the suspicion that
`n = 10` is a small-pool/noisy edge case.

This is not worth pursuing immediately, but two questions remain:

```text
1. Is the small-n explanation correct, and if so should the model or stability
   rule do anything special about it?

2. What does the local curve look like at other resolutions, for example
   n = 21, 22, 23, ... or n = 300, 301, 302, ...?
```

It may turn out that the curve is only smooth-ish everywhere, or that the
irregularity is mostly a small-n phenomenon. This is TBD.
