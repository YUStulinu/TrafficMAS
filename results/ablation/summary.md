# Experiment `ablation`

240 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Remove one mechanism of the negotiating controller at a time to see what each contributes.

## grid_heavy

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 156.5 ± 1.4 | 90.3 ± 1.4 | 6.81 ± 0.13 | 0.00 ± 0.00 | 0.78 ± 0.01 | 20.6 ± 0.1 |
| no_coordinator | 156.4 ± 1.4 | 90.2 ± 1.3 | 6.80 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.00 | 20.6 ± 0.1 |
| no_bids | 156.6 ± 1.5 | 90.4 ± 1.5 | 6.82 ± 0.13 | 0.00 ± 0.00 | 0.78 ± 0.00 | 20.4 ± 0.1 |
| no_credits | 156.5 ± 1.4 | 90.3 ± 1.4 | 6.81 ± 0.13 | 0.00 ± 0.00 | 0.78 ± 0.01 | 20.6 ± 0.1 |
| no_platoons | 156.8 ± 1.5 | 90.6 ± 1.5 | 6.82 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 14.4 ± 0.1 |
| no_commitment | 500.1 ± 12.6 | 430.1 ± 12.2 | 20.9 ± 0.3 | 46213 ± 3746 | 0.74 ± 0.02 | 87.2 ± 6.3 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000136 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.000138 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000145 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 2.65e-11 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 0.00141 | 1 | 1 | 1 | 1 | 0.00504 |
| Messages per agent per minute | 4.87e-09 | 1 | 0.00848 | 1 | 0.000913 | 0.000913 |

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 141.6 ± 1.9 | 73.5 ± 1.9 | 4.07 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 16.2 ± 0.1 |
| no_coordinator | 141.5 ± 1.9 | 73.4 ± 1.9 | 4.06 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 16.2 ± 0.1 |
| no_bids | 141.6 ± 1.9 | 73.4 ± 1.8 | 4.07 ± 0.11 | 0.00 ± 0.00 | 0.78 ± 0.01 | 16.1 ± 0.1 |
| no_credits | 141.6 ± 1.9 | 73.5 ± 1.9 | 4.07 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 16.2 ± 0.1 |
| no_platoons | 141.6 ± 1.8 | 73.4 ± 1.8 | 4.07 ± 0.12 | 0.00 ± 0.00 | 0.78 ± 0.01 | 12.1 ± 0.1 |
| no_commitment | 340.9 ± 11.1 | 272.4 ± 11.1 | 10.5 ± 0.2 | 18332 ± 1469 | 0.54 ± 0.01 | 44.1 ± 3.4 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.00016 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.00016 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000164 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 2.65e-11 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 0.000134 | 1 | 1 | 1 | 1 | 0.000913 |
| Messages per agent per minute | 3.5e-08 | 1 | 0.267 | 1 | 0.000913 | 0.000913 |

## grid_incident

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 113.5 ± 1.1 | 47.5 ± 1.0 | 2.29 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 13.9 ± 0.1 |
| no_coordinator | 113.5 ± 1.1 | 47.4 ± 1.0 | 2.29 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 13.9 ± 0.1 |
| no_bids | 113.5 ± 1.1 | 47.5 ± 1.0 | 2.29 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 13.8 ± 0.1 |
| no_credits | 113.5 ± 1.1 | 47.5 ± 1.0 | 2.29 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 13.9 ± 0.1 |
| no_platoons | 114.0 ± 1.2 | 47.9 ± 1.2 | 2.31 ± 0.06 | 0.00 ± 0.00 | 0.65 ± 0.04 | 10.8 ± 0.1 |
| no_commitment | 150.4 ± 3.6 | 84.0 ± 3.5 | 3.91 ± 0.16 | 1642 ± 122 | 0.28 ± 0.02 | 14.6 ± 0.2 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 9.9e-05 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 9.9e-05 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000119 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 2.65e-11 | 1 | 1 | 1 | 1 | 1 |
| Fairness (Jain index) | 0.000162 | 1 | 1 | 1 | 1 | 0.000913 |
| Messages per agent per minute | 8.27e-08 | 1 | 1 | 1 | 0.000913 | 0.000913 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Avg. queue per approach (veh) | Spillback (link-seconds) | Fairness (Jain index) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|
| **full** | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 21.0 ± 30.6 | 0.54 ± 0.01 | 6.84 ± 0.01 |
| no_coordinator | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 21.0 ± 30.6 | 0.54 ± 0.01 | 6.84 ± 0.01 |
| no_bids | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 21.0 ± 30.6 | 0.54 ± 0.01 | 6.84 ± 0.01 |
| no_credits | 160.7 ± 1.0 | 36.1 ± 0.7 | 0.44 ± 0.01 | 21.0 ± 30.6 | 0.54 ± 0.01 | 6.84 ± 0.01 |
| no_platoons | 160.5 ± 1.0 | 35.9 ± 0.8 | 0.44 ± 0.01 | 25.0 ± 31.3 | 0.54 ± 0.01 | 6.54 ± 0.01 |
| no_commitment | 211.9 ± 16.3 | 87.1 ± 16.2 | 0.79 ± 0.10 | 7834 ± 2348 | 0.15 ± 0.04 | 7.42 ± 0.27 |

Tests against **full**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs no_coordinator | vs no_bids | vs no_credits | vs no_platoons | vs no_commitment |
|---|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000155 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. waiting time (s) | 0.000151 | 1 | 1 | 1 | 1 | 0.000913 |
| Avg. queue per approach (veh) | 0.000146 | 1 | 1 | 1 | 1 | 0.000913 |
| Spillback (link-seconds) | 1.31e-05 | 1 | 1 | 1 | 1 | 0.000659 |
| Fairness (Jain index) | 0.000146 | 1 | 1 | 1 | 1 | 0.000913 |
| Messages per agent per minute | 8.4e-08 | 1 | 1 | 1 | 0.000913 | 0.000913 |
