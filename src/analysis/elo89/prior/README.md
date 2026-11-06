# Elo-89 prior production

This package produces the fixed P1-WL initial ratings used by Elo-89. It is
production code derived from the accepted validation work; it does not repeat
the P1-versus-P1-WL experiment.

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

## Accepted and paired tables

`src.analysis.elo89.config` declares which immutable run is accepted by
Elo-89. The accepted fitted table is currently:

```text
files/output/analysis/elo89/prior/2026-09/run-001/prior.csv
```

That fitting output contains separate values for east and west chii. When
Elo-89 loads it, values belonging to the same rank pair are averaged. Every
production replay writes the resulting paired table as `prior.csv` in the
replay output. In the standard site-data bundle, the exact paired values used
are therefore in:

[`files/output/analysis/site89_bundle/sources/elo89/prior.csv`](../../../../files/output/analysis/site89_bundle/sources/elo89/prior.csv)

The adjacent `manifest.json` records the fitted table's path and SHA-256 hash,
as well as the number of rank pairs written. Both CSV files are generated
artifacts under `files/output`; they are not source-controlled files.

## Publication TBD

**TBD: finalise the content and stable repository location of P1-WL.** The
current fitted and paired tables are generated artifacts under `files/output`
and are therefore absent from a clean checkout. Before the expert account is
published as a permanent repository document, the accepted values and the
provenance needed to identify them must be placed at a stable, source-controlled
location and the links above updated.

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
