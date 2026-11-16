# Experiment `upgrade`

300 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

The upgrade of parts 2 and 3, one mechanism at a time. "before" switches both new mechanisms off: the anticipation rule of the negotiating junctions and the intention sharing of informed drivers. The last two variants repeat the comparison for a fleet in which every driver follows the traffic information.

## grid_light

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 91.3 ± 0.2 | 26.0 ± 0.1 | 0.71 ± 0.01 | 0.00 ± 0.00 | 0.92 ± 0.00 | 0.02 ± 0.00 | 6.68 ± 0.01 |
| anticipation_only | 90.6 ± 0.2 | 25.3 ± 0.1 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.02 ± 0.00 | 6.56 ± 0.01 |
| intentions_only | 91.2 ± 0.2 | 25.8 ± 0.1 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.03 ± 0.00 | 9.28 ± 0.05 |
| **after** | 90.5 ± 0.2 | 25.1 ± 0.2 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.95 ± 0.00 | 0.03 ± 0.00 | 9.21 ± 0.05 |
| all_informed_before | 91.8 ± 0.2 | 26.3 ± 0.1 | 0.71 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.10 ± 0.01 | 6.70 ± 0.03 |
| all_informed_after | 90.7 ± 0.2 | 24.9 ± 0.1 | 0.68 ± 0.01 | 0.00 ± 0.00 | 0.98 ± 0.00 | 0.12 ± 0.00 | 11.6 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 8.31e-08 | 0.00176 | 0.425 | 0.00394 | 0.00123 | 0.425 |
| Avg. waiting time (s) | 5.15e-10 | 0.000913 | 0.0757 | 0.000913 | 0.000913 | 0.0227 |
| Avg. queue per approach (veh) | 0.00112 | 0.312 | 0.623 | 0.615 | 0.129 | 0.216 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 4.05e-10 | 0.000913 | 0.000913 | 0.000913 | 0.00459 | 0.000913 |
| avg_reroutes | 1.05e-10 | 0.000913 | 0.000913 | 0.0113 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.55e-10 | 0.000908 | 0.000908 | 0.064 | 0.000908 | 0.000908 |

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 161.8 ± 1.6 | 95.4 ± 1.5 | 7.08 ± 0.14 | 2.00 ± 3.02 | 0.80 ± 0.01 | 0.07 ± 0.00 | 11.7 ± 0.0 |
| anticipation_only | 162.0 ± 1.5 | 95.5 ± 1.5 | 7.18 ± 0.14 | 2.00 ± 4.52 | 0.80 ± 0.01 | 0.08 ± 0.00 | 11.8 ± 0.1 |
| intentions_only | 158.5 ± 1.4 | 92.3 ± 1.4 | 6.86 ± 0.14 | 2.00 ± 3.02 | 0.77 ± 0.01 | 0.06 ± 0.00 | 20.3 ± 0.1 |
| **after** | 158.4 ± 1.6 | 92.2 ± 1.5 | 6.94 ± 0.14 | 8.00 ± 9.42 | 0.76 ± 0.01 | 0.06 ± 0.00 | 20.5 ± 0.1 |
| all_informed_before | 172.9 ± 2.2 | 105.4 ± 2.1 | 7.78 ± 0.16 | 43.0 ± 26.3 | 0.95 ± 0.00 | 0.36 ± 0.01 | 11.5 ± 0.0 |
| all_informed_after | 149.1 ± 1.1 | 82.7 ± 1.1 | 6.27 ± 0.10 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.28 ± 0.00 | 30.9 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 3.8e-09 | 0.0182 | 0.0108 | 0.623 | 0.000913 | 0.000913 |
| Avg. waiting time (s) | 4.54e-09 | 0.0227 | 0.0174 | 0.571 | 0.000913 | 0.000913 |
| Avg. queue per approach (veh) | 8.05e-09 | 0.0753 | 0.0634 | 0.241 | 0.000913 | 0.000913 |
| Spillback (link-seconds) | 1.56e-05 | 0.562 | 0.491 | 0.562 | 0.0297 | 0.139 |
| Fairness (Jain index) | 2.37e-10 | 0.000913 | 0.000913 | 0.85 | 0.000913 | 0.000913 |
| avg_reroutes | 1.28e-10 | 0.000913 | 0.000913 | 0.0058 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.42e-10 | 0.000908 | 0.000908 | 0.0173 | 0.000908 | 0.000908 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 144.1 ± 1.9 | 75.7 ± 1.9 | 4.11 ± 0.11 | 4.00 ± 3.69 | 0.82 ± 0.01 | 0.07 ± 0.00 | 9.87 ± 0.04 |
| anticipation_only | 144.8 ± 2.1 | 76.5 ± 2.1 | 4.23 ± 0.13 | 9.00 ± 9.20 | 0.81 ± 0.01 | 0.07 ± 0.00 | 9.91 ± 0.05 |
| intentions_only | 141.8 ± 1.9 | 73.6 ± 1.8 | 4.01 ± 0.11 | 1.00 ± 2.26 | 0.79 ± 0.01 | 0.07 ± 0.00 | 16.0 ± 0.1 |
| **after** | 142.2 ± 2.1 | 74.1 ± 2.0 | 4.10 ± 0.12 | 1.00 ± 2.26 | 0.78 ± 0.01 | 0.07 ± 0.00 | 16.2 ± 0.1 |
| all_informed_before | 152.0 ± 4.1 | 82.7 ± 3.9 | 4.50 ± 0.22 | 54.0 ± 32.6 | 0.90 ± 0.01 | 0.33 ± 0.01 | 10.0 ± 0.0 |
| all_informed_after | 135.1 ± 1.4 | 66.6 ± 1.3 | 3.70 ± 0.08 | 0.00 ± 0.00 | 0.89 ± 0.00 | 0.27 ± 0.01 | 23.4 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.4e-07 | 0.324 | 0.227 | 0.521 | 0.00233 | 0.00165 |
| Avg. waiting time (s) | 3.23e-07 | 0.324 | 0.312 | 0.571 | 0.00526 | 0.000913 |
| Avg. queue per approach (veh) | 4.09e-07 | 0.91 | 0.421 | 0.421 | 0.00526 | 0.00165 |
| Spillback (link-seconds) | 7.81e-06 | 0.433 | 0.219 | 1 | 0.00215 | 0.736 |
| Fairness (Jain index) | 7.63e-10 | 0.000913 | 0.00154 | 0.273 | 0.000913 | 0.000913 |
| avg_reroutes | 1.34e-08 | 0.242 | 0.135 | 0.571 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.96e-10 | 0.000913 | 0.000913 | 0.064 | 0.000913 | 0.000913 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 111.8 ± 1.1 | 45.7 ± 1.1 | 2.18 ± 0.06 | 0.00 ± 0.00 | 0.78 ± 0.04 | 0.04 ± 0.00 | 8.74 ± 0.05 |
| anticipation_only | 111.8 ± 1.0 | 45.7 ± 0.9 | 2.20 ± 0.05 | 0.00 ± 0.00 | 0.78 ± 0.03 | 0.04 ± 0.00 | 8.74 ± 0.06 |
| intentions_only | 111.4 ± 1.0 | 45.4 ± 0.9 | 2.16 ± 0.05 | 0.00 ± 0.00 | 0.77 ± 0.03 | 0.05 ± 0.00 | 13.7 ± 0.1 |
| **after** | 111.3 ± 1.0 | 45.2 ± 0.9 | 2.18 ± 0.05 | 0.00 ± 0.00 | 0.76 ± 0.03 | 0.05 ± 0.00 | 13.9 ± 0.1 |
| all_informed_before | 111.1 ± 0.5 | 44.6 ± 0.4 | 2.12 ± 0.03 | 0.00 ± 0.00 | 0.92 ± 0.01 | 0.21 ± 0.01 | 8.95 ± 0.05 |
| all_informed_after | 105.5 ± 0.4 | 39.1 ± 0.4 | 1.90 ± 0.03 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.18 ± 0.00 | 19.0 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 7.36e-05 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 3.04e-05 | 1 | 1 | 1 | 0.849 | 0.000913 |
| Avg. queue per approach (veh) | 1.55e-05 | 1 | 1 | 1 | 0.151 | 0.000913 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 6.8e-08 | 1 | 1 | 1 | 0.000913 | 0.000913 |
| avg_reroutes | 1.27e-08 | 0.0174 | 0.151 | 0.623 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.83e-10 | 0.000913 | 0.000913 | 0.0452 | 0.000913 | 0.000913 |

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
