# Experiment `selfish`

80 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Manipulation test: junction n1_1 multiplies every bid it sends by 5. With credits a bid has to be paid for, so the cheater runs out of credits; without credits nothing stops it. Waiting times are measured at the cheater's own approaches and everywhere else.

## grid_heavy

| variant | Waiting time at the selfish junction (s) | Waiting time at the other junctions (s) | Share of won bids taken by the selfish junction | Avg. time in system (s) | Avg. waiting time (s) |
|---|---:|---:|---:|---:|---:|
| **honest** | 25.0 ± 0.5 | 21.3 ± 0.3 | 0.31 ± 0.06 | 160.1 ± 1.3 | 93.7 ± 1.3 |
| selfish_x5 | 24.9 ± 0.5 | 21.2 ± 0.3 | 0.35 ± 0.06 | 160.0 ± 1.2 | 93.6 ± 1.2 |
| honest_no_credits | 25.0 ± 0.5 | 21.3 ± 0.3 | 0.31 ± 0.06 | 160.1 ± 1.3 | 93.7 ± 1.3 |
| selfish_x5_no_credits | 24.9 ± 0.5 | 21.2 ± 0.3 | 0.36 ± 0.06 | 160.0 ± 1.3 | 93.6 ± 1.3 |

Tests against **honest**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs selfish_x5 | vs honest_no_credits | vs selfish_x5_no_credits |
|---|---:|---:|---:|---:|
| Waiting time at the selfish junction (s) | 0.946 | 1 | 1 | 1 |
| Waiting time at the other junctions (s) | 1 | 1 | 1 | 1 |
| Share of won bids taken by the selfish junction | 0.271 | 0.483 | 1 | 0.421 |
| Avg. time in system (s) | 0.998 | 1 | 1 | 1 |
| Avg. waiting time (s) | 0.998 | 1 | 1 | 1 |

## grid_rush_hour

| variant | Waiting time at the selfish junction (s) | Waiting time at the other junctions (s) | Share of won bids taken by the selfish junction | Avg. time in system (s) | Avg. waiting time (s) |
|---|---:|---:|---:|---:|---:|
| **honest** | 19.6 ± 0.8 | 16.6 ± 0.4 | 0.22 ± 0.04 | 144.4 ± 2.0 | 76.1 ± 1.9 |
| selfish_x5 | 19.6 ± 0.8 | 16.7 ± 0.4 | 0.23 ± 0.04 | 144.5 ± 1.9 | 76.2 ± 1.9 |
| honest_no_credits | 19.6 ± 0.8 | 16.6 ± 0.4 | 0.23 ± 0.04 | 144.4 ± 1.9 | 76.0 ± 1.9 |
| selfish_x5_no_credits | 19.7 ± 0.8 | 16.6 ± 0.4 | 0.25 ± 0.06 | 144.4 ± 1.9 | 76.1 ± 1.9 |

Tests against **honest**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs selfish_x5 | vs honest_no_credits | vs selfish_x5_no_credits |
|---|---:|---:|---:|---:|
| Waiting time at the selfish junction (s) | 0.983 | 1 | 1 | 1 |
| Waiting time at the other junctions (s) | 0.997 | 1 | 1 | 1 |
| Share of won bids taken by the selfish junction | 0.89 | 1 | 1 | 1 |
| Avg. time in system (s) | 0.993 | 1 | 1 | 1 |
| Avg. waiting time (s) | 0.993 | 1 | 1 | 1 |
