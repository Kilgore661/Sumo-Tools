# Inflation investigation

The two experiments belong to one investigation of population turnover,
rating-point circulation and possible inflation in upper-chii ratings.

- [Experiment 1](expt1/README.md): turnover and population-mean accounting;
  implemented, with transition charts and donor diagnostics.
- [Experiment 2](expt2/README.md): individual provenance, proportional transfers,
  persistent ratings across gaps, and post-run inspection. Implemented.

## How the investigation arose

Mean preservation was introduced to address suspected Elo inflation. The
intuition was that many newcomers leave with fewer points than they received
on entry: their opponents retain the points they lost, while replacement
entrants receive fresh allocations. Departures above their entry ratings act
in the opposite direction. The concern was that the balance of these effects
raises upper-chii ratings over time without a corresponding rise in ability.

On reconsideration, neither the meaning of inflation nor the evidence for it
had been established sufficiently clearly to justify correcting it. Mean
preservation also caused problems in the model's results. The investigation
therefore asks whether it is needed, starting with a fixed P1 and replaying
post-1988 history without pre- or post-basho mean restoration.

This question is separate from the choices used to derive initial ratings.
The fixed-point construction was a pragmatic way to obtain plausible starting
values despite incomplete pre-1989 results. Fixing those values, normalising
within that construction, and keeping its chii values tied to ratings are
distinct from repeatedly preserving the population mean during the replay.
These experiments hold P1 fixed rather than reopening its derivation.

The discussion first considered an artificial population with fixed true
strengths, random pairings, common K and replacement of point donors by new
occupants receiving P1. The agreed
[donor-replacement argument and post-proof discussion](../docs/2026%2009%2014%20Donor%20Replacement%20and%20Rating%20Inflation%20-%20Argument.md)
explain why, under the stated redistribution assumptions, repeated donor
replacement raises relaxed upper-rank rating levels. This is a conditional
argument, not evidence that the mechanism explains historical sumo. Its
applicability depends on actual turnover, countervailing departures, changing
ability, opponent selection, divisional K and the time required for ratings
to adjust. For comparisons across time, the working hypothesis is that a
given chii has a fixed meaning in strength; rising ratings alone cannot
establish that hypothesis.

## Experiment 1: does historical turnover supply the points?

The first empirical question is the premise of the mechanism: what enters
and leaves the rating population at each basho transition? The
[original proposal](../docs/2026%2009%2014%20Proposal%201%20-%20Unnormalised%20Turnover%20Accounting.md)
calls for recording incoming and outgoing rating mass, their difference,
population size and mean rating throughout the unnormalised replay. Reactive
HTML charts using Plotly CDN will show the transition series and the mean.

This accounts for both donors and departures that remove more than their
initial allocation. It tests whether turnover supports the proposed mechanism;
it does not by itself establish where the retained points end up. The implementation preserves ratings through temporary gaps, separately
reports their flows, and counts donor deficits only at final observed
departures. See the [completed results](expt1/Results.md).

## Experiment 2: where do the points circulate?

The second question concerns transmission towards the upper ranks. Its
[initial proposal](../docs/2026%2009%2014%20Proposal%202%20-%20Rating%20Updates%20by%20Opponent%20Rank.md)
counted points gained and lost against opponent rank groups. Discussion exposed
the limitation: a yokozuna can acquire points derived from Jonokuchi without
ever fighting a Jonokuchi opponent. Direct bout accounting misses that chain.

The design evolved into individual provenance accounting. Every initial P1
allocation has an individual origin. When someone loses, the proportions of
their current holdings determine the origins of the points transferred;
the actual winner gain and loser loss scale those proportions. The full
record retains individuals, with aggregation deferred to inspection. It can
show both points a subject holds from another origin and points of the
subject's own origin held elsewhere, including in frozen departure records.

Temporary banzuke gaps were initially treated as grounds to exclude returning
appearances. Examination of those cases led to a reversal: absence provides
no evidence of changed performance, so ratings and holdings persist through
gaps and resume unchanged on return, including Sokokurai. A return creates
no new P1 allocation. This decision restored all eligible returning bouts.

The implemented experiment and
[results so far](expt2/docs/2026%2009%2015%20Results%20and%20Interpretation.md)
make that accounting inspectable. They show a suggestive upper-rank pattern,
but an origin's circulating points are not automatically its donated surplus.
In particular, aggregating only by entry division would mostly recover the
fact that most rikishi enter at the bottom. Neither provenance holdings nor
their two-way balances are a counterfactual estimate of inflation caused by
departures. Experiment 1 addresses the turnover premise; Experiment 2 examines
circulation. Together they inform the original question without settling
whether mean preservation is justified.

## Repository and outputs

```text
src/analysis/inflation/
  expt1/                 turnover experiment
  expt2/                 provenance experiment, inspector and documentation

files/output/analysis/inflation/
  expt1/                 turnover run, views and manifest
  expt2/
    run/                 current full replay record
    views/               current explorer, profiles and CSV summaries
    archive/             previous runs and views, retained unchanged
```

The Experiment 2 output root is `files/output/analysis/inflation/expt2`.
Its raw run and post-run views have separate directories so inspection cannot
overwrite the immutable replay record. The generator's `--output-root`
defaults to the `run` directory; the inspector defaults to reading that run
and writing `views`. Explicit output overrides remain available.

Full historical replays use the live store; there is no automatic ZIP fallback.
The September 2026 reruns use `--end 2026/07` to keep the original completed
historical interval fixed while the live store also contains September data.

The relocation changes package/output paths, not the rating or gap policies.
Existing archived manifests retain their original paths and code hashes as
historical provenance; the fresh run records the new code locations.
