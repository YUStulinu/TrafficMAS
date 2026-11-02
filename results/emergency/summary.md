# Experiment `emergency`

160 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Ambulance priority: no priority, local pre-emption and negotiated corridors. Each run is paired with the same run without ambulances to measure the extra delay they cause to the other vehicles.

## grid_emergency

| variant | Ambulance response time (s) | Ambulance delay vs. free flow (s) | Extra delay of other traffic per ambulance (veh-s) | ev_rejections | corridor_conflicts | Avg. time in system (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed/none | 81.8 ± 5.3 | 23.0 ± 1.8 | 189.2 ± 493.8 | 0.00 ± 0.00 | 0.00 ± 0.00 | 138.4 ± 0.4 | 5.55 ± 0.00 |
| fixed/preemption | 65.4 ± 4.7 | 6.50 ± 1.28 | 5097 ± 1348 | 0.00 ± 0.00 | 0.00 ± 0.00 | 141.9 ± 0.9 | 5.55 ± 0.00 |
| fixed/corridor | 64.1 ± 4.3 | 5.12 ± 0.63 | 6224 ± 1100 | 5.00 ± 9.05 | 5.00 ± 9.05 | 142.7 ± 0.9 | 5.73 ± 0.11 |
| negotiation_coord/none | 81.7 ± 5.3 | 24.4 ± 2.1 | 215.3 ± 385.3 | 0.00 ± 0.00 | 0.00 ± 0.00 | 121.7 ± 0.6 | 10.2 ± 0.1 |
| negotiation_coord/preemption | 63.3 ± 3.9 | 6.18 ± 0.90 | 550.9 ± 299.2 | 0.00 ± 0.00 | 0.00 ± 0.00 | 121.9 ± 0.6 | 10.2 ± 0.0 |
| **negotiation_coord/corridor** | 62.4 ± 3.9 | 5.14 ± 0.76 | 790.1 ± 583.0 | 1.00 ± 0.00 | 1.00 ± 0.00 | 122.1 ± 0.8 | 10.3 ± 0.0 |

Tests against **negotiation_coord/corridor**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed/none | vs fixed/preemption | vs fixed/corridor | vs negotiation_coord/none | vs negotiation_coord/preemption |
|---|---:|---:|---:|---:|---:|---:|
| Ambulance response time (s) | 7.67e-07 | 0.00123 | 1 | 1 | 0.00132 | 1 |
| Ambulance delay vs. free flow (s) | 2.9e-08 | 0.000913 | 0.135 | 0.85 | 0.000913 | 0.135 |
| Extra delay of other traffic per ambulance (veh-s) | 9.42e-08 | 0.364 | 0.00132 | 0.000913 | 0.546 | 1 |
| ev_rejections | 2.41e-11 | 7.97e-05 | 7.97e-05 | 0.368 | 7.97e-05 | 7.97e-05 |
| corridor_conflicts | 2.41e-11 | 7.97e-05 | 7.97e-05 | 0.368 | 7.97e-05 | 7.97e-05 |
| Avg. time in system (s) | 1.74e-09 | 0.000913 | 0.000913 | 0.000913 | 0.769 | 0.791 |
| Messages per agent per minute | 3.51e-10 | 0.000854 | 0.000854 | 0.000854 | 0.00263 | 0.00263 |

## craiova_center

| variant | Ambulance response time (s) | Ambulance delay vs. free flow (s) | Extra delay of other traffic per ambulance (veh-s) | ev_rejections | corridor_conflicts | Avg. time in system (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed/none | 123.7 ± 16.6 | 24.4 ± 4.6 | 111.6 ± 346.8 | 0.00 ± 0.00 | 0.00 ± 0.00 | 327.9 ± 10.4 | 5.88 ± 0.00 |
| fixed/preemption | 114.2 ± 14.2 | 15.0 ± 2.4 | -3667 ± 3692 | 0.00 ± 0.00 | 0.00 ± 0.00 | 325.1 ± 11.1 | 5.88 ± 0.00 |
| fixed/corridor | 112.9 ± 14.6 | 13.8 ± 2.5 | -7439 ± 4976 | 0.00 ± 0.00 | 0.00 ± 0.00 | 322.3 ± 11.4 | 5.90 ± 0.00 |
| negotiation_coord/none | 114.9 ± 16.4 | 20.3 ± 4.8 | -33.8 ± 612.1 | 0.00 ± 0.00 | 0.00 ± 0.00 | 167.4 ± 1.2 | 6.23 ± 0.01 |
| negotiation_coord/preemption | 103.5 ± 14.1 | 9.21 ± 1.69 | -226.7 ± 730.2 | 0.00 ± 0.00 | 0.00 ± 0.00 | 167.2 ± 1.1 | 6.23 ± 0.01 |
| **negotiation_coord/corridor** | 103.2 ± 14.2 | 8.58 ± 1.91 | 43.7 ± 665.4 | 0.00 ± 0.00 | 0.00 ± 0.00 | 167.4 ± 1.1 | 6.25 ± 0.01 |

Tests against **negotiation_coord/corridor**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed/none | vs fixed/preemption | vs fixed/corridor | vs negotiation_coord/none | vs negotiation_coord/preemption |
|---|---:|---:|---:|---:|---:|---:|
| Ambulance response time (s) | 0.233 | 0.32 | 0.744 | 0.744 | 0.744 | 0.97 |
| Ambulance delay vs. free flow (s) | 8.03e-08 | 0.000913 | 0.000985 | 0.0044 | 0.000985 | 0.791 |
| Extra delay of other traffic per ambulance (veh-s) | 0.0026 | 1 | 0.103 | 0.0455 | 1 | 1 |
| ev_rejections | nan | 1 | 1 | 1 | 1 | 1 |
| corridor_conflicts | nan | 1 | 1 | 1 | 1 | 1 |
| Avg. time in system (s) | 1.72e-08 | 0.000913 | 0.000913 | 0.000913 | 1 | 1 |
| Messages per agent per minute | 2.04e-10 | 0.000659 | 0.000659 | 0.000659 | 0.00066 | 0.000769 |
