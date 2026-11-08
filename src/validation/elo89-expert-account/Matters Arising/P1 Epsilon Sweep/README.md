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

By default, new runs are written beneath
`files/output/validation/elo89-expert-account/Matters Arising/P1 Epsilon Sweep/output/`.

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

## 2026-11-08 production-aggregation check

The original sweep converted literal cells to paired keys by unweighted
averaging. Production P89 instead applies direct support weighting. Before
promoting a stopping point, iterations 18, 20 and 21 were therefore replayed
again with support weighting held fixed. The retained run is:

```text
output/epsilon-sweep-support-weighted-2026-11-08/
```

| Epsilon | Iteration | Mean log loss | Mean Brier loss |
|---:|---:|---:|---:|
| 10 | 18 | 0.677094 | 0.241965 |
| 8.5 | 20 | 0.677089 | 0.241955 |
| 8 | 21 | 0.677090 | 0.241953 |

Iteration 20 retained the lowest log loss under the production aggregation;
iteration 21 retained the adjacent Brier minimum. Log loss is the declared
primary selection measure, so epsilon 8.5 / iteration 20 was promoted. The
differences are small and use the same history for fitting and scoring. This
supports a choice among nearby points on the retained trajectory; it is not
prospective validation or evidence that 8.5 is a privileged constant.
