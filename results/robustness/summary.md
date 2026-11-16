# Experiment `robustness`

140 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Negotiation over an unreliable radio: message latency and message loss on the bus. Max-pressure needs no messages and is shown as the reference point.

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Spillback (link-seconds) | Ambulance response time (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|
| **ideal** | 141.6 ± 1.9 | 73.5 ± 1.9 | 0.00 ± 0.00 | - | 16.2 ± 0.1 |
| latency_1s | 141.4 ± 1.9 | 73.3 ± 1.9 | 0.00 ± 0.00 | - | 16.2 ± 0.1 |
| latency_3s | 141.6 ± 1.7 | 73.4 ± 1.7 | 0.00 ± 0.00 | - | 16.3 ± 0.1 |
| loss_10pct | 141.4 ± 2.0 | 73.3 ± 1.9 | 3.00 ± 4.83 | - | 16.2 ± 0.1 |
| loss_30pct | 141.8 ± 2.0 | 73.6 ± 1.9 | 2.00 ± 3.02 | - | 16.2 ± 0.1 |
| loss_50pct | 142.4 ± 2.0 | 74.2 ± 2.0 | 2.00 ± 4.52 | - | 16.1 ± 0.1 |
| max_pressure | 152.7 ± 2.2 | 84.5 ± 2.2 | 45.0 ± 45.0 | - | 12.4 ± 0.1 |

Tests against **ideal**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs latency_1s | vs latency_3s | vs loss_10pct | vs loss_30pct | vs loss_50pct | vs max_pressure |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000226 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Avg. waiting time (s) | 0.000226 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Spillback (link-seconds) | 0.0013 | 1 | 1 | 1 | 1 | 1 | 1 |
| Ambulance response time (s) | nan | 1 | 1 | 1 | 1 | 1 | 1 |
| Messages per agent per minute | 9.92e-05 | 1 | 1 | 1 | 1 | 1 | 0.0011 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Spillback (link-seconds) | Ambulance response time (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|
| **ideal** | 160.7 ± 1.0 | 36.1 ± 0.7 | 21.0 ± 30.6 | 102.8 ± 13.9 | 6.84 ± 0.01 |
| latency_1s | 160.8 ± 1.1 | 36.2 ± 0.8 | 20.0 ± 26.8 | 102.0 ± 13.7 | 6.85 ± 0.01 |
| latency_3s | 160.9 ± 1.1 | 36.3 ± 0.8 | 27.0 ± 40.2 | 102.6 ± 13.8 | 6.85 ± 0.01 |
| loss_10pct | 160.9 ± 0.9 | 36.3 ± 0.7 | 35.0 ± 56.3 | 102.4 ± 13.7 | 6.84 ± 0.01 |
| loss_30pct | 161.1 ± 1.0 | 36.5 ± 0.8 | 26.0 ± 37.0 | 102.1 ± 13.8 | 6.84 ± 0.01 |
| loss_50pct | 161.4 ± 1.1 | 36.9 ± 0.8 | 24.0 ± 30.0 | 102.4 ± 14.0 | 6.83 ± 0.01 |
| max_pressure | 207.9 ± 4.8 | 82.8 ± 4.7 | 2697 ± 933 | 109.7 ± 15.1 | 6.62 ± 0.05 |

Tests against **ideal**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs latency_1s | vs latency_3s | vs loss_10pct | vs loss_30pct | vs loss_50pct | vs max_pressure |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000136 | 1 | 1 | 1 | 1 | 0.81 | 0.0011 |
| Avg. waiting time (s) | 0.000117 | 1 | 1 | 1 | 1 | 0.606 | 0.0011 |
| Spillback (link-seconds) | 2.38e-05 | 1 | 1 | 1 | 1 | 1 | 0.00079 |
| Ambulance response time (s) | 0.863 | 1 | 1 | 1 | 1 | 1 | 1 |
| Messages per agent per minute | 2.77e-05 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
