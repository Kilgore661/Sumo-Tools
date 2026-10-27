# P1-WL epsilon sweep

Lower loss is better. The prior and evaluation use the same historical interval, so these are retrospective model-selection results.

Published P1: log loss 0.677111528; Brier loss 0.241981970.

| Epsilon | Iteration | Maximum change | Log loss | Brier loss | Log difference from P1 |
|---:|---:|---:|---:|---:|---:|
| 9 | 19 | 8.882583 | 0.677084062 | 0.241955719 | -0.000027465 |
| 8.5 | 20 | 8.094252 | 0.677082959 | 0.241951760 | -0.000028569 |
| 8 | 21 | 7.908805 | 0.677084523 | 0.241949165 | -0.000027004 |

Best log loss: epsilon 8.5 at iteration 20 (0.677082959).
Best Brier loss: epsilon 8 at iteration 21 (0.241949165).
