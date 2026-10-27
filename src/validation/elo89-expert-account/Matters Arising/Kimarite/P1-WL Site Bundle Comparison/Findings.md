# Findings: P1 versus P1-WL site-bundle comparison

## Decision

The controlled comparison found no reason to prevent P1-WL from progressing
to a complete, non-deployed web-site build.

This is not an exhaustive validation of every numerical change or every
possible interpretation of rank movement. It is sufficient evidence for the
next engineering step: generate the site with P1-WL, then inspect the affected
pages and downstream behaviour in their actual presentation context.

P1-WL is not installed as the canonical prior by this tranche, and nothing is
deployed.

## Experiment

The adopted run is:

```text
output/site-bundle-comparison-2026-10-27-run3
```

It compared two complete `site89` data bundles over 225 basho from `1989/01`
through `2026/09`. The sole intended difference was the fixed entrant prior:

| Run | Prior SHA-256 |
|---|---|
| P1 baseline | `bd2ed9868c883fda5a52615ed96b4430f4d6c2c06db53474bd0e84757497f003` |
| P1-WL candidate | `6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486` |

The selected History fingerprint was
`46d10d006d394a146a4f0d54491741905248d3ef643ee74d05f5ee2f6543806a`.
The root manifest records the remaining input identities. Total wall-clock
time was 200.101 seconds.

## Publication-boundary result

The comparison covered 305 files across 22 declared site artifacts and the
underlying Elo-89 run:

| Measure | Result |
|---|---:|
| Files compared | 305 |
| Semantically changed files | 261 |
| Model-independent files | 40 |
| Changed model-independent files | 0 |
| Invariant violations | 0 |

All observed changes were confined to direct-prior, replay-source or
rating-dependent outputs. Schemas, record counts and stable identity domains
were preserved. An initial apparent violation in `highest_rating.csv` was a
comparison defect: peak date and peak chii had incorrectly been treated as
parts of a rikishi's identity. The comparison now uses `rikishi_id`; the
corrected full run has no violations.

This establishes that the candidate prior propagates through the expected
site-data path without leaking into model-independent products.

## Sekitori effects

The focused report compared each sekitori's post-bout rating throughout the
replay. It retained 129,870 Makuuchi observations and 87,489 Juryo
observations, or 217,359 combined.

| Population | Mean change | Mean absolute change | RMS | 95th percentile absolute | Maximum absolute |
|---|---:|---:|---:|---:|---:|
| Makuuchi | +30.07 | 30.07 | 30.89 | 42.74 | 45.45 |
| Juryo | +22.10 | 22.10 | 22.96 | 35.03 | 44.16 |
| All sekitori | +26.86 | 26.86 | 27.97 | 41.41 | 45.45 |

Every sekitori observation moved upwards. None changed by 50 rating points or
more. The largest changes occur near the 1989 initialization and decline over
time:

| Year | Mean change | Minimum | Maximum |
|---|---:|---:|---:|
| 1989 | +41.30 | +17.16 | +45.45 |
| 2000 | +29.59 | +12.30 | +39.83 |
| 2010 | +25.75 | +11.50 | +34.74 |
| 2020 | +21.90 | +11.91 | +31.40 |
| 2026 | +18.28 | +8.43 | +23.53 |

The common direction and gradual attenuation show that the dominant effect is
an upward relocation of the absolute rating scale inherited from the changed
prior. It is not evidence of widespread competitive reordering. Absolute Elo
levels are published values and therefore still matter to presentation, but
predictions depend on differences between competitors.

A supplementary calculation matched both competitors in 107,395
sekitori-versus-sekitori bouts and compared the change in their rating gap:

| Measure | Absolute change in rating gap |
|---|---:|
| Mean | 2.66 |
| RMS | 3.57 |
| 90th percentile | 5.95 |
| 95th percentile | 7.46 |
| 99th percentile | 10.50 |
| Maximum | 20.83 |

This is the more relevant indication of competitive effect. Even the maximum
gap change implies only about a three-percentage-point probability change in
the most sensitive, approximately even matchup. Most effects are much
smaller. This supplementary result was derived from the retained
`sekitori_rating_differences.csv`; it is not claimed as an exhaustive
predictive re-evaluation.

## Highest-rating records

All 4,558 career-peak rating values changed. Their mean absolute change was
9.04 points and the maximum was 44.92 points, for Hokutoumi. Hakuho remained
the highest-rated rikishi: his recorded peak changed from 3035.344 to
3070.311, at Y1e on 2011/07/10 in both bundles.

The ordering changed more visibly than the ratings. Some 4,380 rikishi moved
position, with a mean absolute movement of 27.54 places and a maximum of 384.
The largest movement was Kiyosuruga, from position 3471 to 3855, following a
29.956-point reduction in his recorded peak. Such large positional movements
are concentrated among closely spaced ratings in the lower reaches of the
table; they are not comparable to a 384-point rating change.

## Chii comparison

The generic comparison subtracts `chii_ordinal` codes. Those codes are ordered
but are not an interval scale: a difference of a given numerical size does not
represent a stable number of banzuke places. Mean, RMS and similar arithmetic
summaries of the raw codes therefore have no general quantitative
interpretation.

The subtraction is nevertheless useful as a diagnostic. Large code changes
draw attention to cases where the observation selected as a rikishi's career
peak moves across a division boundary. In `highest_rating.csv`, 114 rikishi
acquired a different peak chii; 43 crossed a division boundary. Most crossings
were in the lower divisions. Four moved from a Juryo peak to a Makuuchi peak,
and one moved from a Makushita peak to a Juryo peak. These are changes in which
historical observation is selected as the rating peak, not changes to the
historical banzuke itself.

Spot inspection found the expected pattern: many numerically large ordinal
changes are movements between the top of one division and the bottom of the
next. No downstream problem presently justifies a larger investigation.

If rank changes later become material, the comparison should be replaced or
supplemented by a principled chii comparator. At minimum it should report
division crossings separately and compare rank number, side and special rank
status within a division, rather than treating the decimal encoding as a
metric. The current raw ordinal difference remains a warning signal, not a
measurement of distance.

## Limitations and next step

This tranche demonstrates controlled propagation through the complete
site-data bundle and finds small competitive effects among sekitori. It does
not yet provide the visual and behavioural inspection of an assembled static
site anticipated by the original proposal.

The next step is therefore to generate a complete non-deployed web site using
P1-WL and inspect the affected pages. That work should pay particular
attention to absolute rating labels and scales, rating-based ordering, career
peak rank/date selection, cross-division cases, and current or future
torikumi. A principled chii-distance analysis is deferred unless that inspection
or another downstream test exposes a concrete problem.
