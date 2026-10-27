# P1WL3 Evaluation: Findings

## Conclusion

P1WL3 is not an acceptable replacement for P1 or for the accepted
epsilon-10 P1-WL candidate.

Both members of the matched epsilon-3 pair satisfy the declared numerical
stopping rule, but both are substantially worse predictive initializers than
the published and epsilon-10 priors. P1WL3 is also detectably worse than its
same-History epsilon-3 P1 control. The failure is therefore dominated by the
tighter fixed-point iteration, with a further adverse P1WL3-minus-P1 effect;
it is not evidence against including known W/L bouts with missing kimarite.

The run demonstrates that epsilon is not merely a precision setting in this
procedure. With the present unsmoothed literal-chii map it acts as an
early-stopping or regularisation choice. A smaller epsilon permits sparse
cells to develop extreme fitted values before the maximum-update criterion is
met. Numerical convergence alone is not a model-acceptance criterion.

## Inputs

The fitted source pair is:

`../output/p1-wl-comparison-2026-10-25-eps=3_max400_test`

Both variants use the same frozen History, interval, q, K configuration,
base, preprocessing and recentering rule as the accepted epsilon-10 pair.
Their declared controlled difference remains bout eligibility.

| Variant | Epsilon | Maximum iterations | Iterations used | Final maximum update |
|---|---:|---:|---:|---:|
| P1 | 3 | 400 | 295 | 2.988948 |
| P1-WL | 3 | 400 | 310 | 2.989262 |

The repeated downstream evaluation is in
[`output/p1-wl3-evaluation-2026-10-25`](output/p1-wl3-evaluation-2026-10-25).
It used the same six-model initialisation test and the same three exact
Elo-89 replays as the accepted evaluation. Runtime was 155.719 seconds and
the common forecast domain contained 581,634 bouts.

## Test A: initialisation

| Initialisation model | Log loss | Brier loss | ECE |
|---|---:|---:|---:|
| Equal, constant K (`B`) | 0.682522 | 0.244574 | 0.018960 |
| Equal, divisional K (`B_k`) | 0.681792 | 0.244246 | 0.013475 |
| Older informed prior | **0.676749** | **0.241872** | **0.013397** |
| Published P1 | 0.677112 | 0.241982 | 0.014395 |
| Epsilon-3 P1 | 0.687088 | 0.244989 | 0.016869 |
| P1WL3 | 0.688735 | 0.245344 | 0.018111 |

P1WL3 is worse than Basic Elo by 0.006214 log-loss units (95% basho-block
interval 0.003381 to 0.009311) and worse than the epsilon-3 P1 control by
0.001647 (0.001211 to 0.002144). It therefore fails the same predictive gate
which the accepted P1 and epsilon-10 P1-WL candidates pass.

The matched epsilon-3 P1 control is itself worse than Basic Elo. Tightening
the stopping rule has degraded the underlying fitted-prior method before the
kimarite eligibility contrast is considered.

## Test B: exact Elo-89

| Prior | Log loss | Brier loss | ECE |
|---|---:|---:|---:|
| Published P1 | **0.675436** | **0.241267** | **0.014513** |
| Epsilon-3 P1 | 0.688892 | 0.245875 | 0.019100 |
| P1WL3 | 0.690712 | 0.246306 | 0.020756 |

P1WL3 is worse than published P1 by 0.015275 log-loss units (95% interval
0.011957 to 0.018924) and worse than its epsilon-3 P1 control by 0.001819
(0.001348 to 0.002339). Brier loss and ECE give the same direction.

The P1WL3-minus-epsilon-3-P1 loss is concentrated where an entrant prior
should matter. It is +0.004589 for new entrants and +0.007762 for bouts in
which a participant has fewer than 30 previous career bouts; both intervals
exclude zero. Only the 480-plus group shows a very small improvement.

The causal probability difference has a mean absolute value of 0.002893, but
its maximum is 0.129496. This 12.95-percentage-point maximum is materially
larger than the 4.23-point maximum in the accepted epsilon-10 comparison.

## Why the numerical convergence is misleading

At epsilon 10 the matched fits stop after 18 iterations. At epsilon 3 they
continue for roughly 300 iterations. The maximum update falls smoothly below
three, so the implementation has applied its stated rule correctly. The map
to which it is moving is nevertheless unsuitable as an entrant prior.

The clearest symptom is in sparsely represented literal ranks:

| Chii | Support | Epsilon-3 P1 | P1WL3 |
|---|---:|---:|---:|
| `Y1e` | 221 | 2,441.70 | 2,474.83 |
| `Jk65e` | 9 | 3,062.36 | 3,205.47 |
| `Jk65w` | 8 | 2,890.66 | 3,017.87 |
| `Jk66e` | 8 | 2,890.66 | 3,017.87 |

Thus a nine-observation jonokuchi cell acquires a higher initial rating than
yokozuna. P1WL3 spans 1,050.69 to 3,205.47, compared with 906.25 to 2,588.14
for the accepted epsilon-10 P1-WL map. These are not small refinements to the
same curve.

The fixed-point stopping rule asks only whether one complete iteration changes
every cell by less than epsilon. It does not test rank ordering, sparse-cell
variance, predictive adequacy, or whether the map has become more extreme
while approaching that condition. Calling this result `converged=True` is
accurate in the narrow implemented sense but insufficient as evidence that
the result should be adopted.

## Rating and publication consequences

Relative to its matched epsilon-3 P1 control, P1WL3's mean-aligned basho-end
rating difference is 5.10 points on average and 137.96 at maximum. The large
maximum again arises from the sparse prior cells. At the final basho the top
20 retain their order, while the complete current table has 289 of 593
positions changed and a maximum movement of 13 places.

The more important comparison is against published P1. The epsilon-3 P1
control already creates a mean absolute basho-end difference of 83.63 points
and a maximum of 1,331.31; P1WL3 versus published P1 reaches 88.00 and
1,464.92. These effects are much larger than the accepted epsilon-10 repair
and reflect the changed fit, not merely kimarite eligibility.

## Decision

Retain the earlier conclusion that epsilon-10 P1-WL is an acceptable semantic
repair for P1. Reject P1WL3 as a candidate production prior.

This result exposes a separate modelling issue: the existing P1 procedure
uses its stopping threshold as de facto regularisation, while describing it
as convergence tolerance. Before claiming a more fully converged P1 map, the
project would need an explicit sparse-cell treatment or smoothing rule and a
model-selection criterion beyond maximum iteration-to-iteration change.

No canonical P1, production Elo-89 or site artifact was changed by this run.
