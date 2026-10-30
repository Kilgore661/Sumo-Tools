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
