# Individual rating provenance

**Repository reorganisation:** this package is now
`src.analysis.inflation.expt2`, alongside the reserved Experiment 1 package.
The experiment output root is `files/output/analysis/inflation/expt2`:
`run/` contains the replay, `views/` the inspector outputs, and `archive/`
the previous runs and views. The former gap-preserving run is retained under
`archive/gap_preserving_before_move`; the fresh rerun uses the new paths.

Experimental, fixed-P1, post-1988 Elo with pre/post-basho mean preservation
disabled. This implements the individual-level holdings model developed after
the original Experiment 2 proposal. It is an accounting convention for current
holdings, not an estimate of what ratings would have been without a person.

See [Results and interpretation so far](docs/2026%2009%2015%20Results%20and%20Interpretation.md)
for the individual examples, July 2026 rank-group balances and what they do
and do not establish about donor-driven inflation.

**Updated 15 September 2026:** gaps now preserve ratings and provenance and
all returning appearances and eligible bouts are included. The former
first-stint exclusion model is superseded. Its saved run remains available
at `files/output/analysis/inflation/expt2/archive/first_stint`; the new default is
`files/output/analysis/inflation/expt2/run`.

## Run and inspect separately

From the repository root:

```powershell
python -m src.analysis.inflation.expt2 --end 2026/07
python -m src.analysis.inflation.expt2.audit
python -m src.analysis.inflation.expt2.inspect `
  --rikishi Onosato --rikishi Hoshoryu --rikishi Hakuho `
  --output-root files/output/analysis/inflation/expt2/views
```

The generator connects to the live store through the existing analysis loader
and `src.infra.live_store.api.get_history`. There is no automatic ZIP fallback.
The full run recorded below used the live store. The optional explicit
`--history-zip` input is for intentionally selected offline work; the author
required live-store access before conducting the full historical run.

`--end YYYY/MM` optionally limits the loaded History; otherwise the latest
represented date is used. The post-1988 filter is enforced after loading even
when the live store contains earlier years. P1 and K use the existing Elo-89
loaders and defaults; their input hashes and the represented History fingerprint
are saved. Production outputs and prior construction are unchanged.

Inspection needs only the saved record. Choose a rikid or an unambiguous current
or former name. A repeated `--rikishi` builds several profiles in one explorer.
Use `--date 2026/07 --endpoint start` for a particular pre-basho endpoint;
`end` is the default. Without a date, each subject uses its last represented
basho, which provides the latest endpoint for current wrestlers and the last
observed endpoint for departed wrestlers. Disappearance is not independently
verified retirement. All displays use two decimal places; calculations retain
double precision.

## Exact accounting

One origin per individual rikid. At first entry, assign P1 entirely to that
person's own-origin component. Let H[i,j] denote points held by i originating
with j. Row sums equal current scalar ratings; components are nonnegative.

If loser l has pre-bout rating R, loses L and winner w gains G:

```text
proportion[j] = H[l,j] / R
H[w,j] += G * proportion[j]
H[l,j] *= 1 - L/R
```

The two values G and L are the actual updates under the unchanged divisional
K policy. Neither side is forced to equal the other. A separate per-origin
balance accounts for points created or removed by this asymmetry, so columns
can also be reconciled. No tiny components are discarded. Nonpositive scalar
ratings or losses exhausting a rating are rejected because the partition
interpretation would fail in that domain; neither occurred in the recorded run.

Departed holders' rows freeze as a record of what left the active population.
Their origin columns continue to circulate among active holders. The inspector
reports H[i,j] and H[j,i] separately and subtracts them only for the derived
net provenance balance. Its diagonal/self net is zero. It distinguishes
subject-origin holdings with active counterparts from those frozen on departure.
No signed negative holdings or retroactive removal of bouts is used.

## Gap policy

Retain one identity and one P1 allocation per rikishi. At a disappearance,
archive the rating and full provenance row unchanged. On reappearance,
reactivate that same row without initialisation, decay, penalty or a new
allocation. Include every eligible bout, including all bouts after gaps.
Sokokurai follows exactly the same rule. This implements no-new-evidence,
no-update; it does not assert that actual ability remained unchanged.

The source History is never edited.
Membership follows the Elo-89 union of banzuke members and eligible-bout
participants; non-banzuke participants are counted explicitly.

For descriptive donor classification, use the full loaded interval to
distinguish temporary gaps from final observed disappearances. A temporary
gap never counts as a donor departure. A final disappearance means no later
appearance in that interval, not verified retirement. Anyone represented at
the last basho is right-censored; no extra departure is invented beyond it.
Historical gap classification is retrospective and may use a later return;
the rating updates themselves depend only on bouts and carried state.

Active-population mass excludes absent rows while they are away, but their
holdings remain in the full matrix. The transition ledger separates archived
mass leaving/returning at gaps from genuinely new P1 allocations and final
departure deficits. A return restores mass to the represented population;
it does not create a fresh initial allocation.

The earlier 363 affected IDs were counted by first gap, not by actual
retirement. Inspection found 362 last held Jonokuchi ranks and one was
Sokokurai at M16e. The previous exclusion removed 56,995 eligible bouts;
none are excluded for gaps under the new policy. Experiment 1's original
proposal is not silently redefined by this Experiment 2 change.

## Saved full record and scale

