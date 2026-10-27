# P1 epsilon sweep

This mini-project tests whether the fixed-point solver's stopping threshold is
acting as useful regularisation rather than merely as a numerical tolerance.
It fits the P1-WL prior once, from the common flat starting map, and retains the
first iteration whose maximum rating change is below each declared epsilon.
Each retained prior is then assessed as an Elo initializer using the same
post-1988 History, bout selection, q=400 model and divisional K policy.

The default sweep is deliberately broad: 1000 is above the first-iteration
change observed in the current History, so a still larger value would select
the same state; the grid becomes finer around epsilon 10 and continues to 0.1
to show the later trajectory. Lower log loss and Brier loss are better.

This is retrospective model-selection evidence. The same historical interval
is used to fit and assess each prior, so the result is not prospective
validation and selection of a best epsilon will itself need confirmation.

Run from the repository root:

```powershell
py -m src.validation.p1_epsilon_sweep `
  --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip" `
  --start 1989-01 `
  --end 2026-09
```

The program writes its iteration ledger, every retained prior and each score
as soon as they become available. It has no arbitrary iteration ceiling: it
stops when the smallest requested epsilon has been reached. Ordinary
Control-C termination therefore preserves all completed evidence.

## 2026-10-26 result

The full default run is in `output/epsilon-sweep-2026-10-26`; a short
refinement which adds iteration 20 is in
`output/epsilon-sweep-refinement-2026-10-26`.

Performance improved rapidly from epsilon 1000 to the region around epsilon
10, then reversed.  Among the states tested, iteration 20 (epsilon 8.5) had
the lowest log loss and iteration 21 (epsilon 8) had the lowest Brier loss.
The improvements over epsilon 10 were very small.  Epsilon 7 did not select
the next iteration: because the maximum change remained above 7 for a long
plateau, it selected iteration 82 and was already materially worse.  Further
iteration steadily degraded both losses through epsilon 0.1 at iteration
1171.

The appropriate conclusion is therefore that early stopping is acting as
material regularisation and that the useful region is approximately
iterations 18--21.  These retrospective results do not, by themselves,
justify treating epsilon 8 or 8.5 as definitively better than epsilon 10.
