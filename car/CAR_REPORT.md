# Finlay (Aegypti) CAR Experiment

Generated: 2026-09-07T01:57:49.684796+00:00
Aegypti version: unknown
Seed: 20260629

Three subjects on 12330 instances, scored against an independent exact oracle:
**Aegypti**, **Chiba-Nishizeki**, and **matrix multiplication**. The benchmark adds
dense small-clique families (complete tri-/four-partite, balanced bipartite + one
edge) and an exhaustive sweep of all graphs with n <= 7 (Graph Atlas), to
stress the dense branch.

## Headline

- Instances: 12330  (with a triangle: 8860)
- Aegypti correct: 12330/12330  (misses: 0)
- Chiba-Nishizeki correct: 12330/12330
- Matrix multiplication correct: 12330/12330
- Invalid witnesses: 0    All three agree: 12330/12330

### Dense-branch diagnostics

- Dense-regime instances: 5639  (triangle-containing: 4799)
- Dense-branch misses on positives: 0

## By regime

| regime | instances | truth_positive | aegypti_misses | dense_instances | dense_positives | mean_aegypti_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 5639 | 4799 | 0 | 5639 | 4799 | 0.2869 | 0.0340 |
| sparse | 6691 | 4061 | 0 | 0 | 0 | 0.1059 | 0.0208 |

## By family

| family | instances | truth_positive | aegypti_misses | dense_instances | dense_positives | mean_aegypti_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| atlas_exhaustive_n<=7 | 1244 | 1080 | 0 | 91 | 91 | 0.0452 | 0.0077 |
| er_dense | 2500 | 2500 | 0 | 2425 | 2425 | 0.3221 | 0.0304 |
| er_sparse | 2486 | 1139 | 0 | 0 | 0 | 0.1298 | 0.0252 |
| near_turan | 400 | 400 | 0 | 400 | 400 | 0.2942 | 0.0208 |
| omega3_tripartite | 400 | 400 | 0 | 400 | 400 | 0.1904 | 0.0163 |
| omega4_fourpartite | 300 | 300 | 0 | 300 | 300 | 0.2864 | 0.0195 |
| planted_clique | 1000 | 1000 | 0 | 987 | 987 | 0.2576 | 0.0224 |
| planted_triangle | 1500 | 1500 | 0 | 0 | 0 | 0.1173 | 0.0221 |
| structured | 1000 | 541 | 0 | 365 | 196 | 0.1449 | 0.0264 |
| tri_free_bipartite | 1500 | 0 | 0 | 671 | 0 | 0.1894 | 0.0537 |

## Reproduction

    pip install aegypti
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
