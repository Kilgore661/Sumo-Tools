# Off-Banzuke Results

## Status

The canonical-History census is complete. It found five represented bouts
with an endpoint absent from the same-basho parsed banzuke. Every missing
endpoint has the literal source status `Mz`, every bout occurred in `1974-11`,
and none lies in the post-1988 Elo-89 era.

The result is recorded in [`docs/Findings.md`](docs/Findings.md). No historical
include-versus-exclude replay is needed: over the represented Elo-89 History,
the two policies have an empty difference set. The prospective contract and
the separate question of Mz results omitted upstream remain distinguishable
future questions.

The immediate question is whether the current repaired post-1988 `History`
contains a represented result whose participant is absent from that basho's
parsed banzuke. Existing evidence is fragmented:

- a full-history Elo-58/Equelo2 run found five such W/L bouts, all in
  `1974-11`;
- an older post-1988 prediction run found seven `2026-07` bouts involving
  RikId 13011 while he was absent from that version of the banzuke;
- the repaired History now represents RikId 13011 as `Sd80eTD`;
- the rating-persistence census found no represented off-banzuke bout during
  a post-1988 gap, but that was not a census of every bout endpoint; and
- source pages expose mae-zumo activity which may not enter canonical
  `History` at all.

These claims use different epochs, History states and event definitions. This
package will replace them with one provenance-bound account of the current
Elo-89 interval, while retaining the older cases as reconciliation checks.

The experiment specification is in
[`docs/Proposal.md`](docs/Proposal.md).

## Scope boundary

This work distinguishes two questions:

1. Does a result already represented in canonical `History` involve a
   participant absent from the parsed banzuke?
2. Does the upstream source contain an Mz result which canonical `History`
   does not represent?

The first is directly an Elo-89 bout-eligibility and population-policy issue.
The second is a source and data-model completeness issue. It may explain why
the first count is zero, but it must not be silently folded into the same
denominator.

## Current contract conflict

The retained Elo-89 selector accepts every represented binary W/L result
without checking banzuke membership. The replay then adds both participants
to its active population. A participant without a chii receives the unranked
P1-WL fallback and K=35.

Older named-model prose instead says that off-banzuke results are excluded and
reported. The expert account records that the current production ledger has no
affected bout, so the conflict is prospective for the published artifact. It
must nevertheless be resolved before a future result makes the two contracts
diverge.

## Intended outputs

Code will live in `src.validation.off_banzuke_results`. Generated evidence
will be written beneath:

```text
files/output/validation/elo89-expert-account/Matters Arising/
  Off-Banzuke Results/
```

The census is complete. It is not a website build or production change. Its
zero post-1988 result establishes that the prospective contract conflict has
no realised effect on the represented Elo-89 history, while leaving the
source-level Mz completeness question explicitly separate.
