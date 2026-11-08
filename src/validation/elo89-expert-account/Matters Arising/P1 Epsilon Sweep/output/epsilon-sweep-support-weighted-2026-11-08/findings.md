# P1-WL epsilon sweep

Lower loss is better. The prior and evaluation use the same historical interval, so these are retrospective model-selection results.

Published P1: log loss 0.677111528; Brier loss 0.241981970.

| Epsilon | Iteration | Maximum change | Log loss | Brier loss | Log difference from P1 |
|---:|---:|---:|---:|---:|---:|
| 10 | 18 | 9.727844 | 0.677094316 | 0.241964810 | -0.000017212 |
| 8.5 | 20 | 8.094252 | 0.677088860 | 0.241955263 | -0.000022668 |
| 8 | 21 | 7.908805 | 0.677090310 | 0.241952620 | -0.000021218 |

Best log loss: epsilon 8.5 at iteration 20 (0.677088860).
Best Brier loss: epsilon 8 at iteration 21 (0.241952620).
