# Elo-89 literal-prior production

This package produces immutable fitted P1-WL **literal-chii** tables. Those
tables are derivation inputs, not the paired prior consumed directly by the
Elo-89 replay. Production Elo-89 uses the separately persisted P1-prime-WL
table selected by the prior-aggregation work.

The input History is bounded from 1989/01 through `--last-prior-basho`, with
both endpoints included. The default final basho is declared in
`src.analysis.elo89.config`. Results after that boundary cannot affect the
prior. Binary wins and losses are used whether or not a kimarite is present.
The fixed-point fitting replay retains the lifecycle used in the accepted
P1-WL experiment. Frozen persistence is a separate Elo-89 production-replay
policy; it is not another variable in this prior promotion.

Each invocation writes a new, immutable numbered directory:

```text
files/output/analysis/elo89/prior/YYYY-MM/run-NNN/
    prior.csv
    iterations.csv
    manifest.json
```

## Fitted source and installed prior

The accepted fitted P1-WL source is:

```text
files/output/analysis/elo89/prior/2026-09/run-001/prior.csv
```

That output contains separate literal chii ratings and their support. The
accepted aggregation applies direct support weighting to every literal cell
mapped to a consumer key, including east/west and every numbered Y/O/S/K
position present. The resulting 484-row P1-prime-WL table is persisted at:

[`equelo_prior_aggregation/results/priors.csv`](../../equelo_prior_aggregation/results/priors.csv)

Its SHA-256 is
`41430ce50f61bf2769ee7b37e4c964d5ecd00e78fe554a9790a869ad35955d38`.
`src.analysis.elo89.config` identifies this file as the installed replay
prior. The replay loads its exact `rank_pair,ordinal,rating` schema strictly;
it does not refit or reaggregate the prior. Every production replay copies the
values it consumed to its own `prior.csv`. In the standard site-data bundle
that copy is:

[`files/output/analysis/site89_bundle/sources/elo89/prior.csv`](../../../../files/output/analysis/site89_bundle/sources/elo89/prior.csv)

The adjacent `manifest.json` records the installed table's path and SHA-256
hash, as well as the number of rank pairs written. The bundle copy is a
generated artifact; the installed source under `results` is source controlled.

On 6 November 2026, the project accepted P1-prime-WL as the official successor
entrant prior. It applies direct support weighting to every P1-WL literal cell
mapped to a paired key, including east/west and every numbered Y/O/S/K position
present. The decision and exact experimental artifact hashes are recorded in
[`Prior Aggregation`](../../../validation/elo89-expert-account/Matters%20Arising/Prior%20Aggregation/README.md).

There is deliberately no output-path command-line option. Existing runs are
never overwritten, and run numbering is local to the selected boundary.

Use the live History provider:

```powershell
py -m src.analysis.elo89.prior
```

Or use a saved annotated History:

```powershell
py -m src.analysis.elo89.prior `
  --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip" `
  --last-prior-basho 2026-09
```

The command exits with status 2 if the fixed-point solver does not converge,
but retains the run and its diagnostics. A produced run is not automatically
accepted by the Elo-89 site build: acceptance is an explicit configuration
decision made after comparison and review.
