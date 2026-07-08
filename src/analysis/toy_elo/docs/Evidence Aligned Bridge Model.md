# Evidence Aligned Bridge Model

This note records the current specification for the next two-division toy Elo
bridge model and the audit trail behind it.

The goal is not to fully model torikumi formation. The goal is to replace the
earlier artificial bridge-width parameter with a bridge shape that is aligned
with observed Makuuchi-Juryo scheduling evidence, while keeping the toy system
simple enough to understand.

## Current Target

The next toy model should use two fixed divisions:

```text
division 1 size = 42
division 2 size = 28
total players   = 70
```

The bridge should be calibrated from historical Makuuchi-Juryo scheduled
torikumi, but represented in the toy model by distance from the division
boundary rather than by literal historical chii labels.

The current bridge eligibility rule is:

```text
bottom supported players of division 1 may meet division 2 players
top supported players of division 2 may meet division 1 players
```

With the current 1989/01-2026/05 Makuuchi-Juryo evidence and the default
support threshold, this means:

```text
bottom 6 players of division 1 may meet division 2 players
top 6 players of division 2 may meet division 1 players
```

This is the current evidence-aligned bridge shape.

## Evidence Source

The probabilities and support counts are computed inside this repo by:

```text
python -m src.analysis.toy_elo.matchup
```

The code lives in:

```text
src/analysis/toy_elo/matchup/
```

The relevant generated evidence file is:

```text
files/output/toy_elo_matchup/1989_01-2026_05_no_side_boundary_bridge_distribution.csv
```

The supporting plots are:

```text
files/output/toy_elo_matchup/boundary_plots/
```

The historical window is:

```text
1989/01 through 2026/05
```

We use this period because the post-1989 data is sufficiently complete for
the division-boundary analysis.

## What Is Measured

The analysis uses scheduled torikumi, not realised results.

For each boundary coordinate, the bridge probability is:

```text
probability =
  scheduled bouts involving this focal boundary slot against the adjacent division
  /
  all scheduled bouts involving this focal boundary slot
```

For example, the `M bottom 1 -> J` probability is:

```text
scheduled bouts where the bottom Makuuchi rikishi fights any Juryo opponent
/
all scheduled bouts involving the bottom Makuuchi rikishi
```

This is an all-days aggregate. It is not day-specific.

The day-specific quantity:

```text
P(opponent division | focal boundary slot, scheduled bout, day)
```

may matter later, but is intentionally deferred for the first fixed-division
implementation.

## Grouping

The matchup analysis uses the `no_side` grouping:

```text
M15e + M15w -> M15
J3e  + J3w  -> J3
```

Annotations are dropped. Yokozuna, Ozeki, Sekiwake, and Komusubi numbering is
collapsed within each sub-rank, though that detail is not important for the
Makuuchi-Juryo bridge.

## Support Rule

The current support rule is deliberately simple:

```text
retain boundary rows only if interdivision_bout_count >= 160
```

This is the single magic number in the model. It is auditable because it is
applied directly to a generated column in the boundary bridge distribution CSV.

For the Makuuchi side, this keeps:

```text
M bottom 1, M bottom 2, M bottom 3, M bottom 4, M bottom 5, M bottom 6
```

and excludes deeper Makuuchi boundary positions with lower support.

For the Juryo side, this keeps:

```text
J top 1, J top 2, J top 3, J top 4, J top 5, J top 6
```

and excludes deeper Juryo boundary positions with lower support.

This replaces the earlier literal-rank version of the same idea. Literal ranks
such as `M17`, `M18`, or `J14` are historically contingent because division
sizes change. Boundary coordinates directly ask how far from the adjacent
division edge the scheduled rikishi was.

## Retained Historical Probabilities

These are copied from:

```text
files/output/toy_elo_matchup/1989_01-2026_05_no_side_boundary_bridge_distribution.csv
```

### Upper Side

```text
boundary slot  scheduled  bridge  probability
M bottom 1     3168       502     0.15845960
M bottom 2     3243       444     0.13691027
M bottom 3     3274       390     0.11912034
M bottom 4     3202       313     0.09775141
M bottom 5     3189       238     0.07463155
M bottom 6     3231       181     0.05601981
```

### Lower Side

```text
boundary slot  scheduled  bridge  probability
J top 1        3211       459     0.14294612
J top 2        3227       440     0.13634955
J top 3        3231       388     0.12008666
J top 4        3171       344     0.10848313
J top 5        3169       260     0.08204481
J top 6        3261       229     0.07022386
```

The generated CSV also contains Wilson 95% intervals and relative interval
widths for audit.

## Toy Translation

