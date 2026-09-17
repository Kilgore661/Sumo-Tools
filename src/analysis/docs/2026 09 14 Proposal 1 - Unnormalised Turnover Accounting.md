# Proposal 1: Unnormalised turnover accounting

## Status and question

**Implemented 15 September 2026:** see [Experiment 1](../inflation/expt1/README.md)
and its results. The proposal below is the original requirements record. Its
return-to-P1 and separate-episode language is superseded: temporary gaps
preserve ratings, returns restore them without allocation, and donor deficits
are measured only at final observed departures against the one initial
allocation. The implementation uses the live store only.


Initial experiment proposal, 14 September 2026. No replay or chart has yet
been produced. This specifies the first empirical challenge following the
[donor-inflation argument and post-proof discussion](2026%2009%2014%20Donor%20Replacement%20and%20Rating%20Inflation%20-%20Argument.md).

For every transition in post-1988 sumo history, how many rating points enter
and leave with population membership, what is the net change, and how does
the mean evolve when mean preservation is disabled? In particular, does the
historical record support the premise of a net contribution from departing
point donors after countervailing departures are included?

The companion [Proposal 2](2026%2009%2014%20Proposal%202%20-%20Rating%20Updates%20by%20Opponent%20Rank.md)
uses the same experimental run to examine bout updates by opponent rank.

## Shared replay contract

- Start at January 1989 and use the available post-1988 History through the
  selected final represented basho. Record actual coverage rather than assuming
  a fixed number of basho or deriving the endpoint from a ZIP filename.
- Load one fixed P1 using the accepted Elo-89 prior loader and fallback rules;
  do not recompute its fixed point. The current producer defaults to
  `files/output/analysis/equelo_bkp1/prior.csv`.
- Preserve q=400, the production divisional-K policy and configuration, the
  eligible-bout selector, bout ordering, and entry/return policy. The current
  K configuration default is `files/input/elo_fide.json`; record the resolved
  values and hash rather than relying on the filename as the specification.
- Disable both pre-basho and post-basho common mean-restoring shifts. The
  user's phrase "pre/post-bout normalisation" refers here to these basho-boundary
  operations. Individual Elo bout updates still apply.
- Retaining membership while missing bouts retains the rating. Leaving the
  represented population removes it; subsequent return reinitialises from P1,
  as in Elo-89. Retain separate episodes for accounting across such returns.
- Read History from the live store by default, with an explicit History ZIP
  alternative under the repository's existing convention. Enforce the interval
  after loading. Pin and record the History fingerprint, P1, K, code version,
  settings and output schema in a shared run manifest.

This requires a fresh replay. Subtracting shifts from the saved normalised
production ratings would leave different subsequent bout probabilities and
updates unaccounted for. Keep experimental outputs and model identity separate
from production Elo-89 and the published site. Suggested package and output
root: `src.analysis.inflation.expt1` and `files/output/analysis/inflation/expt1`.
These locations were reserved during the repository reorganisation; Experiment
1 is not yet implemented. Experiment 2 lives alongside it in
`src.analysis.inflation.expt2`, with its own run, views and archives under
`files/output/analysis/inflation/expt2`.

The current replay is in `src/analysis/elo89/replay.py`. It defines the active
population as the union of banzuke members and eligible-bout participants.
Preserve that rule for the controlled experiment. Audit and expose any
participants not on the banzuke, so a chart labelled "banzuke turnover" does
not silently include a different population. Store literal banzuke membership
and its transitions alongside replay membership; if they differ, report both
explicitly and use replay membership for the rating-mass reconciliation.
Missing chii receive the existing policy treatment and an explicit unknown
group in summaries, not silent exclusion.

## Transition definitions

For transition from represented basho t-1 to t, use the previous basho-end
ratings and the current pre-basho ratings after membership changes and P1
initialisation, before any current bouts. Survivors' ratings are unchanged at
this boundary even when their chii changes.

Let A be the previous active set, B the new active set, J=B-A the joins and
L=A-B the departures. Record:

```text
mass_before       = sum(previous end ratings over A)
points_added      = sum(P1 assignments to J)
points_removed    = sum(previous end ratings of L)
transition_delta  = points_added - points_removed
mass_start        = mass_before + transition_delta
count_start       = count_before + join_count - departure_count
mean_before       = mass_before / count_before
mean_start        = mass_start / count_start
mean_delta        = mean_start - mean_before
```

