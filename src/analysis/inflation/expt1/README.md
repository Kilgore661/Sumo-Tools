# Experiment 1: turnover accounting

Implemented 15 September 2026. The requirements originated in
[Proposal 1: Unnormalised turnover accounting](../../docs/2026%2009%2014%20Proposal%201%20-%20Unnormalised%20Turnover%20Accounting.md).

Run from the repository root with the live store available:

```powershell
python -m src.analysis.inflation.expt1 --end 2026/07
```

The default endpoint matches Experiment 2. `--prior`, `--k-config` and
`--output-root` allow explicit overrides. There is no ZIP fallback. An output
root must be empty; use a new root for a subsequent immutable run.

Outputs live under `files/output/analysis/inflation/expt1`:

- `run/`: shared Experiment 2 engine's complete fresh replay, bout ledger,
  endpoint observations, individual allocations, gap records and holdings.
- `views/transitions.csv`: independently derived transition and basho mass
  accounts, counts, means and final-departure donor diagnostics.
- `views/membership_events.csv`: individual first appearances, gap starts,
  returns and final departures, with event-time chii and initial allocations.
- `views/banzuke_membership.csv`: literal membership and its joins/departures,
  separately identifying replay participation.
- `views/people.csv`: one allocation and observed career record per individual.
- `views/charts.html`: reactive Plotly CDN charts with embedded data; open
  directly without a server. Network access is required for Plotly itself.
- `views/summary.json` and root `manifest.json`: totals, input/code/output
  hashes and independent audit results.

The replay deliberately reuses Experiment 2's engine rather than introducing
a second Elo implementation. The report derives its accounts from individual
events and observations, not from the engine's transition totals.

## Current definitions

One P1 allocation is made per individual. Temporary absences preserve the
rating and returns restore it unchanged, with no new allocation. The mean
covers the represented population: banzuke members plus eligible-bout
participants. Temporarily absent individuals are excluded from this mean,
although their saved ratings persist. Literal banzuke membership is also saved;
the two populations coincide throughout the completed run.

Gross inflows include new allocations and returning saved ratings. Gross
outflows include temporary gaps and final observed departures. Donor deficits
apply only to final departures and compare departure rating to the individual's
original allocation. A final departure is inferred using the selected history,
not independently verified retirement. Extending the endpoint can revise this
classification. Nothing is inferred beyond the final basho.

The January 1989 stock is excluded from flow totals and charts. Its members'
allocations are observation-start values; the donor panel can exclude this
cohort. Cumulative chart totals restart at the selected range, while the replay
and retrospective departure classification remain fixed.

The report checks these identities within 1e-6 points:

```text
start mass = previous end mass + added - removed
end mass = start mass + sum(actual bout participant deltas)
added - removed = net final-departure donation
                + new allocations - final departures' initial allocations
                + gap returns - gap outflows
```

Counts and survivor ratings also reconcile. The independent replay audit
checks every scalar event and endpoint observation. Tests include a controlled
gap/return/final-departure history and the shared engine's numerical cases.

See [Results](Results.md) for the completed live-store run and its interpretation.
