# Experiment `main`

250 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

The four baselines against negotiation, with and without the zone coordinators, from off-peak traffic to a saturated grid, an incident and the real Craiova network.

## grid_light

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 123.3 ± 0.3 | 57.7 ± 0.2 | 1.48 ± 0.01 | 18.6 ± 0.6 | 0.00 ± 0.00 | 5654 ± 54 | 1.00 ± 0.00 | 0.96 ± 0.00 | 209.9 ± 0.5 | 5.56 ± 0.00 |
| actuated | 92.8 ± 0.3 | 27.4 ± 0.2 | 0.75 ± 0.01 | 14.7 ± 1.0 | 0.00 ± 0.00 | 5772 ± 53 | 1.00 ± 0.00 | 0.95 ± 0.00 | 192.9 ± 0.5 | 5.56 ± 0.00 |
| max_pressure | 114.0 ± 0.9 | 48.4 ± 0.9 | 1.26 ± 0.02 | 15.2 ± 0.7 | 0.00 ± 0.00 | 5700 ± 53 | 1.00 ± 0.00 | 0.96 ± 0.01 | 206.3 ± 0.8 | 5.56 ± 0.00 |
| negotiation | 91.6 ± 0.2 | 26.3 ± 0.1 | 0.71 ± 0.01 | 10.0 ± 1.1 | 0.00 ± 0.00 | 5684 ± 56 | 1.00 ± 0.00 | 0.93 ± 0.00 | 193.7 ± 0.4 | 6.65 ± 0.02 |
| **negotiation_coord** | 91.6 ± 0.2 | 26.3 ± 0.1 | 0.71 ± 0.01 | 10.0 ± 1.1 | 0.00 ± 0.00 | 5684 ± 56 | 1.00 ± 0.00 | 0.93 ± 0.00 | 193.7 ± 0.4 | 6.65 ± 0.02 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 4.53e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. waiting time (s) | 4.53e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 4.53e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Max. queue (veh) | 1.22e-08 | 0.000573 | 0.000573 | 0.000573 | 1 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 |
| Throughput (veh/h) | 0.0397 | 1 | 0.151 | 1 | 1 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 4.66e-08 | 0.000731 | 0.000731 | 0.000731 | 1 |
| CO2 per trip (g) | 4.24e-08 | 0.000731 | 0.0624 | 0.000731 | 1 |
| Messages per agent per minute | 1.68e-07 | 0.000524 | 0.000524 | 0.000524 | 1 |

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 173.3 ± 2.4 | 106.7 ± 2.4 | 7.79 ± 0.17 | 75.1 ± 3.4 | 167.0 ± 162.8 | 16498 ± 92 | 1.00 ± 0.00 | 0.72 ± 0.02 | 239.7 ± 1.3 | 5.56 ± 0.00 |
| actuated | 167.9 ± 1.8 | 101.3 ± 1.8 | 7.58 ± 0.14 | 74.5 ± 3.9 | 108.0 ± 92.1 | 16893 ± 80 | 1.00 ± 0.00 | 0.73 ± 0.02 | 237.5 ± 1.0 | 5.55 ± 0.00 |
| max_pressure | 164.9 ± 2.0 | 98.4 ± 1.9 | 7.31 ± 0.15 | 57.2 ± 3.0 | 0.00 ± 0.00 | 16740 ± 68 | 1.00 ± 0.00 | 0.75 ± 0.01 | 236.6 ± 1.1 | 5.55 ± 0.00 |
| negotiation | 160.1 ± 1.3 | 93.7 ± 1.3 | 6.96 ± 0.11 | 55.3 ± 3.8 | 0.00 ± 0.00 | 16740 ± 78 | 1.00 ± 0.00 | 0.82 ± 0.01 | 234.8 ± 0.8 | 11.8 ± 0.0 |
| **negotiation_coord** | 160.1 ± 1.3 | 93.7 ± 1.3 | 6.97 ± 0.11 | 55.3 ± 3.8 | 0.00 ± 0.00 | 16745 ± 81 | 1.00 ± 0.00 | 0.82 ± 0.01 | 234.8 ± 0.8 | 11.8 ± 0.0 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 3.48e-08 | 0.000731 | 0.000731 | 0.00202 | 1 |
| Avg. waiting time (s) | 3.86e-08 | 0.000731 | 0.000731 | 0.00202 | 1 |
| Avg. queue per approach (veh) | 1.14e-07 | 0.000731 | 0.000731 | 0.00263 | 1 |
| Max. queue (veh) | 4.84e-07 | 0.000706 | 0.000706 | 1 | 1 |
| Spillback (link-seconds) | 1.49e-05 | 0.00885 | 0.00885 | 1 | 1 |
| Throughput (veh/h) | 4.19e-05 | 0.00682 | 0.0466 | 1 | 1 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 8.32e-08 | 0.000731 | 0.000731 | 0.000731 | 1 |
| CO2 per trip (g) | 3.83e-06 | 0.000731 | 0.00394 | 0.0345 | 1 |
| Messages per agent per minute | 8.85e-08 | 0.000691 | 0.000691 | 0.000691 | 1 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 168.5 ± 2.3 | 99.9 ± 2.3 | 5.35 ± 0.13 | 80.0 ± 0.0 | 573.0 ± 198.6 | 12048 ± 83 | 1.00 ± 0.00 | 0.71 ± 0.02 | 241.4 ± 1.3 | 5.55 ± 0.00 |
| actuated | 152.3 ± 2.6 | 83.8 ± 2.6 | 4.62 ± 0.15 | 77.9 ± 3.6 | 338.0 ± 257.8 | 12353 ± 72 | 1.00 ± 0.00 | 0.74 ± 0.03 | 232.9 ± 1.5 | 5.55 ± 0.00 |
| max_pressure | 154.9 ± 2.3 | 86.4 ± 2.2 | 4.70 ± 0.14 | 61.1 ± 4.8 | 23.0 ± 19.4 | 12197 ± 72 | 1.00 ± 0.00 | 0.82 ± 0.01 | 235.6 ± 1.3 | 5.56 ± 0.00 |
| negotiation | 144.4 ± 1.9 | 76.0 ± 1.9 | 4.14 ± 0.12 | 57.3 ± 3.4 | 1.00 ± 2.26 | 12155 ± 93 | 1.00 ± 0.00 | 0.81 ± 0.01 | 231.0 ± 1.1 | 9.89 ± 0.06 |
| **negotiation_coord** | 144.4 ± 2.0 | 76.1 ± 1.9 | 4.15 ± 0.12 | 57.3 ± 3.4 | 2.00 ± 4.52 | 12175 ± 99 | 1.00 ± 0.00 | 0.81 ± 0.01 | 231.0 ± 1.1 | 9.91 ± 0.07 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 2.25e-08 | 0.000731 | 0.00154 | 0.000731 | 1 |
| Avg. waiting time (s) | 2.36e-08 | 0.000731 | 0.00154 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 2.15e-08 | 0.000731 | 0.000879 | 0.000731 | 1 |
| Max. queue (veh) | 2.33e-07 | 0.000248 | 0.000799 | 0.367 | 1 |
| Spillback (link-seconds) | 1.1e-07 | 0.000347 | 0.00114 | 0.0421 | 1 |
| Throughput (veh/h) | 0.000248 | 0.113 | 0.0183 | 1 | 1 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 6.66e-07 | 0.000731 | 0.00132 | 0.769 | 1 |
| CO2 per trip (g) | 1.99e-07 | 0.000731 | 0.0903 | 0.00099 | 0.94 |
| Messages per agent per minute | 2.52e-07 | 0.000637 | 0.000637 | 0.000637 | 0.762 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 144.8 ± 1.8 | 78.7 ± 1.7 | 3.64 ± 0.08 | 80.0 ± 0.0 | 1043 ± 131 | 10347 ± 69 | 1.00 ± 0.00 | 0.57 ± 0.03 | 222.9 ± 1.2 | 5.55 ± 0.00 |
| actuated | 126.2 ± 1.9 | 60.1 ± 1.9 | 2.86 ± 0.10 | 80.0 ± 0.0 | 898.0 ± 168.0 | 10551 ± 81 | 1.00 ± 0.00 | 0.41 ± 0.03 | 212.9 ± 1.1 | 5.55 ± 0.00 |
| max_pressure | 131.6 ± 1.4 | 65.4 ± 1.3 | 3.07 ± 0.07 | 70.7 ± 5.8 | 37.0 ± 55.6 | 10429 ± 78 | 1.00 ± 0.00 | 0.68 ± 0.03 | 217.4 ± 1.0 | 5.55 ± 0.00 |
| negotiation | 115.4 ± 1.2 | 49.3 ± 1.1 | 2.33 ± 0.06 | 57.4 ± 9.0 | 0.00 ± 0.00 | 10399 ± 88 | 1.00 ± 0.00 | 0.63 ± 0.04 | 210.4 ± 0.8 | 8.77 ± 0.06 |
| **negotiation_coord** | 115.3 ± 1.2 | 49.2 ± 1.1 | 2.33 ± 0.06 | 57.3 ± 8.9 | 0.00 ± 0.00 | 10386 ± 85 | 1.00 ± 0.00 | 0.63 ± 0.04 | 210.4 ± 0.8 | 8.76 ± 0.05 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 5.18e-09 | 0.000731 | 0.000731 | 0.000731 | 0.91 |
| Avg. waiting time (s) | 5.19e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 6.58e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Max. queue (veh) | 7.89e-08 | 0.000255 | 0.000255 | 0.0225 | 1 |
| Spillback (link-seconds) | 1.11e-08 | 0.000252 | 0.000252 | 0.07 | 1 |
| Throughput (veh/h) | 0.00868 | 1 | 0.0232 | 1 | 1 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 3.67e-07 | 0.0174 | 0.000731 | 0.0753 | 0.85 |
| CO2 per trip (g) | 1.7e-08 | 0.000731 | 0.00722 | 0.000731 | 0.91 |
| Messages per agent per minute | 2.09e-07 | 0.000634 | 0.000634 | 0.000634 | 0.91 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 322.8 ± 11.1 | 194.3 ± 10.2 | 1.45 ± 0.05 | 61.5 ± 1.1 | 12055 ± 1593 | 4089 ± 43 | 1.00 ± 0.00 | 0.13 ± 0.02 | 419.5 ± 5.8 | 5.90 ± 0.00 |
| actuated | 166.3 ± 2.6 | 41.8 ± 2.4 | 0.51 ± 0.03 | 25.5 ± 1.3 | 472.0 ± 345.7 | 5130 ± 54 | 1.00 ± 0.00 | 0.52 ± 0.03 | 335.4 ± 1.9 | 5.90 ± 0.00 |
| max_pressure | 209.1 ± 4.1 | 84.1 ± 4.1 | 0.93 ± 0.02 | 25.8 ± 0.7 | 2602 ± 908 | 5051 ± 54 | 1.00 ± 0.00 | 0.50 ± 0.04 | 362.1 ± 2.4 | 5.90 ± 0.00 |
| negotiation | 167.5 ± 0.9 | 43.0 ± 0.7 | 0.51 ± 0.01 | 21.8 ± 2.1 | 26.0 ± 33.1 | 5045 ± 51 | 1.00 ± 0.00 | 0.51 ± 0.01 | 336.9 ± 1.3 | 6.25 ± 0.01 |
| **negotiation_coord** | 167.6 ± 1.0 | 43.0 ± 0.7 | 0.51 ± 0.01 | 21.8 ± 2.1 | 27.0 ± 34.9 | 5046 ± 49 | 1.00 ± 0.00 | 0.51 ± 0.01 | 336.9 ± 1.3 | 6.25 ± 0.01 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.18e-07 | 0.000731 | 1 | 0.000731 | 1 |
| Avg. waiting time (s) | 1.08e-07 | 0.000731 | 0.769 | 0.000731 | 0.85 |
| Avg. queue per approach (veh) | 1.01e-07 | 0.000731 | 0.615 | 0.000731 | 0.909 |
| Max. queue (veh) | 6.9e-07 | 0.00034 | 0.0167 | 0.0133 | 1 |
| Spillback (link-seconds) | 2.01e-08 | 0.000598 | 0.0153 | 0.000598 | 1 |
| Throughput (veh/h) | 5.49e-06 | 0.000731 | 0.0421 | 1 | 1 |
| Completed trips (share) | 0.00023 | 0.0597 | 1 | 1 | 1 |
| Fairness (Jain index) | 7.19e-05 | 0.000731 | 1 | 1 | 1 |
| CO2 per trip (g) | 1.05e-07 | 0.000731 | 0.689 | 0.000731 | 0.97 |
| Messages per agent per minute | 3.04e-07 | 0.000727 | 0.000727 | 0.000727 | 0.91 |