Undefined means for an empty population are missing, not zero. Report real
calendar dates and flag gaps between represented basho; do not invent unseen
intermediate transitions. The first basho establishes the initial stock and
has no prior transition. Do not count its entire initial population as a
turnover spike. Do not infer departures after the last observed basho.

Classify joins as first represented appearances or returns. These are not
independently verified career debuts. Departures are disappearance from the
represented set, not automatically permanent retirement. Use the previous
chii for departure grouping and the current chii for joins. Identity is rikid,
not shikona.

## Donor balance, distinct from gross membership flow

The first requested chart shows gross points entering and leaving. With
variable headcount, its delta alone does not establish donor inflation.
For each departing episode also retain:

```text
episode_deficit = episode_entry_rating - departure_rating
donor_points = max(episode_deficit, 0)
above_entry_points_removed = max(-episode_deficit, 0)
net_departing_donation = sum(episode_deficit over departures)
```

These quantities describe whether departing wrestlers left below or above
their own assigned entry values. They are signed episode accounts, not claims
about why a wrestler left or a pure causal contribution to another rating.
With unequal K, an individual's loss need not equal opponents' gains.

Initial January 1989 occupants have observation-start allocations, not known
career-entry ratings. Mark their episodes as left-censored, and show the donor
summary both with all observed episodes and restricted to episodes beginning
after the initial basho. Continuing final episodes are not completed departures.

Keep the following exact identity visible:

```text
transition_delta
  = net_departing_donation
  + sum(current join allocations) - sum(departing episodes' entry allocations)
```

Thus incoming/outgoing allocation differences, headcount changes and donor
deficits are not silently conflated.

## Bout mass and full reconciliation

Keep both actual participant deltas for every eligible bout. Record each
basho's bout mass as sum(delta_a + delta_b). Under unequal K it can be nonzero.

```text
mass_end(t) = mass_end(t-1) + transition_delta(t) + bout_mass(t)
```

For the first basho use the initial allocated stock. Report cumulative
membership flow and cumulative bout mass separately. This measures the K
effect alongside turnover without assuming in advance that it is large or small.

## Interactive HTML deliverables

Use responsive HTML with Plotly loaded from an explicitly versioned CDN.
Embed the chart data so opening the HTML requires no local server; the Plotly
library requires network access. Provide a clear load-error message if the
CDN cannot be reached. Use Plotly.react for filters and responsive resizing.

1. **Transition points chart:** date on the x-axis; points added above zero,
   points removed below zero, and a line for signed transition delta. Hover
   shows unambiguous raw amounts, counts, first appearances, returns and both
   endpoint dates. Provide a cumulative view of added, removed and net amounts.
2. **Mean chart:** pre-basho population mean as the primary series, with an
   optional basho-end series. Hover shows headcount, mass, membership mean
   change and within-basho mean change. A companion headcount panel avoids
   hiding population-size changes. Initial mean may appear as a labelled
   reference, not an enforced target.
3. **Donor diagnostic panel:** donor points, above-entry points removed and
   their net by transition, with the initial-cohort inclusion toggle. This
   makes the premise of the proof inspectable independently of gross flow.

All panels share a date-range control and raw/cumulative modes where meaningful.
Show all history by default, no automatic burn-in or smoothing. Any later
smoothing must remain optional with raw observations visible. Changing a date
filter filters the completed run, not its replay initialisation. Label whether
cumulative totals start at the selected range or at the history origin; default
to the selected range. Group filtering of the mean is optional and must not
mistake sums of group means for the global mean.

## Outputs and checks

Retain the shared replay bout ledger and start/end snapshots, plus transition
summary, individual join/departure ledger, episode ledger, basho mass summary,
manifest, CSV chart data, HTML and a concise findings note.

Verify independently that membership/count identities, mass equations, episode
decompositions and chart aggregates reconcile within a declared floating-point
tolerance. Check returns, rank-changing survivors, initial stock, last-basho
censoring, unequal-K bouts and missing-chii cases. A small controlled comparison
with the accepted replay must show that the intended policy difference is only
the removal of its boundary shifts. Verify the HTML date controls, toggles,
hover labels, zero handling and resize behaviour against the saved data.

The result is a measured historical account under a fixed model. Neither a
positive mass flow nor a rising global mean alone proves inflation specifically
at upper chii. Interpretation should retain the post-proof distinctions and
report countervailing evidence without a preselected pass/fail threshold.
