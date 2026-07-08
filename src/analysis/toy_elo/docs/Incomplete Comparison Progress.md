# Incomplete Comparison Progress

This note records the motivation, experiments, and current interpretation of
the toy Elo work.

## Motivation

The question is not primarily how to design a rating system. The question is
what happens to Elo-style ratings when the match graph is not a complete
round robin.

The motivating case is sumo. Rikishi are arranged into divisions, and they do
not all fight each other. Even within a division, a basho is not a round
robin. The torikumi is sparse, rank-local, and structured. Divisions are
connected by limited boundary interaction, promotion/relegation, and occasional
cross-division bouts.

The abstract question is therefore:

```text
Can Elo recover and maintain a coherent global skill scale when comparisons
are mostly local and only sparsely bridged?
```

The sumo case gives the question practical force, but the toy model is a
controlled study of Elo on incomplete comparison schedules.

## Baseline Model

The baseline toy system has `n` players with fixed hidden skills. Hidden skills
are evenly spaced by a gap `g`, usually:

```text
g = 40
```

The outcome probability is logistic on the hidden skill difference, using the
same `q` scale as Elo. All ratings initially start at the common baseline:

```text
R_i = max_rating / 2
```

For `n = 100`, `gap = 40`, this means:

```text
max_rating = 3960
baseline   = 1980
```

The fully mixed round-robin model was used first because it is the cleanest
case. It gave us a baseline convergence curve and a sense of how `k`, `q`,
`gap`, number of players, number of events, and number of repeated runs affect
the observed behavior.

## Split Divisions

The next model split the `n` players into two isolated divisions. Each division
ran its own round robin, but there were no interdivision matches.

This showed the expected failure mode:

```text
each division can learn its local ladder
the two ladders do not learn their relative offset
```

Because all players start at the same baseline and updates are zero-sum inside
each disconnected component, the top division and bottom division settle into
similar local shapes centered around the same rating level. The whole-system
and cross-division errors are therefore large by construction.

This is the disconnected-scale problem. It is the reason the bridge model is
interesting.

The current evidence-aligned successor to the artificial bridge-width model is
specified separately in `Evidence Aligned Bridge Model.md`. That note records
how the Makuuchi-Juryo torikumi evidence is converted into a fixed
`42 + 28` two-division toy bridge.

## Bridge Model

The bridge model keeps two divisions but rewires some internal matches into
cross-division matches.

For each bridge slot, it removes:

```text
weak top-side player vs strong top-side counterpart
strong bottom-side player vs weak bottom-side counterpart
```

and adds:

```text
weak top-side player vs strong bottom-side player
strong top-side counterpart vs weak bottom-side counterpart
```

This preserves the number of matches per player while introducing controlled
cross-division information flow.

Bridge width is represented as a percentage `d`. For example, with `n = 100`
and two divisions of 50 players, `d = 30` gives 15 bridge slots and 30
cross-division matches per event.

## What The First Bridge Result Suggests

The main successful bridge run so far used:

```text
n = 100
d = 30%
runs = 100
event_step = 50
flat priors
```

It ran about one billion matches. The final ratings formed an almost straight
line against player order:

```text
R^2 ~= 0.999988
```

The adjacent rating-gap RMSE was about:

```text
3.44
```

relative to the true adjacent hidden-skill gap:

```text
40
```

So the adjacent-gap RMSE was roughly:

```text
3.44 / 40 ~= 8.6%
```

The largest adjacent gap error observed in that inspection was about 12 rating
points. That is visible locally, but still modest relative to the 40-point
hidden gap.

This suggests that, at least in the `n = 100`, `d = 30%` case, the bridged
schedule can recover a coherent global rating geometry from flat priors. This
is stronger than merely showing that each division is locally well ordered.

## What We Should Not Overclaim

The word "convergence" was doing real work. The current evidence is best
described as:

```text
the process can recover a desirable global geometry
```

not yet:

```text
the process has been proved to converge and remain there
```

There are two important limitations.

First, the sweep searches tested history lengths in buckets, usually 50 events
at a time. This does not mean that the stability predicate only sees every
50th event: when a candidate history length is tested, the code has the full
event-by-event history up to that point. However, the reported `tested_events`
is still bucketed.

Second, we dropped the boundary-gap slope from the bridge-stability condition.
That was a reasonable experimental choice because the boundary metric remained
noisy even when the global geometry looked good. But it weakens the meaning of
"stable". The current bridge success rule is closer to:

```text
the errors entered an acceptable band for a sustained window
```

than:

```text
the errors entered the band and stopped moving
```

Future reporting should distinguish:

```text
first_success_event
final_success_now
fraction_success_after_first
longest_success_run
max_error_after_first
```

This would let us talk about arrival, persistence, and relapse separately.

## Why The Bridge Model Is Worth Testing

A critic who already understands Elo might say that the logistic update rule
creates a restoring force, so there is no reason to fear arbitrary chaotic
behavior.

That is fair for fully mixed Elo. But the bridge model is not asking whether
Elo works in a full round robin. It asks how much information can pass through
a sparse comparison graph.

With no bridge, the cross-division offset is underdetermined. With a bridge,
the question becomes:

```text
How much cross-division connectivity is enough to align two local rating
systems on a shared scale?
```

The first bridge result is promising because it suggests that a sparse bridge
can transmit enough information to align the global ladder in a sumo-shaped
toy model.

## Prior Experiments We Have Discussed

Several prior experiments remain useful but are not urgent enough to block the
next stage.

One idea is a teleological prior with local gaps equal to `g` but a doubled
gap at the division boundary:

```text
within divisions:  adjacent gap ~= g
division boundary: boundary gap ~= 2g
```

This would test whether bridge matches can repair a plausible but wrong
boundary prior.

Another idea is to use final ratings from a successful run as the next run's
initial ratings. That would test whether a learned global ladder is preserved,
repaired, or distorted under continued sparse play.

The two ideas can be combined:

```text
start from learned final ratings
perturb the division boundary to have a doubled gap
test whether the bridge repairs the perturbation
```

These are good robustness experiments, especially for understanding prior
sensitivity. But they are still experiments inside the round-robin bridge
abstraction.

## Next Step: Torikumi Formation

The next conceptual step is to replace round-robin events with a more careful
model of match scheduling.

In sumo, there is no round robin even within a division. The torikumi is not
random either. It is sparse, rank-local, constrained, and evolves during a
basho.

A useful next toy model should represent:

```text
players ordered by rank
one bout per active player per day
no repeated opponents within one basho
opponents usually drawn from a rank window
later opponents influenced by current record
limited cross-division eligibility near division boundaries
```

The first torikumi model should stay simple enough to understand. A sensible
sequence is:

```text
Model 0: rank-window random matching, no rematches, 15 days
Model 1: rank-window plus same-record preference after early days
Model 2: add division-boundary cross-division eligibility
Model 3: compare with real torikumi data
```

This reframes the main question as:

```text
Can Elo recover global skill geometry under sparse, rank-local,
record-influenced scheduling?
```

That is closer to the sumo motivation than round-robin bridges, while still
remaining controlled enough to interpret.

## Current Position

The current result is best summarized as:

```text
A sparse-bridge Elo schedule can plausibly recover global skill geometry in a
sumo-shaped toy model.
```

The result is promising, not final. It supports moving toward a torikumi-shaped
schedule model, while keeping the bridge work as a useful baseline for
incomplete comparison graphs.
