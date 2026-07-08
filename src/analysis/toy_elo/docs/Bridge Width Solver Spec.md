# Bridge Width Solver Spec

This note defines the requirements and implementation shape for a solver that
studies two Elo divisions connected by bridges of width `d`.

The purpose is to measure how much interdivision connectivity is needed for a
split Elo system to learn the rating offset between the two divisions.

## Context

The no-interaction split-division sweep showed that two isolated divisions
learn their internal rating geometry but cannot learn the cross-division
offset. With common initial ratings, the two learned ladders sit on top of
each other, modulo noise.

The bridge-width experiment keeps the same total number of players and the
same number of matches per player, but rewires some internal division matches
into cross-division matches.

## Requirements

The solver must support any total player count `n >= 2`.

For even `n`, the two divisions have the same size. For odd `n`, the
divisions differ by one player:

```text
top_size = ceil(n / 2)
bottom_size = floor(n / 2)
```

The choice of which division gets the extra player should not affect the
qualitative experiment. The first implementation should put the extra player
in the top division and record both division sizes in the manifest and CSVs.

Players are ordered strongest to weakest. In 1-based division notation:

```text
top division:    T_1, T_2, ..., T_top_size
bottom division: B_1, B_2, ..., B_bottom_size
```

`T_1` is the strongest top-division player, `T_top_size` is the weakest
top-division player, `B_1` is the strongest bottom-division player, and
`B_bottom_size` is the weakest bottom-division player.

The bridge parameter `d` is a percentage, not a raw player count. Let:

```text
m_top = top_size
m_bottom = bottom_size
w_top = int(m_top * d / 100)
w_bottom = int(m_bottom * d / 100)
w = min(w_top, w_bottom)
```

where `w` is the number of matched bridge slots used by the event schedule.
The two divisions may have different sizes, but a bridge slot needs one top
side and one bottom side endpoint, so the effective number of slots is the
smaller of the two percentage-derived counts.

The bridge percentage must produce valid side counts:

```text
0 <= w_top <= floor(m_top / 2)
0 <= w_bottom <= floor(m_bottom / 2)
```

The upper bound avoids duplicate rewrites and self-pairings in the mirrored
schedule. A `d` value that produces an invalid side count should be rejected
rather than silently capped.

For `w = 0`, the solver must reproduce the no-interaction split model:

```text
top division round robin
bottom division round robin
no interdivision matches
```

For `w > 0`, the solver must replace internal matches with cross-division
matches without changing the number of matches per player.

## Bridge Schedule

For each bridge slot:

```text
i = 0, 1, ..., w - 1
```

remove:

```text
T_(top_size-i)      vs T_(i+1)
B_(i+1)             vs B_(bottom_size-i)
```

add:

```text
T_(top_size-i)      vs B_(i+1)
T_(i+1)             vs B_(bottom_size-i)
```

For `i = 0`, this means:

```text
remove:
T_top_size   vs T_1
B_1          vs B_bottom_size

add:
T_top_size   vs B_1
T_1          vs B_bottom_size
```

Each unit of bridge width adds two cross-division matches and removes two
internal matches. Therefore every player still has:

```text
division_size - 1
```

matches per event, where `division_size` is that player's own division size.

In zero-based global player indexes, with top players `0..top_size-1` and
bottom players `top_size..n-1`, each bridge slot `i` rewires:

```text
remove:
(top_size - i - 1, i)
(top_size + i, n - i - 1)

add:
(top_size - i - 1, top_size + i)
(i, n - i - 1)
```

The implementation should build the event schedule as a set of unordered
pairs to make duplicate detection straightforward.

## Solver Behavior

The solver should sweep one or more bridge widths for one or more player
counts.

At minimum it should support:

```text
--players 40,60,80,100,150
--bridge-widths 0,10,20,30
--runs 100
--event-step 50
--event-start 50
--event-stop optional
```

For each `(n, d)`, the solver should run increasingly long histories until the
chosen convergence rule is met. Unlike the earlier split-division sweeps, the
bridge solver should extend the same ensemble in increments rather than
rerunning each longer history from scratch:

```text
run to 100 events
extend the same ensemble to 150 events
extend the same ensemble to 200 events
```

This preserves the same stochastic history for each run while avoiding
duplicated work.

Runtime is expected to increase with:

```text
runs * events * matches_per_event
```

The number of matches per event remains:

```text
top_size * (top_size - 1) / 2 + bottom_size * (bottom_size - 1) / 2
```

because the bridge model rewires matches rather than adding matches.

The dynamical behavior may nevertheless be slower or more complex than the
no-interaction model, because offset information has to enter through the
bridging players and propagate through each division.

## Metrics

The solver should keep the split-division metrics:

```text
top_final_rmse
bottom_final_rmse
whole_final_rmse
cross_final_rmse
division_offset_error
top_first_stable_event
bottom_first_stable_event
internal_first_stable_event
```

It should add bridge-specific diagnostics:

