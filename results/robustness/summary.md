# Experiment `robustness`

140 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Negotiation over an unreliable radio: message latency and message loss on the bus. Max-pressure needs no messages and is shown as the reference point.

## grid_rush_hour

| variant | Avg. time in system (s) | Avg. waiting time (s) | Spillback (link-seconds) | Ambulance response time (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|
| **ideal** | 144.4 ± 2.0 | 76.1 ± 1.9 | 2.00 ± 4.52 | - | 9.91 ± 0.07 |
| latency_1s | 144.3 ± 2.0 | 75.9 ± 1.9 | 1.00 ± 2.26 | - | 9.90 ± 0.06 |
| latency_3s | 144.3 ± 1.9 | 76.0 ± 1.8 | 4.00 ± 6.91 | - | 9.83 ± 0.06 |
| loss_10pct | 144.7 ± 2.3 | 76.4 ± 2.2 | 4.00 ± 6.91 | - | 9.88 ± 0.07 |
| loss_30pct | 144.8 ± 2.0 | 76.4 ± 2.0 | 2.00 ± 3.02 | - | 9.87 ± 0.05 |
| loss_50pct | 145.6 ± 1.7 | 77.3 ± 1.7 | 9.00 ± 9.80 | - | 9.84 ± 0.04 |
| max_pressure | 154.9 ± 2.3 | 86.4 ± 2.2 | 23.0 ± 19.4 | - | 5.56 ± 0.00 |

Tests against **ideal**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs latency_1s | vs latency_3s | vs loss_10pct | vs loss_30pct | vs loss_50pct | vs max_pressure |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000164 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Avg. waiting time (s) | 0.000167 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Spillback (link-seconds) | 0.0496 | 1 | 1 | 1 | 1 | 0.743 | 0.126 |
| Ambulance response time (s) | nan | 1 | 1 | 1 | 1 | 1 | 1 |
| Messages per agent per minute | 1.36e-05 | 0.899 | 0.256 | 0.899 | 0.364 | 0.129 | 0.00101 |

## craiova_center

| variant | Avg. time in system (s) | Avg. waiting time (s) | Spillback (link-seconds) | Ambulance response time (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|
| **ideal** | 167.4 ± 1.1 | 42.9 ± 0.8 | 11.0 ± 15.2 | 103.2 ± 14.2 | 6.25 ± 0.01 |
| latency_1s | 167.5 ± 1.2 | 42.9 ± 0.9 | 24.0 ± 34.4 | 104.2 ± 14.5 | 6.25 ± 0.01 |
| latency_3s | 167.4 ± 1.1 | 42.9 ± 0.9 | 23.0 ± 35.5 | 102.9 ± 13.4 | 6.25 ± 0.01 |
| loss_10pct | 167.7 ± 0.9 | 43.2 ± 0.6 | 17.0 ± 24.1 | 105.3 ± 13.9 | 6.25 ± 0.01 |
| loss_30pct | 167.7 ± 1.1 | 43.2 ± 0.8 | 39.0 ± 51.7 | 105.1 ± 14.9 | 6.25 ± 0.01 |
| loss_50pct | 167.8 ± 1.0 | 43.2 ± 0.7 | 26.0 ± 32.9 | 107.2 ± 14.2 | 6.24 ± 0.01 |
| max_pressure | 211.4 ± 5.5 | 86.4 ± 5.5 | 2983 ± 1034 | 110.0 ± 14.6 | 5.90 ± 0.00 |

Tests against **ideal**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs latency_1s | vs latency_3s | vs loss_10pct | vs loss_30pct | vs loss_50pct | vs max_pressure |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000226 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Avg. waiting time (s) | 0.000254 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Spillback (link-seconds) | 1.94e-05 | 1 | 1 | 1 | 1 | 1 | 0.00079 |
| Ambulance response time (s) | 0.867 | 1 | 1 | 1 | 1 | 1 | 1 |
| Messages per agent per minute | 8.02e-05 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
