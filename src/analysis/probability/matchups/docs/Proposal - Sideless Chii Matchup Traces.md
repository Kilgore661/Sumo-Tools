# Sideless Chii Matchup Traces: Proposal

This proposal defines the next exploration for `probability.matchups`.

The aim is to compare an observed sideless-chii matchup surface with an
Equelo-implied sideless-chii matchup surface.

The purpose is not yet to build a final public page. The purpose is to create
two comparable analysis artefacts that make the relationship between observed
chii outcomes and Equelo-implied probabilities visible.

---

# 1. Motivation

The current matchups work has produced empirical CSV artefacts for observed
chii-vs-chii bout outcomes.

Those artefacts establish the raw empirical basis:

```text
actual scheduled bouts
-> chii pair
-> observed win count
-> observed win probability
```

The next question is:

> Does the observed chii-vs-chii matchup surface resemble the probability
> surface implied by Equelo ratings?

This is a consistency check, not a proof of model truth.

If the two surfaces agree where observed support is strong, then Equelo passes
a useful descriptive check against the empirical chii matchup data.

If they disagree, the disagreement needs interpretation. Possible explanations
include model error, sparse support, torikumi selection effects, or genuine
structure in sumo that the model does not represent.

---

# 2. Core Question

For sideless chii values:

```text
c, d
```

compare:

```text
observed P(c-rikishi beats d-rikishi | actual scheduled bout)
```

with:

```text
Equelo-implied P(rating(c) beats rating(d))
```

Both views should use the same visual grammar:

```text
trace identity: selected sideless chii c
x-axis: opponent sideless chii d
y-axis: P(selected beats opponent)
```

---

# 3. Terminology

## Sideless chii

For this proposal, sideless chii means:

```text
annotation collapsed
side removed
rank identity otherwise preserved
```

Examples:

```text
M3eHD -> M3
M3e   -> M3
M3w   -> M3
J7e   -> J7
J7w   -> J7
Y1e   -> Y1
Y1w   -> Y1
```

This does not collapse different numbers or divisions:

```text
M3 != M4
M3 != J3
Y1 != O1
```

## Equelo rating for sideless chii

The Equelo rating for a sideless chii is defined from the forced-monotone
fixed-v1 initial rating curve. For each sideless chii, take the arithmetic mean
of the available side-specific monotone ratings:

```text
rating(M3) = mean(rating(M3e), rating(M3w))
```

Similarly:

```text
rating(Y1) = mean(rating(Y1e), rating(Y1w))
rating(J7) = mean(rating(J7e), rating(J7w))
```

If only one side-specific monotone rating exists for a sideless chii, the
sideless rating should use that available rating and record that the support
count is one.

The first implementation should preserve:

```text
sideless_chii
rating
n_side_ratings
side_ratings_used
```

so that any asymmetric or missing side data remains visible.

The raw fixed-v1 entrant ratings are not the correct source for this chart,
because they are not strictly monotone by chii. The intended source is the
curated fixed-v1 v5 monotone curve. This curve also defines the presentation
domain.

Observed chii outside the curated v5 domain should be excluded from these trace
charts. There is no separate warts-and-all comparison chart for historical or
rare ranks in this proposal.

---

# 4. Required Artefacts

The implementation should be CSV-first.

Charts should be generated from CSV artefacts, not directly from raw history or
rating files.

## 4.1 Observed trace points CSV

This CSV should contain one row per observed selected/opponent sideless chii
combination.

Candidate file:

```text
files/output/probability/matchups/observed_sideless_trace_points.csv
```

Required columns:

```text
selected_chii
opponent_chii
selected_ordinal
opponent_ordinal
n_obs
n_selected_wins
n_opponent_wins
p_selected_wins
ci95_lower
ci95_upper
```

This file can be derived from:

```text
empirical_sideless_chii_pairs.csv
```

For non-same-chii rows, both directions should be emitted:

```text
c beats d
d beats c
```

using:

```text
P(d beats c) = 1 - P(c beats d)
```

For same-chii rows, emit only one row:

```text
c beats c
```

and do not infer a reverse complement.

## 4.2 Equelo sideless rating CSV

This CSV records the sideless rating map used by the model-implied surface.

Candidate file:

```text
files/output/probability/matchups/equelo_sideless_ratings.csv
```

Required columns:

```text
sideless_chii
sideless_ordinal
rating
n_side_ratings
side_ratings_used
```

The rating should be the arithmetic mean of available side-specific ratings
from the curated fixed-v1 v5 monotone curve.

Observed-domain chii outside that curve should be filtered out before writing
the observed and Equelo trace CSVs. The comparison domain is the intersection of
observed bouts and the curated v5 sideless chii domain.

The metadata should record that the source is the forced-monotone fixed-v1 v5
curve, and may also record the raw fixed-v1 entrant-ratings artefact from which
that curve is derived.

## 4.3 Equelo trace points CSV

This CSV should contain one row per selected/opponent sideless chii combination
present in the curated-domain observed trace-points CSV.

The curated v5 domain defines which chii are eligible for comparison; the
observed data then defines which selected/opponent pairs exist inside that
domain. The Equelo trace CSV is the model image of those observed pairs, not a
complete hypothetical round-robin surface.

Candidate file:

```text
files/output/probability/matchups/equelo_sideless_trace_points.csv
```

Required columns:

