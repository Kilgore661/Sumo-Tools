# Fixed Supported Design

## Status

Waterfall design target.

This document implements the requirement in
`src/analysis/equelo/docs/Fixed Supported Requirements.md`.

It records design decisions accepted after the support-domain feasibility
study. Those decisions are not presented as first principles.

## Support Collapse Policy

Before support is measured, chii are normalised by the rank-family support
collapse policy.

The policy:

- removes annotations from chii;
- maps numbered sanyaku overflow slots beyond the first pair to the west side
  of the canonical first pair;
- leaves ordinary numbered ranks as their exact east/west chii.

For example, `O2e`, `O2w`, and `O3e` contribute support to `O1w`, while
`M12e`, `J1w`, and `Jd73w` remain distinct chii apart from annotation removal.

The purpose of this collapse is to avoid treating administrative sanyaku
overflow slots as separate support domains while preserving the lower-division
tail where the original failure mode occurred.

## Observation World

Use the same represented history world as the process-rating simulation.

For each basho-start chii observation, record whether the rikishi carried a
rating into that basho or whether the value came from entrant initialisation.

For each chii, compute:

```text
count
entry_count
non_entry_count
```

These counts are diagnostic evidence. They explain the original failure mode
and remain useful regression data.

For the production support rule, apply the rank-family support collapse and
count collapsed chii appearances in the represented history.

## Supported Domain

A collapsed chii is eligible for direct fixed-point estimation only if it has
enough represented-history appearances after the support collapse.

Current design decision:

```text
supported if collapsed_appearance_count >= 60
```

This is a policy parameter accepted after the feasibility study. It is not a
mathematical constant. A future revision may choose a different support measure
or threshold, but the chosen rule must be documented and recorded in metadata.

## Direct Initial Ratings

Run the fixed-point solver over the supported domain.

The solver shall produce directly estimated initial ratings only for supported
chii. Unsupported chii must not contribute independent fixed-point buckets to
the direct-estimation result.

## Master Map Completion

After direct estimation, complete the map over every chii required by the
simulation.

Current design decision:

```text
Unsupported required chii use the nearest supported chii by chii ordinal.
```

If two supported chii are equally near, the tie-break shall be deterministic.
The current policy is to choose the stronger, lower-ordinal chii.

Completion is a lookup-policy decision, not an additional fixed-point estimate.

## Process Ratings

The process-rating simulation shall use the completed master chii
initial-rating map when it needs a chii-based initial value.

Day-end and other process-rating artifacts are about rikishi over time. They are
downstream of the master map and should not be confused with it.

## Public Landmarks

Public interpretive landmarks, including `Typical Equelo Ratings`, shall be
derived from the documented production source.

The public Equelo scale shall remain anchored so that the Yokozuna landmark is
approximately 2500 under the accepted base convention.

## Canonical Artifacts

Primary production artifact:

```text
master chii initial-rating map
```

Conceptual columns:

```text
chii
chii_ordinal
initial_rating
source_kind
source_chii
source_chii_ordinal
count
entry_count
non_entry_count
collapsed_appearance_count
```

`source_kind` shall distinguish at least:

```text
direct
nearest_supported
```

Metadata shall record:

```text
history source
support rule
support threshold
support collapse policy
completion rule
tie-break rule
base convention
solver config
generation timestamp
code provenance
```

Downstream production artifacts include process/day-end ratings and public
landmarks. They shall identify the master map or production policy that was
used to produce them.

## Invariants

The master map is keyed by chii, not rikishi.

The master map covers every chii required by the simulation.

Direct fixed-point values exist only for supported chii.

Completed values are deterministic and traceable to supported chii.

Unsupported chii do not receive independent fixed-point estimates.

The public scale remains anchored to the accepted Equelo convention.

No low-support lower-division chii can acquire a spurious Yokozuna-level
initial rating.

## Acceptance Checks

The replacement is acceptable when:

- the master map covers the full simulation chii domain;
- every direct value is for a supported chii;
- every unsupported required chii is completed from a documented supported
  source;
- generated metadata identifies the support rule, completion rule, base
  convention, and input history;
- the process no longer creates spurious Yokozuna-level ratings for
  low-support lower-division chii;
- `Highest Equelo` no longer ranks low-support lower-division artifacts near
  the top;
- the Yokozuna public landmark is approximately 2500 under the accepted base
  convention;
- downstream producers consume production artifacts or APIs, not experiment
  paths.

## Open Implementation Questions

The design does not yet choose final file names, package layout, command names,
or archive location for legacy code.

Those choices are implementation work. They must preserve the distinctions in
this document, especially the distinction between chii initial ratings and
rikishi process ratings.
