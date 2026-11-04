# Experiment `emergency`

160 runs, 10 seeds per configuration. Values are means ± 95% confidence interval (Student t).

Ambulance priority: no priority, local pre-emption and negotiated corridors. Each run is paired with the same run without ambulances to measure the extra delay they cause to the other vehicles.

## grid_emergency

| variant | Ambulance response time (s) | Ambulance delay vs. free flow (s) | Extra delay of other traffic per ambulance (veh-s) | ev_rejections | corridor_conflicts | Avg. time in system (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed/none | 81.9 ± 5.6 | 23.0 ± 2.2 | 147.8 ± 526.3 | 0.00 ± 0.00 | 0.00 ± 0.00 | 138.4 ± 0.4 | 5.55 ± 0.00 |
| fixed/preemption | 65.3 ± 4.8 | 6.44 ± 1.32 | 5230 ± 1303 | 0.00 ± 0.00 | 0.00 ± 0.00 | 142.0 ± 0.8 | 5.56 ± 0.00 |
| fixed/corridor | 63.9 ± 4.3 | 4.87 ± 0.73 | 6193 ± 1109 | 5.00 ± 9.05 | 5.00 ± 9.05 | 142.7 ± 0.9 | 5.73 ± 0.11 |
| negotiation_coord/none | 81.7 ± 5.3 | 24.4 ± 2.2 | 255.2 ± 336.1 | 0.00 ± 0.00 | 0.00 ± 0.00 | 121.7 ± 0.7 | 10.2 ± 0.1 |
| negotiation_coord/preemption | 63.2 ± 3.9 | 6.11 ± 0.82 | 545.0 ± 294.1 | 0.00 ± 0.00 | 0.00 ± 0.00 | 121.9 ± 0.6 | 10.2 ± 0.0 |
| **negotiation_coord/corridor** | 62.4 ± 3.9 | 5.15 ± 0.76 | 710.3 ± 538.7 | 1.00 ± 0.00 | 1.00 ± 0.00 | 122.1 ± 0.7 | 10.3 ± 0.0 |

Tests against **negotiation_coord/corridor**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed/none | vs fixed/preemption | vs fixed/corridor | vs negotiation_coord/none | vs negotiation_coord/preemption |
|---|---:|---:|---:|---:|---:|---:|
| Ambulance response time (s) | 8.17e-07 | 0.00123 | 1 | 1 | 0.00132 | 1 |
| Ambulance delay vs. free flow (s) | 2.69e-08 | 0.000913 | 0.192 | 0.623 | 0.000913 | 0.192 |
| Extra delay of other traffic per ambulance (veh-s) | 9.29e-08 | 0.486 | 0.000985 | 0.000913 | 0.486 | 1 |
| ev_rejections | 2.41e-11 | 7.97e-05 | 7.97e-05 | 0.368 | 7.97e-05 | 7.97e-05 |
| corridor_conflicts | 2.41e-11 | 7.97e-05 | 7.97e-05 | 0.368 | 7.97e-05 | 7.97e-05 |
| Avg. time in system (s) | 1.89e-09 | 0.000913 | 0.000913 | 0.000913 | 1 | 1 |
| Messages per agent per minute | 3.05e-10 | 0.000797 | 0.000797 | 0.000797 | 0.00202 | 0.00202 |

## craiova_center

| variant | Ambulance response time (s) | Ambulance delay vs. free flow (s) | Extra delay of other traffic per ambulance (veh-s) | ev_rejections | corridor_conflicts | Avg. time in system (s) | Messages per agent per minute |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed/none | 122.7 ± 16.9 | 23.6 ± 4.3 | 38.4 ± 239.3 | 0.00 ± 0.00 | 0.00 ± 0.00 | 327.9 ± 10.4 | 5.88 ± 0.00 |
| fixed/preemption | 113.9 ± 14.5 | 14.9 ± 2.6 | -3338 ± 3819 | 0.00 ± 0.00 | 0.00 ± 0.00 | 325.4 ± 10.9 | 5.88 ± 0.00 |
| fixed/corridor | 112.2 ± 14.7 | 13.2 ± 2.7 | -6940 ± 4892 | 0.00 ± 0.00 | 0.00 ± 0.00 | 322.8 ± 11.1 | 5.90 ± 0.00 |
| negotiation_coord/none | 112.4 ± 15.8 | 18.3 ± 3.6 | 172.1 ± 577.5 | 0.00 ± 0.00 | 0.00 ± 0.00 | 167.3 ± 1.3 | 6.23 ± 0.00 |
| negotiation_coord/preemption | 103.1 ± 14.2 | 8.96 ± 2.33 | 683.7 ± 574.2 | 0.00 ± 0.00 | 0.00 ± 0.00 | 167.7 ± 0.9 | 6.23 ± 0.01 |
| **negotiation_coord/corridor** | 103.5 ± 15.0 | 9.45 ± 2.84 | 511.3 ± 549.9 | 0.00 ± 0.00 | 0.00 ± 0.00 | 167.6 ± 1.0 | 6.25 ± 0.01 |

Tests against **negotiation_coord/corridor**: Mann-Whitney U, two-sided, Holm-corrected per metric; Kruskal-Wallis across all variants.

| metric | Kruskal-Wallis p | vs fixed/none | vs fixed/preemption | vs fixed/corridor | vs negotiation_coord/none | vs negotiation_coord/preemption |
|---|---:|---:|---:|---:|---:|---:|
| Ambulance response time (s) | 0.269 | 0.521 | 0.744 | 0.744 | 0.744 | 0.91 |
| Ambulance delay vs. free flow (s) | 1.69e-06 | 0.0022 | 0.0219 | 0.151 | 0.00682 | 0.791 |
| Extra delay of other traffic per ambulance (veh-s) | 0.00137 | 0.216 | 0.312 | 0.0181 | 0.324 | 0.791 |
| ev_rejections | nan | 1 | 1 | 1 | 1 | 1 |
| corridor_conflicts | nan | 1 | 1 | 1 | 1 | 1 |
| Avg. time in system (s) | 1.67e-08 | 0.000913 | 0.000913 | 0.000913 | 1 | 1 |
| Messages per agent per minute | 1.73e-10 | 0.000659 | 0.000659 | 0.000659 | 0.000659 | 0.000659 |
