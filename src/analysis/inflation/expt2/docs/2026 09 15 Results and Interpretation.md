# Experiment 2: results and interpretation so far

Recorded 15 September 2026. This note concerns the completed gap-preserving
individual-provenance run, not the superseded first-stint exclusion run.

## Assessment against the original question

The underlying question was whether the surplus left by departing point
donors reaches upper-rank ratings. Experiment 2 now makes the circulation
of individual-origin points inspectable and shows a suggestive rank pattern
in the two-way provenance balances. It does not yet quantify how much donor
departure has inflated upper-rank ratings.

The accounting is coherent and manageable. Its interpretation remains narrower
than the causal question: points originating with someone who eventually
becomes a donor are not automatically that person's net donated surplus.

## Run and evidence base

- Source: live store, filtered to January 1989 through July 2026, matching the
  earlier run's interval. September data available in the store were not added
  to this comparison.
- 224 basho, 4,551 individual origins and all 579,426 eligible binary bouts.
  The selector excluded 3,022 fusen results; no bouts were excluded for gaps.
- Fixed P1, q=400 and the existing divisional-K policy. Both pre- and
  post-basho mean-preservation operations are disabled.
- One initial allocation per individual. Ratings and provenance remain
  unchanged while absent and resume on return, including Sokokurai.
- 435 completed gaps across 363 individuals. Temporary gaps do not count as
  donor departures. A final departure means the last disappearance with no
  later representation in the selected history, not independently verified
  retirement. Historical gap classification uses later returns retrospectively.
- The independent audit verified 588,809 events, scalar observations and saved
  matrix balances. Scalar discrepancies were below 1e-12 points and matrix
  row/column discrepancies below 3e-11. Seven tests passed.

The run took about 31 seconds. The matrix is about 166 MB and the event and
observation database about 96 MB. There is no need to aggregate individuals
before recording their histories to make this dataset manageable.

Source artifacts are the
[run manifest](../../../../../files/output/analysis/inflation/expt2/run/manifest.json),
`record.sqlite`, `holdings.npy` and `balances.npz` in the same directory.
The manifest records input hashes, the represented-history fingerprint and
output hashes. The History fingerprint, P1 and K inputs match the earlier
first-stint run. That earlier run's 56,995 excluded bouts have all been restored.

After relocation to `src.analysis.inflation.expt2`, a fresh live-store replay
over the same interval reproduced all four raw output files byte for byte
against the archived gap-preserving run. The input hashes and represented
history fingerprint also match. The independent audit and all seven tests
passed, and the Onosato, Hoshoryu and Hakuho inspection views were regenerated
under `files/output/analysis/inflation/expt2/views`. The relocation therefore
leaves the numerical results and their interpretation unchanged.

## What the quantities mean

Write H[i,j] for the points currently held by i that originated in j's initial
allocation. The loser transfers the proportions of their pre-bout holdings;
the winner's actual gain and loser's actual loss scale those proportions
separately when K differs. Departed rows remain frozen as a record of what
left the represented population.

At a selected endpoint, let D be the individuals whose final departure has
already occurred and whose departure rating was below their observed initial
allocation. For an active subject i, report:

```text
donor-origin held       = sum over j in D of H[i,j]
subject-origin removed  = sum over j in D of H[j,i]
net provenance balance  = donor-origin held - subject-origin removed
```

The first term can reach i through many intermediaries. The second term
measures i-origin points held by donors when they departed. It is not the
total of i's direct historical losses to those people. Negative net balances
are possible even though all holdings are nonnegative.

The percentage below is donor-origin held divided by the subject's current
rating. It is a composition percentage under the declared allocation convention,
not a percentage of rating change or an origin-independent measure of inflation.
Initial January 1989 allocations are observation-start values, not necessarily
career-entry values.

## Individual examples

| Rikishi | Endpoint | Current rating | Donor-origin held | Share of rating | Subject-origin removed by donors | Net provenance balance |
|---|---|---:|---:|---:|---:|---:|
| Onosato | July 2026 end | 2487.18 | 174.68 | 7.02% | 0.41 | 174.27 |
| Hoshoryu | July 2026 end | 2491.10 | 393.92 | 15.81% | 5.26 | 388.66 |
| Hakuho | September 2021 end | 2699.61 | 701.95 | 26.00% | 138.12 | 563.83 |

Net figures are calculated before rounding. Hakuho's example uses his last
represented basho; these are not three observations at the same historical
endpoint and should not be treated as a controlled career comparison.

