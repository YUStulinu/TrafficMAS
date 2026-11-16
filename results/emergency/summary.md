# Experiment `emergency`

160 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Ambulance priority: no priority, local pre-emption and negotiated corridors. Each run is paired with the same run without ambulances to measure the extra delay they cause to the other vehicles.

## grid_emergency

| variant | Ambulance response time (s) | Ambulance delay vs. free flow (s) | Extra delay of other traffic per ambulance (veh-s) | ev_rejections | corridor_conflicts | Avg. time in system (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed/none | 81.7 ± 6.0 | 22.9 ± 2.7 | 73.5 ± 165.3 | 0.00 ± 0.00 | 0.00 ± 0.00 | 137.5 ± 0.4 | 12.9 ± 0.1 |
| fixed/preemption | 64.9 ± 4.7 | 6.19 ± 1.20 | 4956 ± 1141 | 0.00 ± 0.00 | 0.00 ± 0.00 | 141.0 ± 0.8 | 13.1 ± 0.1 |
| fixed/corridor | 63.5 ± 4.2 | 4.84 ± 0.78 | 5533 ± 948 | 6.20 ± 8.54 | 6.20 ± 8.54 | 141.4 ± 0.7 | 13.4 ± 0.2 |
| negotiation_coord/none | 81.7 ± 6.2 | 24.7 ± 3.0 | 92.4 ± 358.8 | 0.00 ± 0.00 | 0.00 ± 0.00 | 120.1 ± 0.4 | 16.9 ± 0.1 |
| negotiation_coord/preemption | 62.8 ± 4.5 | 5.79 ± 1.15 | 503.0 ± 520.3 | 0.00 ± 0.00 | 0.00 ± 0.00 | 120.4 ± 0.6 | 16.9 ± 0.1 |
| **negotiation_coord/corridor** | 61.8 ± 4.3 | 4.70 ± 1.02 | 756.2 ± 532.1 | 1.00 ± 0.00 | 1.00 ± 0.00 | 120.5 ± 0.7 | 17.0 ± 0.1 |

Tests against **negotiation_coord/corridor**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed/none | vs fixed/preemption | vs fixed/corridor | vs negotiation_coord/none | vs negotiation_coord/preemption |
|---|---:|---:|---:|---:|---:|---:|
| Ambulance response time (s) | 1.41e-06 | 0.00165 | 0.922 | 1 | 0.00165 | 1 |
| Ambulance delay vs. free flow (s) | 5.79e-08 | 0.000913 | 0.162 | 0.734 | 0.000913 | 0.324 |
| Extra delay of other traffic per ambulance (veh-s) | 7.23e-08 | 0.135 | 0.00132 | 0.000913 | 0.135 | 0.473 |
| ev_rejections | 2.83e-11 | 7.97e-05 | 7.97e-05 | 0.168 | 7.97e-05 | 7.97e-05 |
| corridor_conflicts | 2.83e-11 | 7.97e-05 | 7.97e-05 | 0.168 | 7.97e-05 | 7.97e-05 |
| Avg. time in system (s) | 1.56e-09 | 0.000913 | 0.000913 | 0.000913 | 0.324 | 0.734 |
| Messages per agent per minute | 1.8e-09 | 0.000913 | 0.000913 | 0.000913 | 0.208 | 0.208 |

## craiova_center

| variant | Ambulance response time (s) | Ambulance delay vs. free flow (s) | Extra delay of other traffic per ambulance (veh-s) | ev_rejections | corridor_conflicts | Avg. time in system (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed/none | 122.3 ± 16.5 | 23.2 ± 5.5 | 3.09 ± 303.44 | 0.00 ± 0.00 | 0.00 ± 0.00 | 327.4 ± 10.4 | 6.79 ± 0.18 |
| fixed/preemption | 112.9 ± 14.2 | 13.6 ± 3.0 | -3677 ± 3964 | 0.00 ± 0.00 | 0.00 ± 0.00 | 324.7 ± 10.9 | 6.87 ± 0.19 |
| fixed/corridor | 112.1 ± 14.7 | 12.9 ± 2.7 | -6354 ± 6562 | 0.00 ± 0.00 | 0.00 ± 0.00 | 322.7 ± 11.7 | 6.87 ± 0.20 |
| negotiation_coord/none | 112.1 ± 16.3 | 18.3 ± 3.9 | -130.0 ± 464.7 | 0.00 ± 0.00 | 0.00 ± 0.00 | 160.6 ± 1.0 | 6.83 ± 0.01 |
| negotiation_coord/preemption | 102.2 ± 13.6 | 7.99 ± 2.00 | 214.0 ± 599.7 | 0.00 ± 0.00 | 0.00 ± 0.00 | 160.9 ± 1.0 | 6.83 ± 0.01 |
| **negotiation_coord/corridor** | 102.8 ± 13.9 | 8.79 ± 1.72 | -42.8 ± 434.9 | 0.00 ± 0.00 | 0.00 ± 0.00 | 160.7 ± 1.0 | 6.84 ± 0.01 |

Tests against **negotiation_coord/corridor**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed/none | vs fixed/preemption | vs fixed/corridor | vs negotiation_coord/none | vs negotiation_coord/preemption |
|---|---:|---:|---:|---:|---:|---:|
| Ambulance response time (s) | 0.247 | 0.32 | 0.849 | 0.849 | 0.849 | 0.849 |
| Ambulance delay vs. free flow (s) | 1.87e-06 | 0.00165 | 0.0219 | 0.028 | 0.00526 | 0.345 |
| Extra delay of other traffic per ambulance (veh-s) | 0.00145 | 1 | 0.103 | 0.0229 | 1 | 1 |
| ev_rejections | nan | 1 | 1 | 1 | 1 | 1 |
| corridor_conflicts | nan | 1 | 1 | 1 | 1 | 1 |
| Avg. time in system (s) | 1.66e-08 | 0.000913 | 0.000913 | 0.000913 | 1 | 1 |
| Messages per agent per minute | 0.735 | 1 | 1 | 1 | 0.116 | 0.116 |