```text
selected_chii
opponent_chii
selected_ordinal
opponent_ordinal
selected_rating
opponent_rating
p_selected_wins
```

The model probability should use the same Elo/Bradley-Terry link used by the
relevant Equelo configuration:

```text
P(selected beats opponent)
    = 1 / (1 + 10 ** ((opponent_rating - selected_rating) / q))
```

The value of `q` must be recorded in metadata.

If either side of an observed selected/opponent chii pair lacks a sideless
Equelo rating, the Equelo trace point should be omitted and counted in metadata.

---

# 5. Chart Requirements

The first chart implementation should produce two HTML files.

## 5.1 Observed chii matchup trace chart

Candidate file:

```text
files/output/probability/matchups/observed_sideless_matchup_traces.html
```

Chart grammar:

```text
x-axis: opponent sideless chii, ordered by chii ordinal
y-axis: observed P(selected chii beats opponent chii)
trace: selected sideless chii
```

Requirements:

* include CI95 error bars
* CI95 error bars should be visually subordinate to the trace line and markers
* CI95 error bars should be controlled by an on/off checkbox
* hover should show selected chii, opponent chii, `n_obs`, win count, and
  probability
* initially show only the `Y1` trace
* all other traces should be present but initially hidden via Plotly legend
* the chart should include a division dropdown so the legend can be scoped to
  Makuuchi, Juryo, Makushita, Sandanme, Jonidan, Jonokuchi, or all divisions
* legend double-click should isolate the clicked trace within the current
  division scope
* the visible x-axis domain should be computed from the currently visible
  trace or traces, not from all traces in the dataset
* observed points outside the curated v5 rating domain should be excluded
* displayed sanyaku chii should be limited to `Y1`, `O1`, `S1`, and `K1` on
  both axes and in the legend

## 5.2 Equelo sideless matchup trace chart

Candidate file:

```text
files/output/probability/matchups/equelo_sideless_matchup_traces.html
```

Chart grammar:

```text
x-axis: opponent sideless chii, ordered by chii ordinal
y-axis: Equelo-implied P(selected rating beats opponent rating)
trace: selected sideless chii
```

Requirements:

* initially show only the `Y1` trace
* all other traces should be present but initially hidden via Plotly legend
* the chart should include the same division dropdown policy as the observed
  chart
* legend double-click should isolate the clicked trace within the current
  division scope
* hover should show selected chii, opponent chii, selected rating, opponent
  rating, and probability
* for any visible trace, the x-axis domain should match the observed chart's
  visible domain for the same trace selection
* displayed sanyaku chii should be limited to `Y1`, `O1`, `S1`, and `K1` on
  both axes and in the legend

No confidence intervals are shown on the Equelo chart because it is a
model-implied surface, not an observed frequency estimate.

---

# 6. Comparison Semantics

The observed and Equelo charts share:

```text
trace identity
x-axis
y-axis probability scale
```

They do not have the same y-value semantics.

The observed chart is:

```text
conditional on actual torikumi
support-dependent
restricted to the curated v5 rating domain
```

The Equelo chart is:

```text
model-implied over the observed trace domain
after applying the same curated v5 rating domain filter
smooth by construction
```

Therefore, visual comparison is meaningful, but it must be interpreted as a
consistency check rather than a direct proof.

Where observed support is high and confidence intervals are narrow, large
disagreements between the observed and Equelo surfaces deserve explanation.

Where support is low, disagreement should not be over-interpreted.

---

# 7. Difference Chart

A third chart may later show:

```text
observed_p - equelo_p
```

This is deliberately not part of the first implementation.

The first pass should use the Mark 1.0 human eyeball:

* inspect the observed chart
* inspect the Equelo chart
* decide whether residual analysis is worth formalising

If a difference chart is later added, it should include support-aware
presentation, such as filtering, opacity, or explicit `n_obs` labelling.

---

# 8. Non-Goals

The first implementation should not:

* build a final public presentation-layer page
* implement deployment
* produce residual/difference charts
* claim that Equelo explains torikumi
* claim that observed disagreement proves the model is wrong without
  considering support and selection effects
* replace the existing empirical CSV artefacts

---

# 9. Implementation Notes

The implementation should probably live inside:

```text
src/analysis/probability/matchups/
```

Likely modules:

```text
ratings.py
traces.py
charts.py
```

The current empirical outputs already provide most of the observed side:

```text
empirical_sideless_chii_pairs.csv
```

The new work should add:

```text
observed_sideless_trace_points.csv
equelo_sideless_ratings.csv
equelo_sideless_trace_points.csv
observed_sideless_matchup_traces.html
equelo_sideless_matchup_traces.html
```

The Equelo trace points should be built from the observed trace domain. A
complete Equelo round-robin surface is a separate possible artefact and is not
part of this proposal.

Metadata should record:

```text
date range
oracle collapse policy
sideless rating source
raw rating source, where applicable
q
output filenames
```

---

# 10. Expected Use

The initial reader should be able to open the two HTML charts and compare one
selected sideless chii at a time.

For example:

```text
Y1
O1
M6
M17
J7
```

The observed chart should show what actually happened in scheduled bouts.

The Equelo chart should show what the model would expect from the corresponding
sideless chii ratings.

The first question is not:

> Which chart proves the other?

The first question is:

> Do the shapes broadly agree where the observed data has enough support?