For Onosato, 129.85 of the 174.68 donor-origin points come from donors whose
last recorded rank was Jonidan or Jonokuchi. This identifies a connection
between lower-rank donors and an upper-rank holder under the proportional
accounting rule. It does not mean that all those points were transferred while
the donors occupied those ranks, or that all 129.85 points represent inflation.

The accounting therefore succeeds in representing the indirect connections
that a direct-opponent wins/losses table would miss.

## Distribution across the July 2026 banzuke

For each group of current holders, sum the two terms above and divide by the
number of holders. Sanyaku includes Yokozuna, Ozeki, Sekiwake and Komusubi.
Grouping uses the subject's July 2026 chii; donor status is evaluated at that
endpoint using the selected history's final-departure classification.

| Current rank group | Rikishi | Mean donor-origin held | Mean net provenance balance |
|---|---:|---:|---:|
| Sanyaku | 10 | 345.86 | +333.40 |
| Maegashira | 32 | 333.55 | +290.92 |
| Juryo | 28 | 320.87 | +236.27 |
| Makushita | 120 | 261.93 | +172.71 |
| Sandanme | 161 | 330.89 | +95.22 |
| Jonidan | 198 | 261.26 | -54.98 |
| Jonokuchi | 40 | 157.58 | -143.02 |

The net balance increases towards the upper groups in this snapshot. Gross
donor-origin holdings do not have the same monotonic ordering: Sandanme, for
example, has substantial holdings before the reverse direction is subtracted.

This is consistent with the direction of movement envisaged in the donor
argument. It does not establish growth through time, preferential transmission
independent of career composition, or a causal effect size. Career length,
initial allocations, entry cohorts and competitive success may contribute to
the observed ordering. This table has not controlled for them.

## Why donor-origin holdings are not net donation

Suppose a wrestler enters with 1000 points and leaves with 990. Their observed
entry-to-exit deficit is ten points. During that career, they could have
distributed hundreds of their original points and acquired hundreds from
other origins. The holdings matrix follows those exchanges. It does not
identify ten special inflation points.

Furthermore, a wrestler who ultimately leaves above their initial allocation
can still leave many of their own-origin points circulating elsewhere.
Onosato holds 381.51 points originating with departed non-donors, compared with
174.68 from departed donors. The corresponding subject-origin amount removed
by non-donors is 17.87 points. Substantial positive provenance balances therefore
occur even with people who were not net donors by their entry-to-exit accounts.

This does not invalidate the accounting. It shows that assigning an origin to
the donor/non-donor category does not isolate the turnover surplus which
motivated the experiment. Unequal K also means original allocation is not
conserved exactly by origin; its per-origin creation/removal is separately
reconciled in the saved balances.

Neither donor-origin held nor net provenance balance should be subtracted from
a rating and described as the rating that would have existed without inflation.
A different membership or rating policy could change later probabilities and
bout updates, which this accounting does not recalculate.

## Conclusions and unresolved connection to Experiment 1

We have established that individual-level provenance is practical, that the
bookkeeping reconciles, and that donor-origin points occur in upper-rank
holdings through indirect as well as direct connections. The July 2026 net
balance table provides a concrete pattern worth understanding.

What remains unresolved is the connection between these holdings and the
net turnover surplus that Experiment 1 was designed to measure. The provenance
results do not yet establish the size or time course of upper-chii inflation,
or whether mean preservation is an appropriate response. The accepted
conditional donor-inflation argument is not being reopened; applicability and
measurement in historical sumo remain separate questions.

No new counterfactual replay, attribution rule or additional experiment is
specified by this note. It records where the current investigation has reached.

## Reproduction and inspection

The [README](../README.md) gives generator, audit and inspection commands.
The [interactive explorer](../../../../../files/output/analysis/inflation/expt2/views/explorer.html)
and adjacent `profiles.json` and CSV files contain the three individual
examples and alternative aggregations.

To reproduce the July 2026 rank table from the saved record, select
`observations` with `date='2026/07'` and `endpoint='end'`, grouping by
`rank_group`. Obtain donor indices from `people` where
`departure_rating < initial` and `departure_event` is no later than the
endpoint. The corresponding submatrices of `holdings.npy` supply H[i,j] and
H[j,i]. Sum each direction independently, subtract and divide by the number
of current holders in the group. This is a read-only calculation on the
completed run, not another historical simulation.