The toy model should not treat `M15` or `J3` as literal ranks. Fixed divisions
do not have changing historical chii labels. Instead, retained rows are already
expressed as boundary distances.

Upper side:

```text
M bottom 1 -> div1[-1]  bottom division-1 player
M bottom 2 -> div1[-2]
M bottom 3 -> div1[-3]
M bottom 4 -> div1[-4]
M bottom 5 -> div1[-5]
M bottom 6 -> div1[-6]
```

Lower side:

```text
J top 1 -> div2[0]    top division-2 player
J top 2 -> div2[1]
J top 3 -> div2[2]
J top 4 -> div2[3]
J top 5 -> div2[4]
J top 6 -> div2[5]
```

The implementation preserves the retained probabilities under this mapping.

## Runnable Implementation

The first implementation is:

```text
python -m src.analysis.toy_elo.evidence_bridge
```

The code lives in:

```text
src/analysis/toy_elo/evidence_bridge.py
```

By default it uses:

```text
division 1 size       = 42
division 2 size       = 28
days per event        = 15
support threshold     = 160
profile source        = latest *_no_side_boundary_bridge_distribution.csv
output root           = files/output/toy_elo_evidence_bridge/
```

If a generated `*_no_side_boundary_bridge_distribution.csv` file is present,
the simulator uses that boundary-distance profile. It falls back to the older
literal-rank `*_no_side_bridge_distribution.csv` format only when the boundary
file is unavailable or when an older profile is passed explicitly.

One toy event is treated as a basho-like 15-day schedule, not as a complete
round robin. This keeps the empirical bridge probabilities in their measured
unit: probability per scheduled bout.

## Pairing Rule

The empirical data gives marginal bridge propensities:

```text
P(upper boundary slot fights any lower-division player)
P(lower boundary slot fights any upper-division player)
```

It does not, by itself, define an exact toy pairing algorithm.

The implemented first rule is:

```text
for each day:
  visit retained upper boundary slots in random order
  for each upper slot u:
    create a bridge bout with probability upper_probability[u]
    if a bridge bout is created:
      choose an unused lower slot with probability proportional to lower_probability[l]
  schedule the remaining players within their own divisions
```

Each player can appear at most once per day. Bridge pairs are generated before
ordinary within-division scheduling, so already-bridged players are removed
from same-day ordinary pairing.

This pairing rule is simple and auditable. It uses the observed marginal
propensities without pretending to know the exact human torikumi selection
mechanism.

## Known Simplifications

The current model intentionally ignores:

```text
day-specific bridge timing
records/win-loss state
absences and fusen
promotion/relegation churn
changing historical division sizes
stable/beya constraints
human judgement in torikumi formation
```

These are known omissions, not accidental oversights. The point of this model
is to make the two-division toy Elo bridge evidence-aligned while preserving a
small, inspectable mechanism.

## Gap To Sumo

The toy model remains a toy model. It still has a fixed population, fixed
latent skills, a known hidden truth, and simplified scheduling. Real sumo has
entry, exit, retirement, promotion, demotion, changing rikishi ability,
injuries, absences, changing division sizes, records, day-specific torikumi
logic, stable constraints, and human judgement.

The evidence-aligned bridge does not remove those caveats. It reduces part of
the gap in a specific context:

```text
bridge occurrence is no longer represented by an arbitrary width
bridge occurrence is estimated from scheduled torikumi evidence
bridge candidates can be represented by distance from the division boundary
```

The boundary-distance representation is especially useful because it avoids
depending on historically contingent rank labels. A literal rank such as `M17`
or `Sd101` may or may not exist in a given period, but "bottom 1", "bottom 2",
or "top 1" remains meaningful whenever the division exists.

This means that the caveat about changing division sizes still pertains, but
less strongly for this particular mechanism. We are not claiming to have
modelled historical banzuke structure as a whole. We are claiming that, for
interdivision bridge selection, relative position at the boundary is a more
sumo-aligned coordinate than absolute rank name.

The current charts also suggest two descriptive claims about observed
torikumi:

```text
interdivision probability generally decays with distance from the boundary
M-J and J-Ms have shorter reach than the lower-division bridges
```

Those claims improve the toy bridge shape, but they do not yet model when
inside a basho the bridge happens. Here, "when" means which boundary positions
are selected, not the day or record-state that triggers selection.

## Audit Trail

The repo-local evidence path is:

```text
live History
-> scheduled daily.torikumi
-> no_side chii grouping
-> directed scheduled-bout tallies
-> boundary_bridge_distribution.csv
-> support rule: interdivision_bout_count >= 160
-> retained M/J boundary rows
-> boundary-distance toy bridge
```

No extra-repo legacy code is required to reproduce the probabilities.
