# BKP1 q=400 retrospective predictive gate

The candidate uses the alpha=1 prior produced by the q=400 fixed-point
diagnostic, paired by an unweighted east/west mean, inside the exact
q=400 forecast/update contract used by the established B-family comparison.
Both informed priors are future-informed, so this is retrospective model
selection evidence rather than prospective validation.

## Aggregate result

| Model | Mean log loss | Mean Brier loss | ECE |
|---|---:|---:|---:|
| B | 0.682522 | 0.244574 | 0.018960 |
| B_k | 0.681792 | 0.244246 | 0.013475 |
| B_P | 0.677845 | 0.242336 | 0.016986 |
| B_kP | 0.676749 | 0.241872 | 0.013397 |
| B_kP1 | 0.700308 | 0.248163 | 0.026738 |

Negative paired differences favour BKP1.

| Comparator | Log difference | 95% interval | One-sided 95% upper | Brier difference |
|---|---:|---:|---:|---:|
| B | +0.017787 | [+0.012521, +0.023662] | +0.022594 | +0.003589 |
| B_k | +0.018517 | [+0.013206, +0.024325] | +0.023261 | +0.003917 |
| B_P | +0.022463 | [+0.016872, +0.028314] | +0.027329 | +0.005827 |
| B_kP | +0.023559 | [+0.017953, +0.029398] | +0.028271 | +0.006291 |

The existing non-inferiority margin versus B is 0.000531. BKP1 does not pass that retrospective gate (one-sided upper 0.022594).

## Rating-maturity result

| Population | Bouts | BKP1 log loss | Difference from old B_kP |
|---|---:|---:|---:|
| new_entrant | 2,519 | 0.772471 | +0.082627 |
| career_experience_under_30 | 85,357 | 0.816553 | +0.103059 |
| career_experience_30_59 | 73,185 | 0.714263 | +0.038108 |
| career_experience_60_119 | 113,861 | 0.680819 | +0.011632 |
| career_experience_120_239 | 150,272 | 0.676157 | +0.004349 |
| career_experience_240_359 | 78,783 | 0.673451 | +0.001602 |
| career_experience_360_479 | 39,839 | 0.668691 | +0.000325 |
| career_experience_480_plus | 40,337 | 0.657674 | -0.000007 |
