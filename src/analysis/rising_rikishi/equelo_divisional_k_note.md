# Note: divisional K factors and rising-rikishi metrics

## Summary

Equelo's divisional K factor is selected per bout from the first rikishi in the recorded bout pair.
The same absolute rating movement is then applied symmetrically to both rikishi.

This is acceptable for the first iteration of the rising-rikishi producer, which reports only:

```csv
rik_id,shikona,chii,chii_ordinal,delta,basho_norm,num_bouts,bout_norm
```

The first iteration deliberately does not include a division-max-normalised metric.

## Current Equelo behaviour

The current update logic is effectively:

```python
ordinal_a = banzuke.rikchii[r1].ordinal()
k = params.k(ordinal_a)

expected_a = expected_score(current_ratings[r1], current_ratings[r2])
actual_a = actual_score_for_rikishi_1

delta = k * (actual_a - expected_a)

current_ratings[r1] += delta
current_ratings[r2] -= delta
```

So:

- the selected K factor comes from `rikishi1` / `r1`;
- both rikishi receive the same absolute rating movement, with opposite signs;
- in a same-division bout this is normally unproblematic;
- in an inter-division or cross-K-bucket bout, the movement is tied to the division/rank bucket of the first recorded rikishi.

## Consequence for derived metrics

A future metric could normalise movement by the relevant K factor, for example:

```text
normalised_basho_movement = actual_rating_movement_in_basho / applicable_k_factor
```

Since rikishi remain in the same division within a basho, this can be accumulated on a per-basho basis.
The applicable K factor should be the K factor actually used by the Equelo rating function for the bouts that produced the movement.

The wrinkle is inter-division bouts. In those bouts, the participant whose own division differs from the selected `r1` division receives a rating movement whose K context is not directly comparable to the K context used for other rikishi in that participant's own division.

This is acceptable for exploratory work, but it should be documented if a K-normalised rising-rikishi metric is added later.

## Decision for rising-rikishi v1

Do not add a K-normalised or division-max-normalised column in the first version.

Keep the producer focused on the metrics that are already directly defined from fixed-supported Equelo outputs:

- `delta`: raw Equelo rating change across the window;
- `basho_norm`: `delta / number_of_basho`;
- `num_bouts`: number of rating-updating bouts in the window;
- `bout_norm`: `delta / num_bouts`, blank if `num_bouts == 0`.

## Future option

If a K-normalised metric is added later, calculate it by replaying or instrumenting per-basho/per-bout movement so that the denominator is the K factor actually used by the Equelo rating function, rather than an independently inferred division maximum.

The output should also document that inter-division bouts are normalised according to the K context selected by the current Equelo bout update rule.
