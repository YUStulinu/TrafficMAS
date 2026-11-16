# Experiment `selfish`

80 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Manipulation test: junction n1_1 multiplies every bid it sends by 5. With credits a bid has to be paid for, so the cheater runs out of credits; without credits nothing stops it. Waiting times are measured at the cheater's own approaches and everywhere else.

## grid_heavy

| variant | Waiting time at the selfish junction (s) | Waiting time at the other junctions (s) | Share of won bids taken by the selfish junction | Avg. time in system (s) | Avg. waiting time (s) |
|---|---:|---:|---:|---:|---:|
| **honest** | 21.9 ± 0.5 | 20.7 ± 0.3 | 0.39 ± 0.07 | 156.5 ± 1.4 | 90.3 ± 1.4 |
| selfish_x5 | 21.9 ± 0.5 | 20.7 ± 0.3 | 0.44 ± 0.06 | 156.5 ± 1.4 | 90.3 ± 1.4 |
| honest_no_credits | 21.9 ± 0.5 | 20.7 ± 0.3 | 0.39 ± 0.07 | 156.5 ± 1.4 | 90.3 ± 1.4 |
| selfish_x5_no_credits | 22.0 ± 0.6 | 20.7 ± 0.3 | 0.45 ± 0.06 | 156.4 ± 1.4 | 90.2 ± 1.4 |

Tests against **honest**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs selfish_x5 | vs honest_no_credits | vs selfish_x5_no_credits |
|---|---:|---:|---:|---:|
| Waiting time at the selfish junction (s) | 1 | 1 | 1 | 1 |
| Waiting time at the other junctions (s) | 0.999 | 1 | 1 | 1 |
| Share of won bids taken by the selfish junction | 0.159 | 0.312 | 1 | 0.312 |
| Avg. time in system (s) | 1 | 1 | 1 | 1 |
| Avg. waiting time (s) | 1 | 1 | 1 | 1 |

## grid_rush_hour

| variant | Waiting time at the selfish junction (s) | Waiting time at the other junctions (s) | Share of won bids taken by the selfish junction | Avg. time in system (s) | Avg. waiting time (s) |
|---|---:|---:|---:|---:|---:|
| **honest** | 18.4 ± 0.8 | 16.1 ± 0.4 | 0.39 ± 0.09 | 141.6 ± 1.9 | 73.5 ± 1.9 |
| selfish_x5 | 18.4 ± 0.8 | 16.1 ± 0.4 | 0.41 ± 0.09 | 141.6 ± 1.9 | 73.5 ± 1.9 |
| honest_no_credits | 18.4 ± 0.8 | 16.1 ± 0.4 | 0.39 ± 0.09 | 141.6 ± 1.9 | 73.5 ± 1.9 |
| selfish_x5_no_credits | 18.4 ± 0.8 | 16.1 ± 0.4 | 0.41 ± 0.09 | 141.6 ± 1.9 | 73.5 ± 1.9 |

Tests against **honest**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs selfish_x5 | vs honest_no_credits | vs selfish_x5_no_credits |
|---|---:|---:|---:|---:|
| Waiting time at the selfish junction (s) | 1 | 1 | 1 | 1 |
| Waiting time at the other junctions (s) | 1 | 1 | 1 | 1 |
| Share of won bids taken by the selfish junction | 0.837 | 1 | 1 | 1 |
| Avg. time in system (s) | 1 | 1 | 1 | 1 |
| Avg. waiting time (s) | 1 | 1 | 1 | 1 |
