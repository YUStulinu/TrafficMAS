# Experiment `main`

250 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

The four baselines against negotiation, with and without the zone coordinators, from off-peak traffic to a saturated grid, an incident and the real Craiova network.

## grid_light

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 123.1 ± 0.3 | 57.4 ± 0.3 | 1.47 ± 0.02 | 17.3 ± 0.8 | 0.00 ± 0.00 | 5645 ± 55 | 1.00 ± 0.00 | 0.97 ± 0.00 | 209.3 ± 0.5 | 8.48 ± 0.04 |
| actuated | 92.7 ± 0.3 | 27.2 ± 0.2 | 0.74 ± 0.01 | 14.3 ± 0.8 | 0.00 ± 0.00 | 5769 ± 53 | 1.00 ± 0.00 | 0.96 ± 0.00 | 192.6 ± 0.5 | 8.35 ± 0.04 |
| max_pressure | 113.4 ± 0.9 | 47.8 ± 0.8 | 1.24 ± 0.02 | 15.0 ± 0.8 | 0.00 ± 0.00 | 5694 ± 53 | 1.00 ± 0.00 | 0.96 ± 0.01 | 205.8 ± 0.8 | 8.54 ± 0.04 |
| negotiation | 90.5 ± 0.2 | 25.1 ± 0.1 | 0.69 ± 0.01 | 9.10 ± 0.53 | 0.00 ± 0.00 | 5766 ± 47 | 1.00 ± 0.00 | 0.95 ± 0.00 | 193.8 ± 0.5 | 9.17 ± 0.04 |
| **negotiation_coord** | 90.5 ± 0.2 | 25.1 ± 0.1 | 0.69 ± 0.01 | 9.10 ± 0.53 | 0.00 ± 0.00 | 5766 ± 47 | 1.00 ± 0.00 | 0.95 ± 0.00 | 193.8 ± 0.5 | 9.17 ± 0.04 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 4.53e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. waiting time (s) | 4.53e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 4.53e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Max. queue (veh) | 1.58e-08 | 0.000556 | 0.000556 | 0.000556 | 1 |
| Spillback (link-seconds) | nan | 1 | 1 | 1 | 1 |
| Throughput (veh/h) | 0.00356 | 0.0183 | 1 | 0.162 | 1 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 1.01e-05 | 0.000731 | 0.034 | 0.242 | 1 |
| CO2 per trip (g) | 1.37e-08 | 0.000731 | 0.0044 | 0.000731 | 1 |
| Messages per agent per minute | 1.12e-08 | 0.000731 | 0.000731 | 0.000731 | 1 |

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 173.5 ± 2.1 | 107.2 ± 2.1 | 7.80 ± 0.15 | 75.1 ± 3.7 | 134.0 ± 119.2 | 16428 ± 136 | 1.00 ± 0.00 | 0.68 ± 0.02 | 239.1 ± 1.1 | 14.3 ± 0.1 |
| actuated | 166.9 ± 1.7 | 100.6 ± 1.7 | 7.52 ± 0.14 | 75.0 ± 3.8 | 175.0 ± 150.3 | 16871 ± 79 | 1.00 ± 0.00 | 0.70 ± 0.02 | 236.2 ± 1.0 | 15.1 ± 0.1 |
| max_pressure | 163.5 ± 1.7 | 97.3 ± 1.7 | 7.22 ± 0.14 | 58.5 ± 3.7 | 0.00 ± 0.00 | 16732 ± 86 | 1.00 ± 0.00 | 0.71 ± 0.01 | 235.2 ± 1.0 | 14.5 ± 0.1 |
| negotiation | 156.4 ± 1.4 | 90.2 ± 1.3 | 6.80 ± 0.12 | 55.4 ± 3.8 | 0.00 ± 0.00 | 16959 ± 75 | 1.00 ± 0.00 | 0.78 ± 0.00 | 232.7 ± 0.7 | 20.6 ± 0.1 |
| **negotiation_coord** | 156.5 ± 1.4 | 90.3 ± 1.4 | 6.81 ± 0.13 | 55.4 ± 3.8 | 0.00 ± 0.00 | 16955 ± 72 | 1.00 ± 0.00 | 0.78 ± 0.01 | 232.7 ± 0.8 | 20.6 ± 0.1 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 9.98e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. waiting time (s) | 1.03e-08 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 3.03e-08 | 0.000731 | 0.000731 | 0.00117 | 0.94 |
| Max. queue (veh) | 6.16e-07 | 0.000907 | 0.000915 | 0.257 | 1 |
| Spillback (link-seconds) | 4.2e-06 | 1 | 0.00299 | 1 | 1 |
| Throughput (veh/h) | 1.13e-06 | 0.000731 | 0.28 | 0.00231 | 0.94 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 1.65e-07 | 0.000731 | 0.000731 | 0.000731 | 0.94 |
| CO2 per trip (g) | 6.38e-08 | 0.000731 | 0.00099 | 0.00263 | 1 |
| Messages per agent per minute | 6.56e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 169.2 ± 3.1 | 100.8 ± 3.0 | 5.33 ± 0.14 | 80.0 ± 0.0 | 978.0 ± 320.1 | 11909 ± 107 | 1.00 ± 0.00 | 0.65 ± 0.03 | 241.2 ± 1.7 | 12.0 ± 0.1 |
| actuated | 151.1 ± 2.2 | 82.7 ± 2.1 | 4.56 ± 0.13 | 78.7 ± 1.9 | 419.0 ± 242.0 | 12340 ± 73 | 1.00 ± 0.00 | 0.71 ± 0.03 | 231.7 ± 1.2 | 12.6 ± 0.1 |
| max_pressure | 152.7 ± 2.2 | 84.5 ± 2.2 | 4.60 ± 0.14 | 71.6 ± 4.3 | 45.0 ± 45.0 | 12194 ± 84 | 1.00 ± 0.00 | 0.79 ± 0.02 | 233.9 ± 1.1 | 12.4 ± 0.1 |
| negotiation | 141.5 ± 1.9 | 73.4 ± 1.9 | 4.06 ± 0.12 | 57.9 ± 5.6 | 0.00 ± 0.00 | 12363 ± 72 | 1.00 ± 0.00 | 0.78 ± 0.01 | 229.3 ± 1.1 | 16.2 ± 0.1 |
| **negotiation_coord** | 141.6 ± 1.9 | 73.5 ± 1.9 | 4.07 ± 0.12 | 57.2 ± 4.5 | 0.00 ± 0.00 | 12363 ± 72 | 1.00 ± 0.00 | 0.78 ± 0.01 | 229.4 ± 1.1 | 16.2 ± 0.1 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.47e-08 | 0.000731 | 0.000731 | 0.000731 | 0.85 |
| Avg. waiting time (s) | 1.37e-08 | 0.000731 | 0.000731 | 0.000731 | 0.85 |
| Avg. queue per approach (veh) | 1.93e-08 | 0.000731 | 0.000731 | 0.000731 | 0.94 |
| Max. queue (veh) | 4.28e-08 | 0.000254 | 0.000393 | 0.00174 | 1 |
| Spillback (link-seconds) | 9.95e-09 | 0.000254 | 0.000254 | 0.0119 | 1 |
| Throughput (veh/h) | 8.67e-06 | 0.000985 | 1 | 0.0219 | 1 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 3.26e-07 | 0.000731 | 0.00231 | 0.151 | 0.91 |
| CO2 per trip (g) | 8.37e-08 | 0.000731 | 0.0116 | 0.00132 | 0.85 |
| Messages per agent per minute | 7.4e-09 | 0.000731 | 0.000731 | 0.000731 | 0.85 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 143.3 ± 2.1 | 77.3 ± 2.0 | 3.59 ± 0.10 | 80.0 ± 0.0 | 974.0 ± 156.9 | 10386 ± 90 | 1.00 ± 0.00 | 0.58 ± 0.04 | 221.9 ± 1.3 | 11.1 ± 0.1 |
| actuated | 124.7 ± 2.0 | 58.6 ± 1.9 | 2.79 ± 0.10 | 80.0 ± 0.0 | 868.0 ± 203.1 | 10545 ± 81 | 1.00 ± 0.00 | 0.42 ± 0.04 | 211.9 ± 1.2 | 11.2 ± 0.1 |
| max_pressure | 131.0 ± 1.2 | 64.9 ± 1.1 | 3.04 ± 0.06 | 64.1 ± 6.3 | 13.0 ± 29.4 | 10432 ± 75 | 1.00 ± 0.00 | 0.71 ± 0.04 | 217.0 ± 0.8 | 11.2 ± 0.1 |
| negotiation | 113.5 ± 1.1 | 47.4 ± 1.0 | 2.29 ± 0.06 | 52.2 ± 7.7 | 0.00 ± 0.00 | 10568 ± 76 | 1.00 ± 0.00 | 0.65 ± 0.04 | 209.4 ± 0.8 | 13.9 ± 0.1 |
| **negotiation_coord** | 113.5 ± 1.1 | 47.5 ± 1.0 | 2.29 ± 0.06 | 52.4 ± 7.9 | 0.00 ± 0.00 | 10565 ± 77 | 1.00 ± 0.00 | 0.65 ± 0.04 | 209.5 ± 0.8 | 13.9 ± 0.1 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 4.74e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. waiting time (s) | 4.74e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 5.17e-09 | 0.000731 | 0.000731 | 0.000731 | 1 |
| Max. queue (veh) | 7.66e-08 | 0.000254 | 0.000254 | 0.068 | 1 |
| Spillback (link-seconds) | 5.42e-09 | 0.000254 | 0.000254 | 0.736 | 1 |
| Throughput (veh/h) | 0.00301 | 0.0362 | 0.991 | 0.0516 | 0.991 |
| Completed trips (share) | nan | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 3.16e-07 | 0.00661 | 0.000731 | 0.0903 | 0.94 |
| CO2 per trip (g) | 1.6e-08 | 0.000731 | 0.00565 | 0.000731 | 0.94 |
| Messages per agent per minute | 8.5e-08 | 0.000731 | 0.000731 | 0.000731 | 1 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Max. queue (veh) | Spillback (link-seconds) | Throughput (veh/h) | Completed trips (share) | Fairness (Jain index) | CO2 per trip (g) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | 322.7 ± 11.7 | 194.0 ± 10.8 | 1.45 ± 0.04 | 61.0 ± 0.0 | 12048 ± 1604 | 4095 ± 46 | 1.00 ± 0.00 | 0.13 ± 0.01 | 419.4 ± 6.1 | 6.87 ± 0.20 |
| actuated | 165.1 ± 2.5 | 40.4 ± 2.4 | 0.49 ± 0.02 | 25.9 ± 2.0 | 491.0 ± 493.9 | 5138 ± 49 | 1.00 ± 0.00 | 0.53 ± 0.04 | 334.9 ± 1.7 | 6.55 ± 0.01 |
| max_pressure | 207.9 ± 4.8 | 82.8 ± 4.7 | 0.91 ± 0.03 | 25.8 ± 0.7 | 2697 ± 933 | 5044 ± 58 | 1.00 ± 0.00 | 0.49 ± 0.04 | 361.3 ± 2.8 | 6.62 ± 0.05 |
| negotiation | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 19.3 ± 2.3 | 21.0 ± 30.6 | 5132 ± 53 | 1.00 ± 0.00 | 0.54 ± 0.01 | 333.8 ± 1.3 | 6.84 ± 0.01 |
| **negotiation_coord** | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 19.3 ± 2.3 | 21.0 ± 30.6 | 5132 ± 53 | 1.00 ± 0.00 | 0.54 ± 0.01 | 333.8 ± 1.3 | 6.84 ± 0.01 |

Tests against **negotiation_coord**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed | vs actuated | vs max_pressure | vs negotiation |
|---|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 1.22e-08 | 0.000731 | 0.00341 | 0.000731 | 1 |
| Avg. waiting time (s) | 7.61e-09 | 0.000731 | 0.00117 | 0.000731 | 1 |
| Avg. queue per approach (veh) | 1.09e-08 | 0.000731 | 0.00263 | 0.000731 | 1 |
| Max. queue (veh) | 3.52e-08 | 0.00025 | 0.00141 | 0.000912 | 1 |
| Spillback (link-seconds) | 1.36e-08 | 0.000527 | 0.00766 | 0.000527 | 1 |
| Throughput (veh/h) | 4.29e-06 | 0.000731 | 1 | 0.034 | 1 |
| Completed trips (share) | 0.00023 | 0.0597 | 1 | 1 | 1 |
| Fairness (Jain index) | 1.52e-05 | 0.000731 | 1 | 0.113 | 1 |
| CO2 per trip (g) | 8.91e-08 | 0.000731 | 0.425 | 0.000731 | 1 |
| Messages per agent per minute | 2.16e-06 | 1 | 0.000731 | 0.000731 | 1 |
