# Experiment `upgrade_tight`

70 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

A grid with 80 m blocks at 14000 veh/h: links hold about 20 vehicles, so queues spill back into the junctions behind them whatever a single junction does. This is the regime the README said was needed to see neighbours matter.

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|
| fixed | 234.2 ± 9.5 | 189.8 ± 10.3 | 11127 ± 540 | 0.60 ± 0.01 | 54.0 ± 3.7 |
| actuated | 204.4 ± 19.2 | 164.4 ± 19.2 | 16341 ± 2306 | 0.57 ± 0.03 | 42.2 ± 8.0 |
| max_pressure | 191.8 ± 9.2 | 151.9 ± 9.1 | 15495 ± 950 | 0.64 ± 0.01 | 35.2 ± 4.0 |
| before | 165.7 ± 8.2 | 125.6 ± 8.2 | 13850 ± 1707 | 0.68 ± 0.01 | 15.8 ± 0.2 |
| **after** | 156.9 ± 8.5 | 117.1 ± 8.4 | 12177 ± 2024 | 0.69 ± 0.02 | 29.7 ± 2.5 |
| after_no_bids | 157.0 ± 6.9 | 117.1 ± 6.9 | 12210 ± 1580 | 0.69 ± 0.01 | 26.3 ± 2.6 |
| after_no_coordinator | 155.2 ± 7.2 | 115.3 ± 7.2 | 12331 ± 1583 | 0.72 ± 0.02 | 28.2 ± 2.2 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs before | vs after_no_bids | vs after_no_coordinator |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 2.86e-09 | 0.0011 | 0.00307 | 0.00123 | 0.486 | 1 | 1 |
| Avg. waiting time (s) | 3.61e-09 | 0.0011 | 0.00307 | 0.00123 | 0.637 | 1 | 1 |
| Spillback (link-seconds) | 0.000117 | 1 | 0.0437 | 0.0701 | 0.849 | 1 | 1 |
| Fairness (Jain index) | 2.31e-10 | 0.0011 | 0.0011 | 0.00526 | 0.546 | 0.91 | 0.162 |
| Messages per agent per minute | 6.29e-10 | 0.0011 | 0.0144 | 0.0772 | 0.0011 | 0.108 | 0.307 |