```text
bridge_width
bridge_slots
bridge_match_count_per_event
boundary_rating_gap
boundary_skill_gap
boundary_gap_error
division_mean_rating_gap
division_mean_skill_gap
division_mean_gap_error
```

The boundary gap is:

```text
R(T_top_size) - R(B_1)
```

and the corresponding hidden skill gap is:

```text
S(T_top_size) - S(B_1)
```

In the current uniform hidden-skill model, the true boundary gap is the
adjacent skill gap:

```text
gap = 40
```

The division mean gap is:

```text
mean(R_top) - mean(R_bottom)
```

and should be compared with:

```text
mean(S_top) - mean(S_bottom)
```

This measures whether the bridge is learning the otherwise-missing offset.

## Convergence Rule

The bridge experiment needs more than one convergence notion:

```text
internal convergence:
  both divisions have stable internal RMSE

whole-scale convergence:
  whole-system RMSE is stable and below threshold

bridge convergence:
  division mean gap error is stable and below threshold
  boundary gap error is stable and below threshold

schedule-level global convergence:
  for w = 0, the same as internal convergence
  for w > 0, defaults to bridge convergence
```

The no-interaction case can satisfy internal convergence while failing
whole-scale convergence. For `w = 0`, there is no bridge through which the
whole-scale offset can be learned, so schedule-level global convergence means
both disconnected components have converged internally.

For `w > 0`, the original whole-scale rule can be too strict. A bridge run may
learn the division offset and the boundary gap while still plateauing above
the full round-robin RMSE threshold. Therefore the default `auto` target for
bridged runs is bridge convergence, not whole-scale convergence.

The current bridge convergence thresholds are:

```text
abs(division_mean_gap_error) <= bridge_offset_epsilon
abs(boundary_gap_error) <= bridge_boundary_epsilon
```

The division mean gap error is also required to have slope within
`slope_epsilon` over the stability window. The boundary gap error slope is
recorded for audit, but no longer gates bridge convergence because early
bridge runs showed that this local boundary metric can remain noisy after the
bridge has found the right scale.

The summary should record both first stable events when available:

```text
internal_first_stable_event
whole_first_stable_event
bridge_first_stable_event
global_first_stable_event
```

## Output

Each run must write a timestamped audit directory under:

```text
files/output/toy_elo_bridge_width_sweep/
```

The directory should contain:

```text
manifest.json
attempts.csv
summary.csv
final_ratings_n{players}_d{bridge_width}.csv
```

The manifest should record:

```text
players
bridge_widths
runs
event_start
event_step
event_stop
gap
q
learning_fraction
stable_epsilon
bridge_offset_epsilon
bridge_boundary_epsilon
slope_epsilon
stable_window
seed
```

`attempts.csv` should include one row per tested `(n, d, w, events)`.

For incremental runs, `elapsed_seconds` in `attempts.csv` is the time spent
extending from the previous tested event count to the current tested event
count. It is not the cumulative runtime for the whole history length.

`summary.csv` should include one row per completed `(n, d, w)`.

The summary should be useful even if a long run is interrupted. This means
completed `(n, d, w)` rows must be flushed as soon as they complete.

Each completed case should also write a final ratings dump with one row per
player. This file should include the final mean rating, hidden skill, gap to
the next player, hidden gap to the next player, gap error, and a yes/no
indicator for whether the rating remains descending at that point.

## CLI Shape

The proposed module name is:

```text
src.analysis.toy_elo.bridge_width_sweep
```

Example command:

```text
python -m src.analysis.toy_elo.bridge_width_sweep --players 40,60,80,100,150 --bridge-widths 0,10,20,30 --runs 100 --event-step 50
```

The default bridge widths may be conservative, for example:

```text
0,10,20,30
```

The app should reject invalid widths for a given `n`:

```text
d < 0
int(top_size * d / 100) > floor(top_size / 2)
int(bottom_size * d / 100) > floor(bottom_size / 2)
```

## Implementation Notes

The bridge app should share as much machinery as possible with
`split_division_sweep.py`, especially:

```text
run directory creation
manifest writing
event stepping
runtime estimates
RMSE helpers
progress reporting
summary flushing
```

The cleanest factoring is probably to extract reusable schedule and simulation
helpers before or during implementation:

```text
division player construction
round-robin pair construction
bridge pair construction
metric construction
attempt/summary writing
```

The first implementation should keep the model deterministic under a fixed
seed, as the current sweeps do.

## Expected Qualitative Behavior

For `w = 0`, the result should match the no-interaction split sweep:

```text
small internal RMSE
large whole/cross RMSE
division offset error approximately -20n
```

For `w > 0`, bridge players should transmit offset information between the two
divisions. The immediate rating movement should be:

```text
top-side bridge players upward
bottom-side bridge players downward
```

That information should then propagate through ordinary intradivision matches.

The experiment should show whether the boundary gap:

```text
R(T_top_size) - R(B_1)
```

approaches the true adjacent gap, and how quickly the whole system learns the
division offset as `d` increases.
