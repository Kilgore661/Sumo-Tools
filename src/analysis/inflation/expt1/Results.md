# Experiment 1 results — 15 September 2026

The live-store replay covers 224 basho from January 1989 through July 2026,
with all 579,426 eligible bouts. It uses fixed P1, q=400, existing divisional K
and no mean preservation. Returns retain saved ratings. September data were
not added, keeping the comparison with Experiment 2 fixed.

| Quantity | Points |
|---|---:|
| Gross inflow after initial stock | 5,827,894.80 |
| Gross outflow | 6,105,043.71 |
| Net membership flow | -277,148.91 |
| Final-departure donor deficits | 328,138.71 |
| Above-entry departure surpluses | 265,260.70 |
| Net final-departure donation | 62,878.01 |
| Net donation excluding January 1989 cohort | 44,923.20 |
| Total bout mass change | 2,507.03 |

There are 3,962 final observed departures. The 435 completed temporary gaps
remove and restore exactly the same aggregate 552,784.53 points; they produce
no net allocation over this interval. They remain visible in individual
transition flows.

The pre-basho mean is 1,569.70 in January 1989 and 1,529.80 in July 2026;
July's end mean is 1,529.81. Headcount falls from 749 to 589. These endpoint
comparisons are descriptive, not an estimated time trend or burn-in claim.

The donor balance supports the premise that below-entry departures outweigh
above-entry departures in this replay, including when the initial cohort is
excluded. It does not imply positive gross membership flow: new allocations,
departing allocations and changing headcount matter too. Nor does it imply a
rising global mean, which is not observed in this endpoint comparison.
The result does not locate the net surplus at upper chii or quantify inflation
caused by it. Experiment 2's provenance analysis addresses circulation under
its own accounting convention.

The distinction between an individual's deficit and points received by
opponents remains relevant under unequal K. The measured total bout mass
change is reported separately, without assuming it vanishes.

## Verification and artifacts

The maximum transition reconciliation discrepancy is 1.17e-9 points, below
the 1e-6 tolerance. Literal banzuke membership and replay membership coincide
throughout. The shared independent audit passes; eight tests pass across the
two experiments. Date filtering, cumulative mode, the basho-end mean toggle
and the initial-cohort toggle were exercised in the browser.

- [Interactive charts](../../../../files/output/analysis/inflation/expt1/views/charts.html)
- [Summary](../../../../files/output/analysis/inflation/expt1/views/summary.json)
- [Manifest](../../../../files/output/analysis/inflation/expt1/manifest.json)

The source README describes the complete saved ledgers and reproducible command.
