# Experiment `upgrade_tight`

70 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

A grid with 80 m blocks at 14000 veh/h: links hold about 20 vehicles, so queues spill back into the junctions behind them whatever a single junction does. This is the regime the README said was needed to see neighbours matter.

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|
| fixed | 213.3 ± 10.4 | 169.7 ± 8.8 | 10964 ± 922 | 0.63 ± 0.02 | 43.5 ± 3.3 |
| actuated | 166.5 ± 9.5 | 126.5 ± 9.5 | 12073 ± 1301 | 0.66 ± 0.03 | 26.0 ± 3.8 |
| max_pressure | 167.6 ± 7.5 | 127.7 ± 7.5 | 11559 ± 971 | 0.71 ± 0.01 | 24.8 ± 2.9 |
| before | 162.5 ± 8.6 | 122.4 ± 8.6 | 12778 ± 1975 | 0.72 ± 0.02 | 15.9 ± 0.2 |
| **after** | 157.3 ± 10.3 | 117.5 ± 10.3 | 11208 ± 1789 | 0.70 ± 0.03 | 31.0 ± 3.8 |
| after_no_bids | 156.1 ± 8.6 | 116.2 ± 8.6 | 11148 ± 1469 | 0.70 ± 0.02 | 26.8 ± 3.1 |
| after_no_coordinator | 152.4 ± 7.9 | 112.6 ± 7.8 | 11081 ± 1639 | 0.75 ± 0.02 | 27.5 ± 2.9 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs before | vs after_no_bids | vs after_no_coordinator |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 9.59e-06 | 0.0011 | 0.606 | 0.606 | 1 | 1 | 1 |
| Avg. waiting time (s) | 1.01e-05 | 0.0011 | 0.606 | 0.606 | 1 | 1 | 1 |
| Spillback (link-seconds) | 0.672 | 1 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 3.98e-07 | 0.00198 | 0.303 | 1 | 1 | 1 | 0.0566 |
| Messages per agent per minute | 2.46e-08 | 0.00384 | 0.227 | 0.0845 | 0.0011 | 0.281 | 0.281 |
