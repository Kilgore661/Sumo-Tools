# Frozen Persistence Comparison

## Status

Implemented and run over `1989-01` through `2026-09`. The reset control exactly
reproduced canonical P1-WL Elo-89, all 437 return events matched the retained
census, and no invariant failed. The results support adopting frozen rating
persistence, and that policy is now accepted as part of the intended Elo-89
contract. Production promotion remains separate work.

The ranked-banzuke census established that Elo-89 contains 437
gap-and-return events in the selected post-1988 interval. Of the 436
Jonokuchi-to-Jonokuchi events, 424 explicitly pass through mae-zumo. The sole
substantively different event is Sokokurai's departure from and return to
Makuuchi.

This tranche asks what happens if Elo-89 retains a rikishi's last rating while
he is outside the represented active population, rather than deleting it and
later reinitialising him from the P1-WL prior.

The full experiment specification is in
[`docs/Proposal.md`](docs/Proposal.md).
The retained interpretation is in [`docs/Findings.md`](docs/Findings.md).

## Controlled difference

Both replays will use the accepted P1-WL prior and otherwise identical Elo-89
inputs and rules.

| Run | Departure and return policy |
|---|---|
| Control | Delete on departure; initialise from P1-WL on return |
| Candidate | Archive the last rating unchanged; restore it on return |

An archived rating is inert. It is excluded from active-population means,
normalisation and bout updates. If the rikishi never returns, it has no further
effect. On return it re-enters the ordinary active replay and is treated
normally from that point.

This experiment does not admit `Mz`-versus-`Mz` bouts, introduce an Mz prior,
decay ratings during absence, or carry population shifts into the archive.
