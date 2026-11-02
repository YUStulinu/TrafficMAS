# Experiment `braess`

30 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Braess's paradox. Adding the shortcut A-B makes everybody slower. Informed drivers choose their route selfishly from the congestion broadcasts; uninformed drivers (80% of the conservative profile) take the free-flow shortest route, which is the shortcut.

## braess

| variant | Avg. time in system (s) | Avg. travel time, completed trips (s) | Avg. waiting time (s) | Completed trips (share) | avg_reroutes |
|---|---:|---:|---:|---:|---:|
| **no_shortcut** | 209.3 ± 9.7 | 209.3 ± 9.7 | 55.2 ± 9.7 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| shortcut_informed | 447.1 ± 26.3 | 447.1 ± 26.3 | 315.9 ± 25.7 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| shortcut_uninformed | 683.1 ± 35.9 | 634.0 ± 20.9 | 524.8 ± 20.8 | 0.98 ± 0.01 | 0.00 ± 0.00 |

Tests against **no_shortcut**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs shortcut_informed | vs shortcut_uninformed |
|---|---:|---:|---:|
| Avg. time in system (s) | 2.49e-06 | 0.000365 | 0.000365 |
| Avg. travel time, completed trips (s) | 2.49e-06 | 0.000365 | 0.000365 |
| Avg. waiting time (s) | 2.49e-06 | 0.000365 | 0.000365 |
| Completed trips (share) | 6.63e-06 | 1 | 1 |
| avg_reroutes | nan | 1 | 1 |
