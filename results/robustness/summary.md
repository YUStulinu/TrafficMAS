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
| **ideal** | 167.6 ± 1.0 | 43.0 ± 0.7 | 27.0 ± 34.9 | 103.5 ± 15.0 | 6.25 ± 0.01 |
| latency_1s | 167.3 ± 1.0 | 42.8 ± 0.7 | 25.0 ± 34.9 | 102.6 ± 13.9 | 6.25 ± 0.01 |
| latency_3s | 167.5 ± 1.2 | 42.9 ± 0.9 | 18.0 ± 30.3 | 102.8 ± 14.0 | 6.25 ± 0.01 |
| loss_10pct | 167.8 ± 0.8 | 43.3 ± 0.5 | 28.0 ± 46.8 | 103.8 ± 14.9 | 6.25 ± 0.01 |
| loss_30pct | 167.2 ± 1.1 | 42.7 ± 0.8 | 15.0 ± 17.9 | 104.7 ± 14.5 | 6.24 ± 0.01 |
| loss_50pct | 167.8 ± 1.3 | 43.3 ± 1.0 | 20.0 ± 23.4 | 106.8 ± 15.5 | 6.24 ± 0.00 |
| max_pressure | 209.1 ± 4.1 | 84.1 ± 4.1 | 2602 ± 908 | 109.3 ± 14.6 | 5.90 ± 0.00 |

Tests against **ideal**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs latency_1s | vs latency_3s | vs loss_10pct | vs loss_30pct | vs loss_50pct | vs max_pressure |
|---|---:|---:|---:|---:|---:|---:|---:|
| Avg. time in system (s) | 0.000206 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Avg. waiting time (s) | 0.000169 | 1 | 1 | 1 | 1 | 1 | 0.0011 |
| Spillback (link-seconds) | 1.9e-05 | 1 | 1 | 1 | 1 | 1 | 0.000896 |
| Ambulance response time (s) | 0.848 | 1 | 1 | 1 | 1 | 1 | 1 |
| Messages per agent per minute | 2.24e-05 | 1 | 1 | 1 | 0.965 | 0.0364 | 0.0011 |