The 15 September rerun used the live store, restricted to the same January
1989–July 2026 interval for comparison (the live store also contained September
2026). Its History fingerprint, P1 hash and K hash match the earlier run.
It processed **all 579,426 eligible bouts**, with 435 completed gaps across
363 individuals, zero excluded appearances/bouts and exactly 4,551 initial
allocations. Generation took about 31 seconds. The independent audit checked
588,809 events and all snapshots; scalar error stayed below 1e-12 points and
matrix row/column errors below 3e-11. All seven tests passed.

Sokokurai's gap is May 2011 to July 2013 in the represented history. His
2145.3192947279754 rating at the prior endpoint is exactly his returning
pre-basho rating. He receives no new initial allocation; the same provenance
row is reactivated.

Updated profiles are in
`files/output/analysis/inflation/expt2/views/explorer.html`:

| Subject | Endpoint | Rating | Own-origin held | Departed donor-origin held | Subject-origin removed by donors |
|---|---|---:|---:|---:|---:|
| Onosato | July 2026 end | 2487.18 | 1537.43 | 174.68 | 0.41 |
| Hoshoryu | July 2026 end | 2491.10 | 645.47 | 393.92 | 5.26 |
| Hakuho | September 2021 end | 2699.61 | 511.23 | 701.95 | 138.12 |

Donor figures use final observed disappearances only and remain provenance
balances, not causal inflation estimates.

- `record.sqlite`: people and entry allocations; every retained bout with
  pre-bout ratings, probability, outcome, actual K and both deltas; entry/exit
  events; pre/post-basho scalar observations and rank/name metadata; all gap
  start/end events; per-basho eligible/included counts. Legacy exclusion
  tables are retained for schema continuity but are empty/zero in this model.
- `holdings.npy`: final double-precision matrix, including frozen departed rows.
- `balances.npz`: scalar ratings, initial allocations, active flags and
  per-origin created/removed mass.
- `transitions.csv`: population counts, allocations added/removed, deficit
  balance at final departure, means and bout mass. Gap mass in/out and new
  allocations are distinct. Initial stock is flagged.
- `manifest.json`: settings, input/code fingerprints, sizes, timings, row and
  column reconciliation errors, and output hashes.

Instead of storing a dense matrix after every bout, the event ledger retains
the information needed to reconstruct it at any event. The inspection module
reconstructs historical endpoints from saved transfers, without loading History
or recalculating the Elo model. Final endpoint inspection memory-maps the
matrix. No future allocations appear in an earlier profile. Whether an
absence is a gap or final disappearance is explicitly retrospective.

The **superseded first-stint** live-store run completed on 14 September 2026: 224 basho from January 1989
to July 2026, 4,551 origins, 522,431 retained bouts and 530,989 events. Generation
took approximately 35 seconds in the bundled Python runtime. The raw holdings
matrix is 165.7 MB and SQLite record 88.6 MB; the complete core record is about
255 MB. Individual-level accounting is manageable at this scale.

## Post-run views

The explorer embeds selected profiles and loads Plotly 2.35.2 from its CDN.
It opens as a standalone HTML file, with no server needed. Charts require
network access to that library; tables and filters remain available if it
fails. Data can be regrouped without another historical replay.

Views include individual origins, departure/donor status, entry rank group and
rank group last observed by the selected endpoint. Filters include name/rikid,
status, metric and top-N. All remaining values are explicitly summed as Other.
Full individual rows and all three grouped summaries are exported to CSV.
Temporary gaps have a separate status and their holdings are not included
in points removed by final departures. Initial-cohort allocations are observed January 1989 allocations, not actual
career-entry ratings; entry date/chii remain available in the raw profile.

Percentages describe points currently held divided by the full selected
rating, even after filtering. Counterpart amounts and net provenance balances
are points, not fractions of a net-change denominator. Origins classified as
departed donors have departure rating below their own observed allocation;
that classification and its deficit are kept separate from the origin mass
still held by others. No causal inflation claim follows from that label alone.

Historical first-stint inspection profiles (superseded; retained for comparison):

| Subject | Endpoint | Rating | Own-origin held | Departed donor-origin held | Subject-origin removed by donors |
|---|---|---:|---:|---:|---:|
| Onosato | July 2026 end | 2455.45 | 1530.93 | 166.13 | 0.43 |
| Hoshoryu | July 2026 end | 2459.44 | 645.70 | 381.07 | 5.70 |
| Hakuho | September 2021 end | 2674.33 | 524.76 | 709.19 | 147.91 |

Onosato has positive holdings from 4,223 origins; 3,451 individually contribute
at least 0.01 points. This supports retaining detail first and experimenting
with aggregation afterwards. These are accounting results from the declared
first-stint variant, not published production ratings or measured causal
inflation amounts.

## Verification

```powershell
python -m unittest discover -s tests -p test_inflation_expt2.py -v
python -m src.analysis.inflation.expt2.audit
```

Tests cover the four-person worked example, indirect transmission, frozen
departures, unequal-K scaling, the actual numerical three-bout example,
multiple gap returns without reset, invalid partition domains, live-store defaults,
historical reconstruction, temporary-gap versus final-departure classification
and profile aggregation.
The independent audit recalculates scalar Elo directly from the saved events,
checks every scalar observation, verifies output hashes and reconciles final
rows and columns. The generator also reconciles every basho boundary. The
recorded generation's maximum row and column residuals were approximately
9.1e-12 and 2.3e-11 points respectively.
