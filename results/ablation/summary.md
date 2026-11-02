# Experiment `ablation`

240 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Remove one mechanism of the negotiating controller at a time to see what each contributes.

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 160.1 ± 1.3 | 93.7 ± 1.3 | 6.97 ± 0.11 | 0.00 ± 0.00 | 0.82 ± 0.01 | 11.8 ± 0.0 |
| no_coordinator | 160.1 ± 1.3 | 93.7 ± 1.3 | 6.96 ± 0.11 | 0.00 ± 0.00 | 0.82 ± 0.01 | 11.8 ± 0.0 |
| no_bids | 160.3 ± 1.6 | 93.9 ± 1.6 | 6.97 ± 0.12 | 1.00 ± 2.26 | 0.82 ± 0.01 | 11.5 ± 0.1 |
| no_credits | 160.1 ± 1.3 | 93.7 ± 1.3 | 6.97 ± 0.11 | 0.00 ± 0.00 | 0.82 ± 0.01 | 11.8 ± 0.0 |
| no_platoons | 160.3 ± 1.3 | 93.9 ± 1.3 | 6.94 ± 0.13 | 0.00 ± 0.00 | 0.83 ± 0.01 | 5.75 ± 0.03 |
| no_commitment | 437.7 ± 15.5 | 370.7 ± 15.2 | 20.0 ± 0.2 | 30514 ± 2953 | 0.80 ± 0.02 | 37.1 ± 0.8 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000158 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.000163 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000127 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 1.77e-10 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 0.00956 | 1 | 1 | 1 | 0.849 | 0.0364 |
| Messages per agent per minute | 1.1e-09 | 1 | 0.000913 | 1 | 0.000913 | 0.000913 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 144.4 ± 2.0 | 76.1 ± 1.9 | 4.15 ± 0.12 | 2.00 ± 4.52 | 0.81 ± 0.01 | 9.91 ± 0.07 |
| no_coordinator | 144.4 ± 1.9 | 76.0 ± 1.9 | 4.14 ± 0.12 | 1.00 ± 2.26 | 0.81 ± 0.01 | 9.89 ± 0.06 |
| no_bids | 144.3 ± 1.9 | 76.0 ± 1.8 | 4.15 ± 0.10 | 2.00 ± 4.52 | 0.81 ± 0.01 | 9.74 ± 0.05 |
| no_credits | 144.4 ± 1.9 | 76.0 ± 1.9 | 4.14 ± 0.12 | 2.00 ± 4.52 | 0.81 ± 0.01 | 9.91 ± 0.07 |
| no_platoons | 144.5 ± 1.7 | 76.2 ± 1.6 | 4.14 ± 0.11 | 7.00 ± 6.79 | 0.81 ± 0.01 | 5.72 ± 0.03 |
| no_commitment | 289.0 ± 9.2 | 220.2 ± 9.2 | 10.2 ± 0.3 | 8052 ± 1104 | 0.63 ± 0.01 | 20.2 ± 0.5 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000162 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.00016 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000165 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 1.69e-07 | 1 | 1 | 1 | 0.646 | 0.000437 |
| Fairness (Jain index) | 0.000163 | 1 | 1 | 1 | 1 | 0.000913 |
| Messages per agent per minute | 2.99e-09 | 1 | 0.00394 | 1 | 0.000913 | 0.000913 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 115.3 ± 1.2 | 49.2 ± 1.1 | 2.33 ± 0.06 | 0.00 ± 0.00 | 0.63 ± 0.04 | 8.76 ± 0.05 |
| no_coordinator | 115.4 ± 1.2 | 49.3 ± 1.1 | 2.33 ± 0.06 | 0.00 ± 0.00 | 0.63 ± 0.04 | 8.77 ± 0.06 |
| no_bids | 115.2 ± 1.1 | 49.1 ± 1.1 | 2.31 ± 0.06 | 0.00 ± 0.00 | 0.63 ± 0.04 | 8.69 ± 0.03 |
| no_credits | 115.3 ± 1.2 | 49.2 ± 1.1 | 2.33 ± 0.06 | 0.00 ± 0.00 | 0.63 ± 0.04 | 8.76 ± 0.05 |
| no_platoons | 115.8 ± 1.2 | 49.7 ± 1.1 | 2.35 ± 0.06 | 0.00 ± 0.00 | 0.63 ± 0.04 | 5.63 ± 0.03 |
| no_commitment | 140.5 ± 2.2 | 74.1 ± 2.2 | 3.43 ± 0.11 | 48.0 ± 85.3 | 0.34 ± 0.02 | 9.59 ± 0.14 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000144 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.00013 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000123 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 0.000795 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 0.000148 | 1 | 1 | 1 | 1 | 0.000913 |
| Messages per agent per minute | 1.87e-08 | 1 | 0.0849 | 1 | 0.000913 | 0.000913 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 167.4 ± 1.1 | 42.9 ± 0.8 | 0.51 ± 0.01 | 11.0 ± 15.2 | 0.51 ± 0.01 | 6.25 ± 0.01 |
| no_coordinator | 167.4 ± 1.1 | 42.9 ± 0.8 | 0.51 ± 0.01 | 18.0 ± 24.5 | 0.51 ± 0.01 | 6.25 ± 0.01 |
| no_bids | 167.4 ± 1.1 | 42.9 ± 0.8 | 0.51 ± 0.01 | 11.0 ± 15.2 | 0.51 ± 0.01 | 6.25 ± 0.01 |
| no_credits | 167.4 ± 1.1 | 42.9 ± 0.8 | 0.51 ± 0.01 | 11.0 ± 15.2 | 0.51 ± 0.01 | 6.25 ± 0.01 |
| no_platoons | 167.5 ± 1.1 | 43.0 ± 0.9 | 0.51 ± 0.01 | 17.0 ± 17.9 | 0.52 ± 0.01 | 5.91 ± 0.00 |
| no_commitment | 177.7 ± 2.6 | 53.0 ± 2.3 | 0.62 ± 0.03 | 91.0 ± 79.7 | 0.39 ± 0.02 | 6.25 ± 0.01 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.00016 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.000157 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.00016 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 0.116 | 1 | 1 | 1 | 1 | 0.16 |
| Fairness (Jain index) | 5.8e-05 | 1 | 1 | 1 | 0.648 | 0.000913 |
| Messages per agent per minute | 0.000123 | 1 | 1 | 1 | 0.000913 | 1 |
