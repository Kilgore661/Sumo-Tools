# Exploration of extreme ratings

## Purpose

`Highest Equelo` exposed implausible fixed_v2 process ratings for low-ranked
rikishi with short careers. Examples include rikishi whose highest ranks are in
Jonokuchi, Jonidan or Sandanme but whose maximum fixed_v2 ratings exceed 3000.

The immediate purpose of this work is not to select a repair. It is to
understand the condition that produces these ratings well enough that any later
model change can be tested against evidence rather than against a single
surprising table row.

## Background

The fixed_v2 process uses an Expt2 fixed-point entrant-prior map. The basic
single-pass Elo calculation starts entrants from a constant rating and then
updates ratings from bouts. In checked examples, that basic calculation produces
ordinary ratings for the low-ranked rikishi that appear near the top of
`Highest Equelo`.

The extreme values enter through the fixed-point entrant-prior process. Some
temporary deep-Jonokuchi ranks, such as ranks created during local expansion of
the Jonokuchi banzuke, have very few exact-chii observations. In the suspicious
cases inspected so far, the rank bucket appears to be dominated by fresh entrant
basho-start observations.

That matters because Expt2 aggregates basho-start ratings by chii. If every
observation for a chii is a fresh entrant, the aggregate may observe the prior
assigned by the previous iteration rather than independent evidence from a
carried rating. Repeated fixed-point normalisation can then move an
underidentified chii bucket relative to supported buckets.

This is a hypothesis, not yet a settled diagnosis.

## First Hypothesis

Extreme fixed-point rank priors occur where the aggregate for an exact chii is
made mostly or entirely from ratings assigned by the same prior at entry.

In operational terms:

```text
For a chii r, suspicious support means that many or all basho-start
observations at r are fresh entries: the rikishi had no rating immediately
before entrant initialisation for that basho.
```

The first exploration should test whether the high and locally spiky fixed-point
priors are associated with this kind of self-observation.

## Minimal Data Dump

The first dump should be contribution-level, with one row for each observation
that enters the fixed-point aggregate:

```text
chii
chii_ordinal
date
rikishi_id
basho_start_rating
entry
```

`entry` is true if the rikishi had no rating immediately before the simulator's
entrant-initialisation step for that basho. It is false if the rikishi carried a
rating into the basho.

This dump is deliberately small. It should be sufficient to reconstruct, for
each chii:

```text
count
entry_count
non_entry_count
mean_basho_start_rating
```

The first exploration should avoid adding inferred columns until there is a
clear question that needs them. For example, division can be inferred from the
chii or ordinal and should not be duplicated in the minimal dump.

## Questions To Ask First

The first analysis should answer:

```text
Do the extreme fixed-point chii priors have zero or very low non-entry support?
Do normal-looking chii priors have materially more non-entry support?
Are the suspicious chii concentrated in temporary exact ranks, especially deep
Jonokuchi ranks created by banzuke-size expansion?
Are there counterexamples: high priors with good non-entry support, or
entry-dominated chii with ordinary priors?
```

The goal is to identify the condition, not to choose a threshold.

## Out Of Scope For This Exploration

This exploration does not decide whether fixed_v2 should be changed by:

```text
excluding entrant observations,
smoothing sparse chii,
solving on coarser buckets,
adding support guards,
or changing normalisation.
```

Those are possible later design choices. They should be evaluated only after the
support profile of the current fixed-point aggregate is understood.

## Relationship To Site Artifacts

`Highest Equelo` is not currently assumed to be the source of the problem. It is
treated as an artifact that revealed a possible upstream rating-model defect.

Until the rating-model issue is understood, publication-facing artifacts that
rank historical maximum Equelo ratings may expose misleading values for
low-ranked rikishi.
