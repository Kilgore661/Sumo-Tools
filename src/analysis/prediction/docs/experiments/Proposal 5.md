# Proposal 5: Deterministic Division-only Initialization

## Status

Completed over the represented 1989/01–2026/07 results.

## Question

Can the durable initialization benefit identified by Proposal 4 be reproduced
by broad division membership alone, without exact-Chii differentiation or
selection of a favourable random permutation?

## Fixed producer and data

Retain the Proposal 1 producer and Proposal 3 input surface:

```text
epoch = 1989/01
q = 400
k = 35
eligible result = W/L, irrespective of kimarite
rating identity = RikId
forecast = before the bout update
ratings persist for the complete pass
```

Use Proposal 3's completed `chii_prior.csv`, keyed by authoritative Chii
ordinal. Chii strings are display values only.

## Division prior

Partition the completed Chii-prior rows into the six actual divisions:
Makuuchi, Juryo, Makushita, Sandanme, Jonidan and Jonokuchi. Yokozuna, Ozeki,
Sekiwake, Komusubi and Maegashira are all members of the single Makuuchi
division. Derive membership from the Chii value, not its string form.

For each division, take the unweighted arithmetic mean of all completed
Proposal 3 initial-rating values belonging to that division. Every Chii row
receives one vote, including rows whose Proposal 3 value was interpolated or
obtained from an edge rule.

This mean is not an additionally fitted choice. It is the expected rating
assigned to any fixed Chii by Proposal 4's uniform within-division permutation.
It removes within-division variation while retaining the between-division
locations implied by the same oracle surface.

Whenever a RikId first enters the rating registry, initialize it at the mean
for its pre-bout Chii's actual division. The known unranked RikId 13011 has no
division because of the recorded History-building defect; retain the weakest
domain accommodation by assigning the Jonokuchi mean and record it in the
manifest.

## Comparators and populations

Run three deterministic complete passes over the same bouts:

1. equal initialization at 1500;
2. genuine exact-Chii initialization from Proposal 3;
3. deterministic division-only initialization.

Evaluate all eligible bouts, bouts with two sekitori participants, and bouts
with two sub-sekitori participants. Evaluation membership never removes a bout
from the rating producer.

Read Proposal 4's `cumulative_envelope.csv` as declared comparison evidence.
At each date, retain the within-division randomized median and ordered values 5
and 95. Do not select or reproduce an individual favourable permutation.

## Scores and summaries

Log loss is primary and Brier loss is secondary. For every producer and
population, calculate cumulative mean loss through each basho and report the
same predeclared horizons as Proposal 4:

```text
6 basho
12 basho
30 basho
60 basho
complete represented epoch
```

Report raw loss and paired difference from equal initialization. Compare the
division-only curve descriptively with genuine Chii and with the
within-division randomized 5th-to-95th ordered range.

Proposal 5 does not introduce a threshold for practical importance or a
sampling interval. A smaller observed proper score is better on the represented
bouts, but small differences must be reported as small. Proposal 4's randomized
range measures mapping sensitivity, not historical sampling uncertainty.

## Required artifacts

Write:

- `division_prior.csv`, containing actual division, mean initial rating, Chii
  count, minimum Chii rating and maximum Chii rating;
- `cumulative_comparison.csv`, containing equal, genuine, division-only and the
  Proposal 4 within-division envelope for every population and basho;
- `horizon_comparison.csv` for the declared horizons;
- a responsive Plotly CDN chart with a population selector;
- a manifest containing source paths and digests, model definition and the
  unranked accommodation;
- a short Markdown report;
- `execution_time.txt` containing total wall-clock duration.

## Interpretation boundary

If division-only improves on equal and is comparable with the Proposal 4
within-division distribution, division membership is sufficient to reproduce
the durable placebo result. If genuine Chii remains better only at early
horizons, exact rank is useful primarily for the epoch incumbents. If
division-only fails despite the randomized median's apparent advantage, the
randomized result cannot be summarized by the expected within-division value.

The division means inherit Proposal 3's future outcomes. This remains an oracle
diagnostic, not a prospective initialization rule.
