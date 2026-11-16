# Experiment `braess`

30 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Braess's paradox. Adding the shortcut A-B makes everybody slower. Informed drivers choose their route selfishly from the congestion broadcasts; uninformed drivers (80% of the conservative profile) take the free-flow shortest route, which is the shortcut.

## braess

| variant | Avg. time in system (s) | Avg. travel time, completed trips (s) | Avg. waiting time (s) | Completed trips (share) | avg_reroutes |
|---|---:|---:|---:|---:|---:|
| **no_shortcut** | 177.8 ± 4.0 | 177.8 ± 4.0 | 23.5 ± 4.0 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| shortcut_informed | 286.8 ± 18.4 | 286.8 ± 18.4 | 150.4 ± 17.7 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| shortcut_uninformed | 662.8 ± 32.5 | 616.7 ± 15.7 | 506.7 ± 15.3 | 0.98 ± 0.01 | 0.00 ± 0.00 |

Tests against **no_shortcut**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs shortcut_informed | vs shortcut_uninformed |
|---|---:|---:|---:|
| Avg. time in system (s) | 2.49e-06 | 0.000365 | 0.000365 |
| Avg. travel time, completed trips (s) | 2.49e-06 | 0.000365 | 0.000365 |
| Avg. waiting time (s) | 2.49e-06 | 0.000365 | 0.000365 |
| Completed trips (share) | 3.64e-05 | 1 | 1 |
| avg_reroutes | nan | 1 | 1 |
