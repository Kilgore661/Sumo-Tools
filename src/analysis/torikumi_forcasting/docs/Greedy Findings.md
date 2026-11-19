# Greedy Torikumi Forecasting: Findings

## Status

Experiment 1 from the agreed proposal has been implemented and run without
backtracking or result-driven repair.  The full run used completed basho from
1958/01 through 2026/09 represented in the `1958_01 to 2026_11` History
snapshot.  The incomplete 2026/11 basho was not scored.

The immutable generated bundle is:

```text
files/output/analysis/torikumi_forcasting/greedy_2026-11-19_12-03-14
```

Its [generated report](../../../../files/output/analysis/torikumi_forcasting/greedy_2026-11-19_12-03-14/report.md)
and row-level CSVs remain the numerical evidence for this note.

## Scope correction discovered before the full run

A five-basho 2026 pilot exposed a false assumption in the initial proposal:
cross-division bouts do not occur only when required by odd makuuchi population
parity.  Some target cards have two, three or more makuuchi rikishi facing
juryo opponents.

The agreed correction excludes cards whose actual number of cross-division
makuuchi participants exceeds the parity minimum.  This preserves the narrow
first experiment rather than inventing a rule for forecasting additional
cross-division selections.  The greedy pairing rule itself was not changed in
response to the pilot.

Across all completed represented basho, 710 of 2,055 candidate late-basho
cards were excluded for this reason, leaving 1,345 evaluated cases.  This is a
large scope restriction and must accompany every interpretation of the
forecasting results.

## Principal results

| Measure | Result |
|---|---:|
| Evaluated cards | 1,345 |
| Greedy completion successes | 986 |
| Greedy failures | 359 |
| Failure rate | 26.69% |
| Mean per-card pair recovery | 11.47% |
| Pair-weighted recovery | 2,846 / 25,039 = 11.37% |
| Exact reduced cards | 0 |
| Odd-population cases | 821 |
| Correct unmatched rikishi | 43 (5.24%) |
| Synthetic-heya case appearances | 0 |

A greedy completion success means only that the algorithm left the
parity-appropriate number of rikishi unmatched.  It does not mean that the
result resembled the published card.  Mean pair recovery was effectively the
same for completed forecasts (11.47%) and failed forecasts (11.46%).

The recent twelve-basho comparison split contained 58 eligible cases.  It had
16 greedy failures, 10.53% mean pair recovery and no exact card.  Part of 2026
had already been inspected during the input-validation pilot, so this split
should not be described as wholly unseen evidence.  No greedy rule was changed
after inspecting it.

## Results by target day

| Day | Cases | Failures | Mean pair recovery | Exact cards |
|---:|---:|---:|---:|---:|
| 11 | 300 | 49 | 8.14% | 0 |
| 12 | 276 | 45 | 9.44% | 0 |
| 13 | 275 | 74 | 11.28% | 0 |
| 14 | 254 | 88 | 12.26% | 0 |
| 15 | 240 | 103 | 17.34% | 0 |

Recovery increases late in the basho, but even Day 15 recovers only about one
pair in six on average and produces no exact card.

## What the result establishes

The literal rule of sorting makuuchi by wins through `d - 2`, breaking ties by
chii, and greedily selecting the first eligible opponent is a poor historical
torikumi forecaster.  Its weakness is not confined to rare dead ends:
successfully completed cards recover actual pairs at almost exactly the same
low rate as failed cards.

The result does not yet distinguish between two explanations:

1. greedy local choices rapidly send the remaining card down a different path;
2. the underlying sorted-standings account is itself a poor description of the
   JSA's choices.

Experiment 2, minimum-cost constrained matching over the same eligible cases,
isolated those explanations.  It raised mean recovery only from 11.47% to
12.53%, while finding a proved-optimal complete solution for every case.  The
combined result and its deliberately conservative falsification claim are
recorded in
[Findings - Falsifying the Rule of Thumb](Findings%20-%20Falsifying%20the%20Rule%20of%20Thumb.md).

No missing historical heya affected the evaluated cases.  Family restrictions
remain unrepresented, but they cannot plausibly explain recovery this low.
