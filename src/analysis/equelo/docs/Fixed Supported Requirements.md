# Fixed Supported Requirements

## Status

Waterfall requirement and specification target.

This document describes the Equelo replacement we intend to build. It is not a
description of the current experimental code. The implementation should be
judged against this document, and then changed until it conforms.

The companion design target is
`src/analysis/equelo/docs/Fixed Supported Design.md`.

## Name

The working technical name is `fixed_supported`.

The name means: a fixed-point Equelo artifact package whose chii initial-rating
map is estimated only on empirically supported chii and then completed for the
full simulation domain.

This name is deliberately descriptive rather than version-numbered. Public site
wording should continue to prefer `Equelo` unless provenance or methodology is
being discussed.

## Problem Context

The old raw fixed-point Equelo path estimated an initial rating for every chii.
That allowed exact chii with little or no independent support to acquire
implausibly high initial ratings.

The visible failure was exposed by the `Highest Equelo` table. Deep Jonokuchi
chii such as `Jk73w` could receive initial ratings near 3100, and short-career
lower-division rikishi could then appear near the top of a historical maximum
ratings table. Those ratings were not earned through bout results. They were an
artifact of the fixed-point initialisation process.

## Diagnosis

The failure is caused by underidentified chii buckets.

The fixed-point process aggregates basho-start ratings by chii. When a chii has
many observations where rikishi carried ratings into the basho, the aggregate
contains independent process-rating evidence. When a chii has only, or mostly,
fresh-entry observations, the aggregate mostly observes values assigned by the
previous iteration's initial-rating prior.

That creates a self-referential support problem. The solver can end up learning
from its own prior instead of from carried rating evidence. Sparse and temporary
lower-division chii are especially vulnerable.

The diagnosis identified `non_entry_count` as the signal that distinguishes
carried-rating observations from entrant-prior observations. The feasibility
study then tested support-domain policies and accepted a minimum collapsed
appearance count as the production support rule. This is an empirical design
choice informed by the diagnostic signal, not a claim that appearance count and
independent carried-rating support are identical concepts.

## Requirement

Equelo shall produce a master chii initial-rating map for the rating simulation.

The map shall be keyed by chii, not by rikishi. It answers the question:

```text
What initial rating should the simulator use when it needs a chii-based initial
value for this chii?
```

It does not answer:

```text
What is this rikishi's rating?
```

The map shall preserve full simulation coverage without allowing unsupported
chii to receive independent fixed-point estimates.

## Specification

The Equelo replacement shall generate a complete chii-to-initial-rating map for
use by the process-rating simulation.

For each chii in the supported domain, the map shall contain a directly
estimated fixed-point initial rating.

For each chii required by the simulation but outside the supported domain, the
map shall contain a completed initial rating produced by a documented,
deterministic policy derived from supported chii evidence.

The map shall be complete over the simulation domain, reproducible from
documented inputs and policies, and calibrated to the intended public Equelo
scale.

## Derived Requirements

Unsupported required chii must receive initial ratings. The simulator cannot
run over historical data unless every required chii has an initial value.

Unsupported required chii must not receive independent fixed-point estimates.
That is the condition that created the old failure mode.

Completed values must be traceable. A downstream maintainer must be able to see
whether a value was directly estimated or completed, and if completed, which
supported chii supplied the value.

The completion policy must be deterministic. Running the same code against the
same input history and policy parameters must produce the same map.

## Non-Goals

The master chii initial-rating map is not a table of rikishi ratings.

The map does not try to prove that unsupported chii have independently known
strength values. Its job is to provide reasonable simulation initial values
without creating unstable fixed-point artifacts.

The map is not itself the `Highest Equelo` table, the `Typical Equelo Ratings`
table, or any other public display artifact. Those are downstream consumers or
validation artifacts.

## Acceptance Boundary

The requirements are satisfied only when the implementation can show that:

- the master map covers the full simulation chii domain;
- every direct value is for a supported chii;
- every unsupported required chii is completed from a documented supported
  source;
- generated metadata identifies the support rule, completion rule, base
  convention, and input history;
- the process no longer creates spurious Yokozuna-level ratings for
  low-support lower-division chii;
- downstream producers consume production artifacts or APIs, not experiment
  paths.
