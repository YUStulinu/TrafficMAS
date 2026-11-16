# Experiment `upgrade`

300 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

The upgrade of parts 2 and 3, one mechanism at a time. "before" switches both new mechanisms off: the anticipation rule of the negotiating junctions and the intention sharing of informed drivers. The last two variants repeat the comparison for a fleet in which every driver follows the traffic information.

## grid_light

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 91.3 ± 0.2 | 26.0 ± 0.1 | 0.71 ± 0.01 | 0.00 ± 0.00 | 0.92 ± 0.00 | 0.02 ± 0.00 | 6.68 ± 0.01 |
| anticipation_only | 90.6 ± 0.2 | 25.2 ± 0.1 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.02 ± 0.00 | 6.54 ± 0.02 |
| intentions_only | 91.2 ± 0.2 | 25.8 ± 0.1 | 0.70 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.03 ± 0.00 | 9.28 ± 0.05 |
| **after** | 90.3 ± 0.2 | 24.9 ± 0.1 | 0.69 ± 0.01 | 0.00 ± 0.00 | 0.95 ± 0.00 | 0.03 ± 0.00 | 9.20 ± 0.05 |
| all_informed_before | 91.8 ± 0.2 | 26.3 ± 0.1 | 0.71 ± 0.01 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.10 ± 0.01 | 6.70 ± 0.03 |
| all_informed_after | 90.6 ± 0.2 | 24.8 ± 0.2 | 0.68 ± 0.01 | 0.00 ± 0.00 | 0.98 ± 0.00 | 0.12 ± 0.00 | 11.6 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.06e-08 | 0.000985 | 0.151 | 0.00099 | 0.000913 | 0.151 |
| Avg. waiting time (s) | 4.93e-10 | 0.000913 | 0.00917 | 0.000913 | 0.000913 | 0.241 |
| Avg. queue per approach (veh) | 0.00128 | 0.0845 | 0.192 | 0.192 | 0.00657 | 0.521 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 2.91e-10 | 0.000913 | 0.000913 | 0.000913 | 0.000913 | 0.000913 |
| avg_reroutes | 1.69e-10 | 0.000913 | 0.000913 | 0.064 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.4e-10 | 0.000913 | 0.000913 | 0.0211 | 0.000913 | 0.000913 |

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 161.8 ± 1.6 | 95.4 ± 1.5 | 7.08 ± 0.14 | 2.00 ± 3.02 | 0.80 ± 0.01 | 0.07 ± 0.00 | 11.7 ± 0.0 |
| anticipation_only | 161.8 ± 1.6 | 95.3 ± 1.6 | 7.16 ± 0.15 | 3.00 ± 4.83 | 0.81 ± 0.01 | 0.07 ± 0.00 | 11.8 ± 0.1 |
| intentions_only | 158.5 ± 1.4 | 92.3 ± 1.4 | 6.86 ± 0.14 | 2.00 ± 3.02 | 0.77 ± 0.01 | 0.06 ± 0.00 | 20.3 ± 0.1 |
| **after** | 158.5 ± 1.6 | 92.3 ± 1.6 | 6.94 ± 0.14 | 11.0 ± 15.2 | 0.76 ± 0.01 | 0.06 ± 0.00 | 20.5 ± 0.1 |
| all_informed_before | 172.9 ± 2.2 | 105.4 ± 2.1 | 7.78 ± 0.16 | 43.0 ± 26.3 | 0.95 ± 0.00 | 0.36 ± 0.01 | 11.5 ± 0.0 |
| all_informed_after | 148.6 ± 1.0 | 82.1 ± 1.0 | 6.24 ± 0.09 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.28 ± 0.01 | 31.0 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 4.89e-09 | 0.0273 | 0.0273 | 0.91 | 0.000913 | 0.000913 |
| Avg. waiting time (s) | 6.03e-09 | 0.0421 | 0.0421 | 1 | 0.000913 | 0.000913 |
| Avg. queue per approach (veh) | 9.02e-09 | 0.128 | 0.113 | 0.273 | 0.000913 | 0.000913 |
| Spillback (link-seconds) | 4.92e-05 | 1 | 1 | 1 | 0.0765 | 0.311 |
| Fairness (Jain index) | 2.55e-10 | 0.000913 | 0.000913 | 0.473 | 0.000913 | 0.000913 |
| avg_reroutes | 1.85e-10 | 0.000913 | 0.000913 | 0.257 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.36e-10 | 0.000908 | 0.000908 | 0.00911 | 0.000908 | 0.000908 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 144.1 ± 1.9 | 75.7 ± 1.9 | 4.11 ± 0.11 | 4.00 ± 3.69 | 0.82 ± 0.01 | 0.07 ± 0.00 | 9.87 ± 0.04 |
| anticipation_only | 144.0 ± 2.0 | 75.7 ± 2.0 | 4.19 ± 0.12 | 6.00 ± 6.91 | 0.82 ± 0.01 | 0.07 ± 0.00 | 9.91 ± 0.05 |
| intentions_only | 141.8 ± 1.9 | 73.6 ± 1.8 | 4.01 ± 0.11 | 1.00 ± 2.26 | 0.79 ± 0.01 | 0.07 ± 0.00 | 16.0 ± 0.1 |
| **after** | 141.9 ± 2.1 | 73.7 ± 2.1 | 4.08 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 0.07 ± 0.00 | 16.2 ± 0.1 |
| all_informed_before | 152.0 ± 4.1 | 82.7 ± 3.9 | 4.50 ± 0.22 | 54.0 ± 32.6 | 0.90 ± 0.01 | 0.33 ± 0.01 | 10.0 ± 0.0 |
| all_informed_after | 135.0 ± 1.5 | 66.5 ± 1.5 | 3.69 ± 0.09 | 0.00 ± 0.00 | 0.89 ± 0.00 | 0.28 ± 0.01 | 23.4 ± 0.2 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 2.06e-07 | 0.364 | 0.372 | 0.97 | 0.0022 | 0.0022 |
| Avg. waiting time (s) | 3.28e-07 | 0.421 | 0.421 | 0.91 | 0.00403 | 0.00123 |
| Avg. queue per approach (veh) | 6.58e-07 | 0.689 | 0.558 | 0.689 | 0.00526 | 0.00291 |
| Spillback (link-seconds) | 3.25e-06 | 0.134 | 0.23 | 0.736 | 0.00113 | 1 |
| Fairness (Jain index) | 5.88e-10 | 0.00099 | 0.00099 | 0.212 | 0.000913 | 0.000913 |
| avg_reroutes | 8.83e-09 | 0.108 | 0.0518 | 0.521 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.87e-10 | 0.000913 | 0.000913 | 0.0539 | 0.000913 | 0.000913 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 111.8 ± 1.1 | 45.7 ± 1.1 | 2.18 ± 0.06 | 0.00 ± 0.00 | 0.78 ± 0.04 | 0.04 ± 0.00 | 8.74 ± 0.05 |
| anticipation_only | 111.7 ± 0.9 | 45.6 ± 0.8 | 2.20 ± 0.05 | 0.00 ± 0.00 | 0.78 ± 0.03 | 0.05 ± 0.00 | 8.73 ± 0.03 |
| intentions_only | 111.4 ± 1.0 | 45.4 ± 0.9 | 2.16 ± 0.05 | 0.00 ± 0.00 | 0.77 ± 0.03 | 0.05 ± 0.00 | 13.7 ± 0.1 |
| **after** | 111.3 ± 0.9 | 45.2 ± 0.8 | 2.18 ± 0.05 | 0.00 ± 0.00 | 0.77 ± 0.03 | 0.05 ± 0.00 | 13.8 ± 0.1 |
| all_informed_before | 111.1 ± 0.5 | 44.6 ± 0.4 | 2.12 ± 0.03 | 0.00 ± 0.00 | 0.92 ± 0.01 | 0.21 ± 0.01 | 8.95 ± 0.05 |
| all_informed_after | 105.4 ± 0.4 | 39.0 ± 0.4 | 1.90 ± 0.03 | 0.00 ± 0.00 | 0.94 ± 0.00 | 0.18 ± 0.00 | 19.0 ± 0.1 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 6.79e-05 | 1 | 0.965 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 2.47e-05 | 1 | 1 | 1 | 0.849 | 0.000913 |
| Avg. queue per approach (veh) | 1.17e-05 | 1 | 1 | 0.922 | 0.151 | 0.000913 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 6.87e-08 | 1 | 1 | 1 | 0.000913 | 0.000913 |
| avg_reroutes | 1.35e-08 | 0.0421 | 0.242 | 0.521 | 0.000913 | 0.000913 |
| Messages per agent per minute | 1.67e-10 | 0.000913 | 0.000913 | 0.0757 | 0.000913 | 0.000913 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | avg_reroutes | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 167.6 ± 1.0 | 43.1 ± 0.8 | 0.51 ± 0.01 | 27.0 ± 34.9 | 0.51 ± 0.01 | 0.02 ± 0.00 | 6.25 ± 0.01 |
| anticipation_only | 162.2 ± 1.0 | 37.7 ± 0.7 | 0.46 ± 0.01 | 20.0 ± 23.6 | 0.52 ± 0.01 | 0.02 ± 0.00 | 6.21 ± 0.01 |
| intentions_only | 166.1 ± 0.9 | 41.4 ± 0.6 | 0.49 ± 0.01 | 22.0 ± 32.5 | 0.52 ± 0.01 | 0.03 ± 0.00 | 6.88 ± 0.01 |
| **after** | 160.7 ± 1.0 | 36.1 ± 0.8 | 0.44 ± 0.01 | 36.0 ± 58.6 | 0.54 ± 0.01 | 0.02 ± 0.00 | 6.84 ± 0.01 |
| all_informed_before | 166.6 ± 1.2 | 41.7 ± 0.8 | 0.49 ± 0.01 | 7.00 ± 8.95 | 0.53 ± 0.01 | 0.09 ± 0.01 | 6.23 ± 0.01 |
| all_informed_after | 157.3 ± 0.9 | 31.9 ± 0.6 | 0.39 ± 0.01 | 12.0 ± 17.1 | 0.56 ± 0.01 | 0.09 ± 0.00 | 7.39 ± 0.02 |

Tests against **after**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs before | vs anticipation_only | vs intentions_only | vs all_informed_before | vs all_informed_after |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.5e-09 | 0.000913 | 0.064 | 0.000913 | 0.000913 | 0.000913 |
| Avg. waiting time (s) | 3.51e-10 | 0.000913 | 0.00459 | 0.000913 | 0.000913 | 0.000913 |
| Avg. queue per approach (veh) | 1.14e-09 | 0.000913 | 0.0211 | 0.000913 | 0.000913 | 0.000913 |
| Spillback (link-seconds) | 0.99 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 1.88e-06 | 0.0183 | 0.0345 | 0.034 | 0.162 | 0.00853 |
| avg_reroutes | 5.58e-10 | 0.00263 | 0.00175 | 0.0376 | 0.000913 | 0.000913 |
| Messages per agent per minute | 8.31e-11 | 0.000908 | 0.000908 | 0.00283 | 0.000908 | 0.000908 |
