# Experiment `upgrade`

300 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

The upgrade of parts 2 and 3, one mechanism at a time. "before" switches both new mechanisms off: the anticipation rule of the negotiating junctions and the intention sharing of informed drivers. The last two variants repeat the comparison for a fleet in which every driver follows the traffic information.

## grid_light

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 91.4 ± 0.3 | 26.1 ± 0.2 | 0.71 ± 0.01 | 0.00 ± 0.00 | 0.93 ± 0.00 | 0.02 ± 0.00 | 6.63 ± 0.02 |
| anticipation_only | 90.7 ± 0.2 | 25.3 ± 0.1 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.02 ± 0.00 | 6.49 ± 0.02 |
| intentions_only | 91.2 ± 0.2 | 25.8 ± 0.1 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.03 ± 0.00 | 9.24 ± 0.05 |
| **after** | 90.5 ± 0.2 | 25.1 ± 0.1 | 0.69 ± 0.01 | 0.00 ± 0.00 | 0.95 ± 0.00 | 0.03 ± 0.00 | 9.17 ± 0.04 |
| all_informed_before | 91.8 ± 0.3 | 26.3 ± 0.2 | 0.71 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.10 ± 0.00 | 6.69 ± 0.02 |
| all_informed_after | 90.6 ± 0.2 | 24.8 ± 0.1 | 0.68 ± 0.01 | 0.00 ± 0.00 | 0.98 ± 0.00 | 0.12 ± 0.00 | 11.6 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 3.64e-08 | 0.00132 | 0.769 | 0.00175 | 0.000913 | 0.769 |
| Avg. waiting time (s) | 4e-10 | 0.000913 | 0.014 | 0.000913 | 0.000913 | 0.00917 |
| Avg. queue per approach (veh) | 5.36e-05 | 0.0183 | 0.0634 | 0.0634 | 0.0141 | 0.0634 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 1.11e-09 | 0.000913 | 0.00099 | 0.00099 | 0.00459 | 0.000913 |
| avg_reroutes | 1.52e-10 | 0.000913 | 0.000913 | 0.0412 | 0.000913 | 0.000913 |
| Messages per agent per minute | 9.03e-11 | 0.000913 | 0.000913 | 0.0211 | 0.000913 | 0.000913 |

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 159.9 ± 1.4 | 93.5 ± 1.4 | 6.95 ± 0.12 | 0.00 ± 0.00 | 0.82 ± 0.01 | 0.07 ± 0.00 | 11.8 ± 0.0 |
| anticipation_only | 159.7 ± 1.6 | 93.2 ± 1.6 | 7.02 ± 0.14 | 2.00 ± 4.52 | 0.82 ± 0.01 | 0.07 ± 0.00 | 11.8 ± 0.1 |
| intentions_only | 156.6 ± 1.6 | 90.4 ± 1.6 | 6.71 ± 0.14 | 1.00 ± 2.26 | 0.78 ± 0.01 | 0.06 ± 0.00 | 20.4 ± 0.1 |
| **after** | 156.5 ± 1.4 | 90.3 ± 1.4 | 6.81 ± 0.13 | 0.00 ± 0.00 | 0.78 ± 0.01 | 0.06 ± 0.00 | 20.6 ± 0.1 |
| all_informed_before | 171.6 ± 1.6 | 104.2 ± 1.6 | 7.70 ± 0.15 | 17.0 ± 13.9 | 0.95 ± 0.00 | 0.35 ± 0.01 | 11.5 ± 0.0 |
| all_informed_after | 148.6 ± 1.0 | 82.1 ± 1.0 | 6.24 ± 0.10 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.28 ± 0.01 | 31.0 ± 0.2 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 3.35e-09 | 0.0108 | 0.0146 | 0.91 | 0.000913 | 0.000913 |
| Avg. waiting time (s) | 4.19e-09 | 0.0138 | 0.0182 | 0.791 | 0.000913 | 0.000913 |
| Avg. queue per approach (veh) | 6.16e-09 | 0.128 | 0.0518 | 0.186 | 0.000913 | 0.000913 |
| Spillback (link-seconds) | 0.000234 | 1 | 1 | 1 | 0.0296 | 1 |
| Fairness (Jain index) | 2.44e-10 | 0.000913 | 0.000913 | 0.345 | 0.000913 | 0.000913 |
| avg_reroutes | 2.31e-10 | 0.000913 | 0.000913 | 0.91 | 0.000913 | 0.000913 |
| Messages per agent per minute | 9.3e-11 | 0.000913 | 0.000913 | 0.0022 | 0.000913 | 0.000913 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 143.5 ± 1.9 | 75.2 ± 1.9 | 4.08 ± 0.11 | 1.00 ± 2.26 | 0.81 ± 0.01 | 0.07 ± 0.00 | 9.87 ± 0.04 |
| anticipation_only | 143.2 ± 1.8 | 74.9 ± 1.8 | 4.15 ± 0.11 | 0.00 ± 0.00 | 0.81 ± 0.01 | 0.07 ± 0.00 | 9.93 ± 0.05 |
| intentions_only | 141.7 ± 1.8 | 73.5 ± 1.8 | 4.00 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 0.07 ± 0.00 | 16.1 ± 0.1 |
| **after** | 141.6 ± 1.9 | 73.5 ± 1.9 | 4.07 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 0.07 ± 0.00 | 16.2 ± 0.1 |
| all_informed_before | 152.1 ± 2.3 | 82.9 ± 2.2 | 4.49 ± 0.13 | 76.0 ± 45.9 | 0.90 ± 0.00 | 0.34 ± 0.00 | 10.0 ± 0.1 |
| all_informed_after | 135.1 ± 1.5 | 66.5 ± 1.4 | 3.70 ± 0.09 | 0.00 ± 0.00 | 0.89 ± 0.00 | 0.27 ± 0.00 | 23.4 ± 0.2 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 5.05e-08 | 0.486 | 0.486 | 0.97 | 0.000913 | 0.00132 |
| Avg. waiting time (s) | 6.16e-08 | 0.558 | 0.558 | 0.97 | 0.000913 | 0.000913 |
| Avg. queue per approach (veh) | 3.37e-07 | 0.922 | 0.922 | 0.922 | 0.00291 | 0.00291 |
| Spillback (link-seconds) | 4.57e-09 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 3.24e-10 | 0.000913 | 0.000913 | 0.521 | 0.000913 | 0.000913 |
| avg_reroutes | 5.56e-08 | 0.596 | 0.769 | 0.791 | 0.000913 | 0.000913 |
| Messages per agent per minute | 2.53e-10 | 0.000913 | 0.000913 | 0.162 | 0.000913 | 0.000913 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 114.2 ± 1.1 | 48.1 ± 1.0 | 2.27 ± 0.05 | 0.00 ± 0.00 | 0.68 ± 0.03 | 0.04 ± 0.00 | 8.76 ± 0.05 |
| anticipation_only | 114.1 ± 1.3 | 48.0 ± 1.2 | 2.31 ± 0.06 | 0.00 ± 0.00 | 0.66 ± 0.04 | 0.05 ± 0.00 | 8.75 ± 0.06 |
| intentions_only | 113.9 ± 1.3 | 47.8 ± 1.2 | 2.27 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 0.05 ± 0.00 | 13.8 ± 0.1 |
| **after** | 113.5 ± 1.1 | 47.5 ± 1.0 | 2.29 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 0.05 ± 0.00 | 13.9 ± 0.1 |
| all_informed_before | 110.9 ± 0.6 | 44.4 ± 0.5 | 2.11 ± 0.04 | 0.00 ± 0.00 | 0.92 ± 0.00 | 0.21 ± 0.01 | 8.96 ± 0.05 |
| all_informed_after | 105.6 ± 0.4 | 39.3 ± 0.3 | 1.91 ± 0.03 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.19 ± 0.00 | 19.0 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 3.32e-07 | 1 | 1 | 1 | 0.00526 | 0.000913 |
| Avg. waiting time (s) | 1.54e-07 | 1 | 1 | 1 | 0.00233 | 0.000913 |
| Avg. queue per approach (veh) | 2.02e-07 | 1 | 1 | 1 | 0.00233 | 0.000913 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 5.85e-08 | 0.421 | 0.855 | 0.91 | 0.000913 | 0.000913 |
| avg_reroutes | 5.11e-09 | 0.00661 | 0.324 | 0.571 | 0.000913 | 0.000913 |
| Messages per agent per minute | 2.1e-10 | 0.000913 | 0.000913 | 0.427 | 0.000913 | 0.000913 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 167.6 ± 1.0 | 43.1 ± 0.8 | 0.51 ± 0.01 | 27.0 ± 34.9 | 0.51 ± 0.01 | 0.02 ± 0.00 | 6.25 ± 0.01 |
| anticipation_only | 162.3 ± 1.1 | 37.8 ± 0.8 | 0.46 ± 0.01 | 31.0 ± 50.1 | 0.52 ± 0.01 | 0.02 ± 0.00 | 6.21 ± 0.01 |
| intentions_only | 166.1 ± 0.9 | 41.4 ± 0.6 | 0.49 ± 0.01 | 22.0 ± 32.5 | 0.52 ± 0.01 | 0.03 ± 0.00 | 6.88 ± 0.01 |
| **after** | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 21.0 ± 30.6 | 0.54 ± 0.01 | 0.02 ± 0.00 | 6.84 ± 0.01 |
| all_informed_before | 166.6 ± 1.2 | 41.7 ± 0.8 | 0.49 ± 0.01 | 7.00 ± 8.95 | 0.53 ± 0.01 | 0.09 ± 0.01 | 6.23 ± 0.01 |
| all_informed_after | 157.6 ± 0.8 | 32.2 ± 0.5 | 0.40 ± 0.01 | 8.00 ± 12.06 | 0.56 ± 0.01 | 0.09 ± 0.00 | 7.39 ± 0.02 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.42e-09 | 0.000913 | 0.0539 | 0.000913 | 0.000913 | 0.000913 |
| Avg. waiting time (s) | 3.6e-10 | 0.000913 | 0.0058 | 0.000913 | 0.000913 | 0.000913 |
| Avg. queue per approach (veh) | 1.14e-09 | 0.000913 | 0.0113 | 0.000913 | 0.000913 | 0.000913 |
| Spillback (link-seconds) | 0.96 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 6.34e-07 | 0.00291 | 0.0116 | 0.00661 | 0.121 | 0.00526 |
| avg_reroutes | 3.03e-10 | 0.000913 | 0.000913 | 0.014 | 0.000913 | 0.000913 |
| Messages per agent per minute | 7.66e-11 | 0.000913 | 0.000913 | 0.00101 | 0.000913 | 0.000913 |
